"""Bounded L1 G2 v4: morphology/agreement, planted UD, curves, tree bound.

Microworld: HYBRID suffix morphology + number agreement constructions, a tiny
planted CoNLL-U treebank aligned via production gold_meaning (not a UD parser),
acquisition curves over past-tense pairs, exact canonicalization at |V|<=7,
tree-canonical measurement at a registered finite bound of 12, frozen
realization bootstrap + learned lemma→form with reverse-read. Questions and
modality acquired as new families; v2 negation is cited, not copied.
No hidden LLM. Corpus-scale / open-weight LM / neural realizer are CANNOT_CHECK.
L2/L3 stay locked. v1–v3 RESULT.json are not overwritten.
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
from ocm.kso.warrant import CannotCheck, WarrantProfile
from ocm.language import acquisition as AQ
from ocm.language.constructions import Construction, Slot, seed_constructions
from ocm.language.interpret import Verdict, interpret, tokenize
from ocm.language.lexicon import Category, Lexeme, Lexicon, MorphRule, Reading, RuleKind, Sense
from ocm.language.meaning import MAX_EXACT_CANONICAL, MEdge, MNode, MeaningGraph, canonical, isomorphic
from ocm.language.meaning_tree import canonical_any, is_tree
from ocm.language import realize as RZ
from ocm.learning.language import morphology as MO
from ocm.learning.language import ud as UD
from ocm.learning.learner import UpdateKind, UpdateStatus

HERE = Path(__file__).resolve().parent

TRAIN_SALT = "orion-ocm-l1-linguistic-g2-v4-morph-train"
HELD_SALT = "orion-ocm-l1-linguistic-g2-v4-morph-held"
SCOPE_ID = "l1-microworld.v4.morph"
LANG = "l1v4-en"

V1_SURFACES = frozenset({"red", "blue", "green", "cube", "sphere", "pyramid", "two"})
V2_CONTENT_SURFACES = frozenset(
    {"otter", "heron", "lantern", "casket", "inspect", "lynx", "goblet", "conceal", "bank"}
)
V3_CONTENT_SURFACES = frozenset(
    {"ibis", "stoat", "chalice", "amulet", "reveal", "unseal", "jackal", "reliquary", "bury"}
)

TRAIN_ANIMATE = ("kudu", "wapiti")
TRAIN_ARTIFACT = ("censer", "thurible")
TRAIN_VERB = ("anoint", "gild", "weld")
HELD_ANIMATE = ("caracal",)
HELD_ARTIFACT = ("phylactery",)
HELD_VERB = ("entomb",)
ADJ = ("ochre", "tawny")
AUX_DID = "did"
AUX_DO = "do"
AUX_MAY = "may"

REGULAR_PAST: tuple[tuple[str, str], ...] = (
    ("gild", "gilded"),
    ("purl", "purled"),
    ("weld", "welded"),
    ("lilt", "lilted"),
    ("vault", "vaulted"),
    ("hoist", "hoisted"),
    ("anoint", "anointed"),
    ("enshroud", "enshrouded"),
)
HELD_REGULAR_PAST: tuple[tuple[str, str], ...] = (("entomb", "entombed"), ("varnish", "varnished"))
IRREGULAR_PAST: tuple[tuple[str, str], ...] = (("slay", "slew"),)
HELD_IRREGULAR_PAST: tuple[tuple[str, str], ...] = (("bring", "brought"),)

ALL_VERBS = tuple(dict.fromkeys(v for v, _ in REGULAR_PAST + HELD_REGULAR_PAST + IRREGULAR_PAST + HELD_IRREGULAR_PAST))

EXPLICIT_TREE_CANONICAL_BOUND = 12
SCHEMA = "ocm.l1.linguistic-g2.v4"
V1_FROZEN_SCHEMA = "ocm.l1.linguistic-g2.v1"
V2_FROZEN_SCHEMA = "ocm.l1.linguistic-g2.v2"
V3_FROZEN_SCHEMA = "ocm.l1.linguistic-g2.v3"
FROZEN_TERMINAL = "COMPOSITIONAL_LANGUAGE_LEARNING_ONLY"

BOOTSTRAP_REALIZER_TEMPLATES = (
    "en:transitive",
    "en:passive",
    "en:negation-transitive",
    "en:yesno-transitive",
    "en:intransitive",
)


def _scope() -> Scope:
    return Scope.of(SCOPE_ID)


def _w(*evidence: str) -> WarrantProfile:
    return WarrantProfile.of(set(evidence))


def all_surfaces() -> set[str]:
    nouns = TRAIN_ANIMATE + TRAIN_ARTIFACT + HELD_ANIMATE + HELD_ARTIFACT
    extras = ADJ + (AUX_DID, AUX_DO, AUX_MAY)
    forms = tuple(f for _, f in REGULAR_PAST + HELD_REGULAR_PAST + IRREGULAR_PAST + HELD_IRREGULAR_PAST)
    plurals = tuple(n + "s" for n in nouns)
    pres3 = tuple(v + "s" for v in TRAIN_VERB + HELD_VERB)
    return set(nouns + ALL_VERBS + extras + forms + plurals + pres3)


def gold_past(agent: str, verb: str, patient: str) -> MeaningGraph:
    return MeaningGraph(
        (
            MNode("x1", "entity", agent),
            MNode("e", "event", verb),
            MNode("x2", "entity", patient),
        ),
        (
            MEdge("ROLE:agent", ("e",), ("x1",)),
            MEdge("ROLE:patient", ("e",), ("x2",)),
            MEdge("TENSE", ("e",), ("e",), "past"),
        ),
        root="e",
    )


def gold_present(agent: str, verb: str, patient: str, *, number: str) -> MeaningGraph:
    return MeaningGraph(
        (
            MNode("x1", "entity", agent, (("number", number), ("sort", "animate"))),
            MNode("e", "event", verb),
            MNode("x2", "entity", patient, (("sort", "inanimate"),)),
        ),
        (
            MEdge("ROLE:agent", ("e",), ("x1",)),
            MEdge("ROLE:patient", ("e",), ("x2",)),
            MEdge("TENSE", ("e",), ("e",), "present"),
        ),
        root="e",
    )


def gold_question(agent: str, verb: str, patient: str) -> MeaningGraph:
    return MeaningGraph(
        (
            MNode("x1", "entity", agent),
            MNode("e", "event", verb),
            MNode("x2", "entity", patient),
            MNode("q", "question_variable", None, underspecified=True),
        ),
        (
            MEdge("ROLE:agent", ("e",), ("x1",)),
            MEdge("ROLE:patient", ("e",), ("x2",)),
            MEdge("ASKS", ("q",), ("e",), "polarity"),
        ),
        root="e",
    )


def gold_modality(agent: str, verb: str, patient: str, *, value: str = "may") -> MeaningGraph:
    return MeaningGraph(
        (
            MNode("x1", "entity", agent),
            MNode("e", "event", verb),
            MNode("x2", "entity", patient),
        ),
        (
            MEdge("ROLE:agent", ("e",), ("x1",)),
            MEdge("ROLE:patient", ("e",), ("x2",)),
            MEdge("MODALITY", ("e",), ("e",), value),
        ),
        root="e",
    )


def _label(r: Reading) -> str:
    return r.sense.concept if r.sense else r.lemma


def past_template(b: Mapping[str, Any]) -> MeaningGraph:
    return gold_past(_label(b["S"]), _label(b["V"]), _label(b["O"]))


def present_template(b: Mapping[str, Any]) -> MeaningGraph:
    n = dict(b["S"].features).get("number", "sg")
    return gold_present(_label(b["S"]), _label(b["V"]), _label(b["O"]), number=n)


def question_template(b: Mapping[str, Any]) -> MeaningGraph:
    return gold_question(_label(b["S"]), _label(b["V"]), _label(b["O"]))


def modality_template(b: Mapping[str, Any]) -> MeaningGraph:
    return gold_modality(_label(b["S"]), _label(b["V"]), _label(b["O"]))


def teach_lexicon() -> Lexicon:
    lex = Lexicon()
    sc = _scope()

    def add_noun(surface: str, sort: str) -> None:
        ev = f"lex:v4:{surface}:{TRAIN_SALT}"
        lex.add(
            Lexeme(
                surface,
                Category.NOUN,
                (Sense(f"l1v4:{surface}", surface, "entity", _w(ev), scope=sc),),
                features=(("sort", sort), ("number", "sg")),
                warrant=_w(ev),
                scope=sc,
            )
        )

    def add_verb(surface: str) -> None:
        ev = f"lex:v4:{surface}:{TRAIN_SALT}"
        lex.add(
            Lexeme(
                surface,
                Category.VERB,
                (Sense(f"l1v4:{surface}", surface, "event", _w(ev), scope=sc),),
                warrant=_w(ev),
                scope=sc,
            )
        )

    def add_adj(surface: str) -> None:
        ev = f"lex:v4:{surface}:{TRAIN_SALT}"
        lex.add(
            Lexeme(
                surface,
                Category.ADJ,
                (Sense(f"l1v4:{surface}", surface, "property", _w(ev), scope=sc),),
                warrant=_w(ev),
                scope=sc,
            )
        )

    for w in TRAIN_ANIMATE + HELD_ANIMATE:
        add_noun(w, "animate")
    for w in TRAIN_ARTIFACT + HELD_ARTIFACT:
        add_noun(w, "inanimate")
    for w in ALL_VERBS:
        add_verb(w)
    for w in ADJ:
        add_adj(w)
    ev = f"lex:v4:{AUX_DO}:{TRAIN_SALT}"
    lex.add(
        Lexeme(
            AUX_DO,
            Category.AUX,
            (Sense(f"l1v4:{AUX_DO}", AUX_DO, "value", _w(ev), scope=sc),),
            warrant=_w(ev),
            scope=sc,
        )
    )
    ev = f"lex:v4:{AUX_MAY}:{TRAIN_SALT}"
    lex.add(
        Lexeme(
            AUX_MAY,
            Category.AUX,
            (Sense(f"l1v4:{AUX_MAY}", AUX_MAY, "value", _w(ev), scope=sc),),
            warrant=_w(ev),
            scope=sc,
        )
    )
    return lex


def past_slots() -> list[tuple[str, Slot]]:
    return [
        ("S", Slot("S", Category.NOUN, features=(("sort", "animate"),))),
        ("V", Slot("V", Category.VERB, features=(("tense", "past"),))),
        ("O", Slot("O", Category.NOUN, features=(("sort", "inanimate"),))),
    ]


def sg_slots() -> list[tuple[str, Slot]]:
    return [
        ("S", Slot("S", Category.NOUN, features=(("sort", "animate"), ("number", "sg")))),
        ("V", Slot("V", Category.VERB, features=(("number", "sg"), ("tense", "present")))),
        ("O", Slot("O", Category.NOUN, features=(("sort", "inanimate"),))),
    ]


def pl_slots() -> list[tuple[str, Slot]]:
    return [
        ("S", Slot("S", Category.NOUN, features=(("sort", "animate"), ("number", "pl")))),
        ("V", Slot("V", Category.VERB, features=(("number", "pl"), ("tense", "present")))),
        ("O", Slot("O", Category.NOUN, features=(("sort", "inanimate"),))),
    ]


def question_slots() -> list[tuple[str, Slot]]:
    return [
        ("DID", Slot("DID", Category.AUX, lemma=AUX_DO)),
        ("S", Slot("S", Category.NOUN, features=(("sort", "animate"),))),
        ("V", Slot("V", Category.VERB, forbids=("tense", "participle"))),
        ("O", Slot("O", Category.NOUN, features=(("sort", "inanimate"),))),
    ]


def modality_slots() -> list[tuple[str, Slot]]:
    return [
        ("S", Slot("S", Category.NOUN, features=(("sort", "animate"),))),
        ("MAY", Slot("MAY", Category.AUX, lemma=AUX_MAY)),
        ("V", Slot("V", Category.VERB, forbids=("tense", "participle"))),
        ("O", Slot("O", Category.NOUN, features=(("sort", "inanimate"),))),
    ]


def sg_utt(agent: str, verb: str, patient: str) -> str:
    return f"{agent} {verb}s {patient}"


def pl_utt(agent: str, verb: str, patient: str) -> str:
    return f"{agent}s {verb} {patient}"


def q_utt(agent: str, verb: str, patient: str) -> str:
    return f"{AUX_DID} {agent} {verb} {patient}"


def mod_utt(agent: str, verb: str, patient: str) -> str:
    return f"{agent} {AUX_MAY} {verb} {patient}"


def evidence_id(kind: str, i: int) -> str:
    return f"lesson:v4:{kind}:{i}:{TRAIN_SALT}"


def pair_evidence(lemma: str, form: str) -> str:
    return f"morph:v4:{lemma}:{form}:{TRAIN_SALT}"


def acquire_family(
    name: str,
    slots: list[tuple[str, Slot]],
    template,
    utterances: Sequence[str],
    golds: Sequence[MeaningGraph],
    query: tuple[str, ...],
    lex: Lexicon,
    *,
    kind: str,
    construction_id: str,
) -> tuple[AQ.UpdateProposal, Construction]:
    fam = AQ.ConstructionFamily(name, AQ.order_hypotheses(slots), template, query_family=query, language=LANG)
    demos = [AQ.Demonstration(u, g, evidence_id(kind, i)) for i, (u, g) in enumerate(zip(utterances, golds))]
    proposal = AQ.acquire(fam, lex, demos)
    if proposal.status is not UpdateStatus.PASS or proposal.kind is not UpdateKind.OBJECT:
        raise RuntimeError(f"{name} acquisition failed: {proposal.status} {proposal.detail}")
    return proposal, AQ.construction_from_proposal(fam, proposal, construction_id)


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


def frozen_result_intact(rel: str, schema: str) -> bool:
    data = json.loads((REPO / "research" / rel / "RESULT.json").read_text())
    return data.get("schema") == schema and data.get("terminal") == FROZEN_TERMINAL


def install_morphology(lex: Lexicon) -> dict[str, Any]:
    past_pairs = [MO.Pair(l, f, pair_evidence(l, f)) for l, f in REGULAR_PAST + IRREGULAR_PAST]
    past_ind = MO.induce(past_pairs, MO.Strategy.HYBRID)
    past_ids = MO.install(lex, past_ind, Category.VERB, (("tense", "past"),), "v4:past")
    noun_pairs = [
        MO.Pair(n, n + "s", pair_evidence(n, n + "s"))
        for n in TRAIN_ANIMATE + TRAIN_ARTIFACT
    ]
    noun_ind = MO.induce(noun_pairs, MO.Strategy.HYBRID)
    noun_ids = MO.install(lex, noun_ind, Category.NOUN, (("number", "pl"),), "v4:pl")
    pres_pairs = [MO.Pair(v, v + "s", pair_evidence(v, v + "s")) for v in TRAIN_VERB]
    pres_ind = MO.induce(pres_pairs, MO.Strategy.HYBRID)
    pres_ids = MO.install(lex, pres_ind, Category.VERB, (("number", "sg"), ("tense", "present")), "v4:pres3")
    pl_ev = f"morph:v4:pres-pl:{TRAIN_SALT}"
    lex.add_rule(
        MorphRule(
            "v4:pres-pl",
            RuleKind.PRODUCTIVE,
            Category.VERB,
            (("number", "pl"), ("tense", "present")),
            lambda l: l,
            lambda s: s,
            _w(pl_ev),
        )
    )
    did_ev = f"morph:v4:did:{TRAIN_SALT}"
    lex.add_rule(
        MorphRule(
            "v4:did",
            RuleKind.EXCEPTION,
            Category.AUX,
            (("tense", "past"),),
            lambda l: AUX_DID,
            lambda s: AUX_DO if s == AUX_DID else None,
            _w(did_ev),
            lemmas=frozenset({AUX_DO}),
        )
    )
    return {
        "past_rule": None if past_ind.rule is None else past_ind.rule.name,
        "past_exceptions": [p.lemma for p in past_ind.exceptions],
        "past_ids": past_ids,
        "noun_rule": None if noun_ind.rule is None else noun_ind.rule.name,
        "pres3_rule": None if pres_ind.rule is None else pres_ind.rule.name,
        "split_recommended": past_ind.split_recommended,
        "warrant_ids": tuple(p.evidence_id for p in past_pairs),
    }


def morph_curve() -> list[dict[str, Any]]:
    held_r = [MO.Pair(l, f, "held") for l, f in HELD_REGULAR_PAST]
    held_i = [MO.Pair(l, f, "held") for l, f in HELD_IRREGULAR_PAST]
    points = []
    for n in (0, 1, 2, 4, 8):
        subset = [MO.Pair(l, f, pair_evidence(l, f)) for l, f in REGULAR_PAST[:n]]
        if n == 0 or not subset:
            rule = None
            acc_r = 0.0
            acc_i = 0.0
            pred_r = []
            pred_i = []
        else:
            ind = MO.induce(subset, MO.Strategy.HYBRID)
            rule = None if ind.rule is None else ind.rule.name
            pred_r = [ind.rule.apply(p.lemma) for p in held_r]
            pred_i = [ind.rule.apply(p.lemma) for p in held_i]
            acc_r = sum(a == p.form for a, p in zip(pred_r, held_r)) / len(held_r)
            acc_i = sum(a == p.form for a, p in zip(pred_i, held_i)) / len(held_i)
        points.append(
            {
                "n_train": n,
                "rule": rule,
                "held_regular_accuracy": acc_r,
                "held_irregular_accuracy": acc_i,
                "held_regular_predicted": pred_r,
                "held_irregular_predicted": pred_i,
            }
        )
    return points


def large_tree(n_extra: int) -> MeaningGraph:
    """Rooted tree: event root, agent, patient, then extra theme dependents.

    Edge direction is head→dependent so `meaning_tree.is_tree` holds. Usual
    MODIFIES(property→entity) plus ROLE(event→entity) would give the entity two
    parents and would not be a tree.
    """
    nodes = [
        MNode("e", "event", "anoint"),
        MNode("x1", "entity", "kudu"),
        MNode("x2", "entity", "censer"),
    ]
    edges = [
        MEdge("ROLE:agent", ("e",), ("x1",)),
        MEdge("ROLE:patient", ("e",), ("x2",)),
        MEdge("TENSE", ("e",), ("e",), "past"),
    ]
    for i in range(n_extra):
        nid = f"t{i}"
        nodes.append(MNode(nid, "entity", f"theme{i}"))
        edges.append(MEdge("ROLE:theme", ("e",), (nid,)))
    return MeaningGraph(tuple(nodes), tuple(edges), root="e")


def cycle_graph(n: int) -> MeaningGraph:
    nodes = tuple(MNode(f"n{i}", "entity", "x") for i in range(n))
    edges = tuple(MEdge("COORDINATES", (f"n{i}",), (f"n{(i + 1) % n}",)) for i in range(n))
    return MeaningGraph(nodes, edges)


def try_exact_canonical(g: MeaningGraph) -> str:
    try:
        return canonical(g)[1]
    except CannotCheck as exc:
        return f"CANNOT_CHECK:{exc}"


def try_any_canonical(g: MeaningGraph) -> str:
    try:
        return canonical_any(g)
    except CannotCheck as exc:
        return f"CANNOT_CHECK:{exc}"


def nn_library_status() -> str:
    for name in ("torch", "transformers", "tensorflow"):
        try:
            __import__(name)
        except ImportError:
            continue
        else:
            return f"PRESENT_{name}"
    return "CANNOT_CHECK_NO_NN_LIBRARY"


def persist(path: Path, payload: Mapping[str, Any]) -> None:
    body = dict(payload)
    body["digest"] = content_hash({k: body[k] for k in sorted(body) if k != "digest"})
    path.write_text(json.dumps(body, sort_keys=True))


def load(path: Path) -> dict:
    payload = json.loads(path.read_text())
    digest = content_hash({k: payload[k] for k in sorted(payload) if k != "digest"})
    if digest != payload["digest"]:
        raise RuntimeError("linguistic skill identity mismatch")
    return payload


def rebuild(family: str, hyp: str, slots: list[tuple[str, Slot]], template, evidence: Sequence[str], cid: str) -> Construction:
    fam = AQ.ConstructionFamily(family, AQ.order_hypotheses(slots), template, query_family=(), language=LANG)
    if hyp not in fam.hypotheses:
        raise RuntimeError(f"unknown hypothesis {hyp} for {family}")
    return Construction(cid, family, fam.hypotheses[hyp], template, _w(*evidence), scope=_scope(), language=LANG)


def ud_rows(path: Path) -> list[UD.Sentence]:
    return list(UD.read_conllu(path))


def main(out: Path) -> dict:
    content = all_surfaces()
    if content & V1_SURFACES:
        raise RuntimeError("v4 salts collided with v1 surfaces")
    if content & V2_CONTENT_SURFACES:
        raise RuntimeError("v4 salts collided with v2 content surfaces")
    if content & V3_CONTENT_SURFACES:
        raise RuntimeError("v4 salts collided with v3 content surfaces")

    lex = teach_lexicon()
    morph_meta = install_morphology(lex)
    curve = morph_curve()

    train_past_utts = (
        f"{TRAIN_ANIMATE[0]} anointed {TRAIN_ARTIFACT[0]}",
        f"{TRAIN_ANIMATE[1]} gilded {TRAIN_ARTIFACT[1]}",
        f"{TRAIN_ANIMATE[0]} welded {TRAIN_ARTIFACT[0]}",
    )
    train_past_gold = (
        gold_past(TRAIN_ANIMATE[0], "anoint", TRAIN_ARTIFACT[0]),
        gold_past(TRAIN_ANIMATE[1], "gild", TRAIN_ARTIFACT[1]),
        gold_past(TRAIN_ANIMATE[0], "weld", TRAIN_ARTIFACT[0]),
    )
    held_past = f"{HELD_ANIMATE[0]} entombed {HELD_ARTIFACT[0]}"
    held_past_gold = gold_past(HELD_ANIMATE[0], "entomb", HELD_ARTIFACT[0])
    past_query = (
        f"{TRAIN_ANIMATE[0]} gilded {TRAIN_ARTIFACT[1]}",
        f"{TRAIN_ANIMATE[1]} anointed {TRAIN_ARTIFACT[0]}",
    )
    past_prop, past_c = acquire_family(
        "past_transitive",
        past_slots(),
        past_template,
        train_past_utts,
        train_past_gold,
        past_query,
        lex,
        kind="past",
        construction_id="l1v4:past-transitive",
    )

    held_past_row = parse(held_past, lex, [past_c])
    train_past_row = parse(train_past_utts[0], lex, [past_c])
    mismatch_past = parse(f"{TRAIN_ARTIFACT[0]} anointed {TRAIN_ANIMATE[0]}", lex, [past_c])

    sg_train = (
        sg_utt(TRAIN_ANIMATE[0], TRAIN_VERB[0], TRAIN_ARTIFACT[0]),
        sg_utt(TRAIN_ANIMATE[1], TRAIN_VERB[1], TRAIN_ARTIFACT[1]),
    )
    sg_gold = (
        gold_present(TRAIN_ANIMATE[0], TRAIN_VERB[0], TRAIN_ARTIFACT[0], number="sg"),
        gold_present(TRAIN_ANIMATE[1], TRAIN_VERB[1], TRAIN_ARTIFACT[1], number="sg"),
    )
    sg_query = (sg_utt(TRAIN_ANIMATE[0], TRAIN_VERB[1], TRAIN_ARTIFACT[1]),)
    sg_prop, sg_c = acquire_family(
        "present_sg",
        sg_slots(),
        present_template,
        sg_train,
        sg_gold,
        sg_query,
        lex,
        kind="sg",
        construction_id="l1v4:present-sg",
    )
    pl_train = (
        pl_utt(TRAIN_ANIMATE[0], TRAIN_VERB[0], TRAIN_ARTIFACT[0]),
        pl_utt(TRAIN_ANIMATE[1], TRAIN_VERB[1], TRAIN_ARTIFACT[1]),
    )
    pl_gold = (
        gold_present(TRAIN_ANIMATE[0], TRAIN_VERB[0], TRAIN_ARTIFACT[0], number="pl"),
        gold_present(TRAIN_ANIMATE[1], TRAIN_VERB[1], TRAIN_ARTIFACT[1], number="pl"),
    )
    pl_query = (pl_utt(TRAIN_ANIMATE[0], TRAIN_VERB[1], TRAIN_ARTIFACT[1]),)
    pl_prop, pl_c = acquire_family(
        "present_pl",
        pl_slots(),
        present_template,
        pl_train,
        pl_gold,
        pl_query,
        lex,
        kind="pl",
        construction_id="l1v4:present-pl",
    )
    agree = [sg_c, pl_c]
    held_sg = sg_utt(HELD_ANIMATE[0], HELD_VERB[0], HELD_ARTIFACT[0])
    held_pl = pl_utt(HELD_ANIMATE[0], HELD_VERB[0], HELD_ARTIFACT[0])
    mismatch_sg_pl = f"{HELD_ANIMATE[0]} {HELD_VERB[0]} {HELD_ARTIFACT[0]}"
    mismatch_pl_sg = f"{HELD_ANIMATE[0]}s {HELD_VERB[0]}s {HELD_ARTIFACT[0]}"
    held_sg_row = parse(held_sg, lex, agree)
    held_pl_row = parse(held_pl, lex, agree)
    mismatch_a = parse(mismatch_sg_pl, lex, agree)
    mismatch_b = parse(mismatch_pl_sg, lex, agree)

    q_train = (q_utt(TRAIN_ANIMATE[0], TRAIN_VERB[0], TRAIN_ARTIFACT[0]),)
    q_gold = (gold_question(TRAIN_ANIMATE[0], TRAIN_VERB[0], TRAIN_ARTIFACT[0]),)
    q_query = (q_utt(TRAIN_ANIMATE[1], TRAIN_VERB[1], TRAIN_ARTIFACT[1]),)
    q_prop, q_c = acquire_family(
        "yesno",
        question_slots(),
        question_template,
        q_train,
        q_gold,
        q_query,
        lex,
        kind="yesno",
        construction_id="l1v4:yesno",
    )
    held_q = q_utt(HELD_ANIMATE[0], HELD_VERB[0], HELD_ARTIFACT[0])
    held_q_row = parse(held_q, lex, [q_c])
    held_q_ok = held_q_row["invoked"] and isomorphic(interpret(held_q, lex, [q_c]).meaning, gold_question(HELD_ANIMATE[0], HELD_VERB[0], HELD_ARTIFACT[0]))

    m_train = (mod_utt(TRAIN_ANIMATE[0], TRAIN_VERB[0], TRAIN_ARTIFACT[0]),)
    m_gold = (gold_modality(TRAIN_ANIMATE[0], TRAIN_VERB[0], TRAIN_ARTIFACT[0]),)
    m_query = (mod_utt(TRAIN_ANIMATE[1], TRAIN_VERB[1], TRAIN_ARTIFACT[1]),)
    m_prop, m_c = acquire_family(
        "modality",
        modality_slots(),
        modality_template,
        m_train,
        m_gold,
        m_query,
        lex,
        kind="modality",
        construction_id="l1v4:modality",
    )
    held_m = mod_utt(HELD_ANIMATE[0], HELD_VERB[0], HELD_ARTIFACT[0])
    held_m_row = parse(held_m, lex, [m_c])
    held_m_ok = held_m_row["invoked"] and isomorphic(
        interpret(held_m, lex, [m_c]).meaning, gold_modality(HELD_ANIMATE[0], HELD_VERB[0], HELD_ARTIFACT[0])
    )

    # --- planted UD alignment (teacher-annotated CoNLL-U, not a parser) ---
    train_ud = ud_rows(HERE / "train.conllu")
    held_ud = ud_rows(HERE / "held.conllu")
    if any(s.root() is None for s in train_ud + held_ud):
        raise RuntimeError("planted treebank missing roots")
    simple_train = [s for s in train_ud if UD.is_simple_clause(s)]
    simple_held = [s for s in held_ud if UD.is_simple_clause(s)]
    complex_held = [s for s in held_ud if not UD.is_simple_clause(s)]
    ud_aligned = []
    for s in simple_held:
        gold = UD.gold_meaning(s)
        u = UD.utterance_of(s)
        row = parse(u, lex, [past_c])
        interp = interpret(u, lex, [past_c])
        match = interp.verdict is Verdict.INTERPRETED and isomorphic(interp.meaning, gold)
        ud_aligned.append(
            {
                "sent_id": s.sent_id,
                "utterance": u,
                "n_tokens": len(s.tokens),
                "simple": True,
                "gold_nodes": len(gold.nodes),
                "invoked": row["invoked"],
                "exact_gold_match": match,
                "roles": row["roles"],
                "ud_nsubj": next(t.lemma for t in s.tokens if t.deprel == "nsubj"),
                "ud_obj": next((t.lemma for t in s.tokens if t.deprel == "obj"), None),
            }
        )
    amod_s = next(s for s in simple_held if any(t.deprel == "amod" for t in s.tokens))
    amod_gold = UD.gold_meaning(amod_s)
    amod_interp = interpret(UD.utterance_of(amod_s), lex, [past_c])
    complex_s = complex_held[0]
    ud_three_token_ok = all(r["exact_gold_match"] for r in ud_aligned if r["n_tokens"] == 3)
    ud_amod_incomplete = amod_interp.verdict is not Verdict.INTERPRETED and len(amod_gold.nodes) > 3
    ud_complex_unmapped = not UD.is_simple_clause(complex_s)
    role_aligned = all(
        r["exact_gold_match"] and r["roles"].get("agent") == r["ud_nsubj"] and r["roles"].get("patient") == r["ud_obj"]
        for r in ud_aligned
        if r["n_tokens"] == 3
    )

    # --- realization: freeze bootstrap, learn lemma→form, reverse-read ---
    seed_ids = tuple(c.construction_id for c in seed_constructions())
    realized_form = RZ._form(lex, "entomb", Category.VERB, {"tense": "past"}, ())
    realized_utt = f"{HELD_ANIMATE[0]} {realized_form} {HELD_ARTIFACT[0]}"
    reverse = interpret(realized_utt, lex, [past_c])
    reverse_ok = reverse.verdict is Verdict.INTERPRETED and isomorphic(reverse.meaning, held_past_gold)
    irregular_form = RZ._form(lex, "slay", Category.VERB, {"tense": "past"}, ())
    overreg = RZ._form(lex, "bring", Category.VERB, {"tense": "past"}, ())
    mutant_lex = teach_lexicon()
    mutant_meta = install_morphology(mutant_lex)
    MO.mutant_rule_overrides_exception(mutant_lex, "v4:past")
    mutant_slay = RZ._form(mutant_lex, "slay", Category.VERB, {"tense": "past"}, ())

    # --- canonical bounds ---
    small = gold_past("caracal", "entomb", "phylactery")
    tree9 = large_tree(6)  # 3 + 6 = 9
    tree11 = large_tree(8)  # 3 + 8 = 11
    if len(tree9.nodes) > EXPLICIT_TREE_CANONICAL_BOUND or len(tree11.nodes) > EXPLICIT_TREE_CANONICAL_BOUND:
        raise RuntimeError("study tree exceeds registered finite bound")
    cycle8 = cycle_graph(8)
    small_digest = try_exact_canonical(small)
    tree9_exact = try_exact_canonical(tree9)
    tree9_any = try_any_canonical(tree9)
    tree11_any = try_any_canonical(tree11)
    cycle8_any = try_any_canonical(cycle8)
    tree_ok = (
        is_tree(tree9)
        and is_tree(tree11)
        and (not is_tree(cycle8))
        and small_digest.startswith("CANNOT_CHECK") is False
        and tree9_exact.startswith("CANNOT_CHECK")
        and tree9_any.startswith("tree:")
        and tree11_any.startswith("tree:")
        and tree9_any != tree11_any
        and cycle8_any.startswith("CANNOT_CHECK")
        and len(tree9.nodes) > MAX_EXACT_CANONICAL
        and len(tree11.nodes) <= EXPLICIT_TREE_CANONICAL_BOUND
    )

    # --- persist / restart / revocation ---
    out.parent.mkdir(parents=True, exist_ok=True)
    past_ev = tuple(evidence_id("past", i) for i in range(len(train_past_utts)))
    skill_path = out.parent / "grammar.json"
    persist(
        skill_path,
        {
            "schema": "ocm.l1.linguistic-g2.v4.skill",
            "salt": TRAIN_SALT,
            "past_hypothesis": past_prop.payload["hypothesis"],
            "sg_hypothesis": sg_prop.payload["hypothesis"],
            "pl_hypothesis": pl_prop.payload["hypothesis"],
            "yesno_hypothesis": q_prop.payload["hypothesis"],
            "modality_hypothesis": m_prop.payload["hypothesis"],
            "past_evidence": list(past_ev),
            "morph_rule": morph_meta["past_rule"],
        },
    )
    loaded = load(skill_path)
    restarted = rebuild(
        "past_transitive", loaded["past_hypothesis"], past_slots(), past_template, loaded["past_evidence"], "l1v4:past-transitive"
    )
    restart_row = parse(held_past, lex, [restarted])
    reset_row = parse(held_past, lex, [])
    revoked = set(past_prop.warrant.evidence)
    revoked_row = parse(held_past, lex, [past_c], revoked)
    unrelated_q = parse(held_q, lex, [q_c], revoked)
    alt_ev = f"lesson:v4:past:alt:{TRAIN_SALT}"
    alt_w = WarrantProfile.of(set(past_prop.warrant.evidence), {alt_ev})
    alt_c = Construction(past_c.construction_id, past_c.family, past_c.pattern, past_c.template, alt_w, scope=past_c.scope, language=past_c.language)
    restored = parse(held_past, lex, [alt_c], revoked)

    train_pool = set(train_past_utts) | set(sg_train) | set(pl_train) | set(q_train) | set(m_train)
    _counts, identities = grammar_induction_parent(train_pool)
    parent_has_fresh = tuple(tokenize(held_past)) in identities or tuple(tokenize(held_sg)) in identities

    past_ok = held_past_row["invoked"] and isomorphic(interpret(held_past, lex, [past_c]).meaning, held_past_gold)
    agree_ok = (
        held_sg_row["invoked"]
        and held_pl_row["invoked"]
        and (not mismatch_a["invoked"])
        and (not mismatch_b["invoked"])
        and isomorphic(interpret(held_sg, lex, agree).meaning, gold_present(HELD_ANIMATE[0], HELD_VERB[0], HELD_ARTIFACT[0], number="sg"))
        and isomorphic(interpret(held_pl, lex, agree).meaning, gold_present(HELD_ANIMATE[0], HELD_VERB[0], HELD_ARTIFACT[0], number="pl"))
    )
    morph_ok = (
        morph_meta["past_rule"] == "-∅+ed"
        and "slay" in morph_meta["past_exceptions"]
        and realized_form == "entombed"
        and irregular_form == "slew"
        and overreg == "bringed"
        and mutant_slay == "slayed"
    )
    curve_ok = (
        curve[0]["held_regular_accuracy"] == 0.0
        and curve[-1]["held_regular_accuracy"] == 1.0
        and all(curve[i]["held_regular_accuracy"] <= curve[i + 1]["held_regular_accuracy"] for i in range(len(curve) - 1))
        and curve[-1]["held_irregular_accuracy"] == 0.0
    )
    restart_ok = restart_row["meaning"] == held_past_row["meaning"]
    reset_fails = not reset_row["invoked"]
    revoke_kills = not revoked_row["invoked"]
    unrelated_ok = unrelated_q["invoked"]
    alt_ok = restored["invoked"]
    type_ok = train_past_row["invoked"] and not mismatch_past["invoked"]
    node_rows = (held_past_row, held_sg_row, held_q_row, held_m_row, train_past_row)
    nodes_ok = all(row["n_nodes"] <= MAX_EXACT_CANONICAL for row in node_rows if row["n_nodes"])
    max_nodes = max(row["n_nodes"] for row in node_rows)
    v1_ok = frozen_result_intact("l1-linguistic-g2-v1", V1_FROZEN_SCHEMA)
    v2_ok = frozen_result_intact("l1-linguistic-g2-v2", V2_FROZEN_SCHEMA)
    v3_ok = frozen_result_intact("l1-linguistic-g2-v3", V3_FROZEN_SCHEMA)
    induced = past_prop.payload["hypothesis"] == "SVO"
    g2_ok = past_ok and restart_ok and revoke_kills and reset_fails and not parent_has_fresh
    nn_status = nn_library_status()
    ud_ok = ud_three_token_ok and role_aligned and ud_amod_incomplete and ud_complex_unmapped
    realize_ok = reverse_ok and morph_ok
    bootstrap_frozen = set(BOOTSTRAP_REALIZER_TEMPLATES) <= set(seed_ids)

    if g2_ok and morph_ok and agree_ok and curve_ok and tree_ok and ud_ok and realize_ok and held_q_ok and held_m_ok and v1_ok and v2_ok and v3_ok:
        terminal = "COMPOSITIONAL_LANGUAGE_LEARNING_ONLY"
    elif g2_ok:
        terminal = "PARENT_SUFFICIENT"
    else:
        terminal = "NO_LANGUAGE_META_LEARNING"

    earned = "EARNED_AT_SCOPE"
    checklist = {
        "acquire_corpus_scale_lexicon": "CANNOT_CHECK_MINIATURE_MICROWORLD",
        "retain_polysemy": "CITED_V2_EARNED_AT_SCOPE",
        "induce_constructions": earned if induced else "OPEN",
        "recursive_composition": "CITED_V2_EARNED_AT_SCOPE",
        "meaning_graphs_beyond_bound": "EARNED_AT_TREE_BOUND_12" if tree_ok else "CANNOT_CHECK_NO_LARGER_BOUND",
        "exact_canonicalization": earned if nodes_ok else "OPEN",
        "quantifier_scope": "CITED_V2_EARNED_AT_SCOPE",
        "negation": "CITED_V2_EARNED_AT_SCOPE",
        "typed_entities": "CITED_V2_EARNED_AT_SCOPE",
        "ud_alignment": "EARNED_AT_PLANTED_GOLDTREE_SCOPE" if ud_ok else "OPEN",
        "ud_parser": "CANNOT_CHECK_NO_UD_PARSER",
        "held_out_lexical_fillers": earned if past_ok and agree_ok and not parent_has_fresh else "OPEN",
        "held_out_construction_combinations": "CANNOT_CHECK_NOT_RUN_HERE",
        "held_out_construction_families": "CITED_V3_NO_CROSS_FAMILY_TRANSFER",
        "artificial_non_english": "CITED_V3_EARNED_AT_SCOPE",
        "acquisition_curves": earned if curve_ok else "OPEN",
        "correction_revocation": earned if revoke_kills and unrelated_ok and alt_ok else "OPEN",
        "reset_control": earned if reset_fails else "OPEN",
        "grammar_induction_parent": earned if not parent_has_fresh else "OPEN",
        "persistent_grammar_parent": earned if restart_ok else "OPEN",
        "continual_adaptation_parent": "CANNOT_CHECK_NOT_RUN",
        "open_weight_lm_reference": "CANNOT_CHECK_NO_MODEL_WEIGHTS",
        "g2_causal_reuse_linguistic": earned if g2_ok else "OPEN",
        "learn_morphology_agreement": earned if morph_ok and agree_ok else "OPEN",
        "freeze_realization_bootstrap": earned if bootstrap_frozen else "OPEN",
        "learn_lexical_realization": earned if realize_ok else "OPEN",
        "learn_questions": earned if held_q_ok else "OPEN",
        "learn_modality": earned if held_m_ok else "OPEN",
        "learn_questions_negation_modality": (
            "EARNED_QUESTIONS_MODALITY_CITED_V2_NEGATION" if held_q_ok and held_m_ok else "OPEN"
        ),
        "neural_realizer": nn_status,
        "recursive_composition_lot_l2": "CANNOT_CHECK_L2_LOCKED",
        "multi_session_l3": "CANNOT_CHECK_L3_LOCKED",
        "ud_corpus": "CANNOT_CHECK_MINIATURE_MICROWORLD",
    }
    result = {
        "schema": SCHEMA,
        "terminal": terminal,
        "fresh_invoked": past_ok and agree_ok,
        "past_hypothesis": past_prop.payload["hypothesis"],
        "sg_hypothesis": sg_prop.payload["hypothesis"],
        "pl_hypothesis": pl_prop.payload["hypothesis"],
        "yesno_hypothesis": q_prop.payload["hypothesis"],
        "modality_hypothesis": m_prop.payload["hypothesis"],
        "morph_rule": morph_meta["past_rule"],
        "morph_exceptions": morph_meta["past_exceptions"],
        "held_past_ok": past_ok,
        "agreement_ok": agree_ok,
        "mismatch_rejected": (not mismatch_a["invoked"]) and (not mismatch_b["invoked"]),
        "question_ok": held_q_ok,
        "modality_ok": held_m_ok,
        "ud_three_token_gold_match": ud_three_token_ok,
        "ud_role_aligned": role_aligned,
        "ud_amod_incomplete_mapping": ud_amod_incomplete,
        "ud_complex_unmapped": ud_complex_unmapped,
        "ud_parser_used": False,
        "ud_channel": "DEMONSTRATION (planted CoNLL-U teacher labels; not a UD parser)",
        "realized_held_past_form": realized_form,
        "reverse_read_ok": reverse_ok,
        "irregular_form": irregular_form,
        "held_irregular_overregularised": overreg,
        "mutant_exception_overridden": mutant_slay,
        "acquisition_curve": curve,
        "curve_monotonic_to_one": curve_ok,
        "max_nodes": max_nodes,
        "canonical_bound": MAX_EXACT_CANONICAL,
        "explicit_tree_canonical_bound": EXPLICIT_TREE_CANONICAL_BOUND,
        "tree9_nodes": len(tree9.nodes),
        "tree11_nodes": len(tree11.nodes),
        "tree9_exact": tree9_exact.startswith("CANNOT_CHECK"),
        "tree9_tree_digest_prefix": tree9_any[:5],
        "tree11_tree_digest_prefix": tree11_any[:5],
        "non_tree_over_bound": cycle8_any.startswith("CANNOT_CHECK"),
        "bootstrap_realizer_templates": list(BOOTSTRAP_REALIZER_TEMPLATES),
        "seed_construction_ids": list(seed_ids),
        "restart_equivalent": restart_ok,
        "revocation_removes_effect": revoke_kills,
        "unrelated_survives_revocation": unrelated_ok,
        "alternate_support_restores": alt_ok,
        "reset_has_no_construction": reset_fails,
        "grammar_induction_parent_has_fresh_identity": parent_has_fresh,
        "type_mismatch_rejected": not mismatch_past["invoked"],
        "l2_started": False,
        "l3_started": False,
        "v1_result_intact": v1_ok,
        "v2_result_intact": v2_ok,
        "v3_result_intact": v3_ok,
        "loaded_hypotheses": {
            "past": loaded["past_hypothesis"],
            "sg": loaded["sg_hypothesis"],
            "pl": loaded["pl_hypothesis"],
        },
        "salts": {"train": TRAIN_SALT, "held": HELD_SALT, "scope": SCOPE_ID},
        "checklist": checklist,
        "held_rows": {
            "past": held_past_row,
            "present_sg": held_sg_row,
            "present_pl": held_pl_row,
            "agreement_mismatch": mismatch_a,
            "yesno": held_q_row,
            "modality": held_m_row,
        },
        "ud_held_rows": ud_aligned,
        "ud_complex_sent_id": complex_s.sent_id,
        "claim_ceiling": (
            "Morphology/agreement, planted UD gold-tree alignment, miniature acquisition "
            "curves, tree-canonical bound 12, and lexical realization in an exact microworld. "
            "Not corpus-scale N1. No UD parser. No neural realizer. L2/L3 locked. "
            "v2 negation/quantifier/polysemy and v3 SOV/families are cited, not reticked."
        ),
        "nn_library": nn_status,
        "unused_mutant_meta_ids": mutant_meta["past_ids"],
        "simple_train_count": len(simple_train),
        "bootstrap_frozen": bootstrap_frozen,
    }
    out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(
        json.dumps(
            {
                "terminal": terminal,
                "morph_rule": morph_meta["past_rule"],
                "past": past_ok,
                "agreement": agree_ok,
                "ud": ud_ok,
                "curve": curve_ok,
                "tree": tree_ok,
                "question": held_q_ok,
                "modality": held_m_ok,
                "realize": realize_ok,
            }
        )
    )
    return result


if __name__ == "__main__":
    target = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parent / "RESULT.json"
    main(target)
