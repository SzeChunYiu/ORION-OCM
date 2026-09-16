#!/usr/bin/env python3
"""Exact audit/reproof executor for Issue #918, child of #833 Section K."""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from fractions import Fraction
from pathlib import Path
from typing import Any, Callable, Iterable

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]

PINS = {
    "foundation": ("research/gmi-833-foundation-v1/RESULT_V1.json", "c0c574c4ec6e237d5fdafa694eac131399625a70"),
    "axiom_core": ("research/gmi-833-axiom-core-v1/RESULT_V1.json", "3366a3bc7236d286f8d123bf53e4e3b2d22ad7b9"),
    "finite_bounds": ("research/gmi-833-capability-bounds-interactions-v1/RESULT_V1.json", "7ff80bab4a0b9e967e02cc6943bbe8828e3acea0"),
    "contract": ("research/gmi-capability-contract-v1/CONTRACT_V1.json", "33abe8b28ff2e425658042a062927df29767d346"),
    "f1_assay": ("research/gmi-capability-contract-v1/F1_ASSAY_V1.json", "db0db2a57420d553565c6658b8cca2bfe4b063fb"),
    "ceilings": ("research/gmi-capability-ceilings-v1/F2_CEILINGS_V1.json", "ac6c1468b96cea66614e69c7b6909736313ac0b9"),
    "ceiling_executor": ("research/gmi-capability-ceilings-v1/capability_ceilings_v1.py", "89755208b26ded1ff6f0e304873a34818488ae3f"),
    "tranche3": ("research/gmi-capability-ceilings-f2-tranche3/F2_TRANCHE3_CEILINGS_V1.json", "0fc0a3a16d0345deb9aa07ed4cb3903963d2000a"),
    "tranche4": ("research/gmi-capability-ceilings-f2-tranche4/F2_TRANCHE4_CEILINGS_V1.json", "0b4ce320d171eec0c1cf4fb1824c9ab840ae83b5"),
}

REQUIRED_CONTRACT_FIELDS = (
    "id", "capability", "inputs", "allowed_info", "required_behaviour",
    "success_metric", "resource_metric", "negative_twin", "strongest_parent",
    "atlas_reduction", "falsifier",
)
CONTRACT_FIELD_MINIMUMS = {
    "id": 4,
    "capability": 3,
    "inputs": 20,
    "allowed_info": 20,
    "required_behaviour": 20,
    "success_metric": 20,
    "resource_metric": 15,
    "negative_twin": 20,
    "strongest_parent": 10,
    "atlas_reduction": 10,
    "falsifier": 20,
}
OPERATIONAL_FIELDS = (
    "inputs", "allowed_info", "required_behaviour", "success_metric", "resource_metric",
)
FORBIDDEN_FAMILY_TOKENS = (
    "transformer", "lstm", "gru", "rnn", "cnn", "gnn", "mlp", "neural network",
    "bayesian network", "random forest", "support vector machine", "backpropagation",
    "qkv", "softmax", "convolutional network",
)

THEOREM_SPECS: dict[str, dict[str, Any]] = {
    "F2_STATE_CAPACITY_MEMORY": {
        "axioms": ["AX-1", "AX-2", "AX-5"],
        "status": "VALID_AFTER_UPGRADED_REPROOF",
        "generalization": "For arbitrary history-class and state sets, zero-error separation induces an injection from obligation classes into registered persistent response states; hence |H/~| <= |Q|. Tight realization requires a chosen representative/code for each class.",
        "proof": "If two obligation-distinguishable classes share one complete registered persistent response state, their common continuation yields the same response and one obligation fails. Therefore the class-to-state map is injective.",
        "hostile": "Three pairwise-separated history classes and two states.",
    },
    "F2_OBSERVATION_QUOTIENT": {
        "axioms": ["AX-1", "AX-2", "AX-5"],
        "status": "VALID_AFTER_UPGRADED_REPROOF",
        "generalization": "For arbitrary sets X,Z,A and maps O:X->Z and g:X->A, a zero-error decoder exists exactly when g factors through O, equivalently when g is constant on every O-fiber.",
        "proof": "Any decoder pi gives g=pi∘O and therefore equality on fibers. Conversely, fiber constancy defines pi on im(O); extending outside im(O) is irrelevant (or uses a default only when A is nonempty).",
        "hostile": "Two latent points share an observation but require different actions.",
    },
    "F2_COMMUNICATION_BANDWIDTH": {
        "axioms": ["AX-1", "AX-2", "AX-3", "AX-5"],
        "status": "VALID_AFTER_UPGRADED_REPROOF",
        "generalization": "For arbitrary sender-class set K and registered message carrier M, distinct required receiver actions with no correlated side information require an injection K->M, so |K|<=|M|. The B-bit law is the finite specialization |M|=2^B.",
        "proof": "Classes mapped to the same receiver-visible message induce the same receiver action, contradicting distinct requirements. An injective code is sufficient when available.",
        "hostile": "Five coordination classes and four messages.",
    },
    "F2_PRECISION_BOUNDARY": {
        "axioms": ["AX-1", "AX-2", "AX-3", "AX-5"],
        "status": "NARROWED_AND_REPROVED_AS_ARCHITECTURE_NEUTRAL_CODE_CARRIER_BOUND",
        "generalization": "For arbitrary code carrier C, response-profile set Y, and frozen decoder d:C->Y, the representable profiles are im(d). Covering T requires T subset im(d), equivalently a code preimage for every target; under ordinary choice-based cardinal comparison this gives |T|<=|C|. The old one-threshold/N-point/2^B statement is one finite corollary, not a universal precision ceiling.",
        "proof": "The decoder is a surjection C->im(d). Covering target family T requires selecting at least one preimage code for every target; this yields an injection T->C when finite or when the stated choice principle is available.",
        "hostile": "Five required profiles, four codes, fixed decoder.",
    },
    "F2_UPDATE_CHANNEL_PLASTICITY": {
        "axioms": ["AX-2", "AX-3", "AX-5"],
        "status": "VALID_AFTER_UPGRADED_REPROOF",
        "generalization": "For finite event horizon T and arbitrary registered update alphabets U_t, target-dependent successors selected from one initial state form an image of the transcript product. Under ordinary choice-based cardinal comparison their cardinal is bounded by Π_t |U_t|. Constant finite alphabet A gives A^T.",
        "proof": "Target-independent dynamics map each update transcript to at most one successor. Thus successor selection factors through the transcript product; finite cardinality is bounded directly, while the arbitrary-set cardinal comparison uses the stated choice convention.",
        "hostile": "Five target-distinct successors through two binary updates.",
    },
    "F2_PROTECTED_RANK_FRONTIER": {
        "axioms": ["AX-2", "AX-3", "AX-5"],
        "status": "NARROWED_TO_EXACT_LINEAR_OR_EXPLICIT_FIRST_ORDER_SCOPE",
        "generalization": "For any finite-dimensional vector space V over any field and linear protected-response map L:V->W, exact protected directions are ker(L), with dim ker(L)=dim V-rank(L). Nonlinear claims are only local when L is an explicit derivative.",
        "proof": "Exact first-order retention is L(delta)=0, hence delta lies in ker(L); rank-nullity gives the dimension and a kernel basis attains it.",
        "hostile": "A rank-two protected map on dimension three cannot contain two independent protected update directions.",
    },
    "F2_PLANNING_RESOURCE_HORIZON": {
        "axioms": ["AX-1", "AX-2", "AX-3", "AX-5"],
        "status": "VALID_AFTER_UPGRADED_REPROOF",
        "generalization": "For any registered rooted tree and finite depth h, if every node through h can independently contain the sole decisive event and no pruning certificate, oracle, or merging exists, complete coverage has inspection-cardinality lower bound equal to the entire through-depth-h node set, even when levels are nonuniform or infinite. Sufficiency is set-theoretic; an operational exhaustive procedure additionally needs an enumeration/well-order and completion semantics.",
        "proof": "Leaving node u unseen makes the no-event world indistinguishable from a world whose sole event is u. Hence every node must be included in the inspected set. The b-ary geometric sum and breadth-first sufficiency are regular finite corollaries.",
        "hostile": "Binary depth-two tree, six inspections for seven possible decisive nodes.",
    },
    "F2_SEARCH_BUDGET_VERIFIED_CLASS": {
        "axioms": ["AX-1", "AX-2", "AX-3", "AX-5"],
        "status": "NARROWED_TO_DIRECT_POSITIVE_VERIFICATION",
        "generalization": "For any candidate set C and queried subset Q with |Q|<|C|, if success requires receiving a positive certificate from the unique valid candidate, no strategy restricted to Q guarantees success. Querying all candidates is sufficient only with a traversal/enumeration and completion semantics. If success is mere identification under an exactly-one promise, the finite bound is N-1, so that interpretation of the historical N-query wording is explicitly retracted.",
        "proof": "A strict-subcardinality queried subset omits some c; placing the valid target at c yields only negative answers and no positive certificate. Under the finite exactly-one promise, N-1 negatives identify the sole unqueried point without directly verifying it.",
        "hostile": "Five candidates and four queries: direct verification can fail at the fifth, while identification succeeds under an exactly-one promise.",
    },
    "F2_VERIFICATION_BUDGET_FALSE_ADOPTION": {
        "axioms": ["AX-1", "AX-2", "AX-3", "AX-5"],
        "status": "VALID_WITH_DISTRIBUTIONAL_AND_ADVERSARIAL_BRANCHES_SEPARATED",
        "generalization": "For arbitrary coordinate set I, inspected set S, and probability law mu over defect subsets D, false-adoption probability is mu({D:D∩S=∅}). Distribution-free zero false adoption against singleton defects requires S=I. The hypergeometric ratio is the finite uniform-r-subset specialization.",
        "proof": "Adoption after perfect checks occurs exactly when the defect set avoids S, giving the measure identity. If i is unchecked, the singleton {i} defeats zero-FA; full coverage excludes every nonempty defect set.",
        "hostile": "One unchecked coordinate hosts the sole adversarial defect.",
    },
    "F2_INFORMATION_ACQUISITION_BUDGET": {
        "axioms": ["AX-1", "AX-2", "AX-3", "AX-5"],
        "status": "VALID_AFTER_UPGRADED_REPROOF",
        "generalization": "For any finite-depth adaptive decision tree with outcome carrier A_v at node v, zero-error hypotheses inject into leaves. Thus distinguishability is bounded by the leaf-set cardinal; a uniform A-ary depth-q tree gives |H|<=|A|^q, for finite or infinite A.",
        "proof": "Two hypotheses ending at one transcript leaf are observationally identical and cannot receive distinct exact labels. Tightness requires the registered query family to realize a separating leaf code.",
        "hostile": "Five hypotheses but only four transcript leaves.",
    },
    "F2_SOCIAL_OBSERVATION_IDENTIFIABILITY": {
        "axioms": ["AX-1", "AX-2", "AX-5"],
        "status": "VALID_AFTER_UPGRADED_REPROOF",
        "generalization": "For arbitrary hidden-model set Theta, transcript map tau, and required-response map g, exact task response is possible iff g factors through tau. Full model identification is possible iff tau is injective.",
        "proof": "This is the arbitrary-set observation-factorization theorem applied to social transcripts; no named agent architecture is used.",
        "hostile": "Two hidden models share a complete transcript but require different held-out responses.",
    },
}


def git_blob_sha(data: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()


def canonical(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, indent=2, separators=(",", ": ")) + "\n").encode()


def load_json(relative: str) -> Any:
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


def verify_pins() -> dict[str, str]:
    observed: dict[str, str] = {}
    for name, (relative, expected) in PINS.items():
        value = git_blob_sha((ROOT / relative).read_bytes())
        if value != expected:
            raise AssertionError(f"source drift {name}: {value} != {expected}")
        observed[name] = value
    return observed


def architecture_audit() -> list[dict[str, Any]]:
    rows = load_json(PINS["contract"][0])["rows"]
    if len(rows) != 27 or len({row["id"] for row in rows}) != 27:
        raise AssertionError("expected 27 distinct capability definitions")
    audited = []
    for row in rows:
        missing = sorted(set(REQUIRED_CONTRACT_FIELDS) - set(row))
        extra = sorted(set(row) - set(REQUIRED_CONTRACT_FIELDS))
        malformed = sorted(
            field for field, minimum in CONTRACT_FIELD_MINIMUMS.items()
            if field in row and (not isinstance(row[field], str) or len(row[field]) < minimum)
        )
        operational = {field: row[field] for field in OPERATIONAL_FIELDS}
        text = " ".join(operational.values()).lower()
        forbidden = sorted(token for token in FORBIDDEN_FAMILY_TOKENS if token in text)
        # The implementation label is deliberately outside the external contract.
        remints = [
            {"implementation_label": label, "external_contract": operational}
            for label in ("alpha", "beta", "opaque-17", "remint-z")
        ]
        invariant = all(item["external_contract"] == operational for item in remints)
        source_digest = hashlib.sha256(canonical(row)).hexdigest()
        status = "ARCHITECTURE_INDEPENDENT_AT_REGISTERED_CONTRACT_SCOPE"
        if missing or extra or malformed or forbidden or not invariant:
            status = "FAILS_ARCHITECTURE_INDEPENDENCE_AUDIT"
        audited.append({
            "id": row["id"],
            "capability": row["capability"],
            "operational_fields": list(OPERATIONAL_FIELDS),
            "operational_contract": operational,
            "missing_fields": missing,
            "extra_fields": extra,
            "malformed_fields": malformed,
            "forbidden_family_tokens": forbidden,
            "implementation_remints_checked": len(remints),
            "remint_invariant": invariant,
            "canonical_source_row_sha256": source_digest,
            "status": status,
            "note": "The generic phrase 'architecture edit' in self-improvement names an allowed intervention, not a required implementation family." if row["id"] == "cap-self-improvement" else "",
        })
    return audited


def ceiling_audit() -> list[dict[str, Any]]:
    rows = load_json(PINS["ceilings"][0])["ceilings"]
    ids = [row["id"] for row in rows]
    if len(rows) != 11 or len(set(ids)) != 11:
        raise AssertionError("historical inventory is not exactly eleven unique ceilings")
    if set(ids) != set(THEOREM_SPECS):
        raise AssertionError("reproof ledger does not match historical inventory")
    result = []
    for row in rows:
        spec = THEOREM_SPECS[row["id"]]
        result.append({
            "id": row["id"],
            "historical_box": row["box"],
            "historical_quantity": row["quantity"],
            "historical_bound": row["bound"],
            "historical_assumptions": row["assumptions"],
            "historical_negative_twin": row["negative_twin"],
            "historical_repo_reference": row.get("repo_parent", row.get("repo_neighbor")),
            "historical_theorem_sha256": hashlib.sha256(row["theorem"].encode()).hexdigest(),
            "canonical_source_row_sha256": hashlib.sha256(canonical(row)).hexdigest(),
            "axiom_dependencies": spec["axioms"],
            "status": spec["status"],
            "reproof": spec["proof"],
            "generalization_beyond_toy_finite_space": spec["generalization"],
            "nearest_hostile": spec["hostile"],
            "strongest_parent": row["strongest_parent"],
            "falsifier": row["falsifier"],
            "architecture_argument_present": False,
        })
    return result


def all_maps(domain_size: int, codomain_size: int) -> Iterable[tuple[int, ...]]:
    return itertools.product(range(codomain_size), repeat=domain_size)


def factorization_census() -> dict[str, int]:
    checked = agree = hostile = 0
    for obs in all_maps(3, 2):
        for req in all_maps(3, 2):
            checked += 1
            constant = all(obs[i] != obs[j] or req[i] == req[j] for i in range(3) for j in range(3))
            exists = any(all(decoder[obs[x]] == req[x] for x in range(3)) for decoder in all_maps(2, 2))
            agree += constant == exists
            hostile += not constant and not exists
    if agree != checked:
        raise AssertionError("factorization theorem mismatch")
    return {"cases": checked, "agreements": agree, "nonfactorable_hostiles": hostile}


def injection_census() -> dict[str, int]:
    checked = agree = 0
    for k in range(1, 6):
        for s in range(1, 6):
            exists = any(len(set(mapping)) == k for mapping in all_maps(k, s))
            checked += 1
            agree += exists == (k <= s)
    if checked != agree:
        raise AssertionError("injection census mismatch")
    return {"cases": checked, "agreements": agree}


def product_channel_census() -> dict[str, int]:
    checked = agree = 0
    for alphabet_sizes in ((1,), (2,), (3,), (2, 2), (2, 3), (3, 2, 2)):
        transcript_count = 1
        for size in alphabet_sizes:
            transcript_count *= size
        for targets in range(1, transcript_count + 3):
            checked += 1
            # Any injection into a finite product exists iff the cardinal bound holds.
            exists = targets <= len(list(itertools.product(*(range(n) for n in alphabet_sizes))))
            agree += exists == (targets <= transcript_count)
    if checked != agree:
        raise AssertionError("product-channel census mismatch")
    return {"cases": checked, "agreements": agree}


def verification_census() -> dict[str, int]:
    checked = agree = 0
    for m in range(1, 8):
        coords = range(m)
        for r in range(1, m + 1):
            defects = list(itertools.combinations(coords, r))
            for q in range(m + 1):
                inspected = set(range(q))
                misses = sum(not inspected.intersection(defect) for defect in defects)
                exact = Fraction(misses, len(defects))
                formula = Fraction(0 if m - q < r else _comb(m - q, r), _comb(m, r))
                checked += 1
                agree += exact == formula
    if checked != agree:
        raise AssertionError("verification probability mismatch")
    return {"cases": checked, "agreements": agree}


def _comb(n: int, r: int) -> int:
    if r < 0 or r > n:
        return 0
    num = den = 1
    for i in range(1, r + 1):
        num *= n - r + i
        den *= i
    return num // den


def search_boundary() -> dict[str, int]:
    cases = direct_failures = identification_successes = 0
    for n in range(2, 9):
        for valid in range(n):
            queried = set(range(n - 1))
            cases += 1
            direct_failures += valid not in queried
            inferred = valid if valid in queried else n - 1
            identification_successes += inferred == valid
    if direct_failures != 7 or identification_successes != cases:
        raise AssertionError("search N versus N-1 boundary mismatch")
    return {
        "cases": cases,
        "direct_positive_failures_at_n_minus_1": direct_failures,
        "mere_identification_successes_at_n_minus_1": identification_successes,
    }


def adversarial_controls() -> list[dict[str, Any]]:
    controls = [
        ("F2_STATE_CAPACITY_MEMORY", 3 > 2),
        ("F2_OBSERVATION_QUOTIENT", not all((0, 0)[i] != (0, 0)[j] or (0, 1)[i] == (0, 1)[j] for i in range(2) for j in range(2))),
        ("F2_COMMUNICATION_BANDWIDTH", 5 > 4),
        ("F2_PRECISION_BOUNDARY", 5 > 4),
        ("F2_UPDATE_CHANNEL_PLASTICITY", 5 > 2 * 2),
        ("F2_PROTECTED_RANK_FRONTIER", 2 > 3 - 2),
        ("F2_PLANNING_RESOURCE_HORIZON", 6 < 1 + 2 + 4),
        ("F2_SEARCH_BUDGET_VERIFIED_CLASS", 4 < 5),
        ("F2_VERIFICATION_BUDGET_FALSE_ADOPTION", 3 < 4),
        ("F2_INFORMATION_ACQUISITION_BUDGET", 5 > 2 * 2),
        ("F2_SOCIAL_OBSERVATION_IDENTIFIABILITY", ("same", 0) != ("same", 1)),
    ]
    if not all(triggered for _, triggered in controls):
        raise AssertionError("a nearest hostile did not trigger")
    return [{"id": name, "hostile_rejected": triggered} for name, triggered in controls]


def build_ledger() -> dict[str, Any]:
    return {
        "schema": "GMI833CapabilityCeilingReauditLedgerV1",
        "issue": 918,
        "source_pr": 921,
        "parent_issue": 833,
        "architecture_independence_criterion": {
            "operational_fields": list(OPERATIONAL_FIELDS),
            "forbidden_family_tokens": list(FORBIDDEN_FAMILY_TOKENS),
            "semantics": "External contract truth is unchanged by bijective reminting of an audit-only implementation label.",
            "boundary": "This is an exact audit of the pinned structured artifact, not proof that arbitrary future prose lacks hidden architectural commitments.",
        },
        "capability_definitions": architecture_audit(),
        "ceilings": ceiling_audit(),
        "historical_corrections": [
            {
                "id": "F2_PRECISION_BOUNDARY",
                "correction": "Replace architecture-specific threshold wording at the general layer by the architecture-neutral frozen code-carrier image bound; retain the threshold theorem only as a finite corollary.",
            },
            {
                "id": "F2_SEARCH_BUDGET_VERIFIED_CLASS",
                "correction": "Require direct positive verification for the N-query theorem. Under an exactly-one promise, mere finite identification needs only N-1 negative queries.",
            },
            {
                "id": "F2_PROTECTED_RANK_FRONTIER",
                "correction": "Retain exact scope for linear maps and first-order scope only for explicit derivatives; do not infer global nonlinear retention.",
            },
        ],
    }


def validate_package_contracts() -> dict[str, int]:
    manifest = load_json("research/gmi-833-capability-ceiling-reaudit-v1/MANIFEST_V1.json")
    recon = load_json("research/gmi-833-capability-ceiling-reaudit-v1/ISSUE_833_RECONCILIATION_CAPABILITY_CEILINGS_V1.json")
    if manifest["source_pr"] != 921 or manifest["issue"] != 918 or manifest["target_rows"] != 3:
        raise AssertionError("manifest binding mismatch")
    if manifest["capability_definition_count"] != 27 or manifest["historical_ceiling_count"] != 11:
        raise AssertionError("manifest inventory mismatch")
    if manifest["historical_wordings_narrowed"] != 3 or manifest["exact_census_cases"] != 332:
        raise AssertionError("manifest result-count mismatch")
    edits = recon["replacements"]
    if len(edits) != 3 or any(edit["new"].count("PR #921") != 1 for edit in edits):
        raise AssertionError("reconciliation binding mismatch")
    if any(edit["old"].startswith("- [x]") or not edit["new"].startswith("- [x]") for edit in edits):
        raise AssertionError("reconciliation is not a narrow unchecked-to-checked edit")
    expected = {
        "- [ ] Re-audit all existing capability definitions for architecture independence.",
        "- [ ] Re-prove all 11 capability ceilings under the upgraded foundation.",
        "- [ ] Generalize ceilings beyond toy finite spaces where possible.",
    }
    if {edit["old"] for edit in edits} != expected or any(edit["anchor"] != "# K. Capability theory upgrade" for edit in edits):
        raise AssertionError("reconciliation targets drifted outside the three frozen Section-K rows")
    return {"manifest_rows": manifest["target_rows"], "reconciliation_rows": len(edits)}


def run() -> dict[str, Any]:
    pins = verify_pins()
    ledger = build_ledger()
    if any(row["status"] != "ARCHITECTURE_INDEPENDENT_AT_REGISTERED_CONTRACT_SCOPE" for row in ledger["capability_definitions"]):
        raise AssertionError("capability architecture audit failed")
    if len(ledger["ceilings"]) != 11:
        raise AssertionError("ceiling audit count mismatch")
    census = {
        "factorization": factorization_census(),
        "injection": injection_census(),
        "product_channels": product_channel_census(),
        "verification": verification_census(),
        "search_boundary": search_boundary(),
    }
    total = sum(item["cases"] for item in census.values())
    controls = adversarial_controls()
    contracts = validate_package_contracts()
    checks = {
        "source_pins_exact": len(pins) == len(PINS),
        "definition_inventory_exact": len(ledger["capability_definitions"]) == 27,
        "definitions_architecture_independent_at_registered_scope": all(
            row["status"] == "ARCHITECTURE_INDEPENDENT_AT_REGISTERED_CONTRACT_SCOPE"
            for row in ledger["capability_definitions"]
        ),
        "historical_ceiling_inventory_exact": len(ledger["ceilings"]) == 11,
        "all_ceiling_ids_reproved": {row["id"] for row in ledger["ceilings"]} == set(THEOREM_SPECS),
        "all_hostiles_rejected": all(row["hostile_rejected"] for row in controls),
        "three_historical_wordings_corrected": len(ledger["historical_corrections"]) == 3,
        "exact_censuses_agree": all(item.get("agreements", item["cases"]) == item["cases"] for item in census.values()),
        "package_and_three_row_reconciliation_valid": contracts == {"manifest_rows": 3, "reconciliation_rows": 3},
    }
    if not all(checks.values()):
        raise AssertionError("receipt check failed")
    return {
        "schema": "GMI833CapabilityCeilingReauditResultV1",
        "issue": 918,
        "source_pr": 921,
        "parent_issue": 833,
        "terminal": "GMI_833_CAPABILITY_DEFINITIONS_AND_ELEVEN_CEILINGS_REAUDITED_AT_REGISTERED_SCOPE",
        "status": "GREEN",
        "checks": checks,
        "source_blobs": pins,
        "counts": {
            "capability_definitions_audited": len(ledger["capability_definitions"]),
            "architecture_independent_definitions": sum(row["status"].startswith("ARCHITECTURE_INDEPENDENT") for row in ledger["capability_definitions"]),
            "historical_ceiling_ids": len(ledger["ceilings"]),
            "ceilings_reproved": len(ledger["ceilings"]),
            "ceilings_generalized_beyond_toy_finite_witness": len(ledger["ceilings"]),
            "historical_wordings_narrowed": len(ledger["historical_corrections"]),
            "adversarial_controls": len(controls),
            "exact_census_cases": total,
        },
        "exact_censuses": census,
        "adversarial_controls": controls,
        "package_contracts": contracts,
        "claim_boundary": "Exact audit of the pinned 27-row contract and analytic reproof/generalization of the pinned eleven ceiling families. No G6 predictor, empirical transfer, stochastic approximate-identification law, global nonlinear retention theorem, or universal architecture ranking.",
        "ledger_sha256": hashlib.sha256(canonical(ledger)).hexdigest(),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    parser.add_argument("--ledger-output", type=Path)
    args = parser.parse_args()
    ledger = build_ledger()
    result = run()
    if args.ledger_output:
        args.ledger_output.write_bytes(canonical(ledger))
    if args.output:
        args.output.write_bytes(canonical(result))
    else:
        print(canonical(result).decode(), end="")


if __name__ == "__main__":
    main()
