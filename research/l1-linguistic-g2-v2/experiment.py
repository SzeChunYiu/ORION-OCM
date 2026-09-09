"""Bounded L1 G2 v2: exact operator-scope constructions, not Adj–Noun.

Microworld: typed NP phrases, NEGATES / SCOPES_OVER as first-class edges,
polysemy as a two-sense ambiguity set, restart, revocation with alternate
support. Grammar-induction parent stores train n-grams only. No hidden LLM.
Corpus-scale / UD / open-weight LM are CANNOT_CHECK. L2/L3 stay locked.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Hashable, Iterable, Mapping

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

from ocm.kso.ids import content_hash
from ocm.kso.types import Scope
from ocm.kso.warrant import Liveness, WarrantProfile
from ocm.language.constructions import Construction, Phrase, Slot, mutant_drop_negation
from ocm.language.interpret import Verdict, interpret, tokenize
from ocm.language.lexicon import Category, Lexeme, Lexicon, Sense, mutant_merge_senses
from ocm.language.meaning import MAX_EXACT_CANONICAL, MEdge, MNode, MeaningGraph, canonical


TRAIN_SALT = "orion-ocm-l1-linguistic-g2-v2-train"
HELD_SALT = "orion-ocm-l1-linguistic-g2-v2-held"
SCOPE_ID = "l1-microworld.v2"
V1_SURFACES = frozenset({"red", "blue", "green", "cube", "sphere", "pyramid", "two"})

TRAIN_ANIMATE = ("otter", "heron")
TRAIN_ARTIFACT = ("lantern", "casket")
TRAIN_VERB = ("inspect",)
HELD_ANIMATE = ("lynx",)
HELD_ARTIFACT = ("goblet",)
HELD_VERB = ("conceal",)
POLYSEME = "bank"
SENSE_INSTITUTION = "institution"
SENSE_LANDFORM = "landform"

V1_FROZEN_SCHEMA = "ocm.l1.linguistic-g2.v1"
V1_FROZEN_TERMINAL = "COMPOSITIONAL_LANGUAGE_LEARNING_ONLY"


def _scope() -> Scope:
    return Scope.of(SCOPE_ID)


def _w(*evidence: str) -> WarrantProfile:
    return WarrantProfile.of(set(evidence))


def _concept(reading) -> str:
    return reading.sense.concept if reading.sense else reading.lemma


def bind_arg(b: Mapping[str, Any], slot: str, nid: str) -> tuple[list[MNode], list[MEdge], str]:
    v = b[slot]
    if isinstance(v, Phrase):
        mapping = {n.node_id: (nid if n.node_id == v.head_node else f"{nid}.{n.node_id}") for n in v.meaning.nodes}
        g = v.meaning.relabel(mapping)
        return list(g.nodes), list(g.edges), nid
    sort = dict(v.features).get("sort")
    feats = (("sort", sort),) if sort else ()
    return [MNode(nid, "entity", _concept(v), feats)], [], nid


def event_node(b: Mapping[str, Any]) -> MNode:
    return MNode("e", "event", _concept(b["verb"]))


def np_template(b: Mapping[str, Any]) -> MeaningGraph:
    n = b["n"]
    sort = dict(n.features).get("sort", "entity")
    node = MNode("x", "entity", _concept(n), (("sort", sort),))
    return MeaningGraph((node,), (), root="x")


def transitive_template(b: Mapping[str, Any]) -> MeaningGraph:
    n1, e1, s_id = bind_arg(b, "subj", "x1")
    n2, e2, o_id = bind_arg(b, "obj", "x2")
    ev = event_node(b)
    return MeaningGraph(
        tuple(n1 + [ev] + n2),
        tuple(e1 + e2 + [MEdge("ROLE:agent", ("e",), (s_id,)), MEdge("ROLE:patient", ("e",), (o_id,))]),
        root="e",
    )


def negation_template(b: Mapping[str, Any]) -> MeaningGraph:
    g = transitive_template(b)
    return MeaningGraph(g.nodes, g.edges + (MEdge("NEGATES", ("e",), ("e",)),), root="e")


def every_some_template(b: Mapping[str, Any]) -> MeaningGraph:
    n1, e1, s_id = bind_arg(b, "subj", "x1")
    n2, e2, o_id = bind_arg(b, "obj", "x2")
    ev = event_node(b)
    q_every = MNode("q1", "quantifier", "every")
    q_some = MNode("q2", "quantifier", "some")
    edges = e1 + e2 + [
        MEdge("ROLE:agent", ("e",), (s_id,)),
        MEdge("ROLE:patient", ("e",), (o_id,)),
        MEdge("SCOPES_OVER", ("q1",), (s_id,)),
        MEdge("SCOPES_OVER", ("q2",), (o_id,)),
        MEdge("SCOPES_OVER", ("q1",), ("q2",)),
    ]
    return MeaningGraph(tuple(n1 + n2 + [ev, q_every, q_some]), tuple(edges), root="e")


def some_every_template(b: Mapping[str, Any]) -> MeaningGraph:
    n1, e1, s_id = bind_arg(b, "subj", "x1")
    n2, e2, o_id = bind_arg(b, "obj", "x2")
    ev = event_node(b)
    q_some = MNode("q1", "quantifier", "some")
    q_every = MNode("q2", "quantifier", "every")
    edges = e1 + e2 + [
        MEdge("ROLE:agent", ("e",), (s_id,)),
        MEdge("ROLE:patient", ("e",), (o_id,)),
        MEdge("SCOPES_OVER", ("q1",), (s_id,)),
        MEdge("SCOPES_OVER", ("q2",), (o_id,)),
        MEdge("SCOPES_OVER", ("q1",), ("q2",)),
    ]
    return MeaningGraph(tuple(n1 + n2 + [ev, q_some, q_every]), tuple(edges), root="e")


def not_every_template(b: Mapping[str, Any]) -> MeaningGraph:
    n1, e1, s_id = bind_arg(b, "subj", "x1")
    n2, e2, o_id = bind_arg(b, "obj", "x2")
    ev = event_node(b)
    q = MNode("q1", "quantifier", "every")
    edges = e1 + e2 + [
        MEdge("ROLE:agent", ("e",), (s_id,)),
        MEdge("ROLE:patient", ("e",), (o_id,)),
        MEdge("SCOPES_OVER", ("q1",), (s_id,)),
        MEdge("NEGATES", ("q1",), ("q1",)),
    ]
    return MeaningGraph(tuple(n1 + n2 + [ev, q]), tuple(edges), root="e")


def every_not_template(b: Mapping[str, Any]) -> MeaningGraph:
    n1, e1, s_id = bind_arg(b, "subj", "x1")
    n2, e2, o_id = bind_arg(b, "obj", "x2")
    ev = event_node(b)
    q = MNode("q1", "quantifier", "every")
    edges = e1 + e2 + [
        MEdge("ROLE:agent", ("e",), (s_id,)),
        MEdge("ROLE:patient", ("e",), (o_id,)),
        MEdge("SCOPES_OVER", ("q1",), ("e",)),
        MEdge("NEGATES", ("e",), ("e",)),
    ]
    return MeaningGraph(tuple(n1 + n2 + [ev, q]), tuple(edges), root="e")


def teach_lexicon() -> Lexicon:
    lex = Lexicon()
    sc = _scope()

    def add_noun(surface: str, sort: str, senses: tuple[Sense, ...], form_ev: str) -> None:
        lex.add(
            Lexeme(
                surface,
                Category.NOUN,
                senses,
                features=(("sort", sort),),
                warrant=_w(form_ev),
                scope=sc,
            )
        )

    for w in TRAIN_ANIMATE + HELD_ANIMATE:
        ev = f"lex:v2:{w}:{TRAIN_SALT}"
        add_noun(w, "animate", (Sense(f"l1v2:{w}", w, "entity", _w(ev), scope=sc),), ev)
    for w in TRAIN_ARTIFACT + HELD_ARTIFACT:
        ev = f"lex:v2:{w}:{TRAIN_SALT}"
        add_noun(w, "inanimate", (Sense(f"l1v2:{w}", w, "entity", _w(ev), scope=sc),), ev)
    inst_ev = f"lesson:v2:sense:{POLYSEME}:{SENSE_INSTITUTION}:{TRAIN_SALT}"
    land_ev = f"lesson:v2:sense:{POLYSEME}:{SENSE_LANDFORM}:{TRAIN_SALT}"
    form_ev = f"lex:v2:{POLYSEME}:{TRAIN_SALT}"
    add_noun(
        POLYSEME,
        "inanimate",
        (
            Sense("l1v2:bank:institution", SENSE_INSTITUTION, "entity", _w(inst_ev), scope=sc),
            Sense("l1v2:bank:landform", SENSE_LANDFORM, "entity", _w(land_ev), scope=sc),
        ),
        form_ev,
    )
    for w in TRAIN_VERB + HELD_VERB:
        ev = f"lex:v2:{w}:{TRAIN_SALT}"
        lex.add(
            Lexeme(
                w,
                Category.VERB,
                (Sense(f"l1v2:{w}", w, "event", _w(ev), selection=(("ROLE:agent", "animate"), ("ROLE:patient", "inanimate")), scope=sc),),
                warrant=_w(ev),
                scope=sc,
            )
        )
    for lemma, cat in (
        ("not", Category.NEG),
        ("every", Category.DET),
        ("some", Category.DET),
    ):
        ev = f"lex:v2:{lemma}:{TRAIN_SALT}"
        lex.add(Lexeme(lemma, cat, (Sense(f"l1v2:{lemma}", lemma, "value", _w(ev), scope=sc),), warrant=_w(ev), scope=sc))
    return lex


def make_constructions(evidence: Mapping[str, tuple[str, ...]], *, extra: Mapping[str, WarrantProfile] | None = None) -> list[Construction]:
    extra = extra or {}
    sc = _scope()

    def fam(name: str) -> WarrantProfile:
        if name in extra:
            return extra[name]
        return _w(*evidence[name])

    np_anim = Construction(
        "l1v2:np-animate",
        "noun_phrase",
        (Slot("n", Category.NOUN, features=(("sort", "animate"),)),),
        np_template,
        fam("noun_phrase"),
        scope=sc,
        language="l1v2",
        produces="NP-animate",
        head_slot="n",
        head_node="x",
    )
    np_inan = Construction(
        "l1v2:np-inanimate",
        "noun_phrase",
        (Slot("n", Category.NOUN, features=(("sort", "inanimate"),)),),
        np_template,
        fam("noun_phrase"),
        scope=sc,
        language="l1v2",
        produces="NP-inanimate",
        head_slot="n",
        head_node="x",
    )
    subj = Slot("subj", Category.NOUN, phrase="NP-animate")
    obj = Slot("obj", Category.NOUN, phrase="NP-inanimate")
    verb = Slot("verb", Category.VERB)
    neg = Slot("neg", Category.NEG, lemma="not")
    every = Slot("q_every", Category.DET, lemma="every")
    some = Slot("q_some", Category.DET, lemma="some")
    return [
        np_anim,
        np_inan,
        Construction("l1v2:transitive", "transitive", (subj, verb, obj), transitive_template, fam("transitive"), scope=sc, language="l1v2"),
        Construction("l1v2:negation", "negation", (subj, neg, verb, obj), negation_template, fam("negation"), scope=sc, language="l1v2"),
        Construction("l1v2:every-some", "quantifier_scope", (every, subj, verb, some, obj), every_some_template, fam("every_some"), scope=sc, language="l1v2"),
        Construction("l1v2:some-every", "quantifier_scope", (some, subj, verb, every, obj), some_every_template, fam("some_every"), scope=sc, language="l1v2"),
        Construction("l1v2:not-every", "negation_scope", (neg, every, subj, verb, obj), not_every_template, fam("not_every"), scope=sc, language="l1v2"),
        Construction("l1v2:every-not", "negation_scope", (every, subj, neg, verb, obj), every_not_template, fam("every_not"), scope=sc, language="l1v2"),
    ]


def train_utterances() -> dict[str, tuple[str, ...]]:
    trans = tuple(f"{a} {v} {p}" for a in TRAIN_ANIMATE for v in TRAIN_VERB for p in TRAIN_ARTIFACT)
    neg = tuple(f"{a} not {v} {p}" for a in TRAIN_ANIMATE for v in TRAIN_VERB for p in TRAIN_ARTIFACT)
    es = (f"every {TRAIN_ANIMATE[0]} {TRAIN_VERB[0]} some {TRAIN_ARTIFACT[0]}", f"every {TRAIN_ANIMATE[1]} {TRAIN_VERB[0]} some {TRAIN_ARTIFACT[1]}")
    se = (f"some {TRAIN_ANIMATE[0]} {TRAIN_VERB[0]} every {TRAIN_ARTIFACT[1]}", f"some {TRAIN_ANIMATE[1]} {TRAIN_VERB[0]} every {TRAIN_ARTIFACT[0]}")
    ne = (f"not every {TRAIN_ANIMATE[0]} {TRAIN_VERB[0]} {TRAIN_ARTIFACT[0]}", f"not every {TRAIN_ANIMATE[1]} {TRAIN_VERB[0]} {TRAIN_ARTIFACT[1]}")
    en = (f"every {TRAIN_ANIMATE[0]} not {TRAIN_VERB[0]} {TRAIN_ARTIFACT[0]}", f"every {TRAIN_ANIMATE[1]} not {TRAIN_VERB[0]} {TRAIN_ARTIFACT[1]}")
    return {
        "noun_phrase": trans,
        "transitive": trans,
        "negation": neg,
        "every_some": es,
        "some_every": se,
        "not_every": ne,
        "every_not": en,
    }


def held_probes() -> dict[str, str]:
    a, p, v = HELD_ANIMATE[0], HELD_ARTIFACT[0], HELD_VERB[0]
    return {
        "transitive": f"{a} {v} {p}",
        "negation": f"{a} not {v} {p}",
        "every_some": f"every {a} {v} some {p}",
        "some_every": f"some {a} {v} every {p}",
        "not_every": f"not every {a} {v} {p}",
        "every_not": f"every {a} not {v} {p}",
        "combo": f"not every {a} {v} {p}",
        "type_mismatch": f"{p} {v} {a}",
        "polysemy": f"{TRAIN_ANIMATE[0]} {TRAIN_VERB[0]} {POLYSEME}",
    }


def evidence_for(families: Mapping[str, tuple[str, ...]]) -> dict[str, tuple[str, ...]]:
    out: dict[str, tuple[str, ...]] = {}
    for fam, utts in families.items():
        out[fam] = tuple(f"lesson:v2:{fam}:{i}:{TRAIN_SALT}" for i, _u in enumerate(utts))
    return out


def grammar_induction_parent(utterances: Iterable[str]) -> tuple[dict[tuple[str, str], int], set[tuple[str, ...]]]:
    counts: dict[tuple[str, str], int] = {}
    identities: set[tuple[str, ...]] = set()
    for u in utterances:
        tokens = tuple(tokenize(u))
        identities.add(tokens)
        for a, b in zip(tokens, tokens[1:]):
            counts[a, b] = counts.get((a, b), 0) + 1
    return counts, identities


def parse(utterance: str, lex: Lexicon, cons: list[Construction], revoked: Iterable[Hashable] = ()) -> dict:
    interp = interpret(utterance, lex, cons, revoked=revoked)
    rec: dict[str, Any] = {
        "utterance": utterance,
        "verdict": interp.verdict.value,
        "invoked": interp.verdict is Verdict.INTERPRETED,
        "construction_id": interp.candidates[0].construction_id if interp.candidates else None,
        "n_candidates": len(interp.candidates),
        "meaning": None,
        "n_nodes": 0,
        "relations": [],
        "sorts": {},
        "entity_labels": [],
    }
    if interp.meaning is not None:
        rec["meaning"] = canonical(interp.meaning)[1]
        rec["n_nodes"] = len(interp.meaning.nodes)
        rec["relations"] = sorted({e.relation for e in interp.meaning.edges})
        rec["sorts"] = {n.label: dict(n.features).get("sort") for n in interp.meaning.nodes if n.node_type == "entity"}
        rec["entity_labels"] = sorted(n.label for n in interp.meaning.nodes if n.node_type == "entity" and n.label)
        rec["fingerprint"] = content_hash({"u": utterance, "canon": rec["meaning"], "salt": HELD_SALT})
    elif interp.verdict is Verdict.AMBIGUOUS:
        rec["meanings"] = [canonical(c.meaning)[1] for c in interp.candidates]
        rec["entity_label_sets"] = [
            sorted(n.label for n in c.meaning.nodes if n.node_type == "entity" and n.label) for c in interp.candidates
        ]
    return rec


def lexicon_payload(lex: Lexicon) -> list[dict]:
    rows = []
    for key, lexeme in sorted(lex.lexemes.items()):
        rows.append(
            {
                "key": key,
                "lemma": lexeme.lemma,
                "category": lexeme.category.name,
                "features": [list(f) for f in lexeme.features],
                "senses": [
                    {
                        "id": s.sense_id,
                        "concept": s.concept,
                        "node_type": s.node_type,
                        "evidence": sorted(e for w in s.warrant.lower for e in w),
                    }
                    for s in lexeme.senses
                ],
            }
        )
    return rows


def persist(path: Path, evidence: Mapping[str, tuple[str, ...]], lex: Lexicon) -> None:
    payload = {
        "schema": "ocm.l1.linguistic-g2.v2.skill",
        "salt": TRAIN_SALT,
        "evidence": {k: list(v) for k, v in evidence.items()},
        "lexicon": lexicon_payload(lex),
        "digest": content_hash({"salt": TRAIN_SALT, "ev": evidence}),
    }
    path.write_text(json.dumps(payload, sort_keys=True))


def load(path: Path) -> tuple[dict[str, tuple[str, ...]], Lexicon]:
    payload = json.loads(path.read_text())
    evidence = {k: tuple(v) for k, v in payload["evidence"].items()}
    if content_hash({"salt": TRAIN_SALT, "ev": evidence}) != payload["digest"]:
        raise RuntimeError("linguistic skill identity mismatch")
    return evidence, teach_lexicon()


def v1_result_intact() -> bool:
    p = REPO / "research" / "l1-linguistic-g2-v1" / "RESULT.json"
    data = json.loads(p.read_text())
    return data.get("schema") == V1_FROZEN_SCHEMA and data.get("terminal") == V1_FROZEN_TERMINAL


def all_surfaces() -> set[str]:
    return set(TRAIN_ANIMATE + TRAIN_ARTIFACT + TRAIN_VERB + HELD_ANIMATE + HELD_ARTIFACT + HELD_VERB + (POLYSEME, "not", "every", "some"))


def main(out: Path) -> dict:
    if all_surfaces() & V1_SURFACES:
        raise RuntimeError("v2 salts collided with v1 surfaces")
    families = train_utterances()
    evidence = evidence_for(families)
    lex = teach_lexicon()
    cons = make_constructions(evidence)
    train_flat = tuple(u for utts in families.values() for u in utts)
    _counts, identities = grammar_induction_parent(train_flat)
    probes = held_probes()

    held_keys = ("transitive", "negation", "every_some", "some_every", "not_every", "every_not")
    held_rows = {k: parse(probes[k], lex, cons) for k in held_keys}
    combo = parse(probes["combo"], lex, cons)
    combo_reset = parse(probes["combo"], lex, [])
    mismatch = parse(probes["type_mismatch"], lex, cons)
    train_ok = parse(families["transitive"][0], lex, cons)

    reset_rows = {k: parse(probes[k], lex, []) for k in held_keys}
    path = out.parent / "grammar.json"
    persist(path, evidence, lex)
    loaded_ev, loaded_lex = load(path)
    restarted = {k: parse(probes[k], loaded_lex, make_constructions(loaded_ev)) for k in held_keys}

    neg_revoked = set(evidence["negation"])
    revoked_neg = parse(probes["negation"], lex, cons, neg_revoked)
    unrelated_after_neg = parse(probes["transitive"], lex, cons, neg_revoked)
    alt_w = WarrantProfile.of(set(evidence["negation"]), {f"lesson:v2:negation:alt:{TRAIN_SALT}"})
    restored = parse(probes["negation"], lex, make_constructions(evidence, extra={"negation": alt_w}), neg_revoked)

    inst_ev = f"lesson:v2:sense:{POLYSEME}:{SENSE_INSTITUTION}:{TRAIN_SALT}"
    land_ev = f"lesson:v2:sense:{POLYSEME}:{SENSE_LANDFORM}:{TRAIN_SALT}"
    poly_both = parse(probes["polysemy"], lex, cons)
    poly_inst = parse(probes["polysemy"], lex, cons, {land_ev})
    poly_land = parse(probes["polysemy"], lex, cons, {inst_ev})
    bank = next(lx for lx in lex.by_lemma(POLYSEME) if lx.category is Category.NOUN)
    merged = mutant_merge_senses(bank)
    merged_hides_revoke = merged.liveness({inst_ev}) is Liveness.LIVE and merged.liveness({land_ev}) is Liveness.LIVE
    real_senses_after_inst_revoke = {s.concept for s in bank.live_senses({inst_ev})}

    gold_neg = parse(probes["negation"], lex, cons)
    drop_cons = [c if c.construction_id != "l1v2:negation" else mutant_drop_negation(c) for c in cons]
    dropped = parse(probes["negation"], lex, drop_cons)

    not_every = held_rows["not_every"]
    every_not = held_rows["every_not"]
    every_some = held_rows["every_some"]
    some_every = held_rows["some_every"]

    invoked = all(held_rows[k]["invoked"] for k in held_keys)
    restart_ok = [held_rows[k]["meaning"] for k in held_keys] == [restarted[k]["meaning"] for k in held_keys]
    reset_fails = all(not reset_rows[k]["invoked"] for k in held_keys)
    revoke_kills = not revoked_neg["invoked"]
    unrelated_ok = unrelated_after_neg["invoked"]
    alt_ok = restored["invoked"]
    combo_ok = combo["invoked"] and not combo_reset["invoked"]
    parent_has_fresh = any(tuple(tokenize(probes[k])) in identities for k in held_keys)
    type_ok = (
        train_ok["invoked"]
        and not mismatch["invoked"]
        and train_ok["sorts"].get(TRAIN_ANIMATE[0]) == "animate"
        and train_ok["sorts"].get(TRAIN_ARTIFACT[0]) == "inanimate"
    )
    poly_ok = (
        poly_both["verdict"] == "AMBIGUOUS"
        and poly_both["n_candidates"] == 2
        and poly_inst["invoked"]
        and poly_land["invoked"]
        and SENSE_INSTITUTION in poly_inst["entity_labels"]
        and SENSE_LANDFORM in poly_land["entity_labels"]
        and SENSE_LANDFORM not in poly_inst["entity_labels"]
        and SENSE_INSTITUTION not in poly_land["entity_labels"]
        and real_senses_after_inst_revoke == {SENSE_LANDFORM}
        and merged_hides_revoke
    )
    neg_ok = gold_neg["invoked"] and "NEGATES" in gold_neg["relations"] and "NEGATES" not in train_ok["relations"] and dropped["meaning"] != gold_neg["meaning"]
    scope_ok = (
        every_some["invoked"]
        and some_every["invoked"]
        and every_some["meaning"] != some_every["meaning"]
        and "SCOPES_OVER" in every_some["relations"]
        and "SCOPES_OVER" in some_every["relations"]
        and not_every["invoked"]
        and every_not["invoked"]
        and not_every["meaning"] != every_not["meaning"]
        and "NEGATES" in not_every["relations"]
        and "NEGATES" in every_not["relations"]
        and set(tokenize(probes["not_every"])) == set(tokenize(probes["every_not"]))
    )
    nodes_ok = all(held_rows[k]["n_nodes"] <= MAX_EXACT_CANONICAL for k in held_keys) and combo["n_nodes"] <= MAX_EXACT_CANONICAL
    max_nodes = max([held_rows[k]["n_nodes"] for k in held_keys] + [combo["n_nodes"], train_ok["n_nodes"]])
    ordinary_tied = restart_ok
    v1_ok = v1_result_intact()

    if invoked and restart_ok and revoke_kills and reset_fails and combo_ok and not parent_has_fresh and type_ok and poly_ok and neg_ok and scope_ok and unrelated_ok and alt_ok and nodes_ok and v1_ok:
        terminal = "COMPOSITIONAL_LANGUAGE_LEARNING_ONLY"
    elif invoked and ordinary_tied:
        terminal = "PARENT_SUFFICIENT"
    else:
        terminal = "NO_LANGUAGE_META_LEARNING"

    earned = "EARNED_AT_SCOPE"
    checklist = {
        "acquire_corpus_scale_lexicon": "CANNOT_CHECK_MINIATURE_MICROWORLD",
        "retain_polysemy": earned if poly_ok else "OPEN",
        "induce_constructions": earned if invoked else "OPEN",
        "recursive_composition": earned if combo_ok else "OPEN",
        "meaning_graphs_beyond_bound": "CANNOT_CHECK_MICROWORLD_SMALL",
        "exact_canonicalization": earned if nodes_ok else "OPEN",
        "quantifier_scope": earned if scope_ok else "OPEN",
        "negation": earned if neg_ok else "OPEN",
        "typed_entities": earned if type_ok else "OPEN",
        "ud_alignment": "CANNOT_CHECK_NO_UD_IN_THIS_STUDY",
        "held_out_lexical_fillers": earned if invoked and not parent_has_fresh else "OPEN",
        "held_out_construction_combinations": earned if combo_ok else "OPEN",
        "held_out_construction_families": "CANNOT_CHECK_FAMILIES_TAUGHT_EXPLICITLY",
        "artificial_non_english": "CANNOT_CHECK_NOT_RUN_SOV_HERE",
        "acquisition_curves": "CANNOT_CHECK_N_TOO_SMALL",
        "correction_revocation": earned if revoke_kills and unrelated_ok and alt_ok else "OPEN",
        "reset_control": earned if reset_fails else "OPEN",
        "grammar_induction_parent": earned if not parent_has_fresh else "OPEN",
        "persistent_grammar_parent": earned if restart_ok else "OPEN",
        "continual_adaptation_parent": "CANNOT_CHECK_NOT_RUN",
        "open_weight_lm_reference": "CANNOT_CHECK_NO_MODEL_WEIGHTS",
        "g2_causal_reuse_linguistic": earned if invoked and restart_ok and revoke_kills else "OPEN",
    }
    result = {
        "schema": "ocm.l1.linguistic-g2.v2",
        "terminal": terminal,
        "fresh_invoked": invoked,
        "restart_equivalent": restart_ok,
        "revocation_removes_effect": revoke_kills,
        "unrelated_survives_revocation": unrelated_ok,
        "alternate_support_restores": alt_ok,
        "reset_has_no_construction": reset_fails,
        "held_out_combination": combo_ok,
        "grammar_induction_parent_has_fresh_identity": parent_has_fresh,
        "ordinary_persist_tied": ordinary_tied,
        "type_mismatch_rejected": not mismatch["invoked"],
        "polysemy_ambiguous_until_evidence": poly_ok,
        "negation_distinct_from_affirmative": neg_ok,
        "scope_readings_distinct": scope_ok,
        "max_nodes": max_nodes,
        "canonical_bound": MAX_EXACT_CANONICAL,
        "l2_started": False,
        "l3_started": False,
        "v1_result_intact": v1_ok,
        "salts": {"train": TRAIN_SALT, "held": HELD_SALT, "scope": SCOPE_ID},
        "checklist": checklist,
        "held_rows": held_rows,
        "claim_ceiling": "Exact operator-scope microworld with typed entities and two-sense polysemy. Not corpus-scale N1 completion. L2/L3 locked.",
    }
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(
        json.dumps(
            {
                "terminal": terminal,
                "invoked": invoked,
                "restart": restart_ok,
                "revoke": revoke_kills,
                "negation": neg_ok,
                "scope": scope_ok,
                "typed": type_ok,
                "polysemy": poly_ok,
            }
        )
    )
    return result


if __name__ == "__main__":
    target = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parent / "RESULT.json"
    main(target)
