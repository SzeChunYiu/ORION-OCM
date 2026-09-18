#!/usr/bin/env python3
"""Route A: apply the FROZEN v2 maturity rule to the W4 correction delta.

Registered by research/gmi-833-maturity-rescore-v3-w4-v1/FREEZE_V3_W4.md.

This executor re-labels already-registered evidence under an already-frozen
rule. It creates no evidence and edits no frozen artifact: it reads
THEOREM_SCORES_V2.json and the corpus-passes verdict registers read-only and
writes only inside its own package directory.

Exact integer arithmetic throughout; no float appears in any claim.
Py3.8-safe, stdlib only. Run:  python3 -I -B rescore_v3_w4.py
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from typing import Dict, List, Optional, Sequence, Tuple

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, os.pardir, os.pardir))

# ---------------------------------------------------------------------------
# Frozen constants (FREEZE_V3_W4.md).  Every one is re-verified at run time.
# ---------------------------------------------------------------------------
SOURCE_MAIN = "5126041da7ce608f69157f281ca492ac9618c8e4"
CLAIM_CEILING = "AUDIT_RELABEL_ONLY"

SCORES_REL = "research/gmi-833-maturity-rescore-v2-v1/THEOREM_SCORES_V2.json"
SCORES_BLOB = "0cfca31894960e24c1c12bb7bf05f9e13e63f4aa"
REGISTER_RELS = (
    "research/gmi-833-corpus-passes-v2-v1/VERDICT_REGISTER_V1.json",
    "research/gmi-833-corpus-passes-v2-v1/VERDICT_REGISTER_APPEND_REV_L45_073_V1.json",
    "research/gmi-833-corpus-passes-v2-v1/VERDICT_REGISTER_APPEND_REV_L46_V1.json",
    "research/gmi-833-corpus-passes-v2-v1/VERDICT_REGISTER_APPEND_REV_L47_W4_V1.json",
    "research/gmi-833-corpus-passes-v2-v1/VERDICT_REGISTER_L47_REV_ADDENDUM_V1.json",
)
REGISTER_BLOBS = {
    "VERDICT_REGISTER_V1.json": "a996877453bfdd8fd89b4254e3dc765d23403bae",
    "VERDICT_REGISTER_APPEND_REV_L45_073_V1.json": "e4867ac3c14816b372f8043a8b9d85b61d696b0e",
    "VERDICT_REGISTER_APPEND_REV_L46_V1.json": "7d9f593dcea4566ecd1117c423be03b825a0de87",
    "VERDICT_REGISTER_APPEND_REV_L47_W4_V1.json": "3dd709b7fe912ffae47df8e4330ae68e7d6edfe2",
    "VERDICT_REGISTER_L47_REV_ADDENDUM_V1.json": "578f7ed8229b38c23739f032f3281b2b86e93b13",
}

PARENT_PKG = "gmi-novel-intelligence-w4-v1"
ARRIVAL_PKG = "gmi-novel-intelligence-w4-prospective-v1"
PARENT_DIR = "research/" + PARENT_PKG
ARRIVAL_DIR = "research/" + ARRIVAL_PKG
PARENT_ROW_ID = "GMI833_V2_LEGACY_074_W4-C"

# Parent custody, as adjudicated by #976 and independently re-verified here.
PARENT_FREEZE_FILES = ("FREEZE_V1.md",)
PARENT_OUTCOME_FILES = ("RESULT_V1.json",)
# Arrival custody lives on the PR-#988 branch, anchored by pushed tags.
ARRIVAL_FREEZE_FILES = ("FREEZE_V2_PROSPECTIVE.md", "FREEZE_V2_PROSPECTIVE.json")
ARRIVAL_OUTCOME_FILES = ("RESULT_V1.json", "RECEIPT_MULTIHOST_V1.json", "RUNTIME_V1.json")
ARRIVAL_FREEZE_COMMIT = "56195abea700795d40ccc3761676cea68602fe24"
ARRIVAL_RESULTS_COMMIT = "81d1b9c3f93f2286ab2f3d1df3bf25f70ce218bf"
ARRIVAL_FREEZE_TAG = "rev-l47-w4-freeze-custody"
ARRIVAL_RESULTS_TAG = "rev-l47-w4-results"
ARRIVAL_FREEZE_BLOBS = {
    "FREEZE_V2_PROSPECTIVE.md": "ec68c133d35608b8632250944230ac5f930a481f",
    "FREEZE_V2_PROSPECTIVE.json": "ae20c46f8895efea46da016697d1b0590647c702",
}

# Frozen support-kind table, imported UNCHANGED from
# research/gmi-833-maturity-rescore-v2-v1/FREEZE_V2.md section 4.
SUPPORT_TABLE = {
    "ANALYTIC_PROOF_EXPLICIT": ("EV1", "M1"),
    "ANALYTIC_PROOF_BARE": ("EV0", "M0"),
    "MECHANIZED_PROOF": ("EV1", "M1"),
    "EXACT_FINITE_CERTIFICATE": ("EV2", "M2"),
    "FROZEN_HELDOUT": ("EV3", "M4"),
    "SAMPLED_STATISTICAL": ("UNKNOWN", "M0"),
    "EMPIRICAL_UNFROZEN": ("UNKNOWN", "M0"),
    "PROTOCOL_ONLY": ("EV0", "M0"),
    "LEDGER_ENTRY": ("EV0", "M0"),
    "NONE_FOUND": ("UNKNOWN", "UNKNOWN"),
}
# Ceiling map, frozen (v1 section 2 rule 2).
CEILING = {"EV0": "M1", "EV1": "M2", "EV2": "M3", "EV3": "M4", "EV4": "M5", "EV5": "M6"}
M_ORDER = ("M0", "M1", "M2", "M3", "M4", "M5", "M6")

PUBLISHED_M = {"M0": 48, "M1": 30, "M2": 89, "M3": 6, "M4": 23, "UNKNOWN": 1}
PUBLISHED_EV = {"EV0": 46, "EV1": 30, "EV2": 95, "EV3": 23, "UNKNOWN": 3}


# ---------------------------------------------------------------------------
# small helpers
# ---------------------------------------------------------------------------
def rel(path):
    # type: (str) -> str
    return os.path.join(REPO, path)


def read_bytes(path):
    # type: (str) -> bytes
    with open(rel(path), "rb") as fh:
        return fh.read()


def git_blob_sha1(path):
    # type: (str) -> str
    """git's blob object id, recomputed from disk without invoking git."""
    data = read_bytes(path)
    header = ("blob %d" % len(data)).encode("ascii") + b"\0"
    return hashlib.sha1(header + data).hexdigest()


def load_json(path):
    # type: (str) -> object
    with open(rel(path), "r") as fh:
        return json.load(fh)


def git(args):
    # type: (Sequence[str]) -> Optional[str]
    """Run a git plumbing command. None means UNAVAILABLE, never 'fine'."""
    try:
        p = subprocess.Popen(
            ["git", "-C", REPO] + list(args),
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        )
        out, _ = p.communicate()
    except OSError:
        return None
    if p.returncode != 0:
        return None
    return out.decode("utf-8", "replace")


def git_rc(args):
    # type: (Sequence[str]) -> Optional[int]
    try:
        p = subprocess.Popen(
            ["git", "-C", REPO] + list(args),
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        )
        p.communicate()
    except OSError:
        return None
    return p.returncode


def object_exists(rev):
    # type: (str) -> bool
    return git(["cat-file", "-e", rev + "^{commit}"]) is not None


def first_add_commit(ref, path):
    # type: (str, str) -> Optional[str]
    out = git(["log", ref, "--diff-filter=A", "--format=%H", "--", path])
    if out is None:
        return None
    lines = [ln.strip() for ln in out.splitlines() if ln.strip()]
    return lines[0] if lines else ""


def is_ancestor(a, b):
    # type: (str, str) -> Optional[bool]
    rc = git_rc(["merge-base", "--is-ancestor", a, b])
    if rc is None or rc not in (0, 1):
        return None
    return rc == 0


# ---------------------------------------------------------------------------
# custody predicate -- the FROZEN_HELDOUT precondition, mechanically decided
# ---------------------------------------------------------------------------
PRECEDES = "FREEZE_PRECEDES_OUTCOME"
NOT_PRECEDES = "OUTCOME_PRECEDES_FREEZE"
SINGLE = "SINGLE_COMMIT_INDETERMINATE_ON_THIS_REF"
UNAVAIL = "OBJECTS_UNAVAILABLE__NOT_CHECKED"


def custody_on_ref(ref, pkg_dir, freeze_files, outcome_files):
    # type: (str, str, Sequence[str], Sequence[str]) -> Tuple[str, Dict]
    """Decide freeze-vs-outcome add order on one ref.

    Returns a typed state; OBJECTS_UNAVAILABLE is NEVER conflated with 'fine'.
    """
    detail = {"ref": ref, "freeze_adds": {}, "outcome_adds": {}}
    if not object_exists(ref):
        return UNAVAIL, detail
    fz = {}
    for f in freeze_files:
        c = first_add_commit(ref, pkg_dir + "/" + f)
        if c is None:
            return UNAVAIL, detail
        fz[f] = c
    oc = {}
    for f in outcome_files:
        c = first_add_commit(ref, pkg_dir + "/" + f)
        if c is None:
            return UNAVAIL, detail
        oc[f] = c
    detail["freeze_adds"] = fz
    detail["outcome_adds"] = oc
    fz_c = [c for c in fz.values() if c]
    oc_c = [c for c in oc.values() if c]
    if not fz_c or not oc_c:
        return UNAVAIL, detail
    verdicts = []
    for f in fz_c:
        for o in oc_c:
            if f == o:
                verdicts.append(SINGLE)
                continue
            a = is_ancestor(f, o)
            b = is_ancestor(o, f)
            if a is None or b is None:
                return UNAVAIL, detail
            if a and not b:
                verdicts.append(PRECEDES)
            elif b and not a:
                verdicts.append(NOT_PRECEDES)
            else:
                verdicts.append(SINGLE)
    detail["pairwise"] = sorted(set(verdicts))
    # Conservative: any outcome-before-freeze pair poisons the whole claim.
    if NOT_PRECEDES in verdicts:
        return NOT_PRECEDES, detail
    if SINGLE in verdicts:
        return SINGLE, detail
    return PRECEDES, detail


def arrival_custody():
    # type: () -> Dict
    """Arrival custody: indeterminate on main, decided on the tag-anchored branch.

    The bridge that licenses reading branch evidence onto source_main is blob
    identity of the freeze documents.
    """
    on_main, main_detail = custody_on_ref("HEAD", ARRIVAL_DIR, ARRIVAL_FREEZE_FILES, ARRIVAL_OUTCOME_FILES)
    branch_ref = ARRIVAL_RESULTS_COMMIT
    if not object_exists(branch_ref):
        branch_ref = ARRIVAL_RESULTS_TAG + "^{commit}"
    on_branch, branch_detail = custody_on_ref(branch_ref, ARRIVAL_DIR, ARRIVAL_FREEZE_FILES, ARRIVAL_OUTCOME_FILES)

    # The freeze commit's tree must contain the freeze files and nothing else
    # of the package: no executor, no result, no test.
    tree_at_freeze = None
    out = git(["ls-tree", "-r", "--name-only", ARRIVAL_FREEZE_COMMIT, "--", ARRIVAL_DIR + "/"])
    if out is not None:
        tree_at_freeze = sorted(ln.strip() for ln in out.splitlines() if ln.strip())
    freeze_tree_is_exactly_the_freeze = (
        tree_at_freeze is not None
        and tree_at_freeze == sorted(ARRIVAL_DIR + "/" + f for f in ARRIVAL_FREEZE_FILES)
    )

    # Blob bridge: freeze blobs on disk == blobs at the branch freeze commit.
    blob_bridge = {}
    bridge_ok = True
    for f, pinned in sorted(ARRIVAL_FREEZE_BLOBS.items()):
        disk = git_blob_sha1(ARRIVAL_DIR + "/" + f)
        at_freeze = git(["rev-parse", ARRIVAL_FREEZE_COMMIT + ":" + ARRIVAL_DIR + "/" + f])
        at_freeze = at_freeze.strip() if at_freeze else None
        blob_bridge[f] = {"pinned": pinned, "on_disk": disk, "at_freeze_commit": at_freeze}
        if disk != pinned:
            bridge_ok = False
        if at_freeze is not None and at_freeze != pinned:
            bridge_ok = False

    tags = {}
    for tag, expect in ((ARRIVAL_FREEZE_TAG, ARRIVAL_FREEZE_COMMIT), (ARRIVAL_RESULTS_TAG, ARRIVAL_RESULTS_COMMIT)):
        got = git(["rev-parse", tag + "^{commit}"])
        tags[tag] = {"expected": expect, "resolved": got.strip() if got else None}

    holds = (
        on_branch == PRECEDES
        and freeze_tree_is_exactly_the_freeze
        and bridge_ok
    )
    return {
        "on_source_main": on_main,
        "on_source_main_detail": main_detail,
        "on_pr988_branch": on_branch,
        "on_pr988_branch_detail": branch_detail,
        "freeze_commit_tree": tree_at_freeze,
        "freeze_tree_is_exactly_the_freeze": freeze_tree_is_exactly_the_freeze,
        "blob_bridge": blob_bridge,
        "blob_bridge_ok": bridge_ok,
        "custody_tags": tags,
        "custody_holds": bool(holds),
        "note": (
            "Custody is NOT demonstrable from main alone: PR #988 squash-merged the "
            "whole package into one commit. It IS demonstrable on the tag-anchored "
            "branch, and blob identity of the freeze documents bridges that evidence "
            "onto source_main."
        ),
    }


# ---------------------------------------------------------------------------
# the frozen rule, applied
# ---------------------------------------------------------------------------
def apply_rule(support_kind, prior_free_recovery):
    # type: (str, bool) -> Tuple[str, str]
    if support_kind not in SUPPORT_TABLE:
        raise KeyError("support kind outside the frozen table: %r" % (support_kind,))
    ev, m = SUPPORT_TABLE[support_kind]
    if support_kind == "EXACT_FINITE_CERTIFICATE" and prior_free_recovery:
        m = "M3"  # v1 carve-out, only when the P3/P4 condition is itself evidenced
    if ev in CEILING:
        cap = CEILING[ev]
        if m in M_ORDER and cap in M_ORDER and M_ORDER.index(m) > M_ORDER.index(cap):
            raise AssertionError("ceiling violation %s > %s" % (m, cap))
    return ev, m


def executor_is_exact(path):
    # type: (str) -> Dict
    """Evidence that a support kind is EXACT_FINITE_CERTIFICATE and not sampled."""
    src = read_bytes(path).decode("utf-8", "replace")
    code_lines = []
    for ln in src.splitlines():
        s = ln.strip()
        if s.startswith("#"):
            continue
        code_lines.append(ln)
    code = "\n".join(code_lines)
    return {
        "path": path,
        "float_literal_or_cast": ("float(" in code) or (" float " in code),
        "imports_random": ("import random" in code) or ("from random" in code),
        "imports_numpy": "numpy" in code,
        "samples": ("montecarlo" in code.lower()) or ("random.Random" in code),
    }


def parent_record(custody_state, exactness):
    # type: (str, Dict) -> Dict
    frozen_heldout_available = custody_state == PRECEDES
    if frozen_heldout_available:
        raise AssertionError(
            "P1 falsified: parent custody reads %s, so FROZEN_HELDOUT would still "
            "be available and this correction would be unfounded." % custody_state
        )
    exact = not (
        exactness["float_literal_or_cast"]
        or exactness["imports_random"]
        or exactness["imports_numpy"]
        or exactness["samples"]
    )
    if not exact:
        support = "EMPIRICAL_UNFROZEN"
        reason = "G2 rubric gap: unfrozen and sampled"
    else:
        support = "EXACT_FINITE_CERTIFICATE"
        reason = (
            "FROZEN_HELDOUT is unavailable (its frozen precondition 'freeze artifact "
            "precedes outcome' is FALSE for this package: #976 L47 CONFIRMED, "
            "independently re-verified here). The surviving observed support is the "
            "exhaustive exact checker over the declared bounded universe "
            "F(k) k in {2,3,4} + held-out k=5 + fixed budget B=3: integer-only, no "
            "float, no sampling, no RNG. The G2 row "
            "(SAMPLED_STATISTICAL/EMPIRICAL_UNFROZEN -> UNKNOWN/M0) therefore does "
            "NOT apply: it targets support that is ONLY unfrozen and sampled, and "
            "this package's exactness was never in question and is not what the "
            "audit falsified."
        )
    ev, m = apply_rule(support, prior_free_recovery=False)
    return {
        "result_id": PARENT_ROW_ID,
        "package": PARENT_PKG,
        "theorem_name": "W4-C",
        "tranche": "LEGACY_173",
        "delta_kind": "DOWN_GENERATING",
        "down_generating": True,
        "individually_verified": True,
        "spot_verified": True,
        "verification_note": (
            "v3-W4 adjudicator full read of FORMALIZATION_V1.md (W4-C statement), "
            "RESULT_V1.json (all boxes, held-out k=5), novel_intelligence_w4_v1.py "
            "(exactness scan), FREEZE_V1.md (the falsified prospectiveness claim), "
            "plus independent git custody re-verification. The v2 row was "
            "individually_verified=false; this one is not."
        ),
        "support_kind": support,
        "evidence_EV": ev,
        "maturity_M": m,
        "prior_free_recovery": False,
        "prior_standing": "v2 row GMI833_V2_LEGACY_074_W4-C: M4/EV3, support FROZEN_HELDOUT, individually_verified=false",
        "supersedes": {"maturity_M": "M4", "evidence_EV": "EV3", "support_kind": "FROZEN_HELDOUT"},
        "justification": reason,
        "m3_refused_because": (
            "the P3/P4 architecture-prior-free condition is not evidenced: the family "
            "F(k) is registered by this package itself, so the search saw the target "
            "family. v2 expected the M3 carve-out only for the aj9* blind-recovery family."
        ),
        "citation_paths": [
            PARENT_DIR + "/FORMALIZATION_V1.md",
            PARENT_DIR + "/FREEZE_V1.md",
            PARENT_DIR + "/RESULT_V1.json",
            PARENT_DIR + "/novel_intelligence_w4_v1.py",
            "research/gmi-833-corpus-passes-v2-v1/VERDICT_REGISTER_V1.json",
            SCORES_REL,
        ],
        "forbidden_extrapolations": [
            "PARENT_RESTORED_TO_M4_BY_THE_PROSPECTIVE_CHILD",
            "COMMIT_ORDER_DEFECT_ERASED",
            "EXACTNESS_OF_THE_W4_CERTIFICATE_IN_DOUBT",
        ],
        "exactness_scan": exactness,
        "custody_state": custody_state,
    }


def arrival_record(custody):
    # type: (Dict) -> Dict
    if not custody["custody_holds"]:
        raise AssertionError(
            "P3 falsified: the arrival's custody does NOT hold "
            "(branch=%s, freeze-tree-clean=%s, blob-bridge=%s). Report this loudly; "
            "do NOT score it M4." % (
                custody["on_pr988_branch"],
                custody["freeze_tree_is_exactly_the_freeze"],
                custody["blob_bridge_ok"],
            )
        )
    support = "FROZEN_HELDOUT"
    ev, m = apply_rule(support, prior_free_recovery=False)
    return {
        "result_id": "GMI833_V3_ARRIVAL_W4P_REV-L47-NOVEL-INTELLIGENCE-W4",
        "package": ARRIVAL_PKG,
        "theorem_name": "W4P-REPLICATION (registered prospective prediction set of FREEZE_V2_PROSPECTIVE, decision flags D1-D5)",
        "tranche": "ARRIVALS_V3_W4",
        "delta_kind": "NEW_SCORE",
        "down_generating": False,
        "individually_verified": True,
        "spot_verified": True,
        "verification_note": (
            "v3-W4 adjudicator full read of FREEZE_V2_PROSPECTIVE.md/.json, "
            "RESULT_V1.json, RECEIPT_MULTIHOST_V1.json, independent_route_v1.py and "
            "the package tests, plus independent git custody verification both ways "
            "(git log --diff-filter=A and merge-base --is-ancestor) rather than "
            "trusting the freeze's own text."
        ),
        "support_kind": support,
        "evidence_EV": ev,
        "maturity_M": m,
        "prior_free_recovery": False,
        "prior_standing": "UNSCORED in v2 (outside both frozen inclusion lists; see gap G-NAME)",
        "admitted_under": (
            "v2 section 3 'closest typed rule' convention; recorded gap G-NAME: the Gap 2 "
            "arrivals rule filters by the directory name glob gmi-833-*, which no "
            "revival package for a non-833-named parent can ever satisfy."
        ),
        "justification": (
            "FROZEN_PRE_OUTCOME, and here the frozen precondition is actually met: "
            "FREEZE_V2_PROSPECTIVE.{md,json} are the only package files present at "
            "commit %s, which is a strict ancestor of the executor commit and of the "
            "results commit %s, with the reverse false both ways; the freeze blobs on "
            "source_main are byte-identical to those at the freeze commit. "
            "Registered held-out predictions (extended held-out k in {6,7,8}, negative "
            "control, D1-D5) were recorded before the outcomes existed and all matched."
            % (ARRIVAL_FREEZE_COMMIT[:8], ARRIVAL_RESULTS_COMMIT[:8])
        ),
        "m5_refused_because": (
            "RECEIPT_MULTIHOST_V1.json shows 2 hosts and 2 Python versions bit-identical, "
            "which resembles EV4. The frozen table forbids it in the same cell: "
            "'never M5: intra-package != independent replication' (v1 rule 2). Same "
            "package, same authors, same code."
        ),
        "citation_paths": [
            ARRIVAL_DIR + "/FREEZE_V2_PROSPECTIVE.md",
            ARRIVAL_DIR + "/FREEZE_V2_PROSPECTIVE.json",
            ARRIVAL_DIR + "/RESULT_V1.json",
            ARRIVAL_DIR + "/RECEIPT_MULTIHOST_V1.json",
            ARRIVAL_DIR + "/independent_route_v1.py",
            "research/gmi-833-corpus-passes-v2-v1/VERDICT_REGISTER_APPEND_REV_L47_W4_V1.json",
        ],
        "forbidden_extrapolations": [
            "PARENT_COMMIT_ORDER_DEFECT_ERASED",
            "EV4_OR_M5_FROM_THE_MULTIHOST_RECEIPT",
            "W4_DOMAIN_STATUS_BEYOND_THE_REGISTERED_FINITE_FAMILY",
        ],
        "custody": custody,
    }


# ---------------------------------------------------------------------------
# census: distributions
# ---------------------------------------------------------------------------
def distribution(rows, key):
    # type: (Sequence[Dict], str) -> Dict[str, int]
    out = {}
    for r in rows:
        v = r.get(key, "UNKNOWN")
        out[v] = out.get(v, 0) + 1
    return out


def corrected_rows(published_rows, delta_records):
    # type: (Sequence[Dict], Sequence[Dict]) -> List[Dict]
    by_id = {}
    order = []
    for r in published_rows:
        by_id[r["result_id"]] = dict(r)
        order.append(r["result_id"])
    for d in delta_records:
        rid = d["result_id"]
        if rid in by_id:
            by_id[rid]["maturity_M"] = d["maturity_M"]
            by_id[rid]["evidence_EV"] = d["evidence_EV"]
            by_id[rid]["support_kind"] = d["support_kind"]
            by_id[rid]["individually_verified"] = True
        else:
            by_id[rid] = {
                "result_id": rid,
                "package": d["package"],
                "maturity_M": d["maturity_M"],
                "evidence_EV": d["evidence_EV"],
                "support_kind": d["support_kind"],
                "individually_verified": True,
                "justification": d["justification"],
            }
            order.append(rid)
    return [by_id[r] for r in order]


def delta_counts(new, old):
    # type: (Dict[str,int], Dict[str,int]) -> Dict[str,int]
    keys = sorted(set(list(new.keys()) + list(old.keys())))
    return dict((k, new.get(k, 0) - old.get(k, 0)) for k in keys)


# ---------------------------------------------------------------------------
# W4R-4: propagation sweep
# ---------------------------------------------------------------------------
TIER1 = "CONFIRMED_ADVERSE"
TIER2 = "GAP_STATE_ADVERSE"
NOT_ADVERSE = "NOT_ADVERSE__SELF_TYPED_SCREEN_FALSE_POSITIVE"

REFLECTED = "REFLECTED"
UNREFLECTED = "UNREFLECTED"
IMMATERIAL = "REFLECTED_OR_IMMATERIAL_TO_SCORE"
OUT_OF_POP = "OUT_OF_SCORED_POPULATION"

# Explicit, auditable enumeration of every adverse verdict carried by the
# registers, with the register path each is read from.  Route B rediscovers
# this population by a schema-agnostic recursive walk instead.
def adverse_population(registers):
    # type: (Dict[str, object]) -> List[Dict]
    reg = registers["VERDICT_REGISTER_V1.json"]
    out = []  # type: List[Dict]

    for i, c in enumerate(reg["L47_post_hoc"]["confirmed"]):
        out.append({
            "id": "L47.confirmed[%d]" % i, "package": c["package"], "tier": TIER1,
            "verdict": c["verdict"], "source": "VERDICT_REGISTER_V1.json:L47_post_hoc.confirmed",
        })
    for i, s in enumerate(reg["L47_post_hoc"]["typed_post_hoc"]):
        pkg = s.split(" (")[0].strip()
        tier = NOT_ADVERSE if "screen false positive" in s else TIER2
        out.append({
            "id": "L47.typed_post_hoc[%d]" % i, "package": pkg, "tier": tier,
            "verdict": s[:160], "source": "VERDICT_REGISTER_V1.json:L47_post_hoc.typed_post_hoc",
        })
    # overclaiming freeze texts: register self-types them "gap states, not defects"
    for short in ("g0-grammar-growth", "unseen-form-prediction", "capability-held-freeze",
                  "capability-transfer-freeze", "af-barrier-context"):
        out.append({
            "id": "L47.overclaiming[%s]" % short, "package_fragment": short, "tier": TIER2,
            "verdict": "freeze text claims prospective registration while custody cannot demonstrate it",
            "source": "VERDICT_REGISTER_V1.json:L47_post_hoc.overclaiming_freeze_texts",
        })
    for i, c in enumerate(reg["L49_L53_cost_accounting"]["confirmed"]):
        out.append({
            "id": "L49_L53.confirmed[%d]" % i, "package": c["package"], "tier": TIER1,
            "verdict": "%s / %s" % (c["verdict_L49"], c["verdict_L53"]),
            "source": "VERDICT_REGISTER_V1.json:L49_L53_cost_accounting.confirmed",
        })
    l58 = reg["L58_applied_downgrade"]
    out.append({
        "id": "L58.registered_defect", "package": l58["target"].split("/")[1], "tier": TIER1,
        "verdict": l58["registered_defect"][:160],
        "source": "VERDICT_REGISTER_V1.json:L58_applied_downgrade.registered_defect",
    })
    rev45 = registers["VERDICT_REGISTER_APPEND_REV_L45_073_V1.json"]["prior_verdict"]
    out.append({
        "id": "REV_L45_073.prior_verdict", "package": rev45["package"], "tier": TIER2,
        "verdict": rev45["verdict"], "result_id": rev45["result_id"],
        "source": "VERDICT_REGISTER_APPEND_REV_L45_073_V1.json:prior_verdict",
    })
    rev47 = registers["VERDICT_REGISTER_APPEND_REV_L47_W4_V1.json"]["prior_verdict"]
    out.append({
        "id": "REV_L47_W4.prior_verdict", "package": rev47["package"], "tier": TIER1,
        "verdict": rev47["verdict"],
        "source": "VERDICT_REGISTER_APPEND_REV_L47_W4_V1.json:prior_verdict",
    })
    add = registers["VERDICT_REGISTER_L47_REV_ADDENDUM_V1.json"]["population_disposition"]
    for cls, pkgs in sorted(add.items()):
        for p in pkgs:
            out.append({
                "id": "L47_ADDENDUM.%s[%s]" % (cls, p), "package": p, "tier": TIER2,
                "verdict": "CUSTODY_NON_DEMONSTRABLE at the L47 screen; revived %s" % cls,
                "source": "VERDICT_REGISTER_L47_REV_ADDENDUM_V1.json:population_disposition",
            })
    # verdict-bearing sections that adjudicated to zero confirmed defects are
    # recorded explicitly so a 'zero found' claim has a justified scope.
    for sec in ("L51_hidden_iid_stationarity", "L52_hidden_finite_horizon",
                "L54_L55_encoding_search_sensitivity", "L56_parent_rediscovery"):
        body = reg[sec]
        n = body.get("confirmed_defects", None)
        if n != 0:
            raise AssertionError("section %s no longer reports 0 confirmed defects: %r" % (sec, n))
    return out


def resolve_package(fragment, scored_packages):
    # type: (str, Sequence[str]) -> List[str]
    if fragment in scored_packages:
        return [fragment]
    hits = [p for p in scored_packages if fragment in p]
    return sorted(hits)


def classify(entry, rows_by_pkg):
    # type: (Dict, Dict[str, List[Dict]]) -> Dict
    frag = entry.get("package") or entry.get("package_fragment")
    matches = resolve_package(frag, sorted(rows_by_pkg.keys()))
    res = dict(entry)
    res["resolved_packages"] = matches
    if entry["tier"] == NOT_ADVERSE:
        res["outcome"] = NOT_ADVERSE
        res["reason"] = "the register itself types this a screen false positive; not an adverse verdict"
        return res
    if not matches:
        res["outcome"] = OUT_OF_POP
        res["reason"] = (
            "no row in THEOREM_SCORES_V2.json carries this package: it is outside the "
            "scored population (173 census objects + 24 gmi-833-* arrivals), not a "
            "scoring defect"
        )
        return res
    exposed = []
    for p in matches:
        for r in rows_by_pkg[p]:
            if r.get("maturity_M") in ("M4", "M5", "M6") or r.get("support_kind") == "FROZEN_HELDOUT":
                exposed.append(r)
    if not exposed:
        res["outcome"] = IMMATERIAL
        res["reason"] = "package is scored, but no row sits at M4+ or on FROZEN_HELDOUT support"
        return res
    needle_parts = []
    for tok in ("POST_HOC", "CUSTODY", "OVERSTRONG", "UNAUDITED", "NON_DEMONSTRABLE", "DEGENERATE"):
        needle_parts.append(tok)
    unreflected = []
    for r in exposed:
        blob = " ".join([
            str(r.get("justification", "")), str(r.get("verification_note", "")),
            str(r.get("claim_evidence_gap", "")), " ".join(r.get("forbidden_extrapolations", []) or []),
        ]).upper()
        if not any(tok in blob for tok in needle_parts):
            unreflected.append(r["result_id"])
    if unreflected:
        res["outcome"] = UNREFLECTED
        res["unreflected_rows"] = sorted(unreflected)
        res["reason"] = (
            "rows at M4+/FROZEN_HELDOUT whose justification, verification_note, "
            "claim_evidence_gap and forbidden_extrapolations never mention the finding"
        )
    else:
        res["outcome"] = REFLECTED
        res["reason"] = "every exposed row mentions the finding"
    return res


def sweep(registers, rows):
    # type: (Dict[str, object], Sequence[Dict]) -> Dict
    rows_by_pkg = {}  # type: Dict[str, List[Dict]]
    for r in rows:
        rows_by_pkg.setdefault(r["package"], []).append(r)
    pop = adverse_population(registers)
    results = [classify(e, rows_by_pkg) for e in pop]
    counts = {}
    for r in results:
        counts[r["outcome"]] = counts.get(r["outcome"], 0) + 1
    return {
        "checked": len(results),
        "counts": counts,
        "by_outcome": dict(
            (k, sorted(set(r.get("package") or r.get("package_fragment") for r in results if r["outcome"] == k)))
            for k in sorted(counts)
        ),
        "unreflected_detail": [r for r in results if r["outcome"] == UNREFLECTED],
        "results": results,
    }


# ---------------------------------------------------------------------------
# W4R-4 downstream adjudication of each UNREFLECTED flag
#
# The sweep FLAGS.  A flag is not a finding until it is verified against the
# artifact, by the same machinery used for the arrival.  This is the freeze's
# "validate the checker, verify each finding" discipline applied to the
# checker's own output; the sweep's outcome typing above is untouched.
# ---------------------------------------------------------------------------
G0_PKG = "gmi-833-g0-grammar-growth-v1"
G0_DIR = "research/" + G0_PKG
G0_BRANCH = "65073060b1af5b7c863c883307ff5279c783892c"      # research/833-g0-grammar-expansion-v1 on origin
G0_FREEZE_COMMIT = "10f0ef372d3068dcbfb9021d6a53b20ba576f39d"
G0_FREEZE_FILES = ("FREEZE_V1.md", "FROZEN_FIXTURES_V1.json")
G0_OUTCOME_FILES = ("RESULT_V1.json", "ORACLE_RESULT_V1.json", "g0_grammar_growth_v1.py")
G0_WORDING_COMMIT = "f4d9d7d55fb009213d4068235e510f960907036e"  # #947 terminology migration v2


def adjudicate_g0():
    # type: () -> Dict
    """Is the g0-grammar-growth M4 score actually wrong, or is the flag a
    squash-merge artifact like the arrival's?  Decided mechanically."""
    on_main, _md = custody_on_ref("HEAD", G0_DIR, G0_FREEZE_FILES, G0_OUTCOME_FILES)
    branch_available = object_exists(G0_BRANCH)
    on_branch = UNAVAIL
    tree = None
    if branch_available:
        on_branch, _bd = custody_on_ref(G0_BRANCH, G0_DIR, G0_FREEZE_FILES, G0_OUTCOME_FILES)
        out = git(["ls-tree", "-r", "--name-only", G0_FREEZE_COMMIT, "--", G0_DIR + "/"])
        if out is not None:
            tree = sorted(ln.strip() for ln in out.splitlines() if ln.strip())
    tree_clean = tree is not None and tree == sorted(G0_DIR + "/" + f for f in G0_FREEZE_FILES)

    # The freeze blob differs between branch and main.  Decide whether that is
    # a re-freeze or a wording migration, from git, not from prose.
    at_freeze = git(["rev-parse", G0_FREEZE_COMMIT + ":" + G0_DIR + "/FREEZE_V1.md"])
    at_main = git(["rev-parse", "HEAD:" + G0_DIR + "/FREEZE_V1.md"])
    at_freeze = at_freeze.strip() if at_freeze else None
    at_main = at_main.strip() if at_main else None
    touching = git(["log", "HEAD", "--format=%H", "--", G0_DIR + "/FREEZE_V1.md"])
    touching = [ln.strip() for ln in touching.splitlines() if ln.strip()] if touching else []
    changed_only_by_wording_migration = (
        len(touching) == 2 and touching[0] == G0_WORDING_COMMIT
    )
    numstat = git(["diff", "--numstat", G0_FREEZE_COMMIT, "HEAD", "--", G0_DIR + "/FREEZE_V1.md"])
    added = removed = None
    if numstat:
        parts = numstat.split()
        if len(parts) >= 2 and parts[0].isdigit() and parts[1].isdigit():
            added, removed = int(parts[0]), int(parts[1])
    wording_only = (
        changed_only_by_wording_migration and added is not None
        and added == removed and added <= 4
    )

    sustained = (on_branch == PRECEDES) and tree_clean and wording_only
    if not branch_available or on_branch == UNAVAIL:
        verdict = "NOT_ADJUDICABLE__BRANCH_OBJECTS_UNAVAILABLE"
    elif sustained:
        verdict = "SCORE_SUSTAINED__FLAG_IS_A_SQUASH_ARTIFACT"
    else:
        verdict = "SCORE_NOT_SUSTAINED__ESCALATE_TO_THE_OWNING_LANE"
    if verdict.startswith("SCORE_SUSTAINED"):
        note = (
            "The M4/EV3 score for this package STANDS and is not altered by this "
            "tranche. Its freeze document and frozen fixtures are the only package "
            "files present at the freeze commit, which strictly precedes the "
            "implementation commit on the origin branch; the only post-merge change "
            "to the freeze on main is the #947 terminology migration's heading "
            "renames (equal added/removed line counts, no content change). The L47 "
            "gap-state text is a true statement about what MAIN-ONLY forensics can "
            "see after a squash merge, not a defect in the score."
        )
    elif verdict.startswith("NOT_ADJUDICABLE"):
        note = (
            "COULD NOT CHECK, which is NOT the same as checked-and-fine: the origin "
            "branch objects for this package are not present in this clone. Fetch "
            "research/833-g0-grammar-expansion-v1 and re-run before drawing any "
            "conclusion about this package's score."
        )
    else:
        note = (
            "The flag is NOT explained by squash-merge forensics: branch custody "
            "reads %s, freeze-tree-clean=%s, wording-only=%s. Escalate to the owning "
            "lane; this tranche still alters no score outside its frozen scope."
            % (on_branch, tree_clean, wording_only)
        )
    return {
        "package": G0_PKG,
        "flagged_because": (
            "L47 overclaiming_freeze_texts names it as a freeze text claiming "
            "prospective registration while custody cannot demonstrate it, and its "
            "row GMI833_V2_ARRIVAL_24_g0-grammar-growth-v1 sits at M4/EV3 on "
            "FROZEN_HELDOUT support without mentioning the gap."
        ),
        "custody_on_source_main": on_main,
        "custody_on_origin_branch": on_branch,
        "origin_branch": "research/833-g0-grammar-expansion-v1 @ " + G0_BRANCH[:8],
        "freeze_commit": G0_FREEZE_COMMIT[:8],
        "freeze_commit_tree": tree,
        "freeze_tree_is_exactly_the_freeze": tree_clean,
        "freeze_blob_at_freeze_commit": at_freeze,
        "freeze_blob_on_source_main": at_main,
        "freeze_blob_changed_after_merge": at_freeze != at_main,
        "commits_touching_the_freeze_on_main": touching,
        "post_merge_change_is_the_947_wording_migration": changed_only_by_wording_migration,
        "post_merge_diff_numstat": {"added": added, "removed": removed},
        "wording_only": wording_only,
        "adjudication": verdict,
        "score_change_made_here": None,
        "note": note,
    }


# ---------------------------------------------------------------------------
# hostiles and null
# ---------------------------------------------------------------------------
def lcg(seed):
    # type: (int) -> object
    state = [seed & 0x7FFFFFFF]

    def nxt(n):
        # type: (int) -> int
        state[0] = (1103515245 * state[0] + 12345) & 0x7FFFFFFF
        return state[0] % n
    return nxt


def hostiles(registers, rows):
    # type: (Dict[str, object], Sequence[Dict]) -> Dict
    out = {}

    # H2 (REAL planted positive): the published scores must be flagged.
    real = sweep(registers, rows)
    w4_flagged = any(
        PARENT_PKG in (r.get("resolved_packages") or []) and r["outcome"] == UNREFLECTED
        for r in real["results"]
    )
    out["H2_real_published_flags_w4"] = {"detected": bool(w4_flagged), "must_be": True}

    # H1 (synthetic planted positive): a clean package given an M4/FROZEN_HELDOUT row
    # while carrying a CONFIRMED custody verdict.
    planted = [dict(r) for r in rows]
    planted.append({
        "result_id": "HOSTILE_PLANT_1", "package": "gmi-section-e-searcher-comparison-v2",
        "maturity_M": "M4", "evidence_EV": "EV3", "support_kind": "FROZEN_HELDOUT",
        "justification": "planted row with no mention of the finding",
        "verification_note": "", "claim_evidence_gap": "", "forbidden_extrapolations": [],
    })
    sw = sweep(registers, planted)
    h1 = any(
        "gmi-section-e-searcher-comparison-v2" in (r.get("resolved_packages") or [])
        and r["outcome"] == UNREFLECTED for r in sw["results"]
    )
    out["H1_synthetic_plant"] = {"detected": bool(h1), "must_be": True}

    # H3 (no-alarm, REAL): gmi-capability-interactions-unified-v1 carries the L58
    # OVERSTRONG defect but is scored M2 -> must be IMMATERIAL, never flagged.
    h3 = [r for r in real["results"]
          if "gmi-capability-interactions-unified-v1" in (r.get("resolved_packages") or [])]
    out["H3_no_alarm_capability_interactions"] = {
        "outcomes": sorted(set(r["outcome"] for r in h3)),
        "must_be": [IMMATERIAL],
        "ok": sorted(set(r["outcome"] for r in h3)) == [IMMATERIAL],
    }

    # H3b (no-alarm, REAL): machine-intelligence-morphogenesis-v1 is self-typed a
    # screen false positive and holds 12 M4/FROZEN_HELDOUT rows.  Treating it as
    # adverse would produce 12 false positives in one stroke.
    h3b = [r for r in real["results"]
           if (r.get("package") == "machine-intelligence-morphogenesis-v1")]
    out["H3b_no_alarm_morphogenesis"] = {
        "outcomes": sorted(set(r["outcome"] for r in h3b)),
        "must_be": [NOT_ADVERSE],
        "ok": sorted(set(r["outcome"] for r in h3b)) == [NOT_ADVERSE],
    }

    # H4 (arithmetic tamper): a distribution that does not sum to the row count.
    tampered = dict(distribution(rows, "maturity_M"))
    tampered["M4"] = tampered["M4"] + 1
    out["H4_arithmetic_tamper"] = {
        "detected": sum(tampered.values()) != len(rows), "must_be": True,
    }

    # H5 (custody hostile, REAL): the parent package must FAIL the custody check,
    # proving the check can return FALSE on real data.
    st, _ = custody_on_ref("HEAD", PARENT_DIR, PARENT_FREEZE_FILES, PARENT_OUTCOME_FILES)
    out["H5_custody_check_returns_false_on_parent"] = {
        "state": st, "must_be": NOT_PRECEDES, "ok": st == NOT_PRECEDES,
    }
    return out


def null_control(registers, rows, draws=200, seed=8332026):
    # type: (Dict[str, object], Sequence[Dict], int, int) -> Dict
    """Randomised package-name pairings must produce zero flags."""
    scored = sorted(set(r["package"] for r in rows))
    rows_by_pkg = {}  # type: Dict[str, List[Dict]]
    for r in rows:
        rows_by_pkg.setdefault(r["package"], []).append(r)
    nxt = lcg(seed)
    flags = 0
    for _ in range(draws):
        pkg = scored[nxt(len(scored))]
        fake = {"id": "NULL", "package": pkg + "__NULL_SUFFIX_NOT_A_REAL_PACKAGE", "tier": TIER1,
                "verdict": "randomised null pairing", "source": "null"}
        if classify(fake, rows_by_pkg)["outcome"] == UNREFLECTED:
            flags += 1
    return {"draws": draws, "seed": seed, "flags": flags, "must_be": 0}


# ---------------------------------------------------------------------------
def main():
    # type: () -> int
    # 1. pin verification
    pins = {"source_main": SOURCE_MAIN, "blobs": {}}
    ok = True
    got = git_blob_sha1(SCORES_REL)
    pins["blobs"][SCORES_REL] = {"pinned": SCORES_BLOB, "got": got}
    ok = ok and got == SCORES_BLOB
    registers = {}
    for p in REGISTER_RELS:
        base = os.path.basename(p)
        g = git_blob_sha1(p)
        pins["blobs"][p] = {"pinned": REGISTER_BLOBS[base], "got": g}
        ok = ok and g == REGISTER_BLOBS[base]
        registers[base] = load_json(p)
    pins["all_blobs_match"] = ok
    if not ok:
        print("FAIL: pinned blob mismatch", file=sys.stderr)
        print(json.dumps(pins, indent=1, sort_keys=True), file=sys.stderr)
        return 2

    rows = load_json(SCORES_REL)

    # 2. custody
    parent_state, parent_detail = custody_on_ref("HEAD", PARENT_DIR, PARENT_FREEZE_FILES, PARENT_OUTCOME_FILES)
    if parent_state == UNAVAIL:
        print("FAIL: parent custody NOT CHECKED (git objects unavailable) -- this is "
              "not the same as 'fine'", file=sys.stderr)
        return 3
    arr = arrival_custody()

    # 3. the two delta records, produced by the frozen table
    exactness = executor_is_exact(PARENT_DIR + "/novel_intelligence_w4_v1.py")
    pr = parent_record(parent_state, exactness)
    ar = arrival_record(arr)
    delta = [pr, ar]

    # 4. census
    pub_m = distribution(rows, "maturity_M")
    pub_ev = distribution(rows, "evidence_EV")
    corr = corrected_rows(rows, delta)
    cor_m = distribution(corr, "maturity_M")
    cor_ev = distribution(corr, "evidence_EV")

    m4_pub = sorted(set(r["package"] for r in rows if r["maturity_M"] == "M4"))
    m4_cor = sorted(set(r["package"] for r in corr if r["maturity_M"] == "M4"))

    # 5. propagation sweep + validation
    sw = sweep(registers, rows)
    host = hostiles(registers, rows)
    null = null_control(registers, rows)
    sw_after = sweep(registers, corr)
    adjudications = [adjudicate_g0()]
    w4_after = [r for r in sw_after["results"]
                if PARENT_PKG in (r.get("resolved_packages") or []) and r["outcome"] == UNREFLECTED]

    result = {
        "schema": "GMI_833_MATURITY_RESCORE_V3_W4_RESULT_V1",
        "package": "gmi-833-maturity-rescore-v3-w4-v1",
        "claim_ceiling": CLAIM_CEILING,
        "source_main": SOURCE_MAIN,
        "closes_issue_rows": [],
        "route": "A",
        "pins": pins,
        "W4R1_parent_rescore": pr,
        "W4R1_parent_custody_detail": parent_detail,
        "W4R2_arrival_score": ar,
        "W4R3_distribution": {
            "published_M": pub_m, "corrected_M": cor_m, "delta_M": delta_counts(cor_m, pub_m),
            "published_EV": pub_ev, "corrected_EV": cor_ev, "delta_EV": delta_counts(cor_ev, pub_ev),
            "published_rows": len(rows), "corrected_rows": len(corr),
            "published_sums_to_rows": sum(pub_m.values()) == len(rows),
            "corrected_sums_to_rows": sum(cor_m.values()) == len(corr),
            "M4_total_published": pub_m.get("M4", 0),
            "M4_total_corrected": cor_m.get("M4", 0),
            "M4_total_unchanged": pub_m.get("M4", 0) == cor_m.get("M4", 0),
            "M4_membership_left": sorted(set(m4_pub) - set(m4_cor)),
            "M4_membership_entered": sorted(set(m4_cor) - set(m4_pub)),
            "headline": (
                "M4 stays at %d while its membership changes: %s leaves, %s enters. "
                "The headline count holds AND becomes true; this is a swap, not a null result."
                % (cor_m.get("M4", 0),
                   ", ".join(sorted(set(m4_pub) - set(m4_cor))) or "(none)",
                   ", ".join(sorted(set(m4_cor) - set(m4_pub))) or "(none)")
            ),
        },
        "W4R4_propagation": {
            "checked": sw["checked"],
            "counts": sw["counts"],
            "by_outcome": sw["by_outcome"],
            "unreflected": sorted(
                (r.get("package") or r.get("package_fragment")) for r in sw["unreflected_detail"]
            ),
            "unreflected_detail": sw["unreflected_detail"],
            "after_v3_correction_counts": sw_after["counts"],
            "w4_still_unreflected_after_correction": len(w4_after),
            "definition": (
                "UNREFLECTED iff the package has a scored row at M4+ or on FROZEN_HELDOUT "
                "support AND no row for it mentions the finding in justification, "
                "verification_note, claim_evidence_gap or forbidden_extrapolations."
            ),
        },
        "W4R4_adjudication": adjudications,
        "hostiles": host,
        "null_control": null,
        "published_baseline": {"M": PUBLISHED_M, "EV": PUBLISHED_EV, "rows": 197},
        "no_row_earned": True,
        "produces_reconciliation_json": False,
        "produces_correction_notice": "CORRECTION_NOTICE_V1.json",
    }

    # 6. self-falsifiers
    checks = {
        "published_matches_the_checklist_line": pub_m == PUBLISHED_M and pub_ev == PUBLISHED_EV and len(rows) == 197,
        "corrected_M_sums": sum(cor_m.values()) == len(corr),
        "corrected_EV_sums": sum(cor_ev.values()) == len(corr),
        "parent_left_M4": PARENT_PKG in result["W4R3_distribution"]["M4_membership_left"],
        "arrival_entered_M4": ARRIVAL_PKG in result["W4R3_distribution"]["M4_membership_entered"],
        "H1": host["H1_synthetic_plant"]["detected"] is True,
        "H2": host["H2_real_published_flags_w4"]["detected"] is True,
        "H3": host["H3_no_alarm_capability_interactions"]["ok"] is True,
        "H3b": host["H3b_no_alarm_morphogenesis"]["ok"] is True,
        "H4": host["H4_arithmetic_tamper"]["detected"] is True,
        "H5": host["H5_custody_check_returns_false_on_parent"]["ok"] is True,
        "null_zero": null["flags"] == 0,
        "correction_extinguishes_w4_flag": len(w4_after) == 0,
        "g0_flag_adjudicated_not_left_dangling": all(
            a["adjudication"].startswith("SCORE_") for a in adjudications),
        "g0_adjudication_actually_ran": all(
            a["adjudication"] != "NOT_ADJUDICABLE__BRANCH_OBJECTS_UNAVAILABLE"
            for a in adjudications),
        "no_float_in_claims": all(
            not isinstance(v, float)
            for v in list(cor_m.values()) + list(cor_ev.values()) + list(sw["counts"].values())
        ),
    }
    result["self_checks"] = checks
    result["all_green"] = all(bool(v) for v in checks.values())

    with open(os.path.join(HERE, "RESULT_V1.json"), "w") as fh:
        json.dump(result, fh, indent=1, sort_keys=True)
        fh.write("\n")
    with open(os.path.join(HERE, "SCORES_V3_DELTA.json"), "w") as fh:
        json.dump({
            "schema": "GMI_833_MATURITY_SCORES_V3_DELTA_V1",
            "supersedes_by_reference": SCORES_REL,
            "supersedes_blob": SCORES_BLOB,
            "source_main": SOURCE_MAIN,
            "note": "Delta only. THEOREM_SCORES_V2.json is frozen and is NOT edited; "
                    "every row not named here is carried through unchanged.",
            "records": delta,
        }, fh, indent=1, sort_keys=True)
        fh.write("\n")

    print(json.dumps({
        "all_green": result["all_green"],
        "self_checks": checks,
        "published_M": pub_m,
        "corrected_M": cor_m,
        "delta_M": result["W4R3_distribution"]["delta_M"],
        "M4_left": result["W4R3_distribution"]["M4_membership_left"],
        "M4_entered": result["W4R3_distribution"]["M4_membership_entered"],
        "propagation": sw["counts"],
        "unreflected": result["W4R4_propagation"]["unreflected"],
        "adjudications": [(a["package"], a["adjudication"]) for a in adjudications],
        "parent_custody": parent_state,
        "arrival_custody_holds": arr["custody_holds"],
        "arrival_custody_on_main": arr["on_source_main"],
    }, indent=1, sort_keys=True))
    return 0 if result["all_green"] else 1


if __name__ == "__main__":
    sys.exit(main())
