#!/usr/bin/env python3
"""Generate FREEZE_V1.json for the EB-F0 biosphere formal contract.

Not result-generating code: it hashes files and writes a manifest. It is run
BEFORE any theorem or experiment code, per section 15 of issue #296.

The manifest follows the amendment discipline enforced by
research/hsg-semantic-execution-v1/verify_freeze_chain.py: a file's
authoritative hash is the one in the NEWEST amendment that names it, falling
back to the base manifest. Amendments are numbered and recorded, never silent
edits. `prior_manifest_sha256_observed` records files this freeze asserts it
did not author and did not touch.
"""
import hashlib, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))

BASE_FILES = [
    "DEFINITIONS.md",
    "WORLD_STATE_AND_DYNAMICS_V1.json",
    "COGNITIVE_UNIT_CONTRACT_V1.json",
    "INHERITANCE_SOCIAL_CHANNELS_V1.json",
    "COARSE_GRAINING_INDIVIDUALITY_V1.json",
    "ASSAY_TRANSFER_CONTRACT_V1.json",
    "THEOREM_REGISTRY_V1.json",
    "HOSTILE_REGISTRY_V1.json",
    "EXACT_WORLD_REGISTRY_V1.json",
    "PARENT_LEDGER.md",
]
AMEND_1_FILES = [
    "WORLD_STATE_AND_DYNAMICS_V1_AMEND_1.json",
    "HOSTILE_REGISTRY_V1_AMEND_1.json",
    "NONINTERFERENCE_CHECK_SPEC_V1.json",
    "PARENT_LEDGER_MODULE_BINDING_V1.md",
    "check_noninterference.py",
    "THEOREM_REGISTRY_V1_AMEND_1.json",
]
# Tooling is deliberately NOT in the manifest. Verified against the HSG lane:
# research/hsg-semantic-execution-v1/FREEZE_V1.json names 5 content files and
# excludes verify_freeze_chain.py, selftest_freeze_chain.py and its make_freeze*.py.
# Freezing a generator makes the generator's next edit report as drift on itself,
# which is exactly the false positive the resolution rule exists to avoid.
SUPPORT_FILES = ["README.md", "DUPLICATION_GUARD_V1.json"]
TOOLING_EXCLUDED_FROM_MANIFEST = [
    "make_freeze.py", "verify_freeze_chain.py", "selftest_freeze_chain.py",
]

# Modules this freeze BINDS to and asserts it did not touch.
PRIOR = [
    "research/ocm-form-oracle-v1/oracle/c_immutability.py",
    "research/ocm-form-oracle-v1/oracle/d27_lineage.py",
    "research/ocm-form-oracle-v1/oracle/evolvability.py",
    "research/ocm-form-oracle-v1/oracle/future_family.py",
    "research/ocm-form-oracle-v1/oracle/burden.py",
    "research/ocm-form-oracle-v1/oracle/behaviour_sig.py",
    "research/ocm-form-oracle-v1/oracle/d26_adapters.py",
    "research/ocm-form-oracle-v1/oracle/d26_operators.py",
    "research/ocm-form-oracle-v1/oracle/objectives4.py",
    "research/hsg-semantic-execution-v1/verify_freeze_chain.py",
]


def sha256(path):
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def manifest(names, root):
    out, missing = {}, []
    for n in names:
        p = os.path.join(root, n)
        if not os.path.exists(p):
            missing.append(n)
        else:
            out[n] = sha256(p)
    return out, missing


def main():
    base, m1 = manifest(BASE_FILES + SUPPORT_FILES, HERE)
    am1, m2 = manifest(AMEND_1_FILES, HERE)
    prior, m3 = manifest(PRIOR, REPO)
    missing = m1 + m2 + m3
    if missing:
        print("CANNOT_FREEZE missing: %s" % missing, file=sys.stderr)
        return 3

    doc = {
        "schema": "BIOSPHERE_EBF0_FREEZE_V1",
        "owner_issue": 296,
        "gates_issue": 292,
        "role": "FORMAL_PRECONDITION_NOT_A_COGNITIVE_CORE",
        "contains_results": False,
        "frozen_before_result_generating_code": True,
        "top_rule": ("Formalize what is invariant and what counts as evidence; do not "
                     "formalize the empirical answer. The biosphere must remain free to "
                     "reveal that intelligence is individual, collective, cultural, "
                     "ecology-specific, plural, unstable, or absent."),
        "outcome_neutral": True,
        "open_ended_forbidden_terminal": True,
        "long_earths_refused_until": "EB-F0 GATE_HOLDS",
        "resolution_rule": ("A file's authoritative hash is the one in the NEWEST amendment "
                           "that names it, falling back to this base manifest. Comparing the "
                           "base manifest against a live tree reports FALSE drift on any file "
                           "carrying a legitimate recorded amendment."),
        "supersession_rule": ("Amendments are numbered and recorded, never silent edits. An "
                             "unrecorded change is drift and is reported as such."),
        "manifest_sha256": base,
        "amendments": [
            {
                "id": 1,
                "title": "Kernel reads, observer-side assay kernel, implementable noninterference predicate, hostile no-alarm controls, module binding ledger",
                "reason": ("The base kernel declarations carried writes but not reads, so the "
                           "section 3 ancestor closure had no incoming edges and returned a "
                           "VACUOUS PASS for every world. The protected assay names were also "
                           "absent from the state vocabulary entirely, a second vacuous pass "
                           "found by running the checker rather than by reading the contract. "
                           "The base hostile registry recorded alarms without the clean controls "
                           "that prove the instruments discriminate."),
                "manifest_sha256": am1,
            }
        ],
        "prior_manifest_sha256_observed": prior,
        "prior_manifest_note": ("Modules this freeze BINDS to and asserts it did not author and "
                               "did not touch. See PARENT_LEDGER_MODULE_BINDING_V1.md. Another "
                               "lane may legitimately amend one of these, but only if some freeze "
                               "in ITS OWN directory records that amendment."),
        "closure_conditions_section_17": {
            "1_objects_frozen": "SATISFIED",
            "2_noninterference_machine_checkable": "SATISFIED_FOR_DECLARED_GRAPH__RUN_BINDING_OPEN",
            "3_unit_analysis_outcome_neutral": "SATISFIED",
            "4_resource_matching_and_knockout_frozen": "SATISFIED_FOR_OBJECT_KNOCKOUT__CHANNEL_KNOCKOUT_OPEN",
            "5_evidence_bridge_explicit_non_circular": "SATISFIED",
            "6_theorem_registry_parents_assumptions_falsifiers": "OPEN__3_OF_15_ROWS_LACK_WEAKENINGS",
            "7_hostiles_demonstrate_instruments_can_fail": "OPEN__6_OF_15_ROWS_UNPAIRED",
            "8_claim_ceilings_cannot_silently_become_general_intelligence": "SATISFIED",
        },
        "tooling_excluded_from_manifest": TOOLING_EXCLUDED_FROM_MANIFEST,
        "tooling_exclusion_reason": ("Checkers and generators are not frozen content. Freezing a generator makes its next edit report as drift on itself. Verified against research/hsg-semantic-execution-v1/FREEZE_V1.json, which excludes the same three roles."),
        "verified_by": "verify_freeze_chain.py in this directory, gated by .github/workflows/biosphere-ebf0.yml",
        "GATE_HOLDS": False,
        "gate_holds_reason": ("Conditions 2, 4, 6 and 7 are not fully closed. This freeze records "
                             "the contract; it does not assert the gate. #292 EB-2..EB-8 remain "
                             "refused."),
    }
    p = os.path.join(HERE, "FREEZE_V1.json")
    with open(p, "w") as fh:
        json.dump(doc, fh, indent=2, sort_keys=True)
        fh.write("\n")
    print(json.dumps({"freeze_sha256": sha256(p),
                      "n_base": len(base), "n_amend_1": len(am1), "n_prior": len(prior)},
                     indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
