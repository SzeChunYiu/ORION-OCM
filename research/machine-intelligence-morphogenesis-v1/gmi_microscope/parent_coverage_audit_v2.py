"""Section Q V2: explicit whole-GMI parent coverage after source-backed extension.

V1 measured the historical canonical parent-absorption ledger and found 7 solid,
3 suspect and 13 uncovered traditions. V2 preserves that receipt as the baseline
and asks a narrower, attributable question: does the source-backed extension add
one explicit record for each of the 13 absent and 3 suspect traditions?

Unlike V1, extension coverage is NOT inferred from substring matches. Every
extension entry carries an exact ``section_q_traditions`` field, so adding a
parent cannot accidentally make another tradition green because an author name
contains a token (for example ``Levin`` inside ``Levine``).

Coverage is not adequacy and is never ALL_RELEVANT_PARENTS_KNOWN.
All validation uses explicit checks rather than ``assert`` so optimized Python
cannot remove the fail-closed gates.
"""

from __future__ import annotations

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
MIM = HERE.parent
RESULTS = MIM / "microscopes" / "results"

TRADITIONS = [
    "Universal computation / lambda / register machines",
    "Solomonoff / MDL / algorithmic probability",
    "Levin / OOPS / PowerPlay / Goedel machines",
    "AIXI / universal intelligence",
    "NFL / bounded rationality / rational metareasoning",
    "AutoML-Zero / NAS / NEAT / evolutionary computation",
    "MAML / learned optimizers / meta-RL",
    "DreamCoder / Stitch / program synthesis / GP",
    "Bayesian inference / probabilistic programming / BPL",
    "Categorical / compositional learning theory",
    "ACT-R / Soar / NARS / OpenCog / cognitive architectures",
    "RL / hierarchical RL / model-based planning",
    "Active inference / predictive processing",
    "Causal inference / SCM / active causal learning",
    "Memory systems / CLS / continual learning",
    "RAG / databases / caches / model editing",
    "MoE / modular continual learning",
    "Neuro-symbolic systems",
    "GNN / message passing / CSP / SAT / factor graphs",
    "Hyperdimensional / vector-symbolic computing",
    "Neural cellular automata / morphogenetic computation",
    "Evolutionary / open-ended artificial-life systems",
    "Analog / physical / quantum computation",
]


def fail(message: str) -> "None":
    raise SystemExit(f"PARENT_COVERAGE_V2_FAIL: {message}")


def require(condition: bool, message: str) -> None:
    if not condition:
        fail(message)


def find_repo_root(start: Path) -> Path:
    d = start
    for _ in range(10):
        if (d / "research" / "parent-absorption-v1" / "LEDGER.json").exists():
            return d
        if d.parent == d:
            break
        d = d.parent
    fail("repository root with parent-absorption ledger not found")


def load(path: Path):
    try:
        with path.open("r", encoding="utf-8") as fh:
            return json.load(fh)
    except (OSError, json.JSONDecodeError) as exc:
        fail(f"cannot load {path}: {exc}")


def main() -> None:
    root = find_repo_root(HERE)
    base_ledger_path = root / "research" / "parent-absorption-v1" / "LEDGER.json"
    extension_path = root / "research" / "parent-absorption-v1" / "GMI_602_PARENT_EXTENSION_V1.json"
    v1_receipt_path = RESULTS / "STAGE_PARENT_COVERAGE_V1.json"
    out_path = RESULTS / "STAGE_PARENT_COVERAGE_V2.json"

    base_ledger = load(base_ledger_path)
    extension = load(extension_path)
    v1 = load(v1_receipt_path)

    require(base_ledger.get("schema") == "ocm.parent-absorption.ledger.v1", "unexpected base-ledger schema")
    require(extension.get("schema") == "ocm.parent-absorption.ledger-extension.v1", "unexpected extension schema")
    require(extension.get("issue") == 602 and extension.get("section") == "Q", "extension is not scoped to #602 Section Q")
    require(v1.get("traditions_total") == len(TRADITIONS) == 23, "V1 tradition inventory drifted")
    require(v1.get("traditions_covered_solid") == 7, "V1 solid count is no longer the historical 7")
    require(v1.get("traditions_covered_suspect") == 3, "V1 suspect count is no longer the historical 3")
    require(v1.get("traditions_uncovered") == 13, "V1 uncovered count is no longer the historical 13")

    known = set(TRADITIONS)
    try:
        base_suspects = set(v1["suspect_traditions"])
        base_solid = set(v1["covered"]) - base_suspects
        base_uncovered = set(v1["uncovered"])
    except (KeyError, TypeError) as exc:
        fail(f"malformed V1 receipt: {exc}")
    require(len(base_solid) == 7 and len(base_suspects) == 3 and len(base_uncovered) == 13, "V1 7/3/13 partition drifted")
    require(base_solid | base_suspects | base_uncovered == known, "V1 partition does not equal the registered 23 traditions")
    require(not (base_solid & base_suspects), "V1 solid/suspect overlap")
    require(not (base_solid & base_uncovered), "V1 solid/uncovered overlap")
    require(not (base_suspects & base_uncovered), "V1 suspect/uncovered overlap")

    entries = extension.get("entries")
    require(isinstance(entries, list), "extension entries must be a list")
    ids = [e.get("id") for e in entries if isinstance(e, dict)]
    require(len(ids) == len(entries), "every extension entry must be an object with an id")
    require(all(isinstance(x, str) and x for x in ids), "extension ids must be nonempty strings")
    require(len(ids) == len(set(ids)), "extension parent IDs are not unique")
    require(len(entries) == 16, "V2 must contain exactly the 13-absent + 3-suspect extension")

    by_tradition: dict[str, str] = {}
    dispositions: set[str] = set()
    for entry in entries:
        entry_id = entry["id"]
        rows = entry.get("section_q_traditions")
        require(isinstance(rows, list) and len(rows) == 1, f"{entry_id}: must explicitly own exactly one Q tradition")
        tradition = rows[0]
        require(isinstance(tradition, str) and tradition in known, f"{entry_id}: unknown Section-Q tradition {tradition!r}")
        require(tradition not in by_tradition, f"duplicate extension owner for {tradition}")
        by_tradition[tradition] = entry_id

        parents = entry.get("parents")
        require(isinstance(parents, list) and parents, f"{entry_id}: no cited parents")
        for parent in parents:
            require(isinstance(parent, dict), f"{entry_id}: parent citation row is not an object")
            require(bool(parent.get("name")) and bool(parent.get("citation")), f"{entry_id}: parent must have name and citation")
        for field in (
            "what_parent_explained",
            "disposition",
            "disposition_detail",
            "prior_information_added",
            "higher_order_question_remaining",
            "programme_status",
            "parent_sufficient_at_scope",
            "sources",
        ):
            require(entry.get(field) not in (None, "", []), f"{entry_id}: missing {field}")
        dispositions.add(entry["disposition"])

    extension_coverage = set(by_tradition)
    require(
        extension_coverage == base_suspects | base_uncovered,
        "extension must cover exactly the 3 V1 suspects plus the 13 V1 absences; existing V1 solid rows must not be duplicated",
    )
    require(len(dispositions) >= 2, "parent subtraction collapsed to one disposition")

    final_solid = base_solid | extension_coverage
    uncovered = known - final_solid
    require(final_solid == known and not uncovered, "registered Section-Q coverage is not 23/23")

    claim_boundary = extension.get("claim_boundary", {})
    require(claim_boundary.get("coverage_is_adequacy") is False, "extension promoted coverage to adequacy")
    require(claim_boundary.get("all_relevant_parents_known") is False, "extension claimed universal parent completeness")
    require(claim_boundary.get("mechanism_rediscovery_is_novelty") is False, "extension promoted mechanism rediscovery to novelty")

    receipt = {
        "schema": "GMI_PARENT_COVERAGE_V2",
        "corpus_audit": True,
        "scope": (
            "registered #602 Section-Q coverage only; an explicit source-backed entry exists "
            "for every named tradition. Coverage is not adequacy and does not imply that all "
            "relevant parents in the open literature are known"
        ),
        "base_ledger_path": "research/parent-absorption-v1/LEDGER.json",
        "extension_ledger_path": "research/parent-absorption-v1/GMI_602_PARENT_EXTENSION_V1.json",
        "base_audit_receipt": "research/machine-intelligence-morphogenesis-v1/microscopes/results/STAGE_PARENT_COVERAGE_V1.json",
        "traditions_total": len(TRADITIONS),
        "v1_base_solid": len(base_solid),
        "v1_base_suspect": len(base_suspects),
        "v1_base_uncovered": len(base_uncovered),
        "extension_entries": len(entries),
        "extension_explicit_traditions": len(extension_coverage),
        "resolved_v1_suspects": sorted(base_suspects),
        "newly_covered_v1_absences": sorted(base_uncovered),
        "extension_entry_by_tradition": {k: by_tradition[k] for k in sorted(by_tradition)},
        "traditions_covered_solid": len(final_solid),
        "traditions_uncovered": len(uncovered),
        "uncovered": sorted(uncovered),
        "extension_dispositions": sorted(dispositions),
        "v1_promiscuous_entries_retained_as_historical_signal": v1.get("promiscuous_entries", []),
        "coverage_is_adequacy": False,
        "all_relevant_parents_known": False,
        "mechanism_rediscovery_is_novelty": False,
        "terminal": "PARENT_COVERAGE_SATURATED_AT_REGISTERED_602_SECTION_Q_SCOPE",
    }

    RESULTS.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(receipt, indent=1, sort_keys=True) + "\n", encoding="utf-8")

    print("GMI_PARENT_COVERAGE_V2_VALID")
    print(f"base={len(base_solid)}/23 solid, {len(base_suspects)} suspect, {len(base_uncovered)} absent")
    print(f"extension={len(extension_coverage)} explicit records")
    print(f"final={len(final_solid)}/23 registered-scope coverage")
    print("coverage_is_adequacy=false")
    print("all_relevant_parents_known=false")


if __name__ == "__main__":
    main()
