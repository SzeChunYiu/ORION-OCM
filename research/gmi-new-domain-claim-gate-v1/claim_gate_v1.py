#!/usr/bin/env python3
"""GMI New-Domain Claim Gate v1 — Issue #602 Sections J4 + K (25 boxes).

Executable predicates over a candidate domain dossier. A candidate may receive
novelty wording only when every gate predicate passes and the residual survives
registered-parent / D1–D8 reduction. Otherwise the gate refuses novelty wording.

Wires to:
  - research/gmi-domain-registry-v1 (D1–D8 carriers/operators, burden classes)
  - research/gmi-completeness-attack-v1 (DOMAIN_IDS / DOMAIN_NAMES / E1 burden)

Python 3.8 safe. No third-party imports. Safe under ``python3 -I``.
"""

from __future__ import print_function

import hashlib
import json
import os
import re
import sys
from copy import deepcopy

HERE = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(HERE, os.pardir, os.pardir))

# ---------------------------------------------------------------------------
# Registry alignment (fallback mirrors J1/J2 when sibling packages absent)
# ---------------------------------------------------------------------------

DOMAIN_IDS = ("D1", "D2", "D3", "D4", "D5", "D6", "D7", "D8")

DOMAIN_NAMES = {
    "D1": "coefficient_function_field",
    "D2": "exemplar_memory_indexed",
    "D3": "probabilistic_belief",
    "D4": "symbolic_rule_program",
    "D5": "search_deliberative_frontier",
    "D6": "dynamical_state_controller",
    "D7": "collective_distributed_population",
    "D8": "morphogenetic_self_rewriting",
}

ACCEPTED_BURDEN_CLASSES = (
    "E0_EXACT_ISOMETRY",
    "E1_CONSTANT_FACTOR",
    "E2_POLYNOMIAL",
)

# E3 is evidence-only; never establishes domain equivalence.
REJECTED_EQUIVALENCE_BURDEN = ("E3_APPROXIMATE_OR_EMPIRICAL",)

FORBIDDEN_MACRO_SUBSTRINGS = (
    "backprop",
    "attention",
    "transformer",
    "neuron",
    "bayes",
    "gnn",
    "message_pass",
    "moe",
    "gradient",
    "softmax",
    "qkv",
    "lstm",
    "gru",
)

NOVELTY_REFUSAL = "NOVELTY_WORDING_REFUSED"
NOVELTY_ALLOWED = "NOVELTY_WORDING_PERMITTED_RESIDUAL_SURVIVES"
CLAIM_CEILING = "FINITE_DOSSIER_GATE_NOT_ONTOLOGICAL_NOVELTY"

SCHEMA = "GMI_NEW_DOMAIN_CLAIM_GATE_V1"

# 25 checkboxes: J4 (11) + K (14)
GATE_BOXES = (
    ("J4.1", "distinct_carrier", "Distinct primitive cognitive-state carrier."),
    ("J4.2", "distinct_operator_law", "Distinct native operator/execution law."),
    ("J4.3", "reduction_attempts_d1_d8", "Semantics-preserving reduction attempts to all registered domains."),
    ("J4.4", "burden_separation", "Material lifecycle/asymptotic burden separation when reductions fail."),
    ("J4.5", "prospective_ecology", "Prospectively predicted ecology where candidate enters/leaves frontier."),
    ("J4.6", "matched_negative_twin", "Matched negative twin."),
    ("J4.7", "neutral_recovery", "Neutral recovery without domain-name macros."),
    ("J4.8", "cross_encoding_replication", "Cross-encoding replication."),
    ("J4.9", "cross_search_replication", "Cross-search replication."),
    ("J4.10", "real_transfer_hooks", "Real transfer where applicable."),
    ("J4.11", "parent_review_residual", "Strongest-parent review cannot absorb the residual."),
    ("K.1", "property_first_vector", "Derive property vector from theory before implementation."),
    ("K.2", "freeze_advantage_conditions", "Freeze ecological/resource conditions predicting its advantage."),
    ("K.3", "freeze_negative_twin", "Freeze negative twin predicting its disappearance."),
    ("K.4", "neutral_grammar", "Build neutral grammar with no candidate-specific macro."),
    ("K.5", "neutral_search", "Run neutral search."),
    ("K.6", "posthoc_phenotype_classify", "Classify phenotype only after search."),
    ("K.7", "enrichment_vs_twin", "Test enrichment in predicted ecology vs twin."),
    ("K.8", "remint_replication", "Replicate under reminted semantics."),
    ("K.9", "alternate_encoding_replication", "Replicate under alternate search encoding."),
    ("K.10", "parent_reduce", "Reduce against strongest known parent families."),
    ("K.11", "compiler_overhead", "Quantify compiler/resource overhead to parent."),
    ("K.12", "fresh_residual_prediction", "Make a fresh prediction unique to the surviving residual."),
    ("K.13", "real_regime", "Test on real-regime tasks where relevant."),
    ("K.14", "only_then_novelty_wording", "Only then consider novelty wording."),
)


def canonical_bytes(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def digest(value):
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def _load_json_path(path):
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def discover_siblings():
    """Locate J1 registry / J2 attack packages when present on this checkout."""
    registry_dir = os.path.join(REPO_ROOT, "research", "gmi-domain-registry-v1")
    attack_dir = os.path.join(REPO_ROOT, "research", "gmi-completeness-attack-v1")
    info = {
        "registry_present": os.path.isfile(os.path.join(registry_dir, "DOMAIN_REGISTRY_V1.json")),
        "attack_present": os.path.isfile(os.path.join(attack_dir, "completeness_attack_v1.py")),
        "registry_dir": registry_dir,
        "attack_dir": attack_dir,
        "domain_ids": list(DOMAIN_IDS),
        "domain_names": dict(DOMAIN_NAMES),
        "registered_carrier_ids": [],
        "registered_operator_ids": [],
    }
    if info["registry_present"]:
        registry = _load_json_path(os.path.join(registry_dir, "DOMAIN_REGISTRY_V1.json"))
        carriers = []
        operators = []
        for row in registry.get("domains", []):
            for carrier in row.get("carriers", []):
                carriers.append(carrier["id"])
            for operator in row.get("native_operators", []):
                operators.append(operator["id"])
        info["registered_carrier_ids"] = carriers
        info["registered_operator_ids"] = operators
        info["registry_digest"] = digest(registry)
    if info["attack_present"]:
        if attack_dir not in sys.path:
            sys.path.insert(0, attack_dir)
        try:
            import completeness_attack_v1 as attack  # type: ignore

            info["domain_ids"] = list(attack.DOMAIN_IDS)
            info["domain_names"] = dict(attack.DOMAIN_NAMES)
            info["attack_burden_class"] = getattr(attack, "BURDEN_CLASS", None)
            info["attack_frozen_burden"] = dict(getattr(attack, "FROZEN_BURDEN", {}))
        except Exception as exc:  # pragma: no cover - import edge
            info["attack_import_error"] = str(exc)
    return info


def _fail(predicate_id, reason, **extra):
    row = {"id": predicate_id, "pass": False, "reason": reason}
    row.update(extra)
    return row


def _pass(predicate_id, evidence, **extra):
    row = {"id": predicate_id, "pass": True, "evidence": evidence}
    row.update(extra)
    return row


def _contains_forbidden(text, extra_forbidden=()):
    lowered = str(text).lower()
    banned = list(FORBIDDEN_MACRO_SUBSTRINGS) + [str(x).lower() for x in extra_forbidden]
    hits = [token for token in banned if token and token in lowered]
    return hits


def _require_keys(obj, keys, label):
    missing = [key for key in keys if key not in obj]
    if missing:
        return "missing keys in %s: %s" % (label, ",".join(missing))
    return None


# ---------------------------------------------------------------------------
# Individual predicates
# ---------------------------------------------------------------------------

def check_distinct_carrier(dossier, siblings):
    carrier = dossier.get("carrier") or {}
    err = _require_keys(carrier, ("id", "mathematical_object", "semantic_state"), "carrier")
    if err:
        return _fail("J4.1", err)
    cid = carrier["id"]
    registered = set(siblings.get("registered_carrier_ids") or [])
    # Always treat D1–D8 primary carrier id patterns as registered.
    registered |= {"%s_" % d for d in DOMAIN_IDS}  # prefix guard unused; keep explicit ids below
    fallback_ids = {
        "D1_COEFFICIENT_OBJECT",
        "D2_RECORD_COLLECTION",
        "D3_MEASURE",
        "D4_PROGRAM_STORE",
        "D5_FRONTIER",
        "D6_DYNAMICAL_STATE",
        "D7_POPULATION_STATE",
        "D8_MORPH_GENOME",
    }
    registered |= fallback_ids
    if cid in registered:
        return _fail("J4.1", "carrier id collides with registered domain carrier", carrier_id=cid)
    # Distinctness also requires a non-empty object not equal to any registered name.
    if any(cid.startswith(d + "_") and cid in registered for d in DOMAIN_IDS):
        return _fail("J4.1", "carrier id is a registered domain carrier", carrier_id=cid)
    object_text = "%s %s" % (carrier.get("mathematical_object", ""), carrier.get("semantic_state", ""))
    if not object_text.strip():
        return _fail("J4.1", "carrier mathematical_object/semantic_state empty")
    return _pass("J4.1", "carrier_id=%s distinct from registry" % cid, carrier_id=cid)


def check_distinct_operator_law(dossier, siblings):
    op = dossier.get("operator_law") or {}
    err = _require_keys(op, ("id", "signature", "semantics", "execution_law"), "operator_law")
    if err:
        return _fail("J4.2", err)
    oid = op["id"]
    registered = set(siblings.get("registered_operator_ids") or [])
    registered |= {
        "D1_EVALUATE",
        "D1_PARAMETER_UPDATE",
        "D2_RETRIEVE",
        "D2_INSERT_DELETE",
        "D3_INFER",
        "D3_CONDITION",
        "D4_APPLY_RULE",
        "D4_REWRITE",
        "D5_EXPAND_FRONTIER",
        "D5_SELECT",
        "D6_STEP",
        "D6_RESET",
        "D7_MESSAGE",
        "D7_AGGREGATE",
        "D8_REWRITE_SELF",
        "D8_EMIT_MORPH",
    }
    if oid in registered:
        return _fail("J4.2", "operator id collides with registered native operator", operator_id=oid)
    if not str(op["execution_law"]).strip():
        return _fail("J4.2", "execution_law empty")
    return _pass("J4.2", "operator_id=%s distinct" % oid, operator_id=oid)


def check_reduction_attempts(dossier, siblings):
    attempts = dossier.get("reduction_attempts") or []
    domain_ids = list(siblings.get("domain_ids") or DOMAIN_IDS)
    by_target = {}
    for row in attempts:
        target = row.get("target")
        if target not in domain_ids:
            return _fail("J4.3", "unknown reduction target %s" % target)
        if target in by_target:
            return _fail("J4.3", "duplicate reduction target %s" % target)
        status = row.get("status")
        if status not in ("FAILS", "ABSORBS", "OPEN"):
            return _fail("J4.3", "bad reduction status for %s" % target)
        if status == "FAILS" and not row.get("semantic_preservation_attempt"):
            return _fail("J4.3", "FAILS row missing semantic_preservation_attempt for %s" % target)
        by_target[target] = row
    missing = [d for d in domain_ids if d not in by_target]
    if missing:
        return _fail("J4.3", "missing reduction attempts for %s" % ",".join(missing))
    # Gate requires every registered domain was attempted; survival needs no ABSORBS.
    absorbs = [d for d, row in by_target.items() if row["status"] == "ABSORBS"]
    opens = [d for d, row in by_target.items() if row["status"] == "OPEN"]
    if absorbs:
        return _fail("J4.3", "reduction absorbed by %s" % ",".join(absorbs), absorbs=absorbs)
    if opens:
        return _fail("J4.3", "open reductions remain: %s" % ",".join(opens), opens=opens)
    return _pass("J4.3", "all %d domains attempted; all FAIL" % len(domain_ids), targets=domain_ids)


def check_burden_separation(dossier, _siblings):
    attempts = dossier.get("reduction_attempts") or []
    sep = dossier.get("burden_separation") or {}
    failed = [row for row in attempts if row.get("status") == "FAILS"]
    if not failed:
        return _fail("J4.4", "no failed reductions to separate burden against")
    err = _require_keys(
        sep,
        ("burden_class", "lifecycle_coordinates", "witness", "asymptotic_note"),
        "burden_separation",
    )
    if err:
        return _fail("J4.4", err)
    if sep["burden_class"] in REJECTED_EQUIVALENCE_BURDEN:
        return _fail("J4.4", "E3 cannot establish material domain separation")
    if sep["burden_class"] not in ACCEPTED_BURDEN_CLASSES:
        return _fail("J4.4", "unknown burden class %s" % sep["burden_class"])
    coords = sep["lifecycle_coordinates"]
    if not isinstance(coords, list) or len(coords) < 1:
        return _fail("J4.4", "lifecycle_coordinates must be nonempty")
    # Every failed reduction must be cited in the witness map.
    witness = sep["witness"]
    if not isinstance(witness, dict):
        return _fail("J4.4", "witness must map domain -> coordinate evidence")
    for row in failed:
        target = row["target"]
        if target not in witness or not witness[target]:
            return _fail("J4.4", "missing burden witness for failed target %s" % target)
    return _pass(
        "J4.4",
        "burden_class=%s coords=%d" % (sep["burden_class"], len(coords)),
        burden_class=sep["burden_class"],
    )


def check_prospective_ecology(dossier, _siblings):
    eco = dossier.get("prospective_ecology") or {}
    err = _require_keys(
        eco,
        ("enter_frontier", "leave_frontier", "frozen_before_search", "ecology_digest"),
        "prospective_ecology",
    )
    if err:
        return _fail("J4.5", err)
    if not eco["frozen_before_search"]:
        return _fail("J4.5", "ecology must be frozen before search")
    if not eco["enter_frontier"] or not eco["leave_frontier"]:
        return _fail("J4.5", "enter/leave frontier predicates required")
    if digest(eco["enter_frontier"]) == digest(eco["leave_frontier"]):
        return _fail("J4.5", "enter and leave frontiers must differ")
    if eco["ecology_digest"] != digest({"enter": eco["enter_frontier"], "leave": eco["leave_frontier"]}):
        return _fail("J4.5", "ecology_digest mismatch")
    return _pass("J4.5", "prospective ecology frozen", ecology_digest=eco["ecology_digest"])


def check_matched_negative_twin(dossier, _siblings):
    twin = dossier.get("negative_twin") or {}
    err = _require_keys(
        twin,
        ("changed_coordinate", "base_digest", "twin_digest", "prediction", "matched"),
        "negative_twin",
    )
    if err:
        return _fail("J4.6", err)
    if not twin["matched"]:
        return _fail("J4.6", "negative twin not marked matched")
    if twin["base_digest"] == twin["twin_digest"]:
        return _fail("J4.6", "twin digest equals base")
    if twin["prediction"] not in ("DISAPPEARS", "NO_ADVANTAGE", "PARENT_SUFFICIENT"):
        return _fail("J4.6", "bad twin prediction %s" % twin["prediction"])
    return _pass("J4.6", "matched twin on %s" % twin["changed_coordinate"])


def check_neutral_recovery(dossier, _siblings):
    rec = dossier.get("neutral_recovery") or {}
    err = _require_keys(
        rec,
        ("grammar_symbols", "search_space_size", "winner", "family_macros_absent", "recovered"),
        "neutral_recovery",
    )
    if err:
        return _fail("J4.7", err)
    if not rec["family_macros_absent"] or not rec["recovered"]:
        return _fail("J4.7", "neutral recovery must recover without family macros")
    extra = [dossier.get("candidate_id", "")]
    for symbol in rec["grammar_symbols"]:
        hits = _contains_forbidden(symbol, extra_forbidden=extra)
        if hits:
            return _fail("J4.7", "grammar symbol contains forbidden macro %s" % hits[0], symbol=symbol)
    if int(rec["search_space_size"]) < 2:
        return _fail("J4.7", "search space too small")
    return _pass("J4.7", "recovered winner=%s" % rec["winner"])


def check_cross_encoding(dossier, _siblings):
    row = dossier.get("cross_encoding_replication") or {}
    err = _require_keys(row, ("encoding_a", "encoding_b", "same_residual", "replicated"), "cross_encoding")
    if err:
        return _fail("J4.8", err)
    if row["encoding_a"] == row["encoding_b"]:
        return _fail("J4.8", "encodings must be distinct")
    if not row["same_residual"] or not row["replicated"]:
        return _fail("J4.8", "cross-encoding residual not replicated")
    return _pass("J4.8", "encodings %s / %s" % (row["encoding_a"], row["encoding_b"]))


def check_cross_search(dossier, _siblings):
    row = dossier.get("cross_search_replication") or {}
    err = _require_keys(row, ("search_a", "search_b", "same_residual", "replicated"), "cross_search")
    if err:
        return _fail("J4.9", err)
    if row["search_a"] == row["search_b"]:
        return _fail("J4.9", "search procedures must be distinct")
    if not row["same_residual"] or not row["replicated"]:
        return _fail("J4.9", "cross-search residual not replicated")
    return _pass("J4.9", "searches %s / %s" % (row["search_a"], row["search_b"]))


def check_real_transfer(dossier, _siblings):
    row = dossier.get("real_transfer") or {}
    err = _require_keys(row, ("applicable", "hooks", "status"), "real_transfer")
    if err:
        return _fail("J4.10", err)
    if row["status"] not in ("EXECUTED", "HOOKS_REGISTERED_NOT_APPLICABLE", "DEFERRED_SCOPED"):
        return _fail("J4.10", "bad real_transfer status")
    if not isinstance(row["hooks"], list) or not row["hooks"]:
        return _fail("J4.10", "real transfer hooks required even when not applicable")
    if row["applicable"] and row["status"] != "EXECUTED":
        return _fail("J4.10", "applicable transfer must be EXECUTED")
    if (not row["applicable"]) and row["status"] == "EXECUTED":
        return _fail("J4.10", "non-applicable transfer cannot claim EXECUTED")
    return _pass("J4.10", "status=%s hooks=%d" % (row["status"], len(row["hooks"])))


def check_parent_review(dossier, _siblings):
    review = dossier.get("parent_review") or {}
    err = _require_keys(review, ("attempts", "verdict", "residual_survives"), "parent_review")
    if err:
        return _fail("J4.11", err)
    attempts = review["attempts"]
    if not attempts:
        return _fail("J4.11", "parent review requires attempts")
    # Strongest-parent-first: attempts must be priority-sorted ascending.
    priorities = [int(a["priority"]) for a in attempts]
    if priorities != sorted(priorities):
        return _fail("J4.11", "parent attempts must be strongest-first (ascending priority)")
    allowed = {"ABSORBS", "REFUTES", "OPEN"}
    for attempt in attempts:
        if attempt.get("status") not in allowed:
            return _fail("J4.11", "bad parent status")
    if any(a["status"] == "ABSORBS" for a in attempts):
        return _fail("J4.11", "parent absorbs residual")
    if any(a["status"] == "OPEN" for a in attempts):
        return _fail("J4.11", "open parent attempts remain")
    if review["verdict"] != "RESIDUAL_SURVIVES_REGISTERED_PARENT_SET":
        return _fail("J4.11", "verdict must be residual-survives")
    if not review["residual_survives"]:
        return _fail("J4.11", "residual_survives flag false")
    return _pass("J4.11", "residual survives %d parents" % len(attempts))


def check_property_first(dossier, _siblings):
    pv = dossier.get("property_vector") or {}
    err = _require_keys(pv, ("derived_before_implementation", "vector", "theory_ref"), "property_vector")
    if err:
        return _fail("K.1", err)
    if not pv["derived_before_implementation"]:
        return _fail("K.1", "property vector must predate implementation")
    if not isinstance(pv["vector"], dict) or not pv["vector"]:
        return _fail("K.1", "property vector empty")
    return _pass("K.1", "vector keys=%s" % ",".join(sorted(pv["vector"])))


def check_freeze_advantage(dossier, _siblings):
    fr = dossier.get("freeze_advantage") or {}
    err = _require_keys(fr, ("conditions", "commitment_sha256", "frozen_before_search"), "freeze_advantage")
    if err:
        return _fail("K.2", err)
    if not fr["frozen_before_search"]:
        return _fail("K.2", "advantage conditions not frozen before search")
    expected = digest(fr["conditions"])
    if fr["commitment_sha256"] != expected:
        return _fail("K.2", "advantage commitment mismatch")
    return _pass("K.2", "commitment=%s" % fr["commitment_sha256"][:16])


def check_freeze_negative_twin(dossier, _siblings):
    fr = dossier.get("freeze_negative_twin") or {}
    err = _require_keys(fr, ("twin_spec", "commitment_sha256", "predicts_disappearance"), "freeze_negative_twin")
    if err:
        return _fail("K.3", err)
    if not fr["predicts_disappearance"]:
        return _fail("K.3", "frozen twin must predict disappearance")
    if fr["commitment_sha256"] != digest(fr["twin_spec"]):
        return _fail("K.3", "twin freeze commitment mismatch")
    # Must agree with J4.6 twin coordinate when both present.
    nt = dossier.get("negative_twin") or {}
    if nt and nt.get("changed_coordinate") and fr["twin_spec"].get("changed_coordinate"):
        if nt["changed_coordinate"] != fr["twin_spec"]["changed_coordinate"]:
            return _fail("K.3", "frozen twin coordinate disagrees with matched twin")
    return _pass("K.3", "twin freeze ok")


def check_neutral_grammar(dossier, _siblings):
    gram = dossier.get("neutral_grammar") or {}
    err = _require_keys(gram, ("symbols", "forbidden_checked", "candidate_macros_absent"), "neutral_grammar")
    if err:
        return _fail("K.4", err)
    if not gram["forbidden_checked"] or not gram["candidate_macros_absent"]:
        return _fail("K.4", "grammar macros not cleared")
    extra = [dossier.get("candidate_id", ""), dossier.get("display_name", "")]
    for symbol in gram["symbols"]:
        hits = _contains_forbidden(symbol, extra_forbidden=extra)
        if hits:
            return _fail("K.4", "symbol leaks macro %s" % hits[0])
    if len(gram["symbols"]) < 2:
        return _fail("K.4", "grammar too small")
    return _pass("K.4", "symbols=%d" % len(gram["symbols"]))


def check_neutral_search(dossier, _siblings):
    search = dossier.get("neutral_search") or {}
    err = _require_keys(
        search,
        ("ran", "space_size", "identity_hidden", "result_commitment"),
        "neutral_search",
    )
    if err:
        return _fail("K.5", err)
    if not search["ran"] or not search["identity_hidden"]:
        return _fail("K.5", "neutral search must run with identity hidden")
    if int(search["space_size"]) < 2:
        return _fail("K.5", "search space too small")
    return _pass("K.5", "space_size=%s" % search["space_size"])


def check_posthoc_phenotype(dossier, _siblings):
    ph = dossier.get("phenotype_classification") or {}
    err = _require_keys(ph, ("classified_after_search", "label", "pre_search_label_absent"), "phenotype")
    if err:
        return _fail("K.6", err)
    if not ph["classified_after_search"] or not ph["pre_search_label_absent"]:
        return _fail("K.6", "phenotype must be post-hoc only")
    # Label must not appear in neutral grammar symbols or search space descriptors.
    gram = dossier.get("neutral_grammar") or {}
    for symbol in gram.get("symbols") or []:
        if ph["label"] and ph["label"].lower() in str(symbol).lower():
            return _fail("K.6", "phenotype label leaked into grammar")
    return _pass("K.6", "label=%s post-hoc" % ph["label"])


def check_enrichment(dossier, _siblings):
    enr = dossier.get("enrichment") or {}
    err = _require_keys(
        enr,
        ("predicted_ecology_score", "twin_ecology_score", "enriched"),
        "enrichment",
    )
    if err:
        return _fail("K.7", err)
    if not enr["enriched"]:
        return _fail("K.7", "enrichment flag false")
    if not (enr["predicted_ecology_score"] > enr["twin_ecology_score"]):
        return _fail("K.7", "predicted ecology must strictly beat twin")
    return _pass(
        "K.7",
        "pred=%s twin=%s" % (enr["predicted_ecology_score"], enr["twin_ecology_score"]),
    )


def check_remint(dossier, _siblings):
    row = dossier.get("remint_replication") or {}
    err = _require_keys(row, ("remint_id", "semantics_preserved", "replicated"), "remint")
    if err:
        return _fail("K.8", err)
    if not row["semantics_preserved"] or not row["replicated"]:
        return _fail("K.8", "remint replication failed")
    return _pass("K.8", "remint=%s" % row["remint_id"])


def check_alternate_encoding(dossier, _siblings):
    row = dossier.get("alternate_encoding") or {}
    err = _require_keys(row, ("encoding_id", "replicated", "distinct_from_primary"), "alternate_encoding")
    if err:
        return _fail("K.9", err)
    if not row["replicated"] or not row["distinct_from_primary"]:
        return _fail("K.9", "alternate encoding replication failed")
    return _pass("K.9", "encoding=%s" % row["encoding_id"])


def check_parent_reduce(dossier, _siblings):
    # Reuse parent_review attempts; K.10 is the family-parent reduction row.
    review = dossier.get("parent_review") or {}
    families = dossier.get("parent_family_reduction") or {}
    err = _require_keys(families, ("families", "all_refuted", "residual_survives"), "parent_family_reduction")
    if err:
        return _fail("K.10", err)
    if not families["families"]:
        return _fail("K.10", "no parent families listed")
    if not families["all_refuted"] or not families["residual_survives"]:
        return _fail("K.10", "parent families not fully refuted")
    if review and not review.get("residual_survives"):
        return _fail("K.10", "disagrees with parent_review residual")
    return _pass("K.10", "families=%d" % len(families["families"]))


def check_compiler_overhead(dossier, _siblings):
    oh = dossier.get("compiler_overhead") or {}
    err = _require_keys(
        oh,
        ("to_parent", "coordinates", "bounded", "burden_class"),
        "compiler_overhead",
    )
    if err:
        return _fail("K.11", err)
    if oh["burden_class"] in REJECTED_EQUIVALENCE_BURDEN:
        return _fail("K.11", "E3 overhead insufficient for residual claim")
    if not oh["bounded"] or not oh["coordinates"]:
        return _fail("K.11", "overhead must be bounded on nonempty coordinates")
    # Residual claim: overhead to parent must be material (not free).
    if oh.get("overhead_is_free"):
        return _fail("K.11", "free overhead implies parent absorption")
    return _pass("K.11", "to_parent=%s class=%s" % (oh["to_parent"], oh["burden_class"]))


def check_fresh_prediction(dossier, _siblings):
    pred = dossier.get("fresh_residual_prediction") or {}
    err = _require_keys(
        pred,
        ("statement", "unique_to_residual", "made_after_survival", "falsifier"),
        "fresh_residual_prediction",
    )
    if err:
        return _fail("K.12", err)
    if not pred["unique_to_residual"] or not pred["made_after_survival"]:
        return _fail("K.12", "fresh prediction must be post-survival and residual-unique")
    if not pred["statement"] or not pred["falsifier"]:
        return _fail("K.12", "statement/falsifier required")
    return _pass("K.12", "fresh prediction present")


def check_real_regime(dossier, _siblings):
    row = dossier.get("real_regime") or {}
    err = _require_keys(row, ("relevant", "status", "tasks"), "real_regime")
    if err:
        return _fail("K.13", err)
    if row["status"] not in ("EXECUTED", "NOT_RELEVANT_SCOPED", "DEFERRED_SCOPED"):
        return _fail("K.13", "bad real_regime status")
    if row["relevant"] and row["status"] != "EXECUTED":
        return _fail("K.13", "relevant real-regime must be EXECUTED")
    if row["relevant"] and not row["tasks"]:
        return _fail("K.13", "relevant real-regime requires tasks")
    if (not row["relevant"]) and row["status"] == "EXECUTED":
        return _fail("K.13", "non-relevant cannot claim EXECUTED")
    return _pass("K.13", "status=%s" % row["status"])


def check_only_then_novelty(dossier, prior_results):
    """K.14 — novelty wording only if every prior predicate passed and residual survives."""
    failed = [r["id"] for r in prior_results if not r["pass"]]
    wants = bool((dossier.get("novelty_claim") or {}).get("assert_novelty", False))
    wording = (dossier.get("novelty_claim") or {}).get("wording", "")
    residual = bool((dossier.get("parent_review") or {}).get("residual_survives"))
    if failed:
        if wants or wording:
            return _fail(
                "K.14",
                "novelty wording refused; failed predicates: %s" % ",".join(failed),
                novelty=NOVELTY_REFUSAL,
            )
        return _pass(
            "K.14",
            "correctly withheld novelty after failures",
            novelty=NOVELTY_REFUSAL,
            note="pass means gate disposition is correct (refusal)",
        )
    if not residual:
        return _fail("K.14", "residual did not survive; novelty refused", novelty=NOVELTY_REFUSAL)
    # All prior pass + residual: novelty may be asserted; if asserted, require explicit ceiling.
    claim = dossier.get("novelty_claim") or {}
    if wants:
        if claim.get("claim_ceiling") != CLAIM_CEILING:
            return _fail("K.14", "novelty asserted without required claim ceiling", novelty=NOVELTY_REFUSAL)
        if not wording or "new domain" not in wording.lower():
            return _fail("K.14", "novelty wording missing explicit new-domain phrase", novelty=NOVELTY_REFUSAL)
        return _pass("K.14", "novelty wording permitted", novelty=NOVELTY_ALLOWED)
    # All green but novelty not asserted — still a valid gate pass (optional wording).
    return _pass("K.14", "gates green; novelty optional and not asserted", novelty=NOVELTY_ALLOWED)


PREDICATE_RUNNERS = (
    ("J4.1", check_distinct_carrier),
    ("J4.2", check_distinct_operator_law),
    ("J4.3", check_reduction_attempts),
    ("J4.4", check_burden_separation),
    ("J4.5", check_prospective_ecology),
    ("J4.6", check_matched_negative_twin),
    ("J4.7", check_neutral_recovery),
    ("J4.8", check_cross_encoding),
    ("J4.9", check_cross_search),
    ("J4.10", check_real_transfer),
    ("J4.11", check_parent_review),
    ("K.1", check_property_first),
    ("K.2", check_freeze_advantage),
    ("K.3", check_freeze_negative_twin),
    ("K.4", check_neutral_grammar),
    ("K.5", check_neutral_search),
    ("K.6", check_posthoc_phenotype),
    ("K.7", check_enrichment),
    ("K.8", check_remint),
    ("K.9", check_alternate_encoding),
    ("K.10", check_parent_reduce),
    ("K.11", check_compiler_overhead),
    ("K.12", check_fresh_prediction),
    ("K.13", check_real_regime),
)


def evaluate_dossier(dossier, siblings=None):
    """Run all 25 gate predicates. Returns a structured report."""
    if siblings is None:
        siblings = discover_siblings()
    dossier = deepcopy(dossier)
    results = []
    for _pid, runner in PREDICATE_RUNNERS:
        results.append(runner(dossier, siblings))
    results.append(check_only_then_novelty(dossier, results))

    by_id = {row["id"]: row for row in results}
    # K.14 special: when prior failures exist, K.14 "pass" means correct refusal.
    structural_ids = [pid for pid, _ in PREDICATE_RUNNERS]
    structural_pass = all(by_id[pid]["pass"] for pid in structural_ids)
    residual = bool((dossier.get("parent_review") or {}).get("residual_survives")) and structural_pass
    novelty_disposition = by_id["K.14"].get("novelty", NOVELTY_REFUSAL)
    if not residual:
        novelty_disposition = NOVELTY_REFUSAL

    gate_pass = structural_pass and residual and by_id["K.14"]["pass"]
    return {
        "schema": SCHEMA,
        "issue": 602,
        "sections": ["J4", "K"],
        "box_count": len(GATE_BOXES),
        "candidate_id": dossier.get("candidate_id"),
        "siblings": {
            "registry_present": siblings.get("registry_present"),
            "attack_present": siblings.get("attack_present"),
            "domain_ids": siblings.get("domain_ids"),
            "domain_names": siblings.get("domain_names"),
        },
        "predicates": results,
        "structural_pass": structural_pass,
        "residual_survives": residual,
        "gate_pass": gate_pass,
        "novelty_disposition": novelty_disposition,
        "claim_ceiling": CLAIM_CEILING,
        "dossier_digest": digest(dossier),
    }


def load_fixture(name):
    path = os.path.join(HERE, "fixtures", name)
    return _load_json_path(path)


def run_report():
    siblings = discover_siblings()
    positive = load_fixture("positive_residual_twin.json")
    negative = load_fixture("negative_absorbed_twin.json")
    pos = evaluate_dossier(positive, siblings)
    neg = evaluate_dossier(negative, siblings)
    report = {
        "schema": "GMI_NEW_DOMAIN_CLAIM_GATE_REPORT_V1",
        "positive": {
            "candidate_id": pos["candidate_id"],
            "gate_pass": pos["gate_pass"],
            "novelty_disposition": pos["novelty_disposition"],
            "failed": [r["id"] for r in pos["predicates"] if not r["pass"]],
        },
        "negative": {
            "candidate_id": neg["candidate_id"],
            "gate_pass": neg["gate_pass"],
            "novelty_disposition": neg["novelty_disposition"],
            "failed": [r["id"] for r in neg["predicates"] if not r["pass"]],
        },
        "invariant": {
            "positive_must_pass": pos["gate_pass"] is True,
            "negative_must_fail_or_refuse": (
                neg["gate_pass"] is False and neg["novelty_disposition"] == NOVELTY_REFUSAL
            ),
            "box_count_is_25": len(GATE_BOXES) == 25,
        },
        "siblings": pos["siblings"],
        "claim_ceiling": CLAIM_CEILING,
    }
    return report


def main():
    report = run_report()
    print(json.dumps(report, indent=2, sort_keys=True))
    inv = report["invariant"]
    if not (inv["positive_must_pass"] and inv["negative_must_fail_or_refuse"] and inv["box_count_is_25"]):
        raise SystemExit(2)
    print("GMI_NEW_DOMAIN_CLAIM_GATE_V1_OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
