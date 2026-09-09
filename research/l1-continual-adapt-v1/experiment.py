"""Bounded L1 continual-adaptation parent at planted microworld scope.

Two sessions. Session 1 acquires an SVO transitive construction and persists
the grammar. Session 2 admits a new lexical filler (no construction re-demo)
and a word-order drift (SOV demonstrations of the same family).

Arms:
- reset: wipe constructions; session-2 information only
- continued: persist construction identity; incremental lexicon; revoke on drift
- continual-adaptation parent: experience replay of live demonstrations
  (P4 replay/update under matched information)

v1–v4 RESULT.json are cited, not overwritten. New salts. No src edits.
Not corpus-scale N1. L2/L3 locked. N2 morphology not started.
PARENT_SUFFICIENT is not programme failure.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any, Hashable, Iterable, Mapping, Sequence

REPO = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
SRC = REPO / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from ocm.kso.ids import content_hash
from ocm.kso.types import Scope
from ocm.kso.warrant import WarrantProfile
from ocm.language import acquisition as AQ
from ocm.language.constructions import Construction, Slot
from ocm.language.interpret import Verdict, interpret, tokenize
from ocm.language.lexicon import Category, Lexeme, Lexicon, Sense, mutant_nearest_spelling
from ocm.language.meaning import MAX_EXACT_CANONICAL, MEdge, MNode, MeaningGraph, canonical, isomorphic
from ocm.learning.learner import UpdateKind, UpdateStatus

TRAIN_SALT = "orion-ocm-l1-continual-adapt-v1-s1-train"
HELD_SALT = "orion-ocm-l1-continual-adapt-v1-s2-held"
SCOPE_ID = "l1-microworld.continual-adapt.v1"
LANG = "l1ca-en"
SCHEMA = "ocm.l1.continual-adapt.v1"

S1_ANIMATE = ("numbat", "quokka")
S1_ARTIFACT = ("astrolabe", "orrery")
S1_VERB = ("assay", "anneal")
S2_ANIMATE = ("fennec",)
S2_ARTIFACT = ("pyx",)
S2_VERB = ("inlay",)

V1_SURFACES = frozenset({"red", "blue", "green", "cube", "sphere", "pyramid", "two"})
V2_CONTENT_SURFACES = frozenset(
    {"otter", "heron", "lantern", "casket", "inspect", "lynx", "goblet", "conceal", "bank"}
)
V3_CONTENT_SURFACES = frozenset(
    {"ibis", "stoat", "chalice", "amulet", "reveal", "unseal", "jackal", "reliquary", "bury"}
)
V4_CONTENT_SURFACES = frozenset(
    {
        "kudu",
        "wapiti",
        "censer",
        "thurible",
        "anoint",
        "gild",
        "weld",
        "caracal",
        "phylactery",
        "entomb",
        "ochre",
        "tawny",
        "purl",
        "lilt",
        "vault",
        "hoist",
        "enshroud",
        "varnish",
        "slay",
        "slew",
        "bring",
        "brought",
        "did",
        "do",
        "may",
    }
)

FROZEN_TERMINAL = "COMPOSITIONAL_LANGUAGE_LEARNING_ONLY"
FROZEN_CAPS = (
    ("l1-linguistic-g2-v1", "ocm.l1.linguistic-g2.v1", "3083d4286a8d569771da1dad3dc244a6dafa56652a361a9cd1419be4dcc3fe94"),
    ("l1-linguistic-g2-v2", "ocm.l1.linguistic-g2.v2", "133e8550b0948ddbfb4b3e1673aae80c3d4de225e4004738639ed15e1b301a60"),
    ("l1-linguistic-g2-v3", "ocm.l1.linguistic-g2.v3", "a8943fcbe0ffe92f0537f27b166686cd9aab4a34b21c5dc8ad286e3ec1e3b79f"),
    ("l1-linguistic-g2-v4", "ocm.l1.linguistic-g2.v4", "cf168d7bfcdfabf01f53d0ca462218266ce134aff65fad4aa721062bd3c883ae"),
)

LEGAL_TERMINALS = (
    "CONTINUAL_ADAPTATION_SUPPORTED_AT_SCOPE",
    "PARENT_SUFFICIENT",
    "RESET_PARENT_EQUIVALENT",
)


def _scope() -> Scope:
    return Scope.of(SCOPE_ID)


def _w(*evidence: str) -> WarrantProfile:
    return WarrantProfile.of(set(evidence))


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def all_surfaces() -> set[str]:
    return set(S1_ANIMATE + S1_ARTIFACT + S1_VERB + S2_ANIMATE + S2_ARTIFACT + S2_VERB)


def gold_transitive(agent: str, verb: str, patient: str) -> MeaningGraph:
    return MeaningGraph(
        (
            MNode("x1", "entity", agent, (("sort", "animate"),)),
            MNode("e", "event", verb),
            MNode("x2", "entity", patient, (("sort", "inanimate"),)),
        ),
        (
            MEdge("ROLE:agent", ("e",), ("x1",)),
            MEdge("ROLE:patient", ("e",), ("x2",)),
        ),
        root="e",
    )


def transitive_template(b: Mapping[str, Any]) -> MeaningGraph:
    return gold_transitive(b["S"].lemma, b["V"].lemma, b["O"].lemma)


def role_slots() -> list[tuple[str, Slot]]:
    return [
        ("S", Slot("S", Category.NOUN, features=(("sort", "animate"),))),
        ("V", Slot("V", Category.VERB)),
        ("O", Slot("O", Category.NOUN, features=(("sort", "inanimate"),))),
    ]


def svo_utt(agent: str, verb: str, patient: str) -> str:
    return f"{agent} {verb} {patient}"


def sov_utt(agent: str, verb: str, patient: str) -> str:
    return f"{agent} {patient} {verb}"


def s1_train_utterances() -> tuple[str, ...]:
    return tuple(svo_utt(a, v, p) for a, v, p in zip(S1_ANIMATE, S1_VERB, S1_ARTIFACT))


def s1_query_utterances() -> tuple[str, ...]:
    return (
        svo_utt(S1_ANIMATE[0], S1_VERB[1], S1_ARTIFACT[1]),
        svo_utt(S1_ANIMATE[1], S1_VERB[0], S1_ARTIFACT[0]),
    )


def s1_held_probe() -> str:
    return s1_query_utterances()[0]


def s2_filler_probe() -> str:
    return svo_utt(S2_ANIMATE[0], S2_VERB[0], S2_ARTIFACT[0])


def s2_drift_train() -> tuple[str, ...]:
    return tuple(sov_utt(a, v, p) for a, v, p in zip(S1_ANIMATE, S1_VERB, S1_ARTIFACT))


def s2_drift_probe() -> str:
    a, v, p = S1_ANIMATE[0], S1_VERB[1], S1_ARTIFACT[1]
    return sov_utt(a, v, p)


def add_lexeme(lex: Lexicon, surface: str, category: Category, node_type: str, sort: str | None, salt: str) -> None:
    ev = f"lex:l1ca:{surface}:{salt}"
    features = (("sort", sort),) if sort else ()
    lex.add(
        Lexeme(
            surface,
            category,
            (Sense(f"l1ca:{surface}", surface, node_type, _w(ev), scope=_scope()),),
            features=features,
            warrant=_w(ev),
            scope=_scope(),
        )
    )


def teach_lexicon(include_s2: bool) -> Lexicon:
    lex = Lexicon()
    for w in S1_ANIMATE:
        add_lexeme(lex, w, Category.NOUN, "entity", "animate", TRAIN_SALT)
    for w in S1_ARTIFACT:
        add_lexeme(lex, w, Category.NOUN, "entity", "inanimate", TRAIN_SALT)
    for w in S1_VERB:
        add_lexeme(lex, w, Category.VERB, "event", None, TRAIN_SALT)
    if include_s2:
        admit_session2_lexemes(lex)
    return lex


def admit_session2_lexemes(lex: Lexicon) -> None:
    for w in S2_ANIMATE:
        add_lexeme(lex, w, Category.NOUN, "entity", "animate", HELD_SALT)
    for w in S2_ARTIFACT:
        add_lexeme(lex, w, Category.NOUN, "entity", "inanimate", HELD_SALT)
    for w in S2_VERB:
        add_lexeme(lex, w, Category.VERB, "event", None, HELD_SALT)


def evidence_id(kind: str, i: int) -> str:
    return f"lesson:l1ca:{kind}:{i}:{TRAIN_SALT}"


def family(query: tuple[str, ...]) -> AQ.ConstructionFamily:
    return AQ.ConstructionFamily(
        "transitive",
        AQ.order_hypotheses(role_slots()),
        transitive_template,
        query_family=query,
        language=LANG,
    )


def demos_from_svo(utterances: Sequence[str], kind: str) -> list[AQ.Demonstration]:
    out = []
    for i, u in enumerate(utterances):
        toks = tokenize(u)
        agent, verb, patient = toks[0], toks[1], toks[2]
        out.append(AQ.Demonstration(u, gold_transitive(agent, verb, patient), evidence_id(kind, i)))
    return out


def demos_from_sov(utterances: Sequence[str], kind: str) -> list[AQ.Demonstration]:
    out = []
    for i, u in enumerate(utterances):
        toks = tokenize(u)
        agent, patient, verb = toks[0], toks[1], toks[2]
        out.append(AQ.Demonstration(u, gold_transitive(agent, verb, patient), evidence_id(kind, i)))
    return out


def acquire_from(demos: Sequence[AQ.Demonstration], query: tuple[str, ...], lex: Lexicon, cid: str) -> tuple[AQ.UpdateProposal, Construction | None]:
    fam = family(query)
    proposal = AQ.acquire(fam, lex, demos)
    if proposal.status is not UpdateStatus.PASS or proposal.kind is not UpdateKind.OBJECT:
        return proposal, None
    return proposal, AQ.construction_from_proposal(fam, proposal, cid)


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


def persist(path: Path, hypothesis: str, evidence: Sequence[str]) -> None:
    payload = {
        "schema": "ocm.l1.continual-adapt.v1.skill",
        "salt": TRAIN_SALT,
        "hypothesis": hypothesis,
        "evidence": list(evidence),
        "language": LANG,
        "family": "transitive",
        "digest": content_hash({"salt": TRAIN_SALT, "hyp": hypothesis, "ev": list(evidence), "lang": LANG}),
    }
    path.write_text(json.dumps(payload, sort_keys=True) + "\n")


def load(path: Path) -> dict:
    payload = json.loads(path.read_text())
    digest = content_hash(
        {"salt": TRAIN_SALT, "hyp": payload["hypothesis"], "ev": payload["evidence"], "lang": payload["language"]}
    )
    if digest != payload["digest"]:
        raise RuntimeError("continual-adapt skill identity mismatch")
    return payload


def rebuild(hypothesis: str, evidence: Sequence[str], query: tuple[str, ...]) -> Construction:
    fam = family(query)
    if hypothesis not in fam.hypotheses:
        raise RuntimeError(f"unknown hypothesis {hypothesis}")
    return Construction(
        "l1ca:s1:transitive",
        fam.family,
        fam.hypotheses[hypothesis],
        fam.template,
        _w(*evidence),
        scope=_scope(),
        language=LANG,
    )


def ngram_parent(utterances: Iterable[str]) -> tuple[dict[tuple[str, str], int], set[tuple[str, ...]]]:
    counts: dict[tuple[str, str], int] = {}
    identities: set[tuple[str, ...]] = set()
    for u in utterances:
        tokens = tuple(tokenize(u))
        identities.add(tokens)
        for a, b in zip(tokens, tokens[1:]):
            counts[a, b] = counts.get((a, b), 0) + 1
    return counts, identities


def frozen_citations() -> list[dict[str, Any]]:
    rows = []
    for rel, schema, expected in FROZEN_CAPS:
        path = REPO / "research" / rel / "RESULT.json"
        data = json.loads(path.read_text())
        digest = file_sha256(path)
        rows.append(
            {
                "capsule": rel,
                "schema": data.get("schema"),
                "expected_schema": schema,
                "terminal": data.get("terminal"),
                "continual_adaptation_parent": data.get("checklist", {}).get("continual_adaptation_parent"),
                "sha256": digest,
                "expected_sha256": expected,
                "intact": (
                    data.get("schema") == schema
                    and data.get("terminal") == FROZEN_TERMINAL
                    and data.get("checklist", {}).get("continual_adaptation_parent") == "CANNOT_CHECK_NOT_RUN"
                    and digest == expected
                ),
            }
        )
    return rows


def arm_ok(row: dict, gold: MeaningGraph, lex: Lexicon, cons: Sequence[Construction], revoked: Iterable[Hashable] = ()) -> bool:
    if not row["invoked"]:
        return False
    meaning = interpret(row["utterance"], lex, cons, revoked=revoked).meaning
    return meaning is not None and isomorphic(meaning, gold)


def decide_terminal(
    *,
    continued_add: bool,
    parent_add: bool,
    reset_add: bool,
    continued_drift: bool,
    parent_live_drift: bool,
    reset_drift: bool,
    union_contradiction: bool,
    citations_ok: bool,
) -> str:
    if not citations_ok:
        return "CANNOT_CHECK_FROZEN_CITATION"
    additive_equal = continued_add == parent_add == reset_add
    drift_update_equal = continued_drift == parent_live_drift == reset_drift
    if continued_add and parent_add and not reset_add:
        return "PARENT_SUFFICIENT"
    if continued_add and not parent_add and not reset_add:
        return "CONTINUAL_ADAPTATION_SUPPORTED_AT_SCOPE"
    if additive_equal and drift_update_equal:
        return "RESET_PARENT_EQUIVALENT"
    if parent_add and parent_live_drift and not continued_add:
        return "PARENT_SUFFICIENT"
    if union_contradiction and continued_drift and parent_live_drift:
        return "PARENT_SUFFICIENT" if parent_add or not continued_add else "CONTINUAL_ADAPTATION_SUPPORTED_AT_SCOPE"
    return "CANNOT_CHECK_INCONCLUSIVE"


def box_mapping(terminal: str, payload: Mapping[str, Any]) -> list[dict[str, Any]]:
    add_earned = payload["additive"]["continued"]["s1_retention"] and payload["additive"]["continued"]["s2_filler"]
    parent_add = payload["additive"]["parent_replay"]["s1_retention"] and payload["additive"]["parent_replay"]["s2_filler"]
    return [
        {
            "id": "L1/021-continual_adaptation_parent",
            "checkbox": "continual adaptation parent",
            "at_this_microscope": "CHECK" if terminal in LEGAL_TERMINALS else "CANNOT_CHECK",
            "programme_tick": False,
            "witness": (
                f"{terminal}; additive continued==parent={add_earned and parent_add}; "
                "reset lacks persisted construction so session-2 filler-only lessons do not restore S1."
            ),
        },
        {
            "id": "L1/020-persistent_grammar_parent",
            "checkbox": "persistent grammar/skill parent",
            "at_this_microscope": "CITED_NOT_RETICKED",
            "programme_tick": False,
            "witness": "Cited v1–v4 EARNED_AT_SCOPE; this capsule reuses persist as the continued arm.",
        },
        {
            "id": "L1/001-acquire_corpus_scale_lexicon",
            "checkbox": "acquire corpus-scale lexicon",
            "at_this_microscope": "CANNOT_CHECK_MINIATURE_MICROWORLD",
            "programme_tick": False,
            "witness": "Planted two-session microworld; not corpus-scale N1.",
        },
        {
            "id": "L2/learn_morphology_agreement",
            "checkbox": "learn morphology/agreement",
            "at_this_microscope": "CANNOT_CHECK_N2_LOCKED",
            "programme_tick": False,
            "witness": "N2 morphology boxes are not started. v4 microworld morphology is cited, not promoted to N2.",
        },
        {
            "id": "L2-entire",
            "checkbox": "L2 learned realization/discourse",
            "at_this_microscope": "LOCKED",
            "programme_tick": False,
            "witness": "l2_started=false",
        },
        {
            "id": "L3-entire",
            "checkbox": "L3 provenance-bound open-domain dialogue",
            "at_this_microscope": "LOCKED",
            "programme_tick": False,
            "witness": "l3_started=false; multi-session here is L1 grammar persist, not L3 dialogue.",
        },
    ]


def main(out: Path) -> dict:
    content = all_surfaces()
    if content & V1_SURFACES:
        raise RuntimeError("continual-adapt salts collided with v1 surfaces")
    if content & V2_CONTENT_SURFACES:
        raise RuntimeError("continual-adapt salts collided with v2 content surfaces")
    if content & V3_CONTENT_SURFACES:
        raise RuntimeError("continual-adapt salts collided with v3 content surfaces")
    if content & V4_CONTENT_SURFACES:
        raise RuntimeError("continual-adapt salts collided with v4 content surfaces")

    citations = frozen_citations()
    citations_ok = all(row["intact"] for row in citations)

    s1_lex = teach_lexicon(include_s2=False)
    s1_train = s1_train_utterances()
    s1_query = s1_query_utterances()
    s1_demos = demos_from_svo(s1_train, "s1-svo")
    s1_prop, s1_c = acquire_from(s1_demos, s1_query, s1_lex, "l1ca:s1:transitive")
    if s1_c is None:
        raise RuntimeError(f"session-1 acquisition failed: {s1_prop.status} {s1_prop.detail}")

    s1_held = s1_held_probe()
    s1_gold = gold_transitive(S1_ANIMATE[0], S1_VERB[1], S1_ARTIFACT[1])
    s1_row = parse(s1_held, s1_lex, [s1_c])
    s1_ok = arm_ok(s1_row, s1_gold, s1_lex, [s1_c])

    grammar_path = out.parent / "grammar.json"
    s1_evidence = tuple(d.evidence_id for d in s1_demos)
    persist(grammar_path, s1_prop.payload["hypothesis"], s1_evidence)
    loaded = load(grammar_path)
    restarted = rebuild(loaded["hypothesis"], loaded["evidence"], s1_query)
    restart_row = parse(s1_held, s1_lex, [restarted])
    restart_ok = restart_row["meaning"] == s1_row["meaning"] and s1_ok

    # --- session 2 additive: new lexemes only, no construction re-demo ---
    continued_lex = teach_lexicon(include_s2=False)
    admit_session2_lexemes(continued_lex)
    s2_probe = s2_filler_probe()
    s2_gold = gold_transitive(S2_ANIMATE[0], S2_VERB[0], S2_ARTIFACT[0])
    continued_s1 = parse(s1_held, continued_lex, [restarted])
    continued_s2 = parse(s2_probe, continued_lex, [restarted])
    continued_s1_ok = arm_ok(continued_s1, s1_gold, continued_lex, [restarted])
    continued_s2_ok = arm_ok(continued_s2, s2_gold, continued_lex, [restarted])

    reset_lex = teach_lexicon(include_s2=True)
    reset_s1 = parse(s1_held, reset_lex, [])
    reset_s2 = parse(s2_probe, reset_lex, [])
    reset_s1_ok = reset_s1["invoked"]
    reset_s2_ok = reset_s2["invoked"]

    replay_prop, replay_c = acquire_from(s1_demos, s1_query, continued_lex, "l1ca:replay:transitive")
    if replay_c is None:
        raise RuntimeError(f"replay parent failed to re-induce S1: {replay_prop.status} {replay_prop.detail}")
    parent_s1 = parse(s1_held, continued_lex, [replay_c])
    parent_s2 = parse(s2_probe, continued_lex, [replay_c])
    parent_s1_ok = arm_ok(parent_s1, s1_gold, continued_lex, [replay_c])
    parent_s2_ok = arm_ok(parent_s2, s2_gold, continued_lex, [replay_c])

    spelling = mutant_nearest_spelling(s1_lex, S2_ANIMATE[0])
    spelling_parent_wrong = spelling is not None and spelling.lemma != S2_ANIMATE[0]

    _counts, identities = ngram_parent(s1_train)
    ngram_has_s2 = tuple(tokenize(s2_probe)) in identities

    # --- session 2 drift: same family, SOV demonstrations ---
    drift_demos = demos_from_sov(s2_drift_train(), "s2-sov")
    drift_probe = s2_drift_probe()
    drift_gold = gold_transitive(S1_ANIMATE[0], S1_VERB[1], S1_ARTIFACT[1])

    union_prop, union_c = acquire_from(s1_demos + drift_demos, s1_query, s1_lex, "l1ca:union:transitive")
    union_contradiction = union_c is None and union_prop.status is UpdateStatus.CONTRADICTION
    if not union_contradiction:
        union_contradiction = union_c is None and union_prop.status is not UpdateStatus.PASS

    revoked = set(s1_evidence)
    live_prop, live_c = acquire_from(drift_demos, (drift_probe, s2_drift_train()[1]), s1_lex, "l1ca:live:transitive")
    drift_reset_prop, drift_reset_c = acquire_from(
        drift_demos, (drift_probe, s2_drift_train()[1]), s1_lex, "l1ca:reset-drift:transitive"
    )

    continued_drift_row = parse(drift_probe, s1_lex, [live_c] if live_c else [], revoked)
    continued_after_drift_svo = parse(s1_held, s1_lex, [live_c] if live_c else [], revoked)
    naive_continued_drift = parse(drift_probe, s1_lex, [restarted])
    reset_drift_row = parse(drift_probe, s1_lex, [drift_reset_c] if drift_reset_c else [])
    reset_after_drift_svo = parse(s1_held, s1_lex, [drift_reset_c] if drift_reset_c else [])
    parent_live_drift_row = parse(drift_probe, s1_lex, [live_c] if live_c else [], revoked)
    union_drift_row = parse(drift_probe, s1_lex, [union_c] if union_c else [])

    continued_drift_ok = live_c is not None and arm_ok(
        continued_drift_row, drift_gold, s1_lex, [live_c], revoked
    )
    parent_live_drift_ok = continued_drift_ok
    reset_drift_ok = drift_reset_c is not None and arm_ok(reset_drift_row, drift_gold, s1_lex, [drift_reset_c])
    svo_forgotten_after_drift = (not continued_after_drift_svo["invoked"]) and (not reset_after_drift_svo["invoked"])

    reset_empty = parse(s1_held, s1_lex, [])
    reset_has_no_construction = not reset_empty["invoked"]

    continued_add = continued_s1_ok and continued_s2_ok
    parent_add = parent_s1_ok and parent_s2_ok
    reset_add = reset_s1_ok and reset_s2_ok

    terminal = decide_terminal(
        continued_add=continued_add,
        parent_add=parent_add,
        reset_add=reset_add,
        continued_drift=continued_drift_ok,
        parent_live_drift=parent_live_drift_ok,
        reset_drift=reset_drift_ok,
        union_contradiction=union_contradiction,
        citations_ok=citations_ok,
    )
    if terminal not in LEGAL_TERMINALS and not str(terminal).startswith("CANNOT_CHECK_"):
        raise RuntimeError(f"illegal terminal {terminal}")

    node_rows = [s1_row, continued_s2, continued_drift_row]
    max_nodes = max((row["n_nodes"] for row in node_rows if row["n_nodes"]), default=0)
    nodes_ok = max_nodes <= MAX_EXACT_CANONICAL

    boxes = box_mapping(
        terminal,
        {
            "additive": {
                "continued": {"s1_retention": continued_s1_ok, "s2_filler": continued_s2_ok},
                "parent_replay": {"s1_retention": parent_s1_ok, "s2_filler": parent_s2_ok},
            }
        },
    )
    if any(b["programme_tick"] for b in boxes):
        raise RuntimeError("programme_tick must stay false")

    earned = "EARNED_AT_SCOPE"
    checklist = {
        "acquire_corpus_scale_lexicon": "CANNOT_CHECK_MINIATURE_MICROWORLD",
        "continual_adaptation_parent": terminal,
        "correction_revocation": earned if svo_forgotten_after_drift and continued_drift_ok else "OPEN",
        "g2_causal_reuse_linguistic": earned if continued_s2_ok and restart_ok else "OPEN",
        "grammar_induction_parent": earned if not ngram_has_s2 else "OPEN",
        "held_out_lexical_fillers": "CITED_V1_V4_EARNED_AT_SCOPE",
        "induce_constructions": earned if s1_prop.payload["hypothesis"] == "SVO" else "OPEN",
        "learn_morphology_agreement": "CANNOT_CHECK_N2_LOCKED",
        "learn_questions_negation_modality": "CANNOT_CHECK_N2_LOCKED",
        "meaning_graphs_beyond_bound": "CANNOT_CHECK_MICROWORLD_SMALL",
        "multi_session_l3": "CANNOT_CHECK_L3_LOCKED",
        "open_weight_lm_reference": "CANNOT_CHECK_NO_MODEL_WEIGHTS",
        "persistent_grammar_parent": "CITED_V1_V4_EARNED_AT_SCOPE",
        "reset_control": earned if reset_has_no_construction and not reset_add else "OPEN",
        "recursive_composition_lot_l2": "CANNOT_CHECK_L2_LOCKED",
        "ud_alignment": "CITED_V4_EARNED_AT_PLANTED_GOLDTREE_SCOPE",
        "ud_parser": "CANNOT_CHECK_NO_UD_PARSER",
    }

    result = {
        "schema": SCHEMA,
        "terminal": terminal,
        "legal_terminals": list(LEGAL_TERMINALS),
        "s1_hypothesis": s1_prop.payload["hypothesis"],
        "replay_hypothesis": replay_prop.payload["hypothesis"],
        "live_drift_hypothesis": live_prop.payload.get("hypothesis") if live_c is not None else None,
        "union_status": union_prop.status.value,
        "union_contradiction": union_contradiction,
        "restart_equivalent": restart_ok,
        "reset_has_no_construction": reset_has_no_construction,
        "grammar_induction_parent_has_fresh_identity": ngram_has_s2,
        "spelling_parent_maps_s2_to_s1": spelling_parent_wrong,
        "spelling_parent_lemma": None if spelling is None else spelling.lemma,
        "naive_persist_without_revoke_fails_sov": not naive_continued_drift["invoked"],
        "svo_forgotten_after_drift_revoke": svo_forgotten_after_drift,
        "additive": {
            "session2_lessons": "lexeme_admission_only",
            "continued": {
                "s1_retention": continued_s1_ok,
                "s2_filler": continued_s2_ok,
                "n_construction_demos": 0,
                "row_s1": continued_s1,
                "row_s2": continued_s2,
            },
            "reset": {
                "s1_retention": reset_s1_ok,
                "s2_filler": reset_s2_ok,
                "n_construction_demos": 0,
                "row_s1": reset_s1,
                "row_s2": reset_s2,
            },
            "parent_replay": {
                "s1_retention": parent_s1_ok,
                "s2_filler": parent_s2_ok,
                "n_construction_demos": len(s1_demos),
                "row_s1": parent_s1,
                "row_s2": parent_s2,
            },
        },
        "drift": {
            "kind": "same_family_word_order_svo_to_sov",
            "continued_revoke_reacquire": continued_drift_ok,
            "parent_live_replay": parent_live_drift_ok,
            "reset_s2_only": reset_drift_ok,
            "naive_union_replay": union_c is not None,
            "row_continued": continued_drift_row,
            "row_reset": reset_drift_row,
            "row_union": union_drift_row,
            "row_naive_persist": naive_continued_drift,
            "row_parent_live": parent_live_drift_row,
        },
        "replay_cost": {
            "continued_additive_s1_replays": 0,
            "parent_additive_s1_replays": len(s1_demos),
            "note": "Outcome match on additive probes is PARENT_SUFFICIENT; persist is cheaper than replay but P4 is allowed the update/replay route.",
        },
        "max_nodes": max_nodes,
        "canonical_bound": MAX_EXACT_CANONICAL,
        "nodes_inside_bound": nodes_ok,
        "l2_started": False,
        "l3_started": False,
        "morphology_n2_started": False,
        "corpus_n1_claimed": False,
        "programme_tick": False,
        "parent_sufficient_is_not_failure": True,
        "frozen_citations": citations,
        "v1_result_intact": citations[0]["intact"],
        "v2_result_intact": citations[1]["intact"],
        "v3_result_intact": citations[2]["intact"],
        "v4_result_intact": citations[3]["intact"],
        "loaded_hypothesis": loaded["hypothesis"],
        "salts": {"train": TRAIN_SALT, "held": HELD_SALT, "scope": SCOPE_ID},
        "boxes": boxes,
        "checklist": checklist,
        "claim_ceiling": (
            "Two-session planted microworld: persist grammar, admit a new lexical filler, "
            "and compare reset vs continued vs live-replay continual-adaptation parent. "
            "Not corpus-scale N1. L2/L3 locked. N2 morphology not started. "
            "PARENT_SUFFICIENT is not programme failure."
        ),
    }
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(
        json.dumps(
            {
                "terminal": terminal,
                "s1_hypothesis": s1_prop.payload["hypothesis"],
                "additive_continued": continued_add,
                "additive_parent": parent_add,
                "additive_reset": reset_add,
                "drift_continued": continued_drift_ok,
                "drift_reset": reset_drift_ok,
                "union_contradiction": union_contradiction,
                "programme_tick": False,
            }
        )
    )
    return result


if __name__ == "__main__":
    target = Path(sys.argv[1]) if len(sys.argv) > 1 else HERE / "RESULT.json"
    main(target)
