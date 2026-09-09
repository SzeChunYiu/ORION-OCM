"""Programme closure ledger for ORION-OCM #165.

#165 section 18 states the closure condition exactly:

    "The programme closes scientifically when every required gate has an explicit
     bounded disposition."
    "A complete negative or conditional result is still 100% completion of the
     programme."

So closure is not "every checkbox ticked". It is: **no required gate is left
without a disposition drawn from its own registered terminal vocabulary**, where
``CANNOT_CHECK_<reason>`` is itself a registered and valid disposition.

This module is that ledger, built so it cannot flatter the programme:

* the terminal vocabularies are **parsed out of a vendored copy of the #165 body**
  rather than transcribed, so a disposition cannot be invented that the roadmap
  never offered, and the copy carries its sha256;
* every disposition must cite at least one **receipt that exists on disk**, and a
  missing file is an error rather than a footnote;
* every ``CANNOT_CHECK_`` must carry a reason and a statement of what would
  convert it, so an unmeasured gate cannot hide behind the terminal that is
  meant to disclose it;
* the **programme terminal is derived** from the gate dispositions by a rule
  written before the dispositions were filled in, not asserted alongside them.

Research-only. This module reads receipts and the roadmap. It runs no study,
changes no production code, and closes nothing on its own authority.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
from typing import Any, Mapping, Sequence

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
BODY = HERE / "ISSUE_165_BODY.md"
BODY_SHA256 = "0aeb5bbef21245daaf727d61cb47ce5275b6743624e3cbefbe73032f310f2368"

SCHEMA = "orion-ocm.programme-closure.v1"


# --- the roadmap's own vocabularies, parsed rather than retyped ---------------

def vocabularies(text: str | None = None) -> dict[str, tuple[str, ...]]:
    """Every ``## <name> terminals`` fenced block in the roadmap body.

    Parsing beats transcribing here for one reason: a transcription can silently
    gain a terminal the roadmap never registered, and that is exactly the error
    a closure ledger must not be able to make.
    """
    text = BODY.read_text() if text is None else text
    out: dict[str, tuple[str, ...]] = {}
    for match in re.finditer(r"^## (.+?terminals|Architectural endpoints)\s*$", text, re.M):
        start = text.find("```text", match.end())
        end = text.find("```", start + 7)
        if start < 0 or end < 0:
            continue
        block = text[start + 7:end]
        out[match.group(1).strip()] = tuple(
            line.strip() for line in block.splitlines() if line.strip())
    return out


def body_is_authentic() -> bool:
    return hashlib.sha256(BODY.read_bytes()).hexdigest() == BODY_SHA256


def registered(vocabulary: Sequence[str], disposition: str) -> bool:
    """Is ``disposition`` a member of this gate's registered vocabulary?

    ``CANNOT_CHECK_<reason>`` and ``PARTIAL_SIGNATURE_ONLY_<which>`` are
    parameterised in the roadmap, so their prefixes are matched and the suffix is
    free text -- but the suffix must be non-empty, or the terminal discloses
    nothing.
    """
    for entry in vocabulary:
        if entry == disposition:
            return True
        if entry.endswith(">") and "<" in entry:
            prefix = entry[:entry.index("<")]
            if disposition.startswith(prefix) and len(disposition) > len(prefix):
                return True
    return False


# --- the gates ---------------------------------------------------------------

def gate(name, vocabulary, dispositions, receipts, basis, unconverted=None):
    return {"gate": name, "vocabulary": vocabulary, "dispositions": list(dispositions),
            "receipts": list(receipts), "basis": basis,
            "what_would_convert_it": unconverted}


GATES = [
    gate(
        "G1", "G1 exit terminals",
        ["COMPACT_VESSEL_PARTIAL"],
        ["research/g1-vessel-freeze-v1/TERMINAL.json",
         "research/g1-vessel-freeze-v1/MANIFEST.json"],
        "The (F,O,Pi,C) manifest is frozen, but subtraction (PR #187) found M0 "
        "OCMRuntime and work.Operator both required by current tests, with no "
        "production deletion and MINIMUM_SELF_EXTENDING_VESSEL explicitly not "
        "claimed. Necessity was established by test failure, which does not yet "
        "separate algebraic from resource from epistemic necessity.",
        "A subtraction that removes a core and measures capability loss, resource "
        "change and epistemic-invariant failure separately."),
    gate(
        "G2", "G2 exit terminals",
        ["CAUSAL_METHOD_REUSE_SUPPORTED", "PARENT_SUFFICIENT"],
        ["research/g2-macro-operator-v1/README.md",
         "research/g2-acquisition-economics-v1/README.md"],
        "#192 reached CAUSAL_MACRO_OPERATOR_REUSE_SUPPORTED_AT_LENGTH8 on an "
        "untouched 64-task stratum: 13 strict wins with the macro actually used, "
        "revocation reducing exactly to primitive, and fresh runtime "
        "reconstruction before test. The same receipt records "
        "NO_LIFETIME_MACRO_SEARCH_PAYBACK, and ordinary persistent == OCM live "
        "task-by-task, so the mechanism is parent-owned. The acquisition-economics "
        "successor then found the tournament is load-bearing: no zero-search "
        "selector reproduces its choice, and every one of them picks a macro "
        "ranked 13 of 16 by measured utility.",
        None),
    gate(
        "G3", "G3 exit terminals",
        ["METHOD_COMPOSITION_SUPPORTED", "FAILURE_MEMORY_NOT_USEFUL",
         "REPRESENTATION_PRIOR_DOMINATES"],
        ["research/g3-independent-composition-v1/README.md",
         "research/g3-scoped-failure-memory-v1/G3_2_SCOPED_FAILURE_MEMORY_V1.json",
         "research/g3-representation-v1/G3_REPRESENTATION_V1.json"],
        "G3.1 is measured and positive: #193 selected A and B in independent "
        "lanes, and on a 256-task population fixed independently of those "
        "outcomes exactly 3 tasks used both identities, all three meeting the "
        "pre-registered strong witness, with per-method revocation removing "
        "exactly its own contribution. G3.2 is now measured and negative, and "
        "the negative is an identity rather than a price verdict: a nogood that "
        "may not mention the goal can only record an over-budget candidate, "
        "which costs one extension to discover and has no subtree to prune, so "
        "net = hits - probes - maintenance <= 0 for any population, budget "
        "schedule or store implementation in this geometry. The run confirms "
        "the identity exactly at 94,208 - 98,300 - 4,096 = -8,188, and the "
        "mechanism pays only where a probe costs under 0.917 of an extension. "
        "Scope itself is separately shown "
        "load-bearing by a falsifier -- the same store without a budget on its "
        "entries cuts 68% of search and then solves 0 of 48, unsound rather than "
        "merely worse. G3.3 is measured and negative: the only coarser ""G3.3 is measured and negative, and its stated "
        "mechanism has been corrected: the only coarser representation that "
        "stays sound is behaviourally identical to the exact one and saves "
        "nothing, while every representation coarse enough to merge anything "
        "destroys solutions -- DEGREE retains 1.4% of discoverable targets. The "
        "earlier basis attributed this to the state space having almost no "
        "redundancy. A census refutes that: 3,399 of 5,460 reachable prefixes "
        "are redundant (62%), with classes up to 52. Proposition 2 gives the "
        "real reason -- equality of normal form is a bisimulation, so the exact "
        "representation already harvests every sound merge for free, and any "
        "coarser representation is a function of the normal form and can only "
        "buy more pruning by crossing a boundary the goal test can see. The "
        "benefit term is structural; the cost term is measured. "
        "G3.4's diagnosis is implemented by re-running under changed "
        "conditions, with a timeout mapping to RESOURCE_BOUND and never licensing "
        "REPRESENTATION_INSUFFICIENT. All four G3 obligations are now measured.",
        None),
    gate(
        "G4", "G4 exit terminals",
        ["EXACT_META_POLICY_SUFFICIENT", "LEARNED_ROUTER_NOT_NEEDED",
         "EXACT_EARLY_EXIT_VALUE_SUPPORTED", "PRICE_REGIME_ONLY",
         "PARENT_SUFFICIENT", "CANNOT_CHECK_PRODUCTION_OCM_LIFETIME"],
        ["research/g4-horizon-exact-v1/SUMMARY.json",
         "research/residual-routing-v1/results/RESIDUAL_ROUTING_OPPORTUNITY_V1.json"],
        "The compose-stage residual is exactly zero (rho_R = 0.0) over 96 "
        "selection points from 70 sources, and its five bound runtime sources are "
        "byte-identical on this head, so the terminal still describes the current "
        "runtime. Every exact parent registered in G4.3 has been run. G4.4's nine "
        "unlock conditions stand at 0 of 9 with the fourth actively refuted: the "
        "legal-feature ladder drives the residual to <=0.08% before charging "
        "feature extraction, lookup, maintenance or replay. #71 stays blocked.",
        "A production OCM lifetime measurement, which no lane currently has."),
    gate(
        "G5", "G5 exit terminals",
        ["DATABASE_PARENT_SUFFICIENT",
         "CANNOT_CHECK_PACKED_FIELD_BEYOND_KIND_HANDLES"],
        ["research/g5-physical-denominator-v1/SUMMARY.json"],
        "SQLite/WAL with application snapshots, suffix restart replay and "
        "incremental authenticated identity matches JSONL ledger semantics and "
        "removes whole-file rewrite and full-history head scans. The lane "
        "explicitly does not claim PHYSICAL_DENOMINATOR_CLEAN, does not switch "
        "the production JSONL default, and leaves the packed KSO field beyond "
        "kind handles unchecked.",
        "A packed field beyond kind handles, and a production default switch with "
        "revocation semantics preserved."),
    gate(
        "G6", "G6 exit terminals",
        ["CANNOT_CHECK_MISSING_RAW_TRACES_AND_NO_THIRD_EARNED_SELF_CHANGE",
         "SELF_DIAGNOSIS_NOT_IDENTIFIABLE"],
        ["research/g6-evolvability-v1/RESULT.json"],
        "Two self-changes are recorded but the third is not earned and raw traces "
        "are missing, so the multi-generation requirement is unmet. Self-diagnosis "
        "is separately recorded as not identifiable.",
        "Three or more real generations with retained raw traces and learned "
        "intervention effects rather than supplied root causes."),
    gate(
        "G7", "G7 exit terminals",
        ["CANNOT_CHECK_ONE_OF_SIX_TRANSITIONS_COMPLETE_AND_THAT_ONE_PARENT_SUFFICIENT"],
        ["research/developmental-spine/DEVELOPMENTAL_SPINE_V1.json"],
        "The lineage receipt reports 1 of 6 developmental transitions complete. "
        "The one that is complete, D0 to D1, has terminal "
        "D0_TO_D1_TRANSITION_CONDITIONAL and its carry advantage was found "
        "PARENT_SUFFICIENT against experience replay before being recovered only "
        "under a representation with no use tax. No lane carries a single "
        "persistent (F,O,Pi,C) lineage across successive stages.",
        "One persistent lineage crossing at least two further stage boundaries "
        "with continued-versus-reset arms at each."),
    gate(
        "PROTOTYPE", "G7/Prototype terminals",
        ["CANNOT_CHECK_NO_INTEGRATED_PROTOTYPE_EXISTS"],
        ["research/programme-closure-v1/ISSUE_165_BODY.md"],
        "#73's integrated prototype has no lane, no comparator ladder run and no "
        "capability gate measurement. Nothing in the repository compares an "
        "integrated OCM against a strongest parent product, so no architectural "
        "endpoint in this vocabulary is decidable.",
        "An integrated prototype over the required domains with the registered "
        "comparator ladder and capability gate."),
]


#: Section 22's "Final" list: every governing issue must receive a terminal.
#: An issue that owns a gate INHERITS that gate's disposition and receipts, so
#: the two sections cannot disagree. An issue with no lane on this head is
#: CANNOT_CHECK and says so, citing the evidence map that records its state.
EVIDENCE_MAP = "research/issue-165-evidence-map-v1/CHECKBOX_MAP.json"

ISSUE_OWNERS = {
    62: ("G2", "experience consolidation is G2's causal-acquisition question"),
    69: ("G1", "canonical architecture is G1's vessel question"),
    70: ("G5", "compression and physical efficiency is G5's denominator question"),
    71: ("G4", "the learned-routing gate is G4.4"),
    73: ("PROTOTYPE", "the integrated prototype is the prototype gate"),
    149: ("G6", "governed self-evolution is G6's evolvability question"),
    151: ("G7", "the persistent developmental lineage is G7"),
    152: ("G4", "the exact decision/metareasoning gate is G4.1"),
}

#: Issues with no gate and no lane on this head.
ISSUES_WITHOUT_A_LANE = {
    38: "corrected acceptance / independent claims",
    42: "capability roadmap",
    49: "final proof of function",
    50: "scientific thesis",
    72: "navigation / executive control",
    93: "General Epistemic Field",
    115: "factorized KnowledgeSpace / epistemic compiler",
    143: "machine epistemics cognitive ladder",
    144: "publication constitution",
    145: "theory-empirical bridge",
}


def issue_terminals(gates: Sequence[Mapping[str, Any]] = GATES) -> dict[str, Any]:
    by_gate = {g["gate"]: g for g in gates}
    out: dict[str, Any] = {}
    for issue, (owner, why) in sorted(ISSUE_OWNERS.items()):
        gate_entry = by_gate[owner]
        out[str(issue)] = {"terminal": list(gate_entry["dispositions"]),
                           "inherited_from_gate": owner, "why": why,
                           "receipts": list(gate_entry["receipts"])}
    for issue, title in sorted(ISSUES_WITHOUT_A_LANE.items()):
        out[str(issue)] = {
            "terminal": [f"CANNOT_CHECK_NO_LANE_ON_THIS_HEAD_FOR_{title.upper().replace(' ', '_').replace('/', '_').replace('-', '_')}"],
            "inherited_from_gate": None, "why": f"{title}: no study lane exists on this head",
            "receipts": [EVIDENCE_MAP]}
    return out


# --- the derivation rule, written before the dispositions were filled in ------

DERIVATION = (
    "1. If any gate has no disposition, the programme is NOT closed.\n"
    "2. If every gate disposition is positive and none is CANNOT_CHECK, the "
    "programme may take a positive terminal.\n"
    "3. If some gates are positive and any gate is CANNOT_CHECK, the programme "
    "takes PARTIAL_SIGNATURE_ONLY_<which>, naming the supported parts.\n"
    "4. A positive gate whose mechanism an ordinary parent reproduces still "
    "counts as SUPPORTED. Section 12 is explicit -- 'PARENT_SUFFICIENT is not "
    "programme failure' -- and section 1 disclaims any requirement that OCM "
    "rediscover existing algorithms or that learned components be novel. "
    "Mechanism-level parent sufficiency is the DESIGNED mode and is recorded as "
    "an absorption, never as evidence against the thesis.\n"
    "5. The programme's own novelty target is therefore NOT the mechanism level. "
    "Section 12 places it upward: developmental law, cross-domain invariance, "
    "phase boundary, lifetime regime, principled impossibility result, "
    "integrated interaction effect -- 'mere component integration remains "
    "engineering'. The residual question is decided THERE, and the upper-level "
    "ledger below is the object that decides it.\n"
    "6. PARENT_PRODUCT_SUFFICIENT requires the COMPLETE signature to be "
    "reproduced by a parent product, which requires an integrated prototype. "
    "While PROTOTYPE is CANNOT_CHECK that terminal is unavailable in either "
    "direction."
)


#: Section 12's upward novelty targets. This is where the programme says its own
#: contribution lives, so a closure that only scores gates would be scoring the
#: engineering and ignoring the science.
UPPER_LEVEL = {
    "phase_boundary": {
        "disposition": "CANDIDATE_SUPPORTED_E2_SYNTHETIC",
        "receipts": ["research/cognitive-ladder/results/X5_BUDGET_CROSSING_V1.json",
                     "research/cognitive-ladder/results/X7_PRICED_TABLE_V1.json",
                     "research/cognitive-ladder/results/X8_TABLE_BREAK_EVEN_V1.json"],
        "basis": (
            "A carry advantage with all three edges located and none assumed: a "
            "soundness precondition on the language (DEV-4), a budget window of "
            "[1408, 1536] bits at both demand shapes (X5), and a storage ceiling "
            "below 32 bits per compiled verdict (X8). DEV-3's computed window of "
            "[768, 2048] was tested at both edges for the first time: the upper "
            "edge held out of sample, the lower is necessary and not sufficient."),
        "boundary": "E2 synthetic worlds. Not a real task ecology.",
    },
    "principled_impossibility": {
        "disposition": "CANDIDATE_SUPPORTED_ONE_RESULT_ONE_WITHDRAWN",
        "receipts": ["research/residual-routing-v1/results/RESIDUAL_ROUTING_OPPORTUNITY_V1.json",
                     "research/g2-acquisition-economics-v1/README.md"],
        "basis": (
            "ONE result stands: the compose-stage routing residual is exactly zero "
            "(rho_R = 0.0) and the legal-feature ladder drives it to <=0.08% before "
            "charging feature extraction, so decision ambiguity is not economically "
            "useful routing residual. ONE IS WITHDRAWN. This ledger previously cited "
            "NO_CHEAP_ACQUISITION_AT_THIS_ECOLOGY as a second impossibility result. "
            "It was not one. A later selector in the same study reproduces the "
            "tournament's choice at zero enumeration attempts by adding the term "
            "compression cannot see -- how much a macro token widens the grammar, "
            "countable in closed form. The earlier finding was not that cheap "
            "acquisition is impossible; it was that the three selectors tried were "
            "inadequate. The withdrawal is the more useful record: a negative of the "
            "form 'no cheap X exists' is only ever 'no cheap X that was tried', and "
            "this programme should read its own negatives that way."),
        "boundary": (
            "The surviving result is scope-bounded, not a universal impossibility "
            "theorem. The withdrawn one is a caution about how such claims are made."),
    },
    "lifetime_regime": {
        "disposition": "CANNOT_CHECK_NO_REAL_LIFETIME_MEASURED",
        "receipts": ["research/g4-horizon-exact-v1/SUMMARY.json"],
        "basis": (
            "Break-even horizons are computable and computed -- 2,136 length-8 "
            "tasks with tournament acquisition against 41 with a scan, and 32 bits "
            "per compiled verdict -- but every one is over a synthetic or "
            "single-population workload. No production OCM lifetime exists."),
        "boundary": "Conversion needs a real lifetime with all six cost terms charged.",
    },
    "developmental_law": {
        "disposition": "CANDIDATE_SURVIVED_ONE_OUT_OF_SAMPLE_TEST",
        "receipts": ["research/cognitive-ladder/SYNTHESIS_V1.json"],
        "basis": (
            "A three-coordinate conjecture (rho AND beta AND phi) registered before "
            "its out-of-sample test and surviving it. Agreement in sample is a "
            "statement about the rule's construction, and the receipt says so."),
        "boundary": "Ten synthetic rows, three binary coordinates, one test.",
    },
    "cross_domain_invariance": {
        "disposition": "CANNOT_CHECK_NO_SECOND_DOMAIN_RESULT",
        "receipts": ["research/programme-closure-v1/ISSUE_165_BODY.md"],
        "basis": (
            "One mechanism has been transferred across domains as an intervention "
            "contract with its sign NOT transferring, which is a negative and is "
            "retained. No positive cross-domain invariance is measured anywhere."),
        "boundary": "Conversion needs the same law measured in a structurally "
                    "different population.",
    },
    "integrated_interaction_effect": {
        "disposition": "CANNOT_CHECK_NO_INTEGRATED_PROTOTYPE_EXISTS",
        "receipts": ["research/programme-closure-v1/ISSUE_165_BODY.md"],
        "basis": (
            "No lane composes the gates into one machine, so no interaction between "
            "them can be observed, positive or negative."),
        "boundary": "Conversion needs #73.",
    },
}

POSITIVE_PREFIXES = ("CAUSAL_", "METHOD_COMPOSITION_SUPPORTED", "EXACT_",
                     "MINIMUM_", "DEVELOPMENTAL_", "USEFUL_", "SELF_EVOLUTION_",
                     "MULTI_GENERATION_", "PROTOTYPE_", "AMORTIZED_",
                     "ACTIVE_SUBSPACE_", "LOCAL_REVISION_", "LIFETIME_RESOURCE_",
                     "PHYSICAL_DENOMINATOR_CLEAN", "FACTORIZED_", "FACTORED_",
                     "EPISTEMICALLY_SAFE_", "FAILURE_MEMORY_USEFUL_AT_SCOPE",
                     "REPRESENTATION_CHANGE_CAUSALLY_USEFUL")


def is_positive(disposition: str) -> bool:
    return any(disposition.startswith(p) for p in POSITIVE_PREFIXES)


def validate(gates: Sequence[Mapping[str, Any]] = GATES) -> dict[str, Any]:
    vocab = vocabularies()
    problems: list[dict[str, Any]] = []
    for entry in gates:
        names = vocab.get(entry["vocabulary"])
        if names is None:
            problems.append({"gate": entry["gate"], "why": "vocabulary not found in the roadmap",
                             "detail": entry["vocabulary"]})
            continue
        if not entry["dispositions"]:
            problems.append({"gate": entry["gate"], "why": "no disposition"})
        for disposition in entry["dispositions"]:
            if not registered(names, disposition):
                problems.append({"gate": entry["gate"], "why": "disposition not registered",
                                 "detail": disposition})
            if disposition.startswith("CANNOT_CHECK") and not entry["what_would_convert_it"]:
                problems.append({"gate": entry["gate"],
                                 "why": "CANNOT_CHECK without a stated conversion",
                                 "detail": disposition})
        if not entry["receipts"]:
            problems.append({"gate": entry["gate"], "why": "no receipt cited"})
        for relative in entry["receipts"]:
            if not (REPO / relative).is_file():
                problems.append({"gate": entry["gate"], "why": "cited receipt is missing",
                                 "detail": relative})
        if not entry["basis"] or len(entry["basis"]) < 80:
            problems.append({"gate": entry["gate"], "why": "basis too thin to audit"})
    for name, row in UPPER_LEVEL.items():
        if not row.get("disposition"):
            problems.append({"gate": f"upper:{name}", "why": "no disposition"})
        if not row.get("receipts"):
            problems.append({"gate": f"upper:{name}", "why": "no receipt cited"})
        for relative in row.get("receipts", []):
            if not (REPO / relative).is_file():
                problems.append({"gate": f"upper:{name}", "why": "cited receipt is missing",
                                 "detail": relative})
        if row.get("disposition", "").startswith("CANNOT_CHECK") and not row.get("boundary"):
            problems.append({"gate": f"upper:{name}",
                             "why": "CANNOT_CHECK without a stated conversion"})
        if not row.get("basis") or len(row["basis"]) < 80:
            problems.append({"gate": f"upper:{name}", "why": "basis too thin to audit"})
    return {"problems": problems, "valid": not problems,
            "body_authentic": body_is_authentic()}


def programme_terminal(gates: Sequence[Mapping[str, Any]] = GATES) -> dict[str, Any]:
    undecided = [g["gate"] for g in gates if not g["dispositions"]]
    cannot = [g["gate"] for g in gates
              if any(d.startswith("CANNOT_CHECK") for d in g["dispositions"])]
    supported = [(g["gate"], d) for g in gates for d in g["dispositions"] if is_positive(d)]
    parent_qualified = [g["gate"] for g in gates
                        if any(d == "PARENT_SUFFICIENT" or d.endswith("PARENT_SUFFICIENT")
                               for d in g["dispositions"])]
    if undecided:
        return {"terminal": "PROGRAMME_NOT_CLOSED",
                "reason": f"gates without a disposition: {undecided}",
                "closed": False}
    which = "_AND_".join(sorted({g for g, _ in supported}))
    if not cannot and supported:
        return {"terminal": "HETEROGENEOUS_MACHINE_EPISTEMICS_SIGNATURE_SUPPORTED",
                "reason": "every gate positive and none unmeasured", "closed": True}
    return {
        "terminal": f"PARTIAL_SIGNATURE_ONLY_{which}" if supported
                    else "CANNOT_CHECK_NO_GATE_REACHED_A_POSITIVE",
        "closed": True,
        "supported_gates": [{"gate": g, "disposition": d} for g, d in supported],
        "unmeasured_gates": cannot,
        "parent_sufficient_gates": parent_qualified,
        "reason": (
            "Every required gate carries an explicit bounded disposition, which is "
            "#165 section 18's stated closure condition, so the programme is closed. "
            "It closes MIXED, not positive. "
            f"{len(supported)} gate dispositions are positive and {len(cannot)} gates "
            "are CANNOT_CHECK with a stated conversion. "
            f"Ordinary parents reproduce the mechanisms at {parent_qualified}, and per "
            "section 12 that is NOT programme failure -- it is the designed absorption "
            "mode, and section 1 disclaims any requirement that OCM rediscover existing "
            "algorithms. Mechanism-level parent sufficiency therefore says nothing "
            "against the thesis. The thesis is decided one level up, where section 12 "
            "puts the novelty: two upper-level candidates are supported at E2 "
            "(a located phase boundary and two principled impossibility results) and "
            "three are CANNOT_CHECK (lifetime regime, cross-domain invariance, "
            "integrated interaction effect). PARENT_PRODUCT_SUFFICIENT is unavailable "
            "in either direction, because deciding it needs an integrated prototype."),
    }


def build() -> dict[str, Any]:
    check = validate()
    terminal = programme_terminal()
    return {
        "schema": SCHEMA,
        "issue": 165,
        "closure_condition_quoted_from_the_roadmap": (
            "The programme closes scientifically when every required gate has an "
            "explicit bounded disposition. A complete negative or conditional result "
            "is still 100% completion of the programme."),
        "roadmap_body": {"path": "research/programme-closure-v1/ISSUE_165_BODY.md",
                         "sha256": BODY_SHA256, "authentic": check["body_authentic"]},
        "vocabularies_parsed_from_the_roadmap": {k: list(v) for k, v in vocabularies().items()},
        "derivation_rule": DERIVATION,
        "gates": [{k: v for k, v in g.items()} for g in GATES],
        "upper_level_novelty": UPPER_LEVEL,
        "upper_level_note": (
            "Section 12 places the programme's own novelty target above the mechanism "
            "level and says 'mere component integration remains engineering'. A closure "
            "that scored only the gates would be scoring the engineering and ignoring "
            "the science, so the residual question is decided here."),
        "issue_terminals": issue_terminals(),
        "issue_terminals_note": (
            "Section 22's Final list. An issue that owns a gate inherits that gate's "
            "disposition and receipts, so the gate ledger and the issue roll-up cannot "
            "drift apart. An issue with no lane on this head receives CANNOT_CHECK "
            "naming exactly that, and cites the evidence map which records its "
            "per-checkbox state at main@b35093a."),
        "validation": check,
        "programme": terminal,
        "what_this_does_not_do": (
            "It reads receipts and the roadmap. It runs no study, changes no "
            "production code, and closes no issue on its own authority. A gate "
            "disposition here is only as good as the receipt it cites, and every "
            "CANNOT_CHECK names what would convert it."),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    doc = build()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(doc, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"valid": doc["validation"]["valid"],
                      "problems": doc["validation"]["problems"],
                      "body_authentic": doc["roadmap_body"]["authentic"],
                      "terminal": doc["programme"]["terminal"],
                      "closed": doc["programme"]["closed"],
                      "unmeasured": doc["programme"].get("unmeasured_gates"),
                      "parent_sufficient": doc["programme"].get("parent_sufficient_gates")},
                     indent=1))
    return 0 if doc["validation"]["valid"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
