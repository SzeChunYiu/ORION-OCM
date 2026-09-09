"""L0 language-bootstrap audit (#165 / GitHub #54).

Item-level inventory of language-specific prior, constitutional vs convenience
classification, reduced-bootstrap ablation, and a cheap SOV/artificial hostile.

This is an accounting gate. It does not claim N1 learned understanding. L1 stays
locked until L0 closes.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
N1 = ROOT / "research" / "ocm-n1"
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(N1))

SOURCE_FILES = (
    "src/ocm/language/bootstrap.py",
    "src/ocm/language/lexicon.py",
    "src/ocm/language/constructions.py",
    "src/ocm/language/meaning.py",
    "src/ocm/language/realize.py",
    "src/ocm/language/interpret.py",
    "src/ocm/language/chart.py",
    "src/ocm/language/session.py",
    "src/ocm/language/acquisition.py",
    "src/ocm/language/microworld.py",
    "src/ocm/language/meaning_tree.py",
    "src/ocm/language/field_bridge.py",
    "src/ocm/dialogue/gate.py",
    "src/ocm/dialogue/planner.py",
    "src/ocm/dialogue/reference.py",
    "src/ocm/dialogue/clarify.py",
    "src/ocm/dialogue/surface_text.py",
    "src/ocm/dialogue/session.py",
    "src/ocm/dialogue/microworld.py",
)

# Issue #165 L0 boxes. Values are filled after inventory/ablation.
L0_BOXES = (
    "enumerate every seed lexeme",
    "enumerate morphology priors",
    "enumerate construction priors",
    "enumerate word-order assumptions",
    "enumerate semantic-role mappings",
    "enumerate parser procedures",
    "enumerate realization templates",
    "enumerate dialogue-act rules",
    "enumerate pronoun/reference rules",
    "enumerate clarification rules",
    "enumerate explanation/discourse schemas",
    "enumerate style/register rules",
    "enumerate authored examples/lessons",
    "classify constitutionally necessary vs convenience",
    "count retained language-specific prior information",
    "run reduced-bootstrap ablation",
    "run conflicting artificial/SOV hostile",
)


def git_blob_sha(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def item(
    *,
    item_id: str,
    klass: str,
    name: str,
    classification: str,
    source: str,
    detail: str,
    retained_in_minimal_substrate: bool,
    language_specific: bool,
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    row = {
        "id": item_id,
        "class": klass,
        "name": name,
        "classification": classification,
        "language_specific": language_specific,
        "retained_in_minimal_substrate": retained_in_minimal_substrate,
        "source": source,
        "detail": detail,
    }
    if extra:
        row.update(extra)
    return row


def _slot_desc(slot) -> dict[str, Any]:
    return {
        "name": slot.name,
        "category": slot.category.value,
        "features": list(slot.features),
        "lemma": slot.lemma,
        "optional": slot.optional,
        "requires": list(slot.requires),
        "forbids": list(slot.forbids),
        "phrase": slot.phrase,
    }


def constitutional_items() -> list[dict[str, Any]]:
    """Epistemic machinery that may remain at time zero. Not English competence."""
    rows = [
        ("C1_identity", "object identity and typed relations", "KSO atom/edge identity; not a language.", "src/ocm/kso"),
        ("C2_evidence", "evidence identity and provenance", "Every linguistic object carries evidence ids.", "src/ocm/kso"),
        ("C3_warrant_scope_authority", "warrant / uncertainty / scope / authority", "Three-valued liveness; speaker vs world_truth axes.", "src/ocm/kso"),
        ("C4_revocation", "dependency and exact revocation", "Revoking support reopens exactly dependent linguistic objects.", "src/ocm/kso"),
        ("C5_unknown_cannot_check", "UNKNOWN and CANNOT_CHECK", "Failure knowledge stays scoped; no silent fallback.", "src/ocm/language/interpret.py"),
        ("C6_ambiguity_retention", "ambiguity-preserving select", "AMBIGUOUS is retained; ranking never collapses the lattice.", "src/ocm/language/interpret.py"),
        ("C7_said_authority", "said-records as OBSERVATION", "Speaker-axis rank 1, conversation scope; not world_truth rank 0.", "src/ocm/language/session.py"),
        ("C8_commitment_gate", "external reverse-read commitment gate G1-G6", "Surface must reverse-read to the planned meaning; renderer has no store handle.", "src/ocm/dialogue/gate.py"),
        ("C9_meaning_graph_schema", "MeaningGraph / MNode / MEdge schemas without English instances", "Replaceable registry vocabulary; empty of lexemes.", "src/ocm/language/meaning.py"),
        ("C10_lexeme_construction_schemas", "Lexeme / Sense / MorphRule / Construction / Slot schemas without instances", "Object types for acquisition; no English fill.", "src/ocm/language/lexicon.py"),
        ("C11_version_space", "generic finite version-space acquisition", "Mitchell-style VS; hypothesis class supplied per family as teacher info.", "src/ocm/language/acquisition.py"),
        ("C12_generic_parser", "generic chart/match parser once grammar is supplied", "Earley packed forest + construction matcher; grammar is data.", "src/ocm/language/chart.py"),
        ("C13_exception_override_law", "more-specific live exception wins", "Inherited L0 morphology override; not the English -ed rule itself.", "src/ocm/language/lexicon.py"),
        ("C14_information_value", "information-value clarification objective", "Ask iff collapsing ambiguity changes a registered query cell.", "src/ocm/dialogue/clarify.py"),
        ("C15_canonical_bound", "exact canonical checking with named bound", "MAX_EXACT_CANONICAL=7; tree encoding above bound; else CANNOT_CHECK.", "src/ocm/language/meaning.py"),
        ("C16_field_bridge", "meaning-field binding without new factual authority", "Persistent identity for bounded meanings; admission still through runtime.", "src/ocm/language/field_bridge.py"),
    ]
    return [
        item(
            item_id=i,
            klass="constitutional_mechanism",
            name=n,
            classification="constitutionally_necessary",
            source=s,
            detail=d,
            retained_in_minimal_substrate=True,
            language_specific=False,
        )
        for i, n, d, s in rows
    ]


def charged_general_priors() -> list[dict[str, Any]]:
    """Language-general registries/adapters retained in the registered substrate and charged."""
    from ocm.language.chart import GAP_CATEGORIES
    from ocm.language.lexicon import Category
    from ocm.language.meaning import KNOWLEDGE_RELATIONS, MAX_EXACT_CANONICAL, NODE_TYPES, RELATION_TYPES, ROLES

    rows = [
        item(
            item_id="G1_category_enum",
            klass="parser_procedure",
            name="Category tag inventory",
            classification="convenience",
            source="src/ocm/language/lexicon.py",
            detail="Finite POS-like tags (N/V/A/D/PRO/P/AUX/CONJ/ADV/WH/NEG/PUNCT). Source calls this registry data, not constitution. English-biased but empty of lexemes. Charged if retained.",
            retained_in_minimal_substrate=True,
            language_specific=False,
            extra={"values": [c.name for c in Category], "count": len(Category)},
        ),
        item(
            item_id="G2_role_inventory",
            klass="semantic_role_mapping",
            name="MeaningGraph ROLE and relation registry",
            classification="convenience",
            source="src/ocm/language/meaning.py",
            detail="PropBank/AMR-style role names plus discourse relations. Replaceable registry; charged if a curriculum family uses them as the semantic target schema.",
            retained_in_minimal_substrate=True,
            language_specific=False,
            extra={"roles": list(ROLES), "node_types": list(NODE_TYPES), "relation_count": len(RELATION_TYPES), "knowledge_relations": list(KNOWLEDGE_RELATIONS)},
        ),
        item(
            item_id="G3_tokenizer",
            klass="parser_procedure",
            name="whitespace/lowercase/punctuation tokenizer",
            classification="convenience",
            source="src/ocm/language/interpret.py",
            detail="Declared corpus adapter: split on whitespace, lower, strip .,!?;:. Not learned competence.",
            retained_in_minimal_substrate=True,
            language_specific=False,
        ),
        item(
            item_id="G4_gap_categories",
            klass="parser_procedure",
            name="out-of-lexicon gap admitted only as N",
            classification="convenience",
            source="src/ocm/language/chart.py",
            detail=f"GAP_CATEGORIES={GAP_CATEGORIES!r}. Unknown tokens become underspecified entity placeholders, never a self-grant.",
            retained_in_minimal_substrate=True,
            language_specific=False,
            extra={"gap_categories": list(GAP_CATEGORIES)},
        ),
        item(
            item_id="G5_canonical_max",
            klass="parser_procedure",
            name="MAX_EXACT_CANONICAL bound",
            classification="constitutionally_necessary",
            source="src/ocm/language/meaning.py",
            detail=f"Exact isomorphism check enumerates vertex orderings only for |V| <= {MAX_EXACT_CANONICAL}; larger non-trees are CANNOT_CHECK.",
            retained_in_minimal_substrate=True,
            language_specific=False,
            extra={"max_exact_canonical": MAX_EXACT_CANONICAL},
        ),
        item(
            item_id="G6_order_hypothesis_generator",
            klass="construction_prior",
            name="finite permutation hypothesis generator",
            classification="convenience",
            source="src/ocm/language/acquisition.py",
            detail="order_hypotheses enumerates all slot orders. Language-general search, but the role/slot inventory of a family is teacher information when that family is taught.",
            retained_in_minimal_substrate=True,
            language_specific=False,
        ),
        item(
            item_id="G7_construction_default_language",
            klass="word_order_assumption",
            name="Construction.language default 'en'",
            classification="convenience",
            source="src/ocm/language/constructions.py",
            detail="New Construction objects default language='en'. Scope-check refuses silent English-to-SOV relabel. Default must not be treated as learned English.",
            retained_in_minimal_substrate=False,
            language_specific=True,
        ),
    ]
    return rows


def seed_lexemes() -> list[dict[str, Any]]:
    from ocm.language.bootstrap import acquisition_lexicon, microworld_lexicon

    items = []
    for origin, lx in (("microworld", microworld_lexicon()), ("acquisition_fixture", acquisition_lexicon())):
        for key, lex in sorted(lx.lexemes.items()):
            senses = [
                {"sense_id": s.sense_id, "concept": s.concept, "node_type": s.node_type}
                for s in lex.senses
            ]
            items.append(
                item(
                    item_id=f"L:{origin}:{key}",
                    klass="seed_lexeme",
                    name=lex.lemma,
                    classification="convenience",
                    source="src/ocm/language/bootstrap.py",
                    detail=f"{origin} seed lexeme category={lex.category.name}",
                    retained_in_minimal_substrate=False,
                    language_specific=True,
                    extra={"origin": origin, "category": lex.category.name, "senses": senses, "features": list(lex.features)},
                )
            )
    return items


def morphology_priors() -> list[dict[str, Any]]:
    from ocm.language.bootstrap import acquisition_lexicon, microworld_lexicon

    items = []
    for origin, lx in (("microworld", microworld_lexicon()), ("acquisition_fixture", acquisition_lexicon())):
        for rule in lx.rules:
            items.append(
                item(
                    item_id=f"M:{origin}:{rule.rule_id}",
                    klass="morphology_prior",
                    name=rule.rule_id,
                    classification="convenience",
                    source="src/ocm/language/bootstrap.py",
                    detail=f"{origin} {rule.kind.value} {rule.category.name} features={list(rule.features)} lemmas={sorted(rule.lemmas)}",
                    retained_in_minimal_substrate=False,
                    language_specific=True,
                    extra={
                        "origin": origin,
                        "kind": rule.kind.value,
                        "category": rule.category.name,
                        "features": list(rule.features),
                        "lemmas": sorted(rule.lemmas),
                    },
                )
            )
    return items


def construction_priors() -> list[dict[str, Any]]:
    from ocm.language.constructions import seed_constructions

    items = []
    for c in seed_constructions():
        order = [s.phrase or s.lemma or s.category.value for s in c.pattern]
        items.append(
            item(
                item_id=f"K:{c.construction_id}",
                klass="construction_prior",
                name=c.construction_id,
                classification="convenience",
                source="src/ocm/language/constructions.py",
                detail=f"family={c.family} language={c.language} order={' '.join(order)} invertible={c.invertible} produces={c.produces}",
                retained_in_minimal_substrate=False,
                language_specific=True,
                extra={
                    "family": c.family,
                    "language": c.language,
                    "pattern": [_slot_desc(s) for s in c.pattern],
                    "surface_order": order,
                    "invertible": c.invertible,
                    "produces": c.produces,
                    "head_slot": c.head_slot,
                },
            )
        )
    return items


def word_order_assumptions() -> list[dict[str, Any]]:
    from ocm.language.constructions import seed_constructions

    mapping = {
        "en:np": "English NP = (DET) (ADJ) NOUN",
        "en:transitive": "English SVO = NP V[+tense] NP",
        "en:intransitive": "English SV = NP V[+tense]",
        "en:passive": "English passive = NP be V[pp] by NP (patient-first)",
        "en:negation-transitive": "English do-support negation = NP do not V[-tense] NP",
        "en:yesno-transitive": "English yes/no = do NP V[-tense] NP (aux fronting)",
        "en:wh-object": "English which-object = which N do PRON V[-tense]",
    }
    items = []
    for c in seed_constructions():
        items.append(
            item(
                item_id=f"W:{c.construction_id}",
                klass="word_order_assumption",
                name=mapping[c.construction_id],
                classification="convenience",
                source="src/ocm/language/constructions.py",
                detail="Authored English linearization; not architecture. Same-code SOV learning is the hostile.",
                retained_in_minimal_substrate=False,
                language_specific=True,
                extra={"construction_id": c.construction_id, "family": c.family},
            )
        )
    items.append(
        item(
            item_id="W:realize-svo-templates",
            klass="word_order_assumption",
            name="realizer hardcodes English active/passive/do-support order",
            classification="convenience",
            source="src/ocm/language/realize.py",
            detail="realize() emits '{agent} {past} {patient}', '{patient} was {pp} by {agent}', '{agent} did not {verb} {patient}', 'did {agent} {verb} {patient}'.",
            retained_in_minimal_substrate=False,
            language_specific=True,
        )
    )
    items.append(
        item(
            item_id="W:microworld-generator-svo",
            klass="word_order_assumption",
            name="microworld corpus generator emits English SVO/passive/do-support",
            classification="convenience",
            source="src/ocm/language/microworld.py",
            detail="generate() authors English strings from NOUNS/VERBS_PAST/ADJS. Teaching data, not learned competence.",
            retained_in_minimal_substrate=False,
            language_specific=True,
        )
    )
    return items


def semantic_role_mappings() -> list[dict[str, Any]]:
    rows = [
        ("R:active-agent-patient", "active clause: leftmost NP=ROLE:agent, rightmost NP=ROLE:patient", "src/ocm/language/constructions.py"),
        ("R:passive-swap", "passive: surface subject=ROLE:patient, by-NP=ROLE:agent", "src/ocm/language/constructions.py"),
        ("R:intransitive-agent", "intransitive subject=ROLE:agent", "src/ocm/language/constructions.py"),
        ("R:tense-from-verb-or-aux", "TENSE edge from verb features or aux", "src/ocm/language/constructions.py"),
        ("R:negates", "do-not construction adds NEGATES on the event", "src/ocm/language/constructions.py"),
        ("R:asks-polarity", "yes/no construction adds ASKS polarity question_variable", "src/ocm/language/constructions.py"),
        ("R:wh-object", "which-N is ASKS on the patient node; PRON subject may be underspecified", "src/ocm/language/constructions.py"),
        ("R:np-modifies", "optional ADJ is MODIFIES property on the noun", "src/ocm/language/constructions.py"),
        ("R:definite-the", "optional DET marks entity feature definite=yes", "src/ocm/language/constructions.py"),
        ("R:realize-role-lookup", "realizer reads ROLE:agent/patient to linearize", "src/ocm/language/realize.py"),
    ]
    return [
        item(
            item_id=i,
            klass="semantic_role_mapping",
            name=n,
            classification="convenience",
            source=s,
            detail="Form-to-role correspondence is authored for English seed families. Curriculum families must register their own template as teacher information.",
            retained_in_minimal_substrate=False,
            language_specific=True,
        )
        for i, n, s in rows
    ]


def parser_procedures() -> list[dict[str, Any]]:
    rows = [
        ("P:tokenize", "interpret.tokenize", "src/ocm/language/interpret.py", "convenience", False, True),
        ("P:lexicon-analyse", "Lexicon.analyse lemma plus morphology, exception override", "src/ocm/language/lexicon.py", "constitutionally_necessary", False, True),
        ("P:match-constructions", "bottom-up phrase table + whole-utterance clause match", "src/ocm/language/constructions.py", "constitutionally_necessary", False, True),
        ("P:chart-earley", "packed Earley forest with exact derivation counts and evidence ranking", "src/ocm/language/chart.py", "constitutionally_necessary", False, True),
        ("P:interpret-pipeline", "utterance → readings → matches → select → said-record", "src/ocm/language/interpret.py", "constitutionally_necessary", False, True),
        ("P:select", "exactly one LIVE candidate ⇒ INTERPRETED; else AMBIGUOUS/UNKNOWN", "src/ocm/language/interpret.py", "constitutionally_necessary", False, True),
        ("P:gap-readings", "optional unknown-token gap as N placeholder", "src/ocm/language/chart.py", "convenience", False, True),
        ("P:ahu-tree-canonical", "polynomial tree canonical form above node bound", "src/ocm/language/meaning_tree.py", "constitutionally_necessary", False, True),
    ]
    return [
        item(
            item_id=i,
            klass="parser_procedure",
            name=n,
            classification=cl,
            source=s,
            detail="Generic procedure if grammar/lexicon are data. English enters only through seed objects.",
            retained_in_minimal_substrate=ret,
            language_specific=False,
        )
        for i, n, s, cl, _ls, ret in rows
    ]


def realization_templates() -> list[dict[str, Any]]:
    from ocm.dialogue.surface_text import PHRASES

    items = [
        item(
            item_id="Z:en-transitive",
            klass="realization_template",
            name="{agent} {past} {patient}",
            classification="convenience",
            source="src/ocm/language/realize.py",
            detail="English active.",
            retained_in_minimal_substrate=False,
            language_specific=True,
        ),
        item(
            item_id="Z:en-passive",
            klass="realization_template",
            name="{patient} was {pp} by {agent}",
            classification="convenience",
            source="src/ocm/language/realize.py",
            detail="English passive; 'was' authored.",
            retained_in_minimal_substrate=False,
            language_specific=True,
        ),
        item(
            item_id="Z:en-negation",
            klass="realization_template",
            name="{agent} did not|didn't {verb} {patient}",
            classification="convenience",
            source="src/ocm/language/realize.py",
            detail="English do-support negation plus contraction switch.",
            retained_in_minimal_substrate=False,
            language_specific=True,
        ),
        item(
            item_id="Z:en-yesno",
            klass="realization_template",
            name="did {agent} {verb} {patient}",
            classification="convenience",
            source="src/ocm/language/realize.py",
            detail="English aux-fronted yes/no.",
            retained_in_minimal_substrate=False,
            language_specific=True,
        ),
        item(
            item_id="Z:en-intransitive",
            klass="realization_template",
            name="{agent} {past}",
            classification="convenience",
            source="src/ocm/language/realize.py",
            detail="English intransitive.",
            retained_in_minimal_substrate=False,
            language_specific=True,
        ),
        item(
            item_id="Z:en-np-the",
            klass="realization_template",
            name="optional determiner 'the ' plus adjective sequence",
            classification="convenience",
            source="src/ocm/language/realize.py",
            detail="Definiteness realized as English 'the'.",
            retained_in_minimal_substrate=False,
            language_specific=True,
        ),
        item(
            item_id="Z:capitalize-punct",
            klass="realization_template",
            name="capitalize first character and append . or ?",
            classification="convenience",
            source="src/ocm/language/realize.py",
            detail="English orthographic packaging.",
            retained_in_minimal_substrate=False,
            language_specific=True,
        ),
    ]
    for rel, phrase in sorted(PHRASES.items()):
        items.append(
            item(
                item_id=f"Z:world-phrase:{rel}",
                klass="realization_template",
                name=f"{rel} → '{phrase}'",
                classification="convenience",
                source="src/ocm/dialogue/surface_text.py",
                detail="Bounded-world English relation phrase. Historical checker only.",
                retained_in_minimal_substrate=False,
                language_specific=True,
            )
        )
    return items


def dialogue_act_rules() -> list[dict[str, Any]]:
    from ocm.dialogue.gate import Act
    from ocm.language.session import ReplyKind

    items = []
    for act in Act:
        items.append(
            item(
                item_id=f"D:act:{act.name}",
                klass="dialogue_act_rule",
                name=act.name,
                classification="convenience",
                source="src/ocm/dialogue/gate.py",
                detail="Fixed interaction taxonomy. Commitment markers may stay constitutional; the inventory is prior structure.",
                retained_in_minimal_substrate=act.name in {"ASSERT", "ASK", "CLARIFY", "REPORT_UNKNOWN"},
                language_specific=False,
                extra={"value": act.value},
            )
        )
    for kind in ReplyKind:
        items.append(
            item(
                item_id=f"D:reply:{kind.name}",
                klass="dialogue_act_rule",
                name=f"session ReplyKind.{kind.name}",
                classification="convenience" if kind.name not in {"RECORDED", "CLARIFY", "LEARN", "CANNOT_CHECK"} else "constitutionally_necessary",
                source="src/ocm/language/session.py",
                detail="Session control states over interpretation verdicts.",
                retained_in_minimal_substrate=True,
                language_specific=False,
            )
        )
    english_replies = [
        ("D:text:recorded", "Recorded: {speaker} said …"),
        ("D:text:yes-said", "Yes — {speaker} said so ({id}); I have no independent warrant."),
        ("D:text:no-said", "No — {speaker} said it did not ({id}); I have no independent warrant."),
        ("D:text:unknown-contra", "Unknown — contradictory statements are on record: …"),
        ("D:text:unknown-none", "Unknown — nothing on record supports or denies it."),
        ("D:text:which", "Which did you mean: {options}?"),
        ("D:text:still-which", "I still cannot tell which; answer with the number."),
        ("D:text:learn", "I cannot interpret this yet (… ). Show me what it means."),
        ("D:text:needs-context", "I need to know what you refer to: …"),
    ]
    for i, n in english_replies:
        items.append(
            item(
                item_id=i,
                klass="dialogue_act_rule",
                name=n,
                classification="convenience",
                source="src/ocm/language/session.py",
                detail="Authored English session wording.",
                retained_in_minimal_substrate=False,
                language_specific=True,
            )
        )
    return items


def pronoun_reference_rules() -> list[dict[str, Any]]:
    from ocm.dialogue.reference import ORDINALS, PRONOUNS

    items = []
    for surface, feats in PRONOUNS.items():
        items.append(
            item(
                item_id=f"N:pronoun:{surface}",
                klass="pronoun_reference_rule",
                name=surface,
                classification="convenience",
                source="src/ocm/dialogue/reference.py",
                detail=f"English pronoun feature map {feats}",
                retained_in_minimal_substrate=False,
                language_specific=True,
                extra={"features": feats},
            )
        )
    for surface, idx in ORDINALS.items():
        items.append(
            item(
                item_id=f"N:ordinal:{surface}",
                klass="pronoun_reference_rule",
                name=surface,
                classification="convenience",
                source="src/ocm/dialogue/reference.py",
                detail=f"English ordinal index {idx}",
                retained_in_minimal_substrate=False,
                language_specific=True,
                extra={"index": idx},
            )
        )
    for det in ("the", "this", "that", "these", "those"):
        items.append(
            item(
                item_id=f"N:det:{det}",
                klass="pronoun_reference_rule",
                name=f"description-mention determiner '{det}'",
                classification="convenience",
                source="src/ocm/dialogue/reference.py",
                detail="English definite/deictic mention parser.",
                retained_in_minimal_substrate=False,
                language_specific=True,
            )
        )
    items.append(
        item(
            item_id="N:recency-order-only",
            klass="pronoun_reference_rule",
            name="recency orders clarification candidates but never resolves",
            classification="constitutionally_necessary",
            source="src/ocm/dialogue/reference.py",
            detail="Four-valued resolution; nearest-string mutant is planted and refused.",
            retained_in_minimal_substrate=True,
            language_specific=False,
        )
    )
    return items


def clarification_rules() -> list[dict[str, Any]]:
    return [
        item(
            item_id="Q:value-policy",
            klass="clarification_rule",
            name="information-value ask policy",
            classification="constitutionally_necessary",
            source="src/ocm/dialogue/clarify.py",
            detail="value = expected determined query cells − cost − repeat penalty; ask iff max value > 0.",
            retained_in_minimal_substrate=True,
            language_specific=False,
        ),
        item(
            item_id="Q:did-you-mean",
            klass="clarification_rule",
            name="Did you mean {x}?",
            classification="convenience",
            source="src/ocm/dialogue/clarify.py",
            detail="English binary question wording.",
            retained_in_minimal_substrate=False,
            language_specific=True,
        ),
        item(
            item_id="Q:menu",
            klass="clarification_rule",
            name="Which did you mean: …",
            classification="convenience",
            source="src/ocm/dialogue/clarify.py",
            detail="English menu wording.",
            retained_in_minimal_substrate=False,
            language_specific=True,
        ),
        item(
            item_id="Q:numeric-reply",
            klass="clarification_rule",
            name="clarification resolved by 1-based index or unique string hit",
            classification="convenience",
            source="src/ocm/language/session.py",
            detail="English/arabic-numeral interaction convention.",
            retained_in_minimal_substrate=False,
            language_specific=True,
        ),
    ]


def discourse_schemas() -> list[dict[str, Any]]:
    from ocm.dialogue.planner import FUNCTIONAL_RELATIONS, Rhetorical

    items = []
    for r in Rhetorical:
        items.append(
            item(
                item_id=f"E:rhetorical:{r.name}",
                klass="explanation_discourse_schema",
                name=r.name,
                classification="convenience",
                source="src/ocm/dialogue/planner.py",
                detail="Authored rhetorical relation for planning.",
                retained_in_minimal_substrate=False,
                language_specific=False,
            )
        )
    plans = [
        ("E:plan-answer", "plan_answer yes/no from world+commitments", "src/ocm/dialogue/planner.py"),
        ("E:plan-explain", "plan_explain ELABORATION along IS_A/PART_OF/LOCATED_IN/ORBITS", "src/ocm/dialogue/planner.py"),
        ("E:plan-compare", "plan_compare CONTRAST shared vs differing relations", "src/ocm/dialogue/planner.py"),
        ("E:plan-summary", "plan_summary LIST of speaker commitments", "src/ocm/dialogue/planner.py"),
        ("E:plan-teach-back", "plan_teach_back \"'{lexeme}' means {concept}\"", "src/ocm/dialogue/planner.py"),
        ("E:functional-relations", f"FUNCTIONAL_RELATIONS={sorted(FUNCTIONAL_RELATIONS)}", "src/ocm/dialogue/planner.py"),
    ]
    for i, n, s in plans:
        items.append(
            item(
                item_id=i,
                klass="explanation_discourse_schema",
                name=n,
                classification="convenience",
                source=s,
                detail="Authored explanation/discourse procedure. N2 must learn or count as prior.",
                retained_in_minimal_substrate=False,
                language_specific=True,
            )
        )
    return items


def style_register_rules() -> list[dict[str, Any]]:
    from ocm.language.realize import Style

    style = Style()
    items = [
        item(
            item_id="S:register-enum",
            klass="style_register_rule",
            name="register ∈ {neutral, brief, detailed, formal, casual}",
            classification="convenience",
            source="src/ocm/language/realize.py",
            detail=f"Default Style.register={style.register!r}, contractions={style.contractions}, prefer_passive={style.prefer_passive}.",
            retained_in_minimal_substrate=False,
            language_specific=True,
        ),
        item(
            item_id="S:length-by-register",
            klass="style_register_rule",
            name="explanation length_target brief=2, neutral=4, detailed=8",
            classification="convenience",
            source="src/ocm/dialogue/planner.py",
            detail="Authored register→clause-count map.",
            retained_in_minimal_substrate=False,
            language_specific=True,
        ),
        item(
            item_id="S:epistemic-prefixes",
            klass="style_register_rule",
            name="fixed epistemic marker sentences",
            classification="convenience",
            source="src/ocm/dialogue/surface_text.py",
            detail="Prefixes/suffixes: 'I am not sure whether ', 'A source ({source}) says so, but I have not verified it: ', 'Yes. ', citation wrappers.",
            retained_in_minimal_substrate=False,
            language_specific=True,
        ),
        item(
            item_id="S:moon-sun-earth-the",
            klass="style_register_rule",
            name="world_clause prepends 'the' for moon/sun/earth",
            classification="convenience",
            source="src/ocm/dialogue/surface_text.py",
            detail="English proper-name article exception.",
            retained_in_minimal_substrate=False,
            language_specific=True,
        ),
    ]
    return items


def authored_examples() -> list[dict[str, Any]]:
    from ocm.dialogue import microworld as D
    from ocm.language.meaning import example_meanings
    from ocm.language.microworld import ADJS, NOUNS, VERBS_PAST, generate

    examples = example_meanings()
    items = []
    for utt in examples:
        items.append(
            item(
                item_id=f"X:meaning:{utt}",
                klass="authored_example_lesson",
                name=utt,
                classification="convenience",
                source="src/ocm/language/meaning.py",
                detail="Hand-built M3 example meaning graph.",
                retained_in_minimal_substrate=False,
                language_specific=True,
            )
        )
    items.append(
        item(
            item_id="X:microworld-generator",
            klass="authored_example_lesson",
            name="OCM-M3-MICROWORLD-20260905 generator",
            classification="convenience",
            source="src/ocm/language/microworld.py",
            detail=f"Authored generator seed; default n=240; families transitive/transitive_adj/negation/yes_no/passive; nouns={list(NOUNS)}; verbs={VERBS_PAST}; adjs={list(ADJS)}; held-out dog/book/find.",
            retained_in_minimal_substrate=False,
            language_specific=True,
            extra={"default_n": 240, "seed": "OCM-M3-MICROWORLD-20260905", "generated_count": len(generate())},
        )
    )
    items.append(
        item(
            item_id="X:dialogue-generator",
            klass="authored_example_lesson",
            name="OCM-M4-DIALOGUE-20260905 generator",
            classification="convenience",
            source="src/ocm/dialogue/microworld.py",
            detail="Authored scripted dialogues (statement_question, correction, contradiction, pronoun, topic return, retraction, ten speakers). Default n=120.",
            retained_in_minimal_substrate=False,
            language_specific=True,
            extra={"default_n": 120, "seed": "OCM-M4-DIALOGUE-20260905", "generated_count": len(D.generate())},
        )
    )
    items.append(
        item(
            item_id="X:acquisition-fixture",
            klass="authored_example_lesson",
            name="acquisition_lexicon fixture (robot/door/cat/box/key + open/push/see + -ed/saw)",
            classification="convenience",
            source="src/ocm/language/bootstrap.py",
            detail="Copied M3 test fixture so installed runtimes do not depend on the test suite.",
            retained_in_minimal_substrate=False,
            language_specific=True,
        )
    )
    return items


def build_inventory() -> dict[str, Any]:
    items: list[dict[str, Any]] = []
    items.extend(constitutional_items())
    items.extend(charged_general_priors())
    items.extend(seed_lexemes())
    items.extend(morphology_priors())
    items.extend(construction_priors())
    items.extend(word_order_assumptions())
    items.extend(semantic_role_mappings())
    items.extend(parser_procedures())
    items.extend(realization_templates())
    items.extend(dialogue_act_rules())
    items.extend(pronoun_reference_rules())
    items.extend(clarification_rules())
    items.extend(discourse_schemas())
    items.extend(style_register_rules())
    items.extend(authored_examples())

    ids = [r["id"] for r in items]
    if len(ids) != len(set(ids)):
        raise AssertionError("duplicate inventory ids")

    by_class: dict[str, int] = {}
    for r in items:
        by_class[r["class"]] = by_class.get(r["class"], 0) + 1

    language_specific = [r for r in items if r["language_specific"]]
    convenience = [r for r in items if r["classification"] == "convenience"]
    constitutional = [r for r in items if r["classification"] == "constitutionally_necessary"]
    retained_min = [r for r in items if r["retained_in_minimal_substrate"]]
    retained_langspec = [r for r in items if r["language_specific"] and r["retained_in_minimal_substrate"]]
    stripped_for_n1 = [r for r in items if r["language_specific"] and not r["retained_in_minimal_substrate"]]

    bindings = {}
    for rel in SOURCE_FILES:
        path = ROOT / rel
        bindings[rel] = {
            "git_blob_sha1": git_blob_sha(path) if path.is_file() else "MISSING",
            "sha256": sha256_file(path) if path.is_file() else "MISSING",
            "bytes": path.stat().st_size if path.is_file() else 0,
        }

    return {
        "schema": "ocm.l0-bootstrap-audit.v1",
        "role": "L0_TIME_ZERO_LANGUAGE_PRIOR_AUDIT",
        "github_issue": 54,
        "master_roadmap_issue": 165,
        "master_box": "L0 — Language bootstrap audit (#54)",
        "protected_outcomes_read": False,
        "n1_claim_authority": False,
        "l1_locked": True,
        "question": "What language-specific prior exists before protected N1, and what remains after stripping convenience?",
        "source_bindings": bindings,
        "items": items,
        "counts": {
            "items_total": len(items),
            "by_class": by_class,
            "constitutionally_necessary": len(constitutional),
            "convenience": len(convenience),
            "language_specific": len(language_specific),
            "retained_in_minimal_substrate": len(retained_min),
            "retained_language_specific_prior": len(retained_langspec),
            "stripped_language_specific_for_n1": len(stripped_for_n1),
        },
        "minimal_substrate": {
            "object_stores_at_time_zero": {
                "lexemes": 0,
                "morph_rules": 0,
                "constructions": 0,
                "english_realization_templates": 0,
                "english_pronouns": 0,
            },
            "retain": [r["id"] for r in retained_min],
            "strip": [r["id"] for r in stripped_for_n1],
            "note": (
                "Time-zero object stores are empty. Constitutional mechanisms plus charged "
                "language-general schemas/adapters remain. English instances, word-order, "
                "realizer templates, pronouns, surface phrases, and authored lessons are convenience "
                "and must be absent from the N1 mechanism arm. A family's semantic target schema "
                "and finite hypothesis class are teacher information when that family is taught, "
                "not hidden architecture."
            ),
        },
        "predecessor": {
            "path": "research/ocm-n1/LANGUAGE_BOOTSTRAP_MANIFEST_V1.json",
            "role": "class-level prospective audit; this packet enumerates items",
        },
        "nonclaim": (
            "This does not establish English acquisition, unsupervised grammar induction, "
            "language meta-learning, or N1 learned understanding."
        ),
    }


def _historical_svo_ok() -> dict[str, Any]:
    from ocm.language.bootstrap import microworld_lexicon
    from ocm.language.constructions import seed_constructions
    from ocm.language.interpret import Verdict, interpret

    lx = microworld_lexicon()
    cons = seed_constructions()
    svo = interpret("the girl pushed the ball", lx, cons)
    sov = interpret("the girl the ball pushed", lx, cons)
    sov_bare = interpret("girl ball push", lx, cons)
    return {
        "svo_utterance": "the girl pushed the ball",
        "svo_verdict": svo.verdict.value,
        "sov_utterance": "the girl the ball pushed",
        "sov_verdict": sov.verdict.value,
        "sov_bare_utterance": "girl ball push",
        "sov_bare_verdict": sov_bare.verdict.value,
        "historical_bootstrap_accepts_svo": svo.verdict is Verdict.INTERPRETED,
        "historical_bootstrap_rejects_sov": sov.verdict is not Verdict.INTERPRETED,
        "teacher_events_needed_for_historical_svo": 0,
    }


def run_ablations() -> dict[str, Any]:
    import minimal_construction_recovery as CR
    import minimal_language_learning as LL
    import minimal_morphology_recovery as MR

    historical = _historical_svo_ok()
    svo_cal = LL.run()
    cons_cal = CR.run()
    morph_cal = MR.run()

    # Cheap information-event comparison: historical English SVO is already encoded;
    # the empty-store arm pays explicit word lessons + one demonstration.
    full_vs_minimal = {
        "status": "RAN",
        "scope": "E1_CALIBRATION_NOT_PROTECTED_N1",
        "full_bootstrap_english_svo": {
            "teacher_events": historical["teacher_events_needed_for_historical_svo"],
            "accepts_svo": historical["historical_bootstrap_accepts_svo"],
            "rejects_sov": historical["historical_bootstrap_rejects_sov"],
        },
        "minimal_empty_store_svo": {
            "information_events": svo_cal["svo"]["information_events"],
            "held_out_composition": svo_cal["svo"]["held_out_composition"],
            "learned_hypothesis": svo_cal["svo"]["learned_hypothesis"],
        },
        "minimal_empty_store_sov": {
            "information_events": svo_cal["sov"]["information_events"],
            "held_out_composition": svo_cal["sov"]["held_out_composition"],
            "learned_hypothesis": svo_cal["sov"]["learned_hypothesis"],
        },
        "protected_n1_acquisition_curves": {
            "status": "CANNOT_CHECK",
            "reason": "CANNOT_CHECK_N1_LOCKED_PROTECTED_CURVES_NOT_RUN",
        },
        "note": (
            "Historical bootstrap parses English SVO with zero post-freeze lessons because the "
            "seed already contains that competence. The empty-store arm pays counted teacher "
            "events and the same code learns SOV. This is not a protected N1 curve."
        ),
    }

    construction_removal = {
        "status": "RAN",
        "time_zero_constructions": cons_cal["time_zero_constructions"],
        "learned_construction_objects": cons_cal["learned_construction_objects"],
        "all_seven_recovered": cons_cal["all_seven_recovered"],
        "all_seven_revocable": cons_cal["all_seven_revocable"],
        "teacher_token_lessons": cons_cal["teacher_information"]["token_lessons"],
        "aligned_family_demonstrations": cons_cal["teacher_information"]["aligned_family_demonstrations"],
        "semantic_target_schemas_registered": cons_cal["teacher_information"]["semantic_target_schemas_registered"],
        "terminal": cons_cal["terminal"],
        "protected_claim_authority": cons_cal["protected_claim_authority"],
        "charged_prior_even_at_empty_store": [
            "seven registered semantic target schemas",
            "finite form-order hypothesis classes",
            "Category inventory",
            "strongly supervised token lessons",
        ],
    }

    morphology_removal = {
        "status": "RAN",
        "time_zero_morph_rules": morph_cal["time_zero_morph_rules"],
        "teacher_paradigm_pairs": morph_cal["teacher_paradigm_pairs"],
        "held_out_jump_generalizes": morph_cal["held_out_jump_generalizes"],
        "irregular_see_recognized": morph_cal["irregular_see_recognized"],
        "terminal": morph_cal["terminal"],
        "protected_claim_authority": morph_cal["protected_claim_authority"],
    }

    sov_hostile = {
        "status": "RAN",
        "same_learning_code": svo_cal["same_learning_code"],
        "svo_hypothesis": svo_cal["svo"]["learned_hypothesis"],
        "sov_hypothesis": svo_cal["sov"]["learned_hypothesis"],
        "svo_held_out": svo_cal["svo"]["held_out_composition"],
        "sov_held_out": svo_cal["sov"]["held_out_composition"],
        "svo_rejects_sov": svo_cal["svo"]["rejects_conflicting_order"],
        "sov_rejects_svo": svo_cal["sov"]["rejects_conflicting_order"],
        "historical_seed_rejects_sov": historical["historical_bootstrap_rejects_sov"],
        "historical_sov_verdict": historical["sov_verdict"],
        "terminal": svo_cal["terminal"],
        "protected_claim_authority": svo_cal["protected_claim_authority"],
        "note": (
            "The historical English seed does not accept SOV. The empty-store substrate learns "
            "SVO and a conflicting SOV artificial language from counted demonstrations. "
            "Word category/concept lessons and the transitive role template remain charged."
        ),
    }

    return {
        "schema": "ocm.l0-bootstrap-ablation.v1",
        "study_role": "E1_ENGINEERING_CALIBRATION",
        "protected_claim_authority": False,
        "historical_seed_probe": historical,
        "reduced_bootstrap": {
            "full_vs_minimal_information_events": full_vs_minimal,
            "construction_family_removal_recovery": construction_removal,
            "morphology_removal_recovery": morphology_removal,
        },
        "sov_artificial_hostile": sov_hostile,
        "cannot_check": [
            {
                "item": "protected N1 full-bootstrap vs minimal-bootstrap acquisition curves",
                "terminal": "CANNOT_CHECK_N1_LOCKED_PROTECTED_CURVES_NOT_RUN",
            }
        ],
    }


def derive_terminal(inventory: dict[str, Any], ablation: dict[str, Any]) -> dict[str, Any]:
    counts = inventory["counts"]
    if counts["stripped_language_specific_for_n1"] <= 0:
        return {
            "terminal": "BOOTSTRAP_PRIOR_DOMINATES",
            "reason": "no language-specific convenience items were identified for stripping",
        }
    sov = ablation["sov_artificial_hostile"]
    cons = ablation["reduced_bootstrap"]["construction_family_removal_recovery"]
    morph = ablation["reduced_bootstrap"]["morphology_removal_recovery"]
    hist = ablation["historical_seed_probe"]
    if not (
        sov["status"] == "RAN"
        and sov["svo_held_out"]
        and sov["sov_held_out"]
        and sov["same_learning_code"]
        and cons["all_seven_recovered"]
        and morph["held_out_jump_generalizes"]
        and hist["historical_bootstrap_rejects_sov"]
    ):
        return {
            "terminal": "CANNOT_CHECK_ABLATION_OR_HOSTILE_FAILED",
            "reason": "a required cheap calibration did not pass",
        }
    return {
        "terminal": "MINIMAL_LANGUAGE_SUBSTRATE_REGISTERED",
        "scope": (
            "Registered time-zero substrate has empty lexeme/morphology/construction stores and "
            "no English realizer/pronoun/surface templates. Constitutional KSO/select/gate/"
            "schema/parser/acquisition machinery is retained. Category tags, meaning-role "
            "registry, tokenizer, and per-family semantic target schemas are charged priors "
            "when used. Historical runtime remains convenience-heavy and is not the N1 start "
            "state. Protected N1 curves are not run. L1 stays locked."
        ),
        "retained_language_specific_prior_count": counts["retained_language_specific_prior"],
        "stripped_language_specific_count": counts["stripped_language_specific_for_n1"],
    }


def l0_box_status(inventory: dict[str, Any], ablation: dict[str, Any]) -> list[dict[str, Any]]:
    by_class = inventory["counts"]["by_class"]
    required = {
        "enumerate every seed lexeme": by_class.get("seed_lexeme", 0) > 0,
        "enumerate morphology priors": by_class.get("morphology_prior", 0) > 0,
        "enumerate construction priors": by_class.get("construction_prior", 0) > 0,
        "enumerate word-order assumptions": by_class.get("word_order_assumption", 0) > 0,
        "enumerate semantic-role mappings": by_class.get("semantic_role_mapping", 0) > 0,
        "enumerate parser procedures": by_class.get("parser_procedure", 0) > 0,
        "enumerate realization templates": by_class.get("realization_template", 0) > 0,
        "enumerate dialogue-act rules": by_class.get("dialogue_act_rule", 0) > 0,
        "enumerate pronoun/reference rules": by_class.get("pronoun_reference_rule", 0) > 0,
        "enumerate clarification rules": by_class.get("clarification_rule", 0) > 0,
        "enumerate explanation/discourse schemas": by_class.get("explanation_discourse_schema", 0) > 0,
        "enumerate style/register rules": by_class.get("style_register_rule", 0) > 0,
        "enumerate authored examples/lessons": by_class.get("authored_example_lesson", 0) > 0,
        "classify constitutionally necessary vs convenience": inventory["counts"]["constitutionally_necessary"] > 0
        and inventory["counts"]["convenience"] > 0,
        "count retained language-specific prior information": True,
        "run reduced-bootstrap ablation": ablation["reduced_bootstrap"]["construction_family_removal_recovery"]["status"]
        == "RAN",
        "run conflicting artificial/SOV hostile": ablation["sov_artificial_hostile"]["status"] == "RAN",
    }
    out = []
    for box in L0_BOXES:
        out.append({"box": box, "checked": bool(required[box])})
    return out


def verify() -> dict[str, Any]:
    inventory = build_inventory()
    ablation = run_ablations()
    decision = derive_terminal(inventory, ablation)
    boxes = l0_box_status(inventory, ablation)
    if not all(b["checked"] for b in boxes):
        raise AssertionError(f"unchecked L0 boxes: {[b for b in boxes if not b['checked']]}")
    if inventory["protected_outcomes_read"] or inventory["n1_claim_authority"]:
        raise AssertionError("L0 audit lost prospective-only scope")
    if decision["terminal"] != "MINIMAL_LANGUAGE_SUBSTRATE_REGISTERED":
        raise AssertionError(decision)
    counts = inventory["counts"]
    if counts["by_class"].get("seed_lexeme") < 26:
        raise AssertionError("microworld seed lexemes missing from item inventory")
    if counts["retained_language_specific_prior"] != 0:
        raise AssertionError("registered minimal arm still retains language-specific objects")
    return {
        "receipt": "L0_LANGUAGE_BOOTSTRAP_AUDIT_V1",
        "terminal": decision["terminal"],
        "scope": decision["scope"],
        "counts": counts,
        "l0_boxes": boxes,
        "protected_claim_authority": False,
        "l1_locked": True,
    }


def write_artifacts(inventory: dict[str, Any], ablation: dict[str, Any], decision: dict[str, Any], boxes: list[dict[str, Any]]) -> None:
    (HERE / "INVENTORY.json").write_text(json.dumps(inventory, indent=2, sort_keys=False) + "\n", encoding="utf-8")
    (HERE / "ABLATION.json").write_text(json.dumps(ablation, indent=2, sort_keys=False) + "\n", encoding="utf-8")
    receipt = {
        "receipt": "L0_LANGUAGE_BOOTSTRAP_AUDIT_V1",
        "terminal": decision["terminal"],
        "scope": decision["scope"],
        "counts": inventory["counts"],
        "l0_boxes": boxes,
        "protected_outcomes_read": False,
        "n1_claim_authority": False,
        "l1_locked": True,
        "cannot_check": ablation["cannot_check"],
    }
    (HERE / "RECEIPT.json").write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    inventory = build_inventory()
    ablation = run_ablations()
    decision = derive_terminal(inventory, ablation)
    boxes = l0_box_status(inventory, ablation)
    write_artifacts(inventory, ablation, decision, boxes)
    summary = {
        "terminal": decision["terminal"],
        "counts": inventory["counts"],
        "boxes_checked": sum(1 for b in boxes if b["checked"]),
        "boxes_total": len(boxes),
        "l1_locked": True,
    }
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
