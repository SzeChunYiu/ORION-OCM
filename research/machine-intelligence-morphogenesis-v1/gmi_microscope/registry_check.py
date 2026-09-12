"""Validator for GMI_TRANSFORMER_MICROFEATURE_REGISTRY_V1.json.

Checks, on the COMMITTED json (not on the builder's in-memory object):

  1. every feature carries every required field, and no required field is empty;
  2. `gmi_type` is a non-empty subset of the declared type alphabet C S R T N U H V G P D;
  3. `evidence_status` is one of the nine claim levels of GMI_RECURSIVE_THEORY_HARDENING_FIXED_POINT_V1.md section 3
     (EMPIRICALLY_SUPPORTED_AT_TIER_X is a schema: only the tiers declared in the registry's `tiers` block may instantiate it);
  4. ids are unique and well formed (TF-NNN);
  5. `formal_theorem`, when present, names a theorem in TMT-1..TMT-15 and a receipt check that EXISTS in the executed
     GMI_TRANSFORMER_MICROFEATURE_EXACT_RECEIPT_V1.json, and that check passed;
  6. `resource_effect.components` is a non-empty subset of the declared Delta_f names;
  7. no boilerplate: the entry-specific fields are not repeated verbatim across entries;
  8. PROVED_AT_SCOPE is used only where a formal_theorem with a receipt check is present;
  9. the registry's own recorded counts and sha256 agree with its contents.

Prints counts and exits non-zero on failure.

Run: python3 -m gmi_microscope.registry_check
"""
from __future__ import annotations

import json
import os
import re
import sys

from .core import sha256_of

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
REGISTRY_PATH = os.path.join(ROOT, "GMI_TRANSFORMER_MICROFEATURE_REGISTRY_V1.json")
RECEIPT_PATH = os.path.join(ROOT, "GMI_TRANSFORMER_MICROFEATURE_EXACT_RECEIPT_V1.json")

ALPHABET = set("CSRTNUHVGPD")
CLAIM_LEVELS = {"PROVED_AT_SCOPE", "PARENT_THEOREM_UNDER_ASSUMPTIONS", "EMPIRICALLY_SUPPORTED_AT_TIER_X",
                "REGISTERED_FOR_EXPERIMENT", "REDUCED_TO_PARENT", "FALSIFIED_AND_REPLACED", "OPEN_BLOCKING",
                "OPEN_NONBLOCKING", "OUT_OF_SCOPE"}
TMT_IDS = {"TMT-%d" % i for i in range(1, 16)}
REQUIRED = ["id", "name", "exact_definition", "gmi_type", "gmi_type_note", "semantic_invariance", "mechanism_hypothesis",
            "resource_effect", "negative_twin", "implementation_equivalent_alternative", "parent_literature",
            "formal_theorem", "experiment", "kill_condition", "evidence_status", "hidden_cost_rule", "calculus_section"]
# formal_theorem may be null by design; every other required field must be non-empty.
NULLABLE = {"formal_theorem"}
# fields that must be entry-specific (no verbatim duplication across entries)
DISTINCT = ["exact_definition", "gmi_type_note", "mechanism_hypothesis", "negative_twin",
            "implementation_equivalent_alternative", "kill_condition", "hidden_cost_rule"]
MIN_CHARS = 40   # a "specific, non-boilerplate" prose field is at least this long


def _nonempty(v):
    if v is None:
        return False
    if isinstance(v, str):
        return len(v.strip()) > 0
    if isinstance(v, (list, dict)):
        return len(v) > 0
    return True


def check(registry_path=REGISTRY_PATH, receipt_path=RECEIPT_PATH, verbose=True):
    errors = []
    reg = json.load(open(registry_path, encoding="utf-8"))
    receipt = json.load(open(receipt_path, encoding="utf-8"))

    if reg.get("schema") != "GMITransformerMicrofeatureRegistryV1":
        errors.append("schema is %r, expected GMITransformerMicrofeatureRegistryV1" % reg.get("schema"))

    # the receipt's executed check ids, and whether each passed
    receipt_checks = {}
    for c in receipt.get("checks", []):
        cid = c.get("check")
        if cid:
            receipt_checks[cid] = bool(c.get("passed"))
    if not receipt_checks:
        errors.append("no X-TMT check ids found in %s" % os.path.basename(receipt_path))

    declared_alphabet = set(reg.get("type_alphabet", {}))
    if declared_alphabet != ALPHABET:
        errors.append("declared type_alphabet %s != C S R T N U H V G P D" % sorted(declared_alphabet))
    declared_levels = set(reg.get("claim_levels", []))
    if declared_levels != CLAIM_LEVELS:
        errors.append("declared claim_levels %s != the nine hardening closure states" % sorted(declared_levels))
    delta_names = set(reg.get("effect_vector", []))
    if len(delta_names) != 11:
        errors.append("effect_vector has %d entries, expected the 11 Delta_f components" % len(delta_names))
    tiers = set(reg.get("tiers", {}))
    allowed_status = (CLAIM_LEVELS - {"EMPIRICALLY_SUPPORTED_AT_TIER_X"}) | {"EMPIRICALLY_SUPPORTED_AT_TIER_" + t for t in tiers}

    features = reg.get("features", [])
    if not features:
        errors.append("registry has no features")

    seen_ids = {}
    distinct_seen = {k: {} for k in DISTINCT}
    counts = {}
    type_counts = {}

    for f in features:
        fid = f.get("id", "<missing id>")
        def err(msg):
            errors.append("%s: %s" % (fid, msg))

        # 1. required fields present and non-empty
        for k in REQUIRED:
            if k not in f:
                err("missing required field %r" % k)
            elif not _nonempty(f[k]) and k not in NULLABLE:
                err("required field %r is empty" % k)
        if not isinstance(f.get("semantic_invariance"), dict) or not all(
                _nonempty(f["semantic_invariance"].get(k)) for k in ("preserved", "not_preserved")):
            err("semantic_invariance must carry non-empty 'preserved' and 'not_preserved'")

        # 4. id well formed and unique
        if not re.fullmatch(r"TF-\d{3}", str(fid)):
            err("id is not of the form TF-NNN")
        if fid in seen_ids:
            err("duplicate id (also at index %d)" % seen_ids[fid])
        seen_ids[fid] = len(seen_ids)

        # 2. types
        t = f.get("gmi_type") or []
        if not t:
            err("gmi_type is empty")
        if not set(t) <= ALPHABET:
            err("gmi_type %s is not a subset of the alphabet" % t)
        if len(set(t)) != len(t):
            err("gmi_type %s repeats a letter" % t)
        for letter in t:
            type_counts[letter] = type_counts.get(letter, 0) + 1

        # 3. claim level
        st = f.get("evidence_status")
        if st not in allowed_status:
            err("evidence_status %r is not one of the nine claim levels (tiers declared: %s)" % (st, sorted(tiers)))
        counts[st] = counts.get(st, 0) + 1

        # 5. theorem / receipt reference
        th = f.get("formal_theorem")
        if th is not None:
            if not isinstance(th, dict):
                err("formal_theorem must be null or an object")
            else:
                if th.get("tmt") not in TMT_IDS:
                    err("formal_theorem.tmt %r is outside TMT-1..TMT-15" % th.get("tmt"))
                rc = th.get("receipt_check")
                if rc not in receipt_checks:
                    err("formal_theorem.receipt_check %r is not an executed check in the receipt" % rc)
                elif not receipt_checks[rc]:
                    err("formal_theorem.receipt_check %r did not pass in the receipt" % rc)
                if th.get("check_kind") != "MATH_IMPLEMENTATION_CHECK__NOT_EMPIRICAL_NEURAL_EVIDENCE":
                    err("formal_theorem.check_kind must record that the check is not neural evidence")

        # 8. PROVED_AT_SCOPE requires an executed check
        if st == "PROVED_AT_SCOPE" and not (isinstance(th, dict) and th.get("receipt_check") in receipt_checks):
            err("PROVED_AT_SCOPE without an executed receipt check")

        # 6. resource effect
        re_ = f.get("resource_effect") or {}
        comps = re_.get("components") or []
        if not comps:
            err("resource_effect.components is empty")
        if not set(comps) <= delta_names:
            err("resource_effect.components %s not a subset of Delta_f" % sorted(set(comps) - delta_names))
        if not _nonempty(re_.get("direction")):
            err("resource_effect.direction is empty")

        # parent literature
        pl = f.get("parent_literature") or []
        if not 1 <= len(pl) <= 4:
            err("parent_literature has %d entries, expected 1..4" % len(pl))
        for p in pl:
            if not _nonempty(p.get("citation")) or not _nonempty(p.get("owns")):
                err("a parent_literature entry lacks a citation or an owns clause")
            if "citation_status" not in p:
                err("a parent_literature entry lacks citation_status")

        # 7. no boilerplate
        for k in DISTINCT:
            v = f.get(k)
            if isinstance(v, str):
                if len(v.strip()) < MIN_CHARS:
                    err("field %r is only %d chars; specific fields must be substantive" % (k, len(v.strip())))
                key = v.strip()
                if key in distinct_seen[k]:
                    err("field %r is verbatim identical to %s (boilerplate)" % (k, distinct_seen[k][key]))
                distinct_seen[k][key] = fid

    # 9. recorded counts and sha
    if reg.get("n_features") != len(features):
        errors.append("n_features %r != %d actual" % (reg.get("n_features"), len(features)))
    if reg.get("counts_by_evidence_status") != counts:
        errors.append("counts_by_evidence_status disagrees with the features: recorded %s, actual %s"
                      % (reg.get("counts_by_evidence_status"), counts))
    if reg.get("counts_by_type") != type_counts:
        errors.append("counts_by_type disagrees with the features")
    sha = sha256_of({k: v for k, v in reg.items() if k != "registry_sha256"})
    if reg.get("registry_sha256") != sha:
        errors.append("registry_sha256 %s does not match the content (%s)" % (reg.get("registry_sha256", "")[:16], sha[:16]))

    if verbose:
        print("registry: %s" % os.path.basename(registry_path))
        print("features: %d   sha256: %s" % (len(features), str(reg.get("registry_sha256"))[:16]))
        print("receipt checks available: %d (%d passed)" % (len(receipt_checks), sum(receipt_checks.values())))
        print("counts by evidence status:")
        for k in sorted(counts, key=lambda k: -counts[k]):
            print("  %-40s %3d" % (k, counts[k]))
        print("counts by GMI type:")
        print("  " + "  ".join("%s=%d" % (k, type_counts[k]) for k in sorted(type_counts)))
        n_th = sum(1 for f in features if f.get("formal_theorem"))
        print("entries with a formal theorem + executed receipt check: %d" % n_th)
        print("A TYPED LOCATION IS NOT EVIDENCE: every receipt check above is a mathematical implementation check "
              "on a finite enumerated scope, not evidence about a trained neural network.")
        if errors:
            print("\nFAILED: %d problem(s)" % len(errors))
            for e in errors[:50]:
                print("  - " + e)
            if len(errors) > 50:
                print("  ... and %d more" % (len(errors) - 50))
        else:
            print("\nOK: registry valid.")
    return errors


def main():
    return check()


if __name__ == "__main__":
    sys.exit(1 if main() else 0)
