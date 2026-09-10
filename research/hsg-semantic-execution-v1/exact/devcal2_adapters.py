"""DEV-CAL-2 adapter records: grants are DATA, never code.

Freeze clause `adapters_are_data` (DEV_CAL_2_KNOCKOUT_PROTOCOL_FREEZE_V1.json):
"every grant is a DECLARATIVE adapter record consumed by the unchanged runner
(component name, certificate digests, keying rule id, transport map id,
amortisation rule id); adapters are sha256-bound and emitted in the receipts;
NO runner code change is authorised by this freeze."

This module is the adapter loader + the single-component verifier
(checker_requirements[0]) + the sha256 digest binding
(checker_requirements[1]).  It grants NOTHING at import time; it only
declares, digests, and fail-closed-verifies records.

Component registry (freeze clause `interface_components`):
  REPRESENTATION     histories may store/serve typed-operator STRUCTURAL
                     CERTIFICATES (m* template DAG modulo relabeling, support
                     multiset, digest-bound, DEV-CAL-1 certificate format).
  RETRIEVAL_KEYING   retrieval keyed by structural certificate (the three
                     frozen certificate types) instead of the surface
                     signature; a reminted target retrieves its latent class.
  TRANSPORT_MAP      the verified homomorphism (DEV-CAL-1 certificate (c))
                     carries a retrieved certificate onto the reminted
                     surface symbols.
  CHARGING_MODEL     per-world acquisition amortised across the world family
                     sharing the certificate.

Arms (freeze clauses `ladder_arms_PRIMARY`, `leave_one_out_SECONDARY`):
cumulative ladder + 4 minus-one arms from the full KO-4 stack.  Each arm's
component set is EXACT; a record naming anything else (more OR fewer than its
arm's set, or a capability field set for an ungranted component) FAILS CLOSED.

Rule ids are frozen here; no numeric parameter lives in an adapter that is
not itself derived from committed DEV-CAL-1 data at run time (the
amortisation divisor is derived from the committed world freeze table, never
hand-tuned).

Python 3.8+ stdlib only; no DEV-CAL-1 file is modified.
"""
from __future__ import annotations

from exact.devcal1_certificates import canonical_json, sha

COMPONENTS = ("REPRESENTATION", "RETRIEVAL_KEYING", "TRANSPORT_MAP",
              "CHARGING_MODEL")

LADDER = ("KO-1_REPRESENTATION", "KO-2_PLUS_RETRIEVAL", "KO-3_PLUS_TRANSPORT",
          "KO-4_PLUS_CHARGING")
LEAVE_ONE_OUT = ("LOO_MINUS_REPRESENTATION", "LOO_MINUS_RETRIEVAL",
                 "LOO_MINUS_TRANSPORT", "LOO_MINUS_CHARGING")
ALL_KO_ARMS = LADDER + LEAVE_ONE_OUT

# exactly the components each arm grants (freeze: single-component grants,
# cumulative; leave-one-out = full stack minus exactly one)
ARM_COMPONENTS = {
    "KO-1_REPRESENTATION": ("REPRESENTATION",),
    "KO-2_PLUS_RETRIEVAL": ("REPRESENTATION", "RETRIEVAL_KEYING"),
    "KO-3_PLUS_TRANSPORT": ("REPRESENTATION", "RETRIEVAL_KEYING",
                            "TRANSPORT_MAP"),
    "KO-4_PLUS_CHARGING": ("REPRESENTATION", "RETRIEVAL_KEYING",
                           "TRANSPORT_MAP", "CHARGING_MODEL"),
    "LOO_MINUS_REPRESENTATION": ("RETRIEVAL_KEYING", "TRANSPORT_MAP",
                                 "CHARGING_MODEL"),
    "LOO_MINUS_RETRIEVAL": ("REPRESENTATION", "TRANSPORT_MAP",
                            "CHARGING_MODEL"),
    "LOO_MINUS_TRANSPORT": ("REPRESENTATION", "RETRIEVAL_KEYING",
                            "CHARGING_MODEL"),
    "LOO_MINUS_CHARGING": ("REPRESENTATION", "RETRIEVAL_KEYING",
                           "TRANSPORT_MAP"),
}

RULE_REGISTRY = {
    "keying": ("SURFACE_SIGNATURE_V1", "STRUCTURAL_CERTIFICATE_V1"),
    "transport": ("BLIND_PER_SLOT_BINDING_V1", "CERT_C_HOMOMORPHISM_V1"),
    "amortisation": ("NO_AMORTISATION_V1", "CERT_FAMILY_AMORTISATION_V1"),
}


class AdapterDefect(Exception):
    """Fail-closed verdict on an adapter record (never silently accepted)."""


# ------------------------------------------------------------- records -------
def adapter_digest(record):
    """sha256 over the canonical record WITHOUT the digest field itself
    (checker_requirements[1]: any post-hoc adapter edit is drift)."""
    body = {k: v for k, v in record.items() if k != "adapter_sha256"}
    return sha(canonical_json(body))


def make_adapter(arm):
    """Build the canonical frozen adapter record for `arm`.

    Capability fields are set IFF the arm grants the component; ungranted
    components carry their inert rule id (the unchanged-pipeline behaviour):
      keying       SURFACE_SIGNATURE_V1        = existing surface probe
      transport    BLIND_PER_SLOT_BINDING_V1   = existing per-slot adaptation
      amortisation NO_AMORTISATION_V1          = existing per-world charge
    `certificate_digests` is filled at run time by the runner (digests are
    world-pair data from the committed freeze table); the record here binds
    the DIGEST SOURCE, the individual digests ride in the receipts.
    """
    if arm not in ARM_COMPONENTS:
        raise AdapterDefect("unknown arm: %r" % (arm,))
    granted = set(ARM_COMPONENTS[arm])
    rec = {
        "schema": "OCM_DC2_ADAPTER_RECORD",
        "adapter_id": "DC2-ADAPTER-%s" % arm,
        "arm": arm,
        "components_granted": list(ARM_COMPONENTS[arm]),
        "certificate_digest_source":
            "exact/results/DEVCAL1_world_freeze_table.json" if
            "REPRESENTATION" in granted else None,
        "certificate_digests": [],          # filled per world-pair at run time
        "keying_rule_id": "STRUCTURAL_CERTIFICATE_V1"
        if "RETRIEVAL_KEYING" in granted else "SURFACE_SIGNATURE_V1",
        "transport_map_id": "CERT_C_HOMOMORPHISM_V1"
        if "TRANSPORT_MAP" in granted else "BLIND_PER_SLOT_BINDING_V1",
        "amortisation_rule_id": "CERT_FAMILY_AMORTISATION_V1"
        if "CHARGING_MODEL" in granted else "NO_AMORTISATION_V1",
        "grants_authorised": "components_granted only; see "
                             "explicitly_not_authorized_by_this_freeze",
    }
    rec["adapter_sha256"] = adapter_digest(rec)
    return rec


GRANT_RULE = {  # rule id -> the component whose grant it IS
    "STRUCTURAL_CERTIFICATE_V1": "RETRIEVAL_KEYING",
    "CERT_C_HOMOMORPHISM_V1": "TRANSPORT_MAP",
    "CERT_FAMILY_AMORTISATION_V1": "CHARGING_MODEL",
}


# ------------------------------------------------- single-component verifier --
def verify_adapter(rec):
    """checker_requirements[0]: each adapter names EXACTLY its arm's
    components; any extra capability -- in components_granted OR smuggled in
    via a rule id / digest field ('including via adapter side effects') --
    fails closed.  Returns (ok: bool, errors: list[str])."""
    errs = []
    if not isinstance(rec, dict):
        return False, ["record is not a JSON object"]
    arm = rec.get("arm")
    if arm not in ARM_COMPONENTS:
        return False, ["unknown arm: %r" % (arm,)]
    want = ARM_COMPONENTS[arm]
    got = rec.get("components_granted")
    if not isinstance(got, list) or sorted(got) != sorted(want):
        errs.append("components_granted %r != arm set %r (extra or missing "
                    "grant)" % (got, list(want)))
        granted = set(got) if isinstance(got, list) else set()
    else:
        granted = set(got)
    # digest self-consistency (checker_requirements[1])
    if "adapter_sha256" not in rec:
        errs.append("missing adapter_sha256")
    elif rec["adapter_sha256"] != adapter_digest(rec):
        errs.append("adapter_sha256 drift: record edited after digest")
    # capability fields: a GRANT rule id may appear only if granted; a
    # declared grant must carry its rule id (never silently inert)
    kid = rec.get("keying_rule_id")
    tid = rec.get("transport_map_id")
    aid = rec.get("amortisation_rule_id")
    for rid, comp, field in ((kid, "RETRIEVAL_KEYING", "keying_rule_id"),
                             (tid, "TRANSPORT_MAP", "transport_map_id"),
                             (aid, "CHARGING_MODEL", "amortisation_rule_id")):
        if rid in GRANT_RULE and comp not in granted:
            errs.append("side-effect grant: %s=%r grants %s which arm %s "
                        "does not declare" % (field, rid, comp, arm))
    if "RETRIEVAL_KEYING" in granted and kid != "STRUCTURAL_CERTIFICATE_V1":
        errs.append("RETRIEVAL_KEYING granted but keying_rule_id=%r" % (kid,))
    if "TRANSPORT_MAP" in granted and tid != "CERT_C_HOMOMORPHISM_V1":
        errs.append("TRANSPORT_MAP granted but transport_map_id=%r" % (tid,))
    if "CHARGING_MODEL" in granted and aid != "CERT_FAMILY_AMORTISATION_V1":
        errs.append("CHARGING_MODEL granted but amortisation_rule_id=%r"
                    % (aid,))
    # representation content: certificates may ride only with the grant
    dig = rec.get("certificate_digests")
    src = rec.get("certificate_digest_source")
    if "REPRESENTATION" in granted:
        if src is None:
            errs.append("REPRESENTATION granted without digest source")
    else:
        if dig:
            errs.append("certificate digests present without REPRESENTATION "
                        "grant: %r" % (dig,))
        if src is not None:
            errs.append("certificate_digest_source set without "
                        "REPRESENTATION grant")
    return (not errs), errs


def verify_adapter_suite(records, arms=None):
    """A run's adapter suite: every requested arm covered by EXACTLY ONE
    verified record, no unrequested records.  Returns (ok, errors)."""
    errs = []
    want_arms = list(arms) if arms is not None else list(ALL_KO_ARMS)
    seen = {}
    for rec in records:
        arm = rec.get("arm") if isinstance(rec, dict) else None
        ok, rerrs = verify_adapter(rec)
        if not ok:
            errs.extend("[%s] %s" % (arm, e) for e in rerrs)
            continue
        if arm not in want_arms:
            errs.append("adapter for unrequested arm %r" % (arm,))
            continue
        if arm in seen:
            errs.append("duplicate adapter for arm %r" % (arm,))
        seen[arm] = rec
    for arm in want_arms:
        if arm not in seen:
            errs.append("missing adapter for arm %r" % (arm,))
    return (not errs), errs


def load_adapters(path, arms=None):
    """Load a committed adapter file (list of records, or a JSON object
    wrapping {"adapters": [...]}) and fail closed on ANY defect."""
    import json
    with open(path, encoding="utf-8") as f:
        doc = json.load(f)
    records = doc.get("adapters") if isinstance(doc, dict) else doc
    if not isinstance(records, list):
        raise AdapterDefect("adapter file %s is not a record list" % path)
    ok, errs = verify_adapter_suite(records, arms)
    if not ok:
        raise AdapterDefect("adapter suite failed verification: %s"
                            % "; ".join(errs))
    return records


# ------------------------------------------- component prerequisites ----------
COMPONENT_PREREQUISITES = {
    "RETRIEVAL_KEYING": ("REPRESENTATION",),
    "TRANSPORT_MAP": ("REPRESENTATION", "RETRIEVAL_KEYING"),
    "CHARGING_MODEL": ("REPRESENTATION",),
}


def effective_components(rec):
    """What the unchanged runner can actually OPERATE from this record.
    A component whose prerequisite is not granted degrades to the
    unchanged-pipeline behaviour (recorded, never silent) -- this is the
    leave-one-out semantics: removing REPRESENTATION collapses certificate
    keying and transport because their input content no longer exists.
    Returns (effective: set, degradations: dict comp -> reason)."""
    granted = set(rec.get("components_granted") or [])
    effective, degraded = set(granted), {}
    for comp, prereqs in COMPONENT_PREREQUISITES.items():
        if comp in granted:
            missing = [p for p in prereqs if p not in granted]
            if missing:
                effective.discard(comp)
                degraded[comp] = (
                    "prerequisite component(s) %s not granted; degrades to "
                    "unchanged-pipeline behaviour" % ",".join(missing))
    return effective, degraded


# ------------------------------------------------ amortisation (data-derived) --
def cert_family_key(structural_check):
    """The certificate CONTENT key for amortisation: the canonical root hash
    of the shared decomposition (certificate (a) detail), falling back to the
    certificate digest.  Two worlds share an amortisation family iff they
    share this key -- derived from the committed checker output, never tuned.
    None when no certificate is held (family size 1: nothing to amortise)."""
    if not structural_check or structural_check.get("latent_same") is not True:
        return None
    a = ((structural_check.get("checks") or {}).get("a") or {})
    return a.get("canonical_t") or structural_check.get("certificate_digest")


def amortisation_divisor(structural_check, cert_rows):
    """CERT_FAMILY_AMORTISATION_V1: divide the measured per-world acquisition
    by the number of frozen worlds carrying the SAME certificate content key.

    `cert_rows` = the per-world structural checks of the FROZEN matrix,
    recomputed by the UNCHANGED checker on the UNCHANGED world code (frozen
    seeds; deterministic) and digest-matched against the committed
    DEVCAL1_world_freeze_table.json by the caller -- so the divisor is
    derived from committed data, never tuned.  Divisor >= 1; worlds without
    a certificate amortise over 1 (recorded)."""
    key = cert_family_key(structural_check)
    if key is None:
        return 1, None
    n = sum(1 for row in cert_rows if cert_family_key(row) == key)
    return max(1, n), key
