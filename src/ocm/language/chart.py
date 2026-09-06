"""Packed-forest chart parser over M3 constructions (N1 obligation from ledger S39).

The M3 matcher enumerates every phrase over every span and is exponential in attachment ambiguity.
This parser is an Earley recogniser over the construction inventory whose items are slots: a
lexical slot matches one token reading of the slot's category (with the slot's feature/lemma
requirements), a phrase slot matches a completed phrase of the slot's `phrase` type.  Completed
phrases are *packed* per (start, end, phrase type, lexical readings of the span) — batch 11 K1 (ix): never
by sub-derivation identity — the chart records derivation COUNTS (exact, by summation with delta
propagation) and one representative derivation per node, so the number of analyses is exact and the item
count is polynomial in the token count while only one meaning per packed node is ever built.  Verdicts:

  INTERPRETED           exactly one clause-level derivation spans the whole utterance
  AMBIGUOUS(k)          k > 1 derivations (k is exact; the representative meanings of up to
                        `max_unpack` derivations are unpacked for the clarification policy)
  UNKNOWN_LEXEME        a token has no live reading
  UNKNOWN_CONSTRUCTION  no clause-level derivation spans the utterance

Evidence ranking (N1 phase E): a learned construction may carry its demonstration count in its lineage
(``count:N``).  Every derivation is scored by the MINIMUM count over the constructions it uses (the weakest
evidence licenses the whole derivation; across packings the best score is kept).  An AMBIGUOUS result
reports the clause items ranked by that score.  Ranking never turns AMBIGUOUS into INTERPRETED: the
top-ranked reading is a hypothesis with its own warrant, and the alternatives are not refuted by it.

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
    score: int | None = None                        # evidence score: min demonstration count along the best derivation


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


def evidence_count(c: Construction) -> int | None:
    """Demonstration count recorded in a learned construction's lineage (``count:N``); None if not recorded."""
    for tag in getattr(c, "lineage", ()) or ():
        if isinstance(tag, str) and tag.startswith("count:"):
            try:
                return int(tag.split(":", 1)[1])
            except ValueError:
                return None
    return None


def _min_score(a, b):
    if a is None:
        return b
    if b is None:
        return a
    return min(a, b)


class ChartCap(Exception):
    """The declared item cap was exceeded: the sentence is CANNOT_CHECK under this inventory (never a silent truncation)."""


GAP_CATEGORIES = ("N",)      # an out-of-lexicon token is admitted as an entity placeholder only (proper nouns, numbers, symbols)


def gap_readings(token: str, categories: Iterable[str] = GAP_CATEGORIES) -> list[Reading]:
    """N1 phase D: an out-of-lexicon token becomes an UNDERSPECIFIED reading with an UNKNOWN warrant
    (⟦0, U⟧: no exhibited evidence, not refuted) — interpretation proceeds with a declared gap and the
    resulting meaning can never be LIVE (M3 §2 underspecified nodes; batch 5 E1: never a self-grant)."""
    from ocm.language.lexicon import Category
    return [Reading(token, token, Category(c), None, (("gap", "yes"),), WarrantProfile.of(complete=False), ("gap",)) for c in categories]


def parse(tokens: Sequence[str], lexicon: Lexicon, constructions: Iterable[Construction], *, revoked: Iterable[Hashable] = (), max_unpack: int = 8, max_items: int = 2_000_000, gaps: bool = False, admit=None) -> dict[str, Any]:
    """`admit(construction, bindings) -> bool` (N1 phase G): an optional evidence gate applied to every completed
    phrase and clause; a completion it refuses is not packed and not counted — refutation by absent attachment
    evidence, never a ranking.  None admits everything (the phase C–F behaviour)."""
    rv = frozenset(revoked)
    cons = [c for c in constructions if c.liveness(rv) is not Liveness.DEAD]
    per_token: list[list[Reading]] = []
    gap_tokens: list[str] = []
    for t in tokens:
        a = lexicon.analyse(t, rv)
        rs = [r for r in a.readings if r.warrant.liveness(rv) is not Liveness.DEAD]
        if not rs:
            if not gaps:
                return {"verdict": "UNKNOWN_LEXEME", "token": t, "count": 0, "meanings": []}
            rs = gap_readings(t)
            gap_tokens.append(t)
        per_token.append(rs)
    n = len(tokens)
    # Earley items keyed by (construction, dot, start, lexspan): `lexspan` is the tuple of (position, reading
    # identity) the item has consumed so far.  Completed phrases are PACKED per (start, end, phrase type, lexspan)
    # — theory batch 11 K1 (ix): packing by span and lexical readings, never by sub-derivation identity — so the
    # forest holds one node per span reading, exact derivation COUNTS are kept by summation (deltas are propagated
    # to waiting items, so a node whose count grows after first use still yields exact totals), and one
    # representative derivation per node is built lazily.
    ccount = [evidence_count(c) for c in cons]
    chart: list[dict[tuple, tuple[int, dict[str, Any], int | None]]] = [dict() for _ in range(n + 1)]
    completed: dict[tuple[int, int, str], dict[tuple, Packed]] = defaultdict(dict)    # (start, end, produces) -> lexspan -> Packed
    contributed: dict[tuple, int] = {}          # completed item key -> count already added to its pack
    admitted_cache: dict[tuple, bool] = {}      # completed item key -> admit verdict (phase G)
    applied: dict[tuple, int] = {}              # (parent item key at `start`, pack id) -> product already added to the advanced item
    items = [0]

    def rid(r: Reading) -> tuple:
        return (r.lemma, r.sense.sense_id if r.sense else None, tuple(sorted(r.features)))

    waiting: list[dict[str, list[tuple]]] = [defaultdict(list) for _ in range(n + 1)]   # k -> phrase type -> item keys waiting for it

    def add(k: int, key: tuple, count: int, b: dict[str, Any], score: int | None, lexspan: tuple) -> None:
        key = (key[0], key[1], key[2], lexspan)
        old = chart[k].get(key)
        if old is None:
            items[0] += 1
            if items[0] > max_items:
                raise ChartCap(f"chart items exceeded {max_items}")
            chart[k][key] = (count, b, score)
            c, dot = cons[key[0]], key[1]
            if dot < len(c.pattern):
                slot = c.pattern[dot]
                if slot.phrase is not None:
                    waiting[k][slot.phrase].append(key)
                elif slot.optional and dot + 1 < len(c.pattern) and c.pattern[dot + 1].phrase is not None:
                    waiting[k][c.pattern[dot + 1].phrase].append(key)
        else:
            better = score is not None and (old[2] is None or score > old[2])
            chart[k][key] = (old[0] + count, b if better else old[1], score if better else old[2])

    by_produces: dict[str | None, list[int]] = defaultdict(list)
    for i, c in enumerate(cons):
        by_produces[c.produces].append(i)

    def can_start(ci: int, k: int, wanted: set) -> tuple[bool, str | None]:
        """Top-down filtered prediction: a construction is predicted at k only if its pattern can begin here —
        its leading lexical slot (after any optional prefix) accepts a reading at k, or its leading phrase slot's
        type is itself wanted at k.  Returns (predict?, phrase type this construction wants at k, if any)."""
        c = cons[ci]
        for d, slot in enumerate(c.pattern):
            if slot.phrase is not None:
                return (slot.phrase in wanted), slot.phrase
            if k < n and any(_slot_accepts_reading(slot, r) for r in per_token[k]):
                return True, None
            if not slot.optional:
                return False, None
        return False, None

    def predict(k: int) -> None:
        # phrase types wanted at k: closure from every clause-level construction and every construction that can start here
        wanted: set = set()
        candidates = list(range(len(cons)))
        predicted: set = set()
        changed = True
        while changed:
            changed = False
            for ci in candidates:
                if ci in predicted:
                    continue
                c = cons[ci]
                if c.produces is not None and c.produces not in wanted:
                    continue                      # a phrase construction is predicted only when its type is wanted here
                ok, want = can_start(ci, k, wanted)
                if want is not None and want not in wanted and (c.produces is None or c.produces in wanted):
                    wanted.add(want); changed = True
                if ok:
                    predicted.add(ci); changed = True
                    add(k, (ci, 0, k), 1, {}, ccount[ci], ())

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

    def advance(pack: Packed, start: int, k: int) -> bool:
        """Advance every item at `start` waiting for this pack's phrase type by the pack's count delta."""
        changed = False
        produces = pack.construction.produces
        for key2 in list(waiting[start].get(produces, ())):
            count2, b2, score2 = chart[start][key2]
            cj, dot2, start2, lex2 = key2
            c2 = cons[cj]
            slot = c2.pattern[dot2]
            if slot.phrase == produces:
                nxt, name = dot2 + 1, slot.name
            else:
                nxt, name = dot2 + 2, c2.pattern[dot2 + 1].name
            ak = (key2, id(pack))
            product = count2 * pack.count
            delta = product - applied.get(ak, 0)
            if delta <= 0:
                continue
            applied[ak] = product
            nb = dict(b2)
            nb[name] = pack
            add(k, (cj, nxt, start2), delta, nb, _min_score(score2, pack.score), lex2 + pack.key)
            changed = True
        return changed

    def complete(k: int) -> None:
        changed = True
        while changed:
            changed = False
            for key, (count, b, score) in list(chart[k].items()):
                ci, dot, start, lexspan = key
                c = cons[ci]
                if dot < len(c.pattern):
                    continue
                if admit is not None and key not in admitted_cache:
                    admitted_cache[key] = bool(admit(c, b))
                if admit is not None and not admitted_cache[key]:
                    continue
                if c.produces is None:
                    continue
                packs = completed[(start, k, c.produces)]
                pack = packs.get(lexspan)
                delta = count - contributed.get(key, 0)
                if pack is None:
                    pack = packs[lexspan] = Packed(c, start, k, lexspan, 0, b, score=score)
                elif score is not None and (pack.score is None or score > pack.score):
                    pack.score, pack.bindings, pack.construction = score, b, c
                if delta > 0:
                    pack.count += delta
                    contributed[key] = count
                    if advance(pack, start, k):
                        changed = True

    def scan(k: int) -> None:
        for key, (count, b, score) in list(chart[k].items()):
            ci, dot, start, lexspan = key
            c = cons[ci]
            d = dot
            while d < len(c.pattern) and c.pattern[d].optional and c.pattern[d].phrase is None:
                for r in per_token[k]:
                    if _slot_accepts_reading(c.pattern[d], r):
                        nb = dict(b)
                        nb[c.pattern[d].name] = r
                        add(k + 1, (ci, d + 1, start), count, nb, score, lexspan + ((k, rid(r)),))
                d += 1
                if d < len(c.pattern):
                    add(k, (ci, d, start), count, b, score, lexspan)
            if d < len(c.pattern) and c.pattern[d].phrase is None:
                for r in per_token[k]:
                    if _slot_accepts_reading(c.pattern[d], r):
                        nb = dict(b)
                        nb[c.pattern[d].name] = r
                        add(k + 1, (ci, d + 1, start), count, nb, score, lexspan + ((k, rid(r)),))

    for k in range(n + 1):
        predict(k)
        complete(k)
        if k < n:
            scan(k)
    clause_items = [(key, cb) for key, cb in chart[n].items() if key[2] == 0 and cons[key[0]].produces is None and key[1] == len(cons[key[0]].pattern)
                    and (admit is None or admitted_cache.get(key, admit(cons[key[0]], cb[1])))]
    total = sum(cb[0] for _, cb in clause_items)
    if total == 0:
        return {"verdict": "UNKNOWN_CONSTRUCTION", "count": 0, "meanings": []}
    # evidence ranking: best-scored clause items first (None scores last); the order is a report, not a licence
    clause_items.sort(key=lambda kc: (-(kc[1][2] if kc[1][2] is not None else -1), kc[0]))
    meanings = []
    for (ci, _, _, _), (count, b, score) in clause_items[:max_unpack]:
        c = cons[ci]
        # resolve packed phrases in the representative binding
        resolved = {k_: (phrase_of(v) if isinstance(v, Packed) else v) for k_, v in b.items()}
        try:
            meanings.append({"construction_id": c.construction_id, "count": count, "evidence_score": score, "meaning": c.template(resolved), "warrant": meet_all_profiles([c.warrant, *[v.warrant for v in resolved.values()]])})
        except Exception as exc:  # noqa: BLE001
            meanings.append({"construction_id": c.construction_id, "count": count, "evidence_score": score, "meaning": None, "error": f"{type(exc).__name__}: {exc}"})
    verdict = "INTERPRETED" if total == 1 else "AMBIGUOUS"
    if gap_tokens and total == 1:
        verdict = "INTERPRETED_WITH_GAPS"
    scores = [cb[2] for _, cb in clause_items]
    top = scores[0] if scores else None
    ranking = {"scored": top is not None, "top_score": top, "top_items": sum(1 for x in scores if x == top) if top is not None else 0,
               "top_unique_derivation": bool(top is not None and sum(1 for x in scores if x == top) == 1 and clause_items[0][1][0] == 1),
               "licence": "RANKED_BY_MIN_EVIDENCE_COUNT (a report; not a unique parse)"}
    return {"verdict": verdict, "count": total, "meanings": meanings, "gaps": gap_tokens, "ranking": ranking}


def mutant_first_derivation_only(result: dict[str, Any]) -> dict[str, Any]:
    """Planted (M3 hostile 'force top-1'): report AMBIGUOUS as INTERPRETED using the first derivation."""
    return {**result, "verdict": "INTERPRETED", "count": 1}
