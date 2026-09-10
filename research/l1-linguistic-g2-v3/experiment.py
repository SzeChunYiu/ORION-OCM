"""Bounded L1 G2 v3: SOV hostile + held-out construction families.

Microworld: version-space acquisition over the finite {S,V,O} order class.
English-order constructions do not parse SOV (hostile relabel does not yield
gold roles). The same class learns SOV from SOV demonstrations. A disjoint
negation family is not invented by training transitive order; if that transfer
fails, the study says so. No hidden LLM. Corpus-scale / UD / open-weight LM
are CANNOT_CHECK. L2/L3 stay locked. v1 and v2 RESULT.json are not overwritten.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Hashable, Iterable, Mapping, Sequence

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

from ocm.kso.ids import content_hash
from ocm.kso.types import Scope
from ocm.kso.warrant import WarrantProfile
from ocm.language import acquisition as AQ
from ocm.language.constructions import Construction, Slot, mutant_word_order_swap
from ocm.language.interpret import Verdict, interpret, tokenize
from ocm.language.lexicon import Category, Lexeme, Lexicon, Sense
from ocm.language.meaning import MAX_EXACT_CANONICAL, MEdge, MNode, MeaningGraph, canonical, isomorphic
from ocm.learning.language import transfer as T
from ocm.learning.learner import UpdateKind, UpdateStatus


TRAIN_SALT = "orion-ocm-l1-linguistic-g2-v3-sov-train"
HELD_SALT = "orion-ocm-l1-linguistic-g2-v3-sov-held"
SCOPE_ID = "l1-microworld.v3.sov"
LANG_SVO = "l1v3-svo"
LANG_SOV = "l1v3-sov"

V1_SURFACES = frozenset({"red", "blue", "green", "cube", "sphere", "pyramid", "two"})
V2_CONTENT_SURFACES = frozenset(
    {"otter", "heron", "lantern", "casket", "inspect", "lynx", "goblet", "conceal", "bank"}
)

TRAIN_ANIMATE = ("ibis", "stoat")
TRAIN_ARTIFACT = ("chalice", "amulet")
TRAIN_VERB = ("reveal", "unseal")
HELD_ANIMATE = ("jackal",)
HELD_ARTIFACT = ("reliquary",)
HELD_VERB = ("bury",)
NEG_PARTICLE = "not"

V1_FROZEN_SCHEMA = "ocm.l1.linguistic-g2.v1"
V2_FROZEN_SCHEMA = "ocm.l1.linguistic-g2.v2"
FROZEN_TERMINAL = "COMPOSITIONAL_LANGUAGE_LEARNING_ONLY"
SCHEMA = "ocm.l1.linguistic-g2.v3"


def _scope() -> Scope:
    return Scope.of(SCOPE_ID)


def _w(*evidence: str) -> WarrantProfile:
    return WarrantProfile.of(set(evidence))


def gold_transitive(agent: str, verb: str, patient: str, *, negated: bool = False) -> MeaningGraph:
    nodes = (
        MNode("x1", "entity", agent, (("sort", "animate"),)),
        MNode("e", "event", verb),
        MNode("x2", "entity", patient, (("sort", "inanimate"),)),
    )
    edges = [
        MEdge("ROLE:agent", ("e",), ("x1",)),
        MEdge("ROLE:patient", ("e",), ("x2",)),
    ]
    if negated:
        edges.append(MEdge("NEGATES", ("e",), ("e",)))
    return MeaningGraph(nodes, tuple(edges), root="e")


def transitive_template(b: Mapping[str, Any]) -> MeaningGraph:
    s, v, o = b["S"], b["V"], b["O"]
    return gold_transitive(s.lemma, v.lemma, o.lemma)


def negation_template(b: Mapping[str, Any]) -> MeaningGraph:
    s, v, o = b["S"], b["V"], b["O"]
    return gold_transitive(s.lemma, v.lemma, o.lemma, negated=True)


def teach_lexicon() -> Lexicon:
    lex = Lexicon()
    sc = _scope()

    def add_noun(surface: str, sort: str) -> None:
        ev = f"lex:v3:{surface}:{TRAIN_SALT}"
        lex.add(
            Lexeme(
                surface,
                Category.NOUN,
                (Sense(f"l1v3:{surface}", surface, "entity", _w(ev), scope=sc),),
                features=(("sort", sort),),
                warrant=_w(ev),
                scope=sc,
            )
        )

    for w in TRAIN_ANIMATE + HELD_ANIMATE:
        add_noun(w, "animate")
    for w in TRAIN_ARTIFACT + HELD_ARTIFACT:
        add_noun(w, "inanimate")
    for w in TRAIN_VERB + HELD_VERB:
        ev = f"lex:v3:{w}:{TRAIN_SALT}"
        lex.add(
            Lexeme(
                w,
                Category.VERB,
                (Sense(f"l1v3:{w}", w, "event", _w(ev), scope=sc),),
                warrant=_w(ev),
                scope=sc,
            )
        )
    ev = f"lex:v3:{NEG_PARTICLE}:{TRAIN_SALT}"
    lex.add(
        Lexeme(
            NEG_PARTICLE,
            Category.NEG,
            (Sense(f"l1v3:{NEG_PARTICLE}", NEG_PARTICLE, "value", _w(ev), scope=sc),),
            warrant=_w(ev),
            scope=sc,
        )
    )
    return lex


def role_slots() -> list[tuple[str, Slot]]:
    return [
        ("S", Slot("S", Category.NOUN, features=(("sort", "animate"),))),
        ("V", Slot("V", Category.VERB)),
        ("O", Slot("O", Category.NOUN, features=(("sort", "inanimate"),))),
    ]


def neg_role_slots() -> list[tuple[str, Slot]]:
    return [
        ("S", Slot("S", Category.NOUN, features=(("sort", "animate"),))),
        ("NEG", Slot("NEG", Category.NEG, lemma=NEG_PARTICLE)),
        ("V", Slot("V", Category.VERB)),
        ("O", Slot("O", Category.NOUN, features=(("sort", "inanimate"),))),
    ]


def svo_utt(agent: str, verb: str, patient: str) -> str:
    return f"{agent} {verb} {patient}"


def sov_utt(agent: str, verb: str, patient: str) -> str:
    return f"{agent} {patient} {verb}"


def neg_utt(agent: str, verb: str, patient: str) -> str:
    return f"{agent} {NEG_PARTICLE} {verb} {patient}"


def train_svo_utterances() -> tuple[str, ...]:
    return tuple(svo_utt(a, v, p) for a, v, p in zip(TRAIN_ANIMATE, TRAIN_VERB, TRAIN_ARTIFACT))


def train_sov_utterances() -> tuple[str, ...]:
    return tuple(sov_utt(a, v, p) for a, v, p in zip(TRAIN_ANIMATE, TRAIN_VERB, TRAIN_ARTIFACT))


def train_neg_utterances() -> tuple[str, ...]:
    return tuple(neg_utt(a, v, p) for a, v, p in zip(TRAIN_ANIMATE, TRAIN_VERB, TRAIN_ARTIFACT))


def query_svo() -> tuple[str, ...]:
    return (
        svo_utt(TRAIN_ANIMATE[0], TRAIN_VERB[1], TRAIN_ARTIFACT[1]),
        svo_utt(TRAIN_ANIMATE[1], TRAIN_VERB[0], TRAIN_ARTIFACT[0]),
    )


def query_sov() -> tuple[str, ...]:
    return (
        sov_utt(TRAIN_ANIMATE[0], TRAIN_VERB[1], TRAIN_ARTIFACT[1]),
        sov_utt(TRAIN_ANIMATE[1], TRAIN_VERB[0], TRAIN_ARTIFACT[0]),
    )


def query_neg() -> tuple[str, ...]:
    return (
        neg_utt(TRAIN_ANIMATE[0], TRAIN_VERB[1], TRAIN_ARTIFACT[1]),
        neg_utt(TRAIN_ANIMATE[1], TRAIN_VERB[0], TRAIN_ARTIFACT[0]),
    )


def held_probes() -> dict[str, str]:
    a, p, v = HELD_ANIMATE[0], HELD_ARTIFACT[0], HELD_VERB[0]
    return {
        "svo": svo_utt(a, v, p),
        "sov": sov_utt(a, v, p),
        "negation": neg_utt(a, v, p),
        "type_mismatch_svo": svo_utt(p, v, a),
    }


def evidence_id(kind: str, i: int) -> str:
    return f"lesson:v3:{kind}:{i}:{TRAIN_SALT}"


def transitive_family(language: str, query: tuple[str, ...]) -> AQ.ConstructionFamily:
    return AQ.ConstructionFamily(
        "transitive",
        AQ.order_hypotheses(role_slots()),
        transitive_template,
        query_family=query,
        language=language,
    )


def negation_family() -> AQ.ConstructionFamily:
    return AQ.ConstructionFamily(
        "negation",
        AQ.order_hypotheses(neg_role_slots()),
        negation_template,
        query_family=query_neg(),
        language=LANG_SVO,
    )


def acquire_order(
    language: str,
    utterances: Sequence[str],
    query: tuple[str, ...],
    lex: Lexicon,
    *,
    kind: str,
) -> tuple[AQ.UpdateProposal, Construction]:
    fam = transitive_family(language, query)
    demos = []
    for i, u in enumerate(utterances):
        toks = tokenize(u)
        if language == LANG_SOV:
            agent, patient, verb = toks[0], toks[1], toks[2]
        else:
            agent, verb, patient = toks[0], toks[1], toks[2]
        demos.append(AQ.Demonstration(u, gold_transitive(agent, verb, patient), evidence_id(kind, i)))
    proposal = AQ.acquire(fam, lex, demos)
    if proposal.status is not UpdateStatus.PASS or proposal.kind is not UpdateKind.OBJECT:
        raise RuntimeError(f"order acquisition failed for {language}: {proposal.status} {proposal.detail}")
    return proposal, AQ.construction_from_proposal(fam, proposal, f"l1v3:{language}:transitive")


def acquire_negation(lex: Lexicon, utterances: Sequence[str]) -> tuple[AQ.UpdateProposal, Construction]:
    fam = negation_family()
    demos = []
    for i, u in enumerate(utterances):
        toks = tokenize(u)
        agent, verb, patient = toks[0], toks[2], toks[3]
        demos.append(
            AQ.Demonstration(u, gold_transitive(agent, verb, patient, negated=True), evidence_id("negation", i))
        )
    proposal = AQ.acquire(fam, lex, demos)
    if proposal.status is not UpdateStatus.PASS or proposal.kind is not UpdateKind.OBJECT:
        raise RuntimeError(f"negation acquisition failed: {proposal.status} {proposal.detail}")
    return proposal, AQ.construction_from_proposal(fam, proposal, "l1v3:svo:negation")


def parse(utterance: str, lex: Lexicon, cons: Sequence[Construction], revoked: Iterable[Hashable] = ()) -> dict:
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
        "roles": {},
        "fingerprint": content_hash({"u": utterance, "salt": HELD_SALT, "v": interp.verdict.value}),
    }
    if interp.meaning is not None:
        rec["meaning"] = canonical(interp.meaning)[1]
        rec["n_nodes"] = len(interp.meaning.nodes)
        rec["relations"] = sorted({e.relation for e in interp.meaning.edges})
        rec["roles"] = {
            "agent": next(interp.meaning.node(e.heads[0]).label for e in interp.meaning.edges if e.relation == "ROLE:agent"),
            "patient": next(interp.meaning.node(e.heads[0]).label for e in interp.meaning.edges if e.relation == "ROLE:patient"),
            "event": interp.meaning.node(interp.meaning.root).label,
        }
        rec["fingerprint"] = content_hash({"u": utterance, "canon": rec["meaning"], "salt": HELD_SALT})
    return rec


def grammar_induction_parent(utterances: Iterable[str]) -> tuple[dict[tuple[str, str], int], set[tuple[str, ...]]]:
    counts: dict[tuple[str, str], int] = {}
    identities: set[tuple[str, ...]] = set()
    for u in utterances:
        tokens = tuple(tokenize(u))
        identities.add(tokens)
        for a, b in zip(tokens, tokens[1:]):
            counts[a, b] = counts.get((a, b), 0) + 1
    return counts, identities


def rebuild_transitive(language: str, hyp: str, evidence: Sequence[str], query: tuple[str, ...]) -> Construction:
    fam = transitive_family(language, query)
    if hyp not in fam.hypotheses:
        raise RuntimeError(f"unknown order hypothesis {hyp} for {language}")
    return Construction(
        f"l1v3:{language}:transitive",
        fam.family,
        fam.hypotheses[hyp],
        fam.template,
        _w(*evidence),
        scope=_scope(),
        language=language,
    )


def persist(path: Path, svo_hyp: str, sov_hyp: str, svo_ev: Sequence[str], sov_ev: Sequence[str]) -> None:
    payload = {
        "schema": "ocm.l1.linguistic-g2.v3.skill",
        "salt": TRAIN_SALT,
        "svo_hypothesis": svo_hyp,
        "sov_hypothesis": sov_hyp,
        "svo_evidence": list(svo_ev),
        "sov_evidence": list(sov_ev),
        "digest": content_hash(
            {"salt": TRAIN_SALT, "svo": svo_hyp, "sov": sov_hyp, "svo_ev": list(svo_ev), "sov_ev": list(sov_ev)}
        ),
    }
    path.write_text(json.dumps(payload, sort_keys=True))


def load(path: Path) -> dict:
    payload = json.loads(path.read_text())
    digest = content_hash(
        {
            "salt": TRAIN_SALT,
            "svo": payload["svo_hypothesis"],
            "sov": payload["sov_hypothesis"],
            "svo_ev": payload["svo_evidence"],
            "sov_ev": payload["sov_evidence"],
        }
    )
    if digest != payload["digest"]:
        raise RuntimeError("linguistic skill identity mismatch")
    return payload


def frozen_result_intact(rel: str, schema: str) -> bool:
    p = REPO / "research" / rel / "RESULT.json"
    data = json.loads(p.read_text())
    return data.get("schema") == schema and data.get("terminal") == FROZEN_TERMINAL


def all_surfaces() -> set[str]:
    return set(
        TRAIN_ANIMATE
        + TRAIN_ARTIFACT
        + TRAIN_VERB
        + HELD_ANIMATE
        + HELD_ARTIFACT
        + HELD_VERB
        + (NEG_PARTICLE,)
    )


def main(out: Path) -> dict:
    content = all_surfaces() - {NEG_PARTICLE}
    if content & V1_SURFACES:
        raise RuntimeError("v3 salts collided with v1 surfaces")
    if content & V2_CONTENT_SURFACES:
        raise RuntimeError("v3 salts collided with v2 content surfaces")

    lex = teach_lexicon()
    svo_utts = train_svo_utterances()
    sov_utts = train_sov_utterances()
    neg_utts = train_neg_utterances()
    probes = held_probes()
    held_gold = gold_transitive(HELD_ANIMATE[0], HELD_VERB[0], HELD_ARTIFACT[0])
    held_neg_gold = gold_transitive(HELD_ANIMATE[0], HELD_VERB[0], HELD_ARTIFACT[0], negated=True)

    svo_prop, svo_c = acquire_order(LANG_SVO, svo_utts, query_svo(), lex, kind="svo")
    sov_prop, sov_c = acquire_order(LANG_SOV, sov_utts, query_sov(), lex, kind="sov")

    svo_on_svo = parse(probes["svo"], lex, [svo_c])
    svo_on_sov = parse(probes["sov"], lex, [svo_c])
    sov_on_sov = parse(probes["sov"], lex, [sov_c])
    sov_on_svo = parse(probes["svo"], lex, [sov_c])
    mismatch = parse(probes["type_mismatch_svo"], lex, [svo_c])
    train_svo_ok = parse(svo_utts[0], lex, [svo_c])

    forced = T.mutant_transfer_word_order(svo_c, LANG_SOV)
    forced_row = parse(probes["sov"], lex, [forced])
    swapped = mutant_word_order_swap(svo_c)
    swapped_row = parse(probes["svo"], lex, [swapped])
    scope_ok = AQ.scope_check(svo_c, LANG_SVO) and not AQ.scope_check(svo_c, LANG_SOV)
    wo_transfer = T.propose_transfer("cons:l1v3:svo:transitive", T.TransferClass.WORD_ORDER, LANG_SVO, LANG_SOV)
    meaning_transfer = T.propose_transfer("meaning:transitive", T.TransferClass.MEANING_STRUCTURE, LANG_SVO, LANG_SOV)

    family_transfer = parse(probes["negation"], lex, [svo_c])
    neg_prop, neg_c = acquire_negation(lex, neg_utts)
    neg_after_own_family = parse(probes["negation"], lex, [neg_c])
    neg_train_ok = parse(neg_utts[0], lex, [neg_c])

    _counts, identities = grammar_induction_parent(svo_utts + sov_utts)
    parent_has_fresh = tuple(tokenize(probes["svo"])) in identities or tuple(tokenize(probes["sov"])) in identities

    path = out.parent / "grammar.json"
    svo_ev = tuple(evidence_id("svo", i) for i in range(len(svo_utts)))
    sov_ev = tuple(evidence_id("sov", i) for i in range(len(sov_utts)))
    persist(path, svo_prop.payload["hypothesis"], sov_prop.payload["hypothesis"], svo_ev, sov_ev)
    loaded = load(path)
    restarted_svo = rebuild_transitive(LANG_SVO, loaded["svo_hypothesis"], loaded["svo_evidence"], query_svo())
    restarted_sov = rebuild_transitive(LANG_SOV, loaded["sov_hypothesis"], loaded["sov_evidence"], query_sov())
    restart_svo = parse(probes["svo"], lex, [restarted_svo])
    restart_sov = parse(probes["sov"], lex, [restarted_sov])

    reset_svo = parse(probes["svo"], lex, [])
    reset_sov = parse(probes["sov"], lex, [])

    revoked = set(svo_prop.warrant.evidence)
    revoked_svo = parse(probes["svo"], lex, [svo_c], revoked)
    unrelated_sov = parse(probes["sov"], lex, [sov_c], revoked)
    alt_ev = f"lesson:v3:svo:alt:{TRAIN_SALT}"
    alt_w = WarrantProfile.of(set(svo_prop.warrant.evidence), {alt_ev})
    alt_c = Construction(
        svo_c.construction_id,
        svo_c.family,
        svo_c.pattern,
        svo_c.template,
        alt_w,
        scope=svo_c.scope,
        language=svo_c.language,
    )
    restored = parse(probes["svo"], lex, [alt_c], revoked)

    svo_meaning_ok = svo_on_svo["invoked"] and isomorphic(interpret(probes["svo"], lex, [svo_c]).meaning, held_gold)
    sov_meaning_ok = sov_on_sov["invoked"] and isomorphic(interpret(probes["sov"], lex, [sov_c]).meaning, held_gold)
    english_rejects_sov = not svo_on_sov["invoked"]
    sov_rejects_svo = not sov_on_svo["invoked"]
    forced_interp = interpret(probes["sov"], lex, [forced])
    forced_hostile = (not forced_row["invoked"]) or (
        forced_interp.meaning is not None and not isomorphic(forced_interp.meaning, held_gold)
    )
    swapped_hostile = swapped_row["invoked"] and swapped_row["roles"].get("agent") == HELD_ARTIFACT[0]
    family_transfer_failed = not family_transfer["invoked"]
    negation_own_family_ok = neg_after_own_family["invoked"] and isomorphic(
        interpret(probes["negation"], lex, [neg_c]).meaning, held_neg_gold
    )
    restart_ok = restart_svo["meaning"] == svo_on_svo["meaning"] and restart_sov["meaning"] == sov_on_sov["meaning"]
    reset_fails = (not reset_svo["invoked"]) and (not reset_sov["invoked"])
    revoke_kills = not revoked_svo["invoked"]
    unrelated_ok = unrelated_sov["invoked"]
    alt_ok = restored["invoked"]
    type_ok = train_svo_ok["invoked"] and not mismatch["invoked"]
    node_rows = (svo_on_svo, sov_on_sov, neg_after_own_family, train_svo_ok, neg_train_ok)
    nodes_ok = all(row["n_nodes"] <= MAX_EXACT_CANONICAL for row in node_rows if row["n_nodes"])
    max_nodes = max(row["n_nodes"] for row in node_rows)
    v1_ok = frozen_result_intact("l1-linguistic-g2-v1", V1_FROZEN_SCHEMA)
    v2_ok = frozen_result_intact("l1-linguistic-g2-v2", V2_FROZEN_SCHEMA)
    induced = svo_prop.payload["hypothesis"] == "SVO" and sov_prop.payload["hypothesis"] == "SOV"
    transfer_refused = (not wo_transfer.allowed) and meaning_transfer.allowed

    artificial_ok = (
        induced
        and svo_meaning_ok
        and sov_meaning_ok
        and english_rejects_sov
        and sov_rejects_svo
        and forced_hostile
        and scope_ok
        and transfer_refused
    )
    g2_ok = svo_meaning_ok and restart_ok and revoke_kills and reset_fails and not parent_has_fresh

    if artificial_ok and family_transfer_failed and negation_own_family_ok and g2_ok and v1_ok and v2_ok:
        terminal = "COMPOSITIONAL_LANGUAGE_LEARNING_ONLY"
    elif g2_ok:
        terminal = "PARENT_SUFFICIENT"
    else:
        terminal = "NO_LANGUAGE_META_LEARNING"

    earned = "EARNED_AT_SCOPE"
    checklist = {
        "acquire_corpus_scale_lexicon": "CANNOT_CHECK_MINIATURE_MICROWORLD",
        "retain_polysemy": "CANNOT_CHECK_NOT_RUN_HERE",
        "induce_constructions": earned if induced else "OPEN",
        "recursive_composition": "CANNOT_CHECK_NOT_RUN_HERE",
        "meaning_graphs_beyond_bound": "CANNOT_CHECK_MICROWORLD_SMALL",
        "exact_canonicalization": earned if nodes_ok else "OPEN",
        "quantifier_scope": "CANNOT_CHECK_NOT_RUN_HERE",
        "negation": earned if negation_own_family_ok else "OPEN",
        "typed_entities": earned if type_ok else "OPEN",
        "ud_alignment": "CANNOT_CHECK_NO_UD_IN_THIS_STUDY",
        "held_out_lexical_fillers": earned if svo_meaning_ok and sov_meaning_ok and not parent_has_fresh else "OPEN",
        "held_out_construction_combinations": "CANNOT_CHECK_NOT_RUN_HERE",
        "held_out_construction_families": "NO_CROSS_FAMILY_TRANSFER" if family_transfer_failed and negation_own_family_ok else "OPEN",
        "artificial_non_english": earned if artificial_ok else "OPEN",
        "acquisition_curves": "CANNOT_CHECK_N_TOO_SMALL",
        "correction_revocation": earned if revoke_kills and unrelated_ok and alt_ok else "OPEN",
        "reset_control": earned if reset_fails else "OPEN",
        "grammar_induction_parent": earned if not parent_has_fresh else "OPEN",
        "persistent_grammar_parent": earned if restart_ok else "OPEN",
        "continual_adaptation_parent": "CANNOT_CHECK_NOT_RUN",
        "open_weight_lm_reference": "CANNOT_CHECK_NO_MODEL_WEIGHTS",
        "g2_causal_reuse_linguistic": earned if g2_ok else "OPEN",
    }
    result = {
        "schema": SCHEMA,
        "terminal": terminal,
        "fresh_invoked": svo_meaning_ok and sov_meaning_ok,
        "svo_hypothesis": svo_prop.payload["hypothesis"],
        "sov_hypothesis": sov_prop.payload["hypothesis"],
        "negation_hypothesis": neg_prop.payload["hypothesis"],
        "english_rejects_sov": english_rejects_sov,
        "sov_rejects_svo": sov_rejects_svo,
        "sov_meaning_intact": sov_meaning_ok,
        "forced_word_order_hostile": forced_hostile,
        "scope_blocks_silent_relabel": scope_ok,
        "word_order_transfer_refused": not wo_transfer.allowed,
        "meaning_structure_transfer_allowed": meaning_transfer.allowed,
        "family_transfer_succeeded": not family_transfer_failed,
        "family_transfer_failure_is_mechanism": family_transfer_failed and negation_own_family_ok,
        "held_out_family": "negation",
        "trained_family": "transitive",
        "negation_acquirable_from_own_family": negation_own_family_ok,
        "restart_equivalent": restart_ok,
        "revocation_removes_effect": revoke_kills,
        "unrelated_survives_revocation": unrelated_ok,
        "alternate_support_restores": alt_ok,
        "reset_has_no_construction": reset_fails,
        "grammar_induction_parent_has_fresh_identity": parent_has_fresh,
        "type_mismatch_rejected": not mismatch["invoked"],
        "swapped_roles_mutant_detected": swapped_hostile,
        "max_nodes": max_nodes,
        "canonical_bound": MAX_EXACT_CANONICAL,
        "l2_started": False,
        "l3_started": False,
        "v1_result_intact": v1_ok,
        "v2_result_intact": v2_ok,
        "loaded_hypotheses": {"svo": loaded["svo_hypothesis"], "sov": loaded["sov_hypothesis"]},
        "salts": {"train": TRAIN_SALT, "held": HELD_SALT, "scope": SCOPE_ID},
        "checklist": checklist,
        "held_rows": {
            "svo_on_svo": svo_on_svo,
            "svo_on_sov": svo_on_sov,
            "sov_on_sov": sov_on_sov,
            "sov_on_svo": sov_on_svo,
            "forced_svo_pattern_on_sov": forced_row,
            "family_transfer_negation": family_transfer,
            "negation_own_family": neg_after_own_family,
        },
        "claim_ceiling": (
            "SOV hostile and held-out family transfer check in an exact microworld. "
            "Transitive order transfers across lexical fillers, not across construction families. "
            "Not corpus-scale N1 completion. L2/L3 locked."
        ),
    }
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(
        json.dumps(
            {
                "terminal": terminal,
                "svo": svo_prop.payload["hypothesis"],
                "sov": sov_prop.payload["hypothesis"],
                "english_rejects_sov": english_rejects_sov,
                "sov_meaning_intact": sov_meaning_ok,
                "family_transfer": not family_transfer_failed,
                "negation_own_family": negation_own_family_ok,
                "artificial": checklist["artificial_non_english"],
                "held_families": checklist["held_out_construction_families"],
            }
        )
    )
    return result


if __name__ == "__main__":
    target = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parent / "RESULT.json"
    main(target)
