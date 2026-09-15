"""Per-cell audit: which of the 159 K4 THEORY_RED cells target a substitution.

Items 22 / 23 / 35 clause (a). Reads AUDIT_INPUT_V1.json (property vectors from
the LOFO freeze) and classifies each cell under a decidable predicate. Does not
mutate frozen V4/V7 bytes or rewrite frozen verdicts.
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
MIM = REPO / "research" / "machine-intelligence-morphogenesis-v1"
INPUT_PATH = HERE / "AUDIT_INPUT_V1.json"
RECEIPT_PATH = HERE / "RECEIPT_V1.json"

SCHEMA = "GMIK4SubstitutionCellAuditReceiptV1"
AUDIT_ID = "GMI_K4_SUBSTITUTION_CELL_AUDIT_V2"

# Pins: fail closed if this audit is used as cover for mutating frozen bytes.
FROZEN_PINS = {
    "gmi_k4_resource_native_v4.py": (
        "1e29c745c61c95e73da696dbc190bf4035f8b2ac9b3255cbf29dd6ad285c87c1"
    ),
    "gmi_k4_search_v4.py": (
        "d8aaac3707983553a810c574c66855a24d2316aa5e3a25bdb8840b54c201bc24"
    ),
    "GMI_K4_LOFO_FREEZE_V1.json": (
        "83cd6a006fa53c1c56fbbf8d2c9243018c3c291037e400d2df693f7d0f668153"
    ),
    "GMI_K4_MEASURED_RESOURCE_SUCCESSOR_FREEZE_V4.json": (
        "d0196684f99838143a40bc3b5e2b9ecc136d0e7d743268cd6dc4510c412cfd32"
    ),
    "GMI_K4_EXECUTION_FREEZE_V7.json": (
        "e0d138482636aaa7277cfa057fe9382cd0bd6fe83df5037771e82e689b380ec0"
    ),
    "gmi_k4_substitution_repair_v1.py": (
        "6efe125face8fb368b8d27560a6836ab5fc3bd96616571e786f32e86cfb4ed2f"
    ),
}

# Context axes that turn a compressed state into a per-use serve cost.
_CONTEXT_AXES = (
    "length",
    "positions",
    "rounds",
    "window",
    "n_edges",
)

# Root-cause substitution kinds (GMI_K4_COST_STRUCTURE_ROOT_CAUSE_V1.md).
SUBSTITUTION_KINDS = (
    "retention_caching",
    "external_authority",
    "amortisation",
    "parameter_sharing",
    "sparsity_specialisation",
    "latent_compression",
)


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def assert_frozen_untouched() -> dict:
    """Fail closed if frozen V4/V7 / repair overlay bytes moved."""
    out = {}
    for name, expected in FROZEN_PINS.items():
        path = MIM / name
        got = sha256_file(path)
        ok = got == expected
        out[name] = {"expected": expected, "got": got, "ok": ok}
        if not ok:
            raise AssertionError(
                "frozen/repair pin drift for %s: expected %s got %s" % (name, expected, got)
            )
    return out


def load_input(path: Path = INPUT_PATH) -> dict:
    obj = json.loads(path.read_text())
    if obj.get("schema") != "GMIK4SubstitutionCellAuditInputV1":
        raise ValueError("unexpected audit input schema: %r" % (obj.get("schema"),))
    cells = obj.get("cells")
    if not isinstance(cells, list) or len(cells) != 159:
        raise ValueError(
            "expected exactly 159 cells, got %s"
            % (len(cells) if isinstance(cells, list) else type(cells))
        )
    return obj


def _tokens(scale: str) -> set:
    return {t for t in str(scale).split("_") if t}


def _serve_has_context(serve: str) -> bool:
    return any(axis in serve for axis in _CONTEXT_AXES)


def _amortises(pv: dict) -> bool:
    """State is a compressed / shared index; serve multiplies it by a context axis.

    Detectable when state_scales_with != serve_scales_with and serve names a
    context axis (length / positions / rounds / window / edges / steps), while
    the state axis is not itself that full context product.
    """
    state = str(pv["state_scales_with"])
    serve = str(pv["serve_scales_with"])
    if state == serve:
        return False
    if not _serve_has_context(serve):
        return False
    state_toks = _tokens(state)
    # Amortisation: serve grows with a context axis beyond the state axis.
    if any(axis in serve and axis not in state_toks for axis in _CONTEXT_AXES):
        return True
    # Or serve literally embeds the state token then multiplies.
    if state in serve and state != serve:
        return True
    return False


def _parameter_sharing(pv: dict) -> bool:
    """Shared parameters reused across a context axis (specialisation / tying)."""
    if pv.get("sharing") != "shared":
        return False
    state = str(pv["state_scales_with"])
    serve = str(pv["serve_scales_with"])
    if state == serve:
        return False
    return _serve_has_context(serve)


def substitution_hits(pv: dict) -> list:
    """Return ordered (kind, reason) hits for a LOFO property vector."""
    hits = []
    retrieval = pv.get("retrieval", "none")
    if retrieval != "none":
        hits.append(
            (
                "retention_caching",
                "property_vector.retrieval=%r: morphology consults retained store "
                "(retention/caching substitution)" % (retrieval,),
            )
        )
    if pv.get("external_authority") is True:
        hits.append(
            (
                "external_authority",
                "property_vector.external_authority=True: corpus storage substitutes "
                "for internalized parameters",
            )
        )
    if _amortises(pv):
        hits.append(
            (
                "amortisation",
                "state_scales_with=%r vs serve_scales_with=%r: compressed state "
                "amortised over a context axis"
                % (pv.get("state_scales_with"), pv.get("serve_scales_with")),
            )
        )
    if _parameter_sharing(pv):
        hits.append(
            (
                "parameter_sharing",
                "sharing=shared with serve context axis: parameter tying / "
                "specialisation substitution",
            )
        )
    serve = str(pv.get("serve_scales_with", ""))
    if "window" in serve:
        hits.append(
            (
                "sparsity_specialisation",
                "serve_scales_with contains window: sparse/local mixing substitutes "
                "for dense long-range mixing",
            )
        )
    state = str(pv.get("state_scales_with", ""))
    if "latent" in state:
        hits.append(
            (
                "latent_compression",
                "state_scales_with contains latent: low-dimensional latent "
                "substitutes for full-dimensional generation state",
            )
        )
    # Deduplicate by kind, keep first reason.
    seen = set()
    ordered = []
    for kind, reason in hits:
        if kind in seen:
            continue
        seen.add(kind)
        ordered.append((kind, reason))
    return ordered


def classify_property_vector(pv: dict) -> dict:
    """Classify one family property vector."""
    hits = substitution_hits(pv)
    if hits:
        kinds = [k for k, _ in hits]
        reasons = [r for _, r in hits]
        return {
            "targets_substitution": True,
            "substitution_kinds": kinds,
            "reason": "; ".join(reasons),
            "primary_kind": kinds[0],
        }
    # Explicit non-substitution reasons (hostile: do not silently yes).
    retrieval = pv.get("retrieval", "none")
    sharing = pv.get("sharing")
    state = pv.get("state_scales_with")
    serve = pv.get("serve_scales_with")
    if pv.get("verifier_gated") is True:
        reason = (
            "verifier_gated proposal/check trade is within-serve compute composition, "
            "not a storage↔serve / amortisation / specialisation channel substitution"
        )
    elif sharing == "unshared" and state == serve:
        reason = (
            "unshared identical state/serve scales: variance/ensemble claim, not a "
            "resource-channel substitution"
        )
    elif retrieval == "none" and state == serve:
        reason = (
            "retrieval=none and state_scales_with==serve_scales_with=%r: no retained "
            "store and no amortisation axis" % (state,)
        )
    elif retrieval == "none" and not _amortises(pv) and "latent" not in str(state):
        reason = (
            "no retrieval, no amortisation/latent/window marker on scales "
            "(state=%r, serve=%r); defining claim is not a resource substitution"
            % (state, serve)
        )
    else:
        reason = "no substitution marker matched on LOFO property vector"
    return {
        "targets_substitution": False,
        "substitution_kinds": [],
        "reason": reason,
        "primary_kind": None,
    }


def classify_cell(cell: dict, family_vectors: dict) -> dict:
    """Classify one THEORY_RED cell from the audit input."""
    family = cell["family"]
    if family not in family_vectors:
        raise KeyError("missing family_property_vectors for %s" % family)
    pv = family_vectors[family]
    cls = classify_property_vector(pv)
    return {
        "schema": "GMIK4SubstitutionCellAuditCellV1",
        "family": family,
        "grammar": cell["grammar"],
        "cell": cell["cell"],
        "frozen_verdict": cell.get("verdict"),
        "frozen_status": cell.get("status"),
        "targets_substitution": cls["targets_substitution"],
        "substitution_kinds": cls["substitution_kinds"],
        "primary_kind": cls["primary_kind"],
        "reason": cls["reason"],
        "claim_label": "admissible",
        "frozen_verdict_rewritten": False,
    }


def run_audit(input_obj=None) -> dict:
    """Classify all 159 cells; return receipt dict."""
    pins = assert_frozen_untouched()
    obj = input_obj if input_obj is not None else load_input()
    vectors = obj["family_property_vectors"]
    cells_out = [classify_cell(c, vectors) for c in obj["cells"]]

    n_yes = sum(1 for c in cells_out if c["targets_substitution"])
    n_no = sum(1 for c in cells_out if not c["targets_substitution"])
    if n_yes + n_no != 159:
        raise AssertionError("cell count partition broken: yes=%d no=%d" % (n_yes, n_no))

    by_family = {}
    for c in cells_out:
        fam = c["family"]
        slot = by_family.setdefault(
            fam,
            {
                "n_cells": 0,
                "targets_substitution_yes": 0,
                "targets_substitution_no": 0,
                "primary_kind": None,
            },
        )
        slot["n_cells"] += 1
        if c["targets_substitution"]:
            slot["targets_substitution_yes"] += 1
            slot["primary_kind"] = c["primary_kind"]
        else:
            slot["targets_substitution_no"] += 1

    kind_counts = {k: 0 for k in SUBSTITUTION_KINDS}
    for c in cells_out:
        for k in c["substitution_kinds"]:
            kind_counts[k] = kind_counts.get(k, 0) + 1

    families_yes = sorted(
        fam for fam, s in by_family.items() if s["targets_substitution_yes"] > 0
    )
    families_no = sorted(
        fam for fam, s in by_family.items() if s["targets_substitution_yes"] == 0
    )

    return {
        "schema": SCHEMA,
        "audit_id": AUDIT_ID,
        "closes": {
            "issues": ["#592", "#602"],
            "checklist_items": ["22", "23", "35"],
            "remaining_clause": "a",
            "clause_text": (
                "per-cell audit of which of the 159 target a substitution"
            ),
        },
        "source_input": {
            "path": str(INPUT_PATH.name),
            "schema": obj.get("schema"),
            "source_freeze": obj.get("source_freeze"),
            "source_sweep": obj.get("source_sweep"),
            "n_theory_red": obj.get("n_theory_red"),
            "sha256": sha256_file(INPUT_PATH),
        },
        "pins": pins,
        "cells": cells_out,
        "summary": {
            "n_cells": len(cells_out),
            "targets_substitution_yes": n_yes,
            "targets_substitution_no": n_no,
            "families_yes": families_yes,
            "families_no": families_no,
            "n_families_yes": len(families_yes),
            "n_families_no": len(families_no),
            "kind_cell_hits": kind_counts,
            "by_family": by_family,
        },
        "claim_ceiling": {
            "admissible": (
                "Classifies which of the 159 frozen THEORY_RED cells have a "
                "substitution-defined target property under the LOFO property "
                "vector, so NS-1 consequence 2 (INCONCLUSIVE_GRAMMAR) applies "
                "admissibly to those cells given the diagnosed instrument defect."
            ),
            "reachable": (
                "Does NOT claim that any cell is reachable / green under frozen "
                "or repaired pricing. Reachability under repaired pricing is "
                "clause (c), registered separately."
            ),
            "frozen_verdicts_rewritten": False,
            "frozen_model_mutated": False,
        },
        "frozen_verdicts_rewritten": False,
        "frozen_model_mutated": False,
    }


def main(argv=None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    receipt = run_audit()
    out = RECEIPT_PATH
    if argv:
        out = Path(argv[0])
    out.write_text(json.dumps(receipt, indent=1, sort_keys=True) + "\n")
    print(
        json.dumps(
            {
                "audit_id": receipt["audit_id"],
                "n_cells": receipt["summary"]["n_cells"],
                "targets_substitution_yes": receipt["summary"]["targets_substitution_yes"],
                "targets_substitution_no": receipt["summary"]["targets_substitution_no"],
                "families_yes": receipt["summary"]["families_yes"],
                "families_no": receipt["summary"]["families_no"],
                "receipt": str(out),
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
