"""Packed-forest chart parser over M3 constructions (N1 obligation from ledger S39).

The M3 matcher enumerates every phrase over every span and is exponential in attachment ambiguity.
This parser is an Earley recogniser over the construction inventory whose items are slots: a
lexical slot matches one token reading of the slot's category (with the slot's feature/lemma
requirements), a phrase slot matches a completed phrase of the slot's `phrase` type.  Completed
phrases are *packed* per (start, end, phrase type, construction, bound-readings digest): the chart
records derivation COUNTS and one representative derivation, so the number of analyses is exact and
polynomial to compute while only one meaning per packed node is ever built.  Verdicts:

  INTERPRETED           exactly one clause-level derivation spans the whole utterance
  AMBIGUOUS(k)          k > 1 derivations (k is exact; the representative meanings of up to
                        `max_unpack` derivations are unpacked for the clarification policy)
  UNKNOWN_LEXEME        a token has no live reading
  UNKNOWN_CONSTRUCTION  no clause-level derivation spans the utterance

Templates are applied exactly as in the M3 matcher (bindings: slot name → Reading or Phrase), so a
parse agrees with the matcher wherever the matcher terminates.
"""
from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any, Hashable, Iterable, Sequence

from ocm.kso.warrant import Liveness, WarrantProfile, meet_all_profiles
from ocm.language.constructions import Construction, Phrase, Slot
from ocm.language.lexicon import Lexicon, Reading


@dataclass
class Packed:
    """A packed node: all derivations of `construction` over [start, end) with the same lexical readings
    (derivations differing only in how sub-phrases attach are packed together and counted)."""
    construction: Construction
    start: int
    end: int
    key: tuple = ()
    count: int = 0
    bindings: dict[str, Any] | None = None          # one representative binding (slot → Reading | Packed)
    warrant: WarrantProfile | None = None
    phrase: Phrase | None = None                    # built lazily from the representative binding


def _slot_accepts_reading(slot: Slot, r: Reading) -> bool:
    if slot.phrase is not None or r.category is not slot.category:
        return False
    if slot.lemma is not None and r.lemma != slot.lemma:
        return False
    feats = dict(r.features)
    for k, v in slot.features:
        if feats.get(k) != v:
            return False
    if any(k not in feats for k in slot.requires) or any(k in feats for k in slot.forbids):
        return False
    return True


def _lex_key(b: dict[str, Any]) -> tuple:
    """Identity of the lexical readings bound so far (sense ids); packed phrases contribute their own key."""
    out = []
    for k in sorted(b):
        v = b[k]
        if isinstance(v, Reading):
            out.append((k, v.lemma, v.sense.sense_id if v.sense else None, tuple(sorted(v.features))))
        else:
            out.append((k, "P", v.key))
    return tuple(out)


class ChartCap(Exception):
    """The declared item cap was exceeded: the sentence is CANNOT_CHECK under this inventory (never a silent truncation)."""


def parse(tokens: Sequence[str], lexicon: Lexicon, constructions: Iterable[Construction], *, revoked: Iterable[Hashable] = (), max_unpack: int = 8, max_items: int = 2_000_000) -> dict[str, Any]:
    rv = frozenset(revoked)
    cons = [c for c in constructions if c.liveness(rv) is not Liveness.DEAD]
    per_token: list[list[Reading]] = []
    for t in tokens:
        a = lexicon.analyse(t, rv)
        rs = [r for r in a.readings if r.warrant.liveness(rv) is not Liveness.DEAD]
        if not rs:
            return {"verdict": "UNKNOWN_LEXEME", "token": t, "count": 0, "meanings": []}
        per_token.append(rs)
    n = len(tokens)
    # Earley items: (construction index, dot, start) with partial bindings kept only for the representative
    by_produces: dict[str | None, list[int]] = defaultdict(list)
    for i, c in enumerate(cons):
        by_produces[c.produces].append(i)
    # chart[k] = dict[(ci, dot, start)] -> (count, representative bindings)
    chart: list[dict[tuple, tuple[int, dict[str, Any]]]] = [dict() for _ in range(n + 1)]
    completed: dict[tuple[int, int, str], dict[tuple, Packed]] = defaultdict(dict)    # (start, end, phrase type) -> (ci, lexkey) -> Packed

    items = [0]

    def add(k: int, key: tuple, count: int, b: dict[str, Any]) -> None:
        key = (key[0], key[1], key[2], _lex_key(b))
        old = chart[k].get(key)
        if old is None:
            items[0] += 1
            if items[0] > max_items:
                raise ChartCap(f"chart items exceeded {max_items}")
        chart[k][key] = (old[0] + count, old[1]) if old else (count, b)

    def predict(k: int) -> None:
        # every construction may start at k (no top symbol: any clause-level or phrase construction)
        for ci in range(len(cons)):
            add(k, (ci, 0, k), 1, {})

    def phrase_of(p: Packed) -> Phrase:
        if p.phrase is None:
            c = p.construction
            resolved = {k_: (phrase_of(v) if isinstance(v, Packed) else v) for k_, v in p.bindings.items()}
            p.bindings = resolved
            meaning = c.template(resolved)
            head = p.bindings[c.head_slot] if c.head_slot else next(v for v in p.bindings.values() if isinstance(v, Reading))
            parts = [v.warrant for v in p.bindings.values()]
            p.phrase = Phrase(c.produces, head, meaning, c.head_node, meet_all_profiles([c.warrant, *parts]), (p.start, p.end), c.construction_id)
        return p.phrase

    def complete(k: int) -> None:
        changed = True
        while changed:
            changed = False
            for key, (count, b) in list(chart[k].items()):
                ci, dot, start, lk = key
                c = cons[ci]
                if dot < len(c.pattern):
                    continue
                if c.produces is None:
                    continue
                packs = completed[(start, k, c.produces)]
                pk = (ci, lk)
                if pk in packs:
                    if packs[pk].count != count:
                        packs[pk].count = count
                        changed = True
                    continue
                packs[pk] = Packed(c, start, k, pk, count, b)
                changed = True
                # advance every item waiting for this phrase type at position `start`
                for key2, (count2, b2) in list(chart[start].items()):
                    cj, dot2, start2, _ = key2
                    c2 = cons[cj]
                    if dot2 >= len(c2.pattern):
                        continue
                    slot = c2.pattern[dot2]
                    if slot.phrase == c.produces:
                        nb = dict(b2)
                        nb[slot.name] = packs[pk]
                        add(k, (cj, dot2 + 1, start2), count2 * count, nb)
                    elif slot.optional and dot2 + 1 < len(c2.pattern) and c2.pattern[dot2 + 1].phrase == c.produces:
                        nb = dict(b2)
                        nb[c2.pattern[dot2 + 1].name] = packs[pk]
                        add(k, (cj, dot2 + 2, start2), count2 * count, nb)

    def scan(k: int) -> None:
        for key, (count, b) in list(chart[k].items()):
            ci, dot, start, _ = key
            c = cons[ci]
            # optional lexical slots may be skipped
            d = dot
            while d < len(c.pattern) and c.pattern[d].optional and c.pattern[d].phrase is None:
                for r in per_token[k]:
                    if _slot_accepts_reading(c.pattern[d], r):
                        nb = dict(b)
                        nb[c.pattern[d].name] = r
                        add(k + 1, (ci, d + 1, start), count, nb)
                d += 1
                if d < len(c.pattern):
                    add(k, (ci, d, start), count, b)
            if d < len(c.pattern) and c.pattern[d].phrase is None:
                for r in per_token[k]:
                    if _slot_accepts_reading(c.pattern[d], r):
                        nb = dict(b)
                        nb[c.pattern[d].name] = r
                        add(k + 1, (ci, d + 1, start), count, nb)

    for k in range(n + 1):
        predict(k)
        complete(k)
        if k < n:
            scan(k)
    # clause-level readings spanning [0, n): items with dot == len(pattern), start == 0, produces None
    clause_items = [(key, cb) for key, cb in chart[n].items() if key[2] == 0 and cons[key[0]].produces is None and key[1] == len(cons[key[0]].pattern)]
    total = sum(cb[0] for _, cb in clause_items)
    if total == 0:
        return {"verdict": "UNKNOWN_CONSTRUCTION", "count": 0, "meanings": []}
    meanings = []
    for (ci, _, _, _), (count, b) in clause_items[:max_unpack]:
        c = cons[ci]
        # resolve packed phrases in the representative binding
        resolved = {k_: (phrase_of(v) if isinstance(v, Packed) else v) for k_, v in b.items()}
        try:
            meanings.append({"construction_id": c.construction_id, "count": count, "meaning": c.template(resolved), "warrant": meet_all_profiles([c.warrant, *[v.warrant for v in resolved.values()]])})
        except Exception as exc:  # noqa: BLE001
            meanings.append({"construction_id": c.construction_id, "count": count, "meaning": None, "error": f"{type(exc).__name__}: {exc}"})
    return {"verdict": "INTERPRETED" if total == 1 else f"AMBIGUOUS", "count": total, "meanings": meanings}


def mutant_first_derivation_only(result: dict[str, Any]) -> dict[str, Any]:
    """Planted (M3 hostile 'force top-1'): report AMBIGUOUS as INTERPRETED using the first derivation."""
    return {**result, "verdict": "INTERPRETED", "count": 1}
