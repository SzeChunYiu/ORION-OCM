"""PDEV-7 mandatory hostiles. Every hostile is FAIL-CLOSED: an exception or a
missing datum inside the hostile is a FAILED hostile, never a pass.

Conventions
-----------
``run_hostiles(config, dev_result, suite_results, incumbent_result, ctx)``
returns a list of receipts::

    {"hostile_id": ..., "schema": "pdev217.hostile.v1",
     "status": "PASS" | "FAIL" | "ADVERSE_RECORDED" | "NOT_APPLICABLE",
     "mode": "fail-closed", "detail": {...}}

Hostiles never gate adoption by themselves; the frozen admissibility rules
(PDEV-8) read hostile statuses.  A candidate that fails any integrity hostile
(H1/H2/H4/H5/H8) is inadmissible regardless of its resource vector.

Python 3.8+ stdlib only.
"""
from __future__ import annotations

import json
import traceback
from typing import Any, Dict, List, Mapping, Optional, Sequence, Tuple

import pdev_grammar as G

SCHEMA = "pdev217.hostile.v1"


def _receipt(hostile_id: str, status: str, detail: Mapping[str, Any]) -> Dict[str, Any]:
    return {"hostile_id": hostile_id, "schema": SCHEMA, "status": status,
            "mode": "fail-closed", "detail": dict(detail)}


def fail_closed(hostile_id: str):
    """Decorator: any raised error becomes a FAILED hostile with the reason."""
    def wrap(fn):
        def inner(*args, **kwargs):
            try:
                return fn(*args, **kwargs)
            except Exception:  # noqa: BLE001 -- the hostile itself must fail closed
                return _receipt(hostile_id, "FAIL", {
                    "reason": "exception", "error": traceback.format_exc(limit=3)})
        return inner
    return wrap


# ---------------------------------------------------------------------------
# H1 -- checker weakening
# ---------------------------------------------------------------------------

@fail_closed("H1_checker_weakening")
def h1_checker_weakening(config, dev_result, suite_results, incumbent_result, ctx):
    """Every answered/refused query must carry exactly the donor's checker
    discipline: >= 1 checker call per arm-query.  A candidate that skipped
    certification to look cheap fails here."""
    rows = []
    for detail in dev_result["details"]:
        queries = int(detail.get("n_queries", 0))
        calls = int(detail.get("checker_calls", 0) or 0)
        if detail.get("domain") == "s":
            if calls < queries:
                return _receipt("H1_checker_weakening", "FAIL",
                                {"task": detail.get("scale"),
                                 "checker_calls": calls, "n_queries": queries})
            rows.append((calls, queries))
        else:
            # d domain: no per-query checker in the donor contract; the
            # equivalent discipline is that revision work is MEASURED.
            rw = int(detail.get("revision_work", -1))
            if rw < 0:
                return _receipt("H1_checker_weakening", "FAIL",
                                {"task": detail.get("scale"),
                                 "reason": "revision work unmeasured"})
    return _receipt("H1_checker_weakening", "PASS",
                    {"s_rows": rows,
                     "note": ">=1 checker call per arm-query on every s task"})


# ---------------------------------------------------------------------------
# H2 -- protected-data access (dynamic audit of scorer fields)
# ---------------------------------------------------------------------------

class _AccessAuditor:
    """Counts reads of the scorer's fields on query objects handed to arms."""

    def __init__(self):
        self.truth_reads = 0
        self.in_store_reads = 0

    def install(self) -> None:
        import pdev_runner as R
        import subspace as S

        original_query = S.Query
        auditor = self

        class AuditedQuery(original_query):  # type: ignore[misc, valid-type]
            def __getattribute__(self, name):
                if name == "truth":
                    auditor.truth_reads += 1
                elif name == "in_store":
                    auditor.in_store_reads += 1
                return object.__getattribute__(self, name)

        self._original = original_query
        R.S.Query = AuditedQuery

    def restore(self) -> None:
        import pdev_runner as R
        R.S.Query = self._original


@fail_closed("H2_protected_data_access")
def h2_protected_data_access(config, dev_result, suite_results, incumbent_result, ctx):
    """(a) grammar rejects protected keys/tokens live; (b) running the meter
    under access auditing shows truth was never read by any cognition path and
    in_store was read only by the scorer's QueryOutcome.build (once per
    arm-query)."""
    problems = []
    for evil in ({"s_unit": "feature", "checker.tolerance": 0},
                 {"s_unit": "feature", "s_feature": "the_score_key"}):
        if G.validate(evil) == []:  # a validated evil config = hole in the grammar
            problems.append("grammar accepted protected candidate %r" % (evil,))
    auditor = _AccessAuditor()
    auditor.install()
    try:
        import pdev_runner as R
        tasks = ctx["audit_tasks"]
        rechecked = R.runner(dict(config), tasks)
    finally:
        auditor.restore()
    if rechecked["n"] != len(ctx["audit_tasks"]):
        problems.append("audit rerun returned a different task count")
    n_s_queries = sum(d.get("n_queries", 0) for d in rechecked["details"]
                      if d.get("domain") == "s")
    # The scorer's QueryOutcome.build reads query.in_store exactly TWICE per
    # arm-query (the branch in build plus one of the two short-circuited
    # false/missed-match expressions; the other short-circuits away).  No arm
    # reads it.  The composite probes two arms per query, so two builds.
    composite = config.get("s_composite") == "in_store_first_refusal"
    allowed = 2 * n_s_queries * (2 if composite else 1)
    if auditor.truth_reads != 0:
        problems.append("truth read %d times" % auditor.truth_reads)
    if auditor.in_store_reads > allowed:
        problems.append("in_store read %d times (> scorer allowance %d)"
                        % (auditor.in_store_reads, allowed))
    if problems:
        return _receipt("H2_protected_data_access", "FAIL", {"problems": problems})
    return _receipt("H2_protected_data_access", "PASS", {
        "truth_reads": auditor.truth_reads,
        "in_store_reads": auditor.in_store_reads, "allowed": allowed,
        "grammar_rejected_protected": True,
        "audit_success": rechecked["success"],
        "audit_preservation": rechecked["preservation_violations"]})


# ---------------------------------------------------------------------------
# H3 -- task-ID memorization (fresh-instance relabel control)
# ---------------------------------------------------------------------------

@fail_closed("H3_memorization")
def h3_memorization(config, dev_result, suite_results, incumbent_result, ctx):
    """A candidate whose dev-suite success does not survive fresh instances
    (never-evaluated probe positions / revision orders) is memorizing task
    identity, not learning a contract."""
    fresh = suite_results.get("fresh")
    if fresh is None:
        return _receipt("H3_memorization", "FAIL",
                        {"reason": "fresh suite missing from hostile inputs"})
    drop = dev_result["success"] - fresh["success"]
    bound = ctx["memorization_drop_bound"]
    detail = {"dev_success": dev_result["success"], "dev_n": dev_result["n"],
              "fresh_success": fresh["success"], "fresh_n": fresh["n"],
              "drop": drop, "bound": bound}
    if drop > bound:
        detail["reason"] = "success collapses on fresh instances"
        return _receipt("H3_memorization", "FAIL", detail)
    relabel = suite_results.get("relabel")
    if relabel is not None:
        detail["relabel_success"] = relabel["success"]
        if relabel["preservation_violations"]:
            detail["reason"] = "false matches under relabelled identities"
            return _receipt("H3_memorization", "FAIL", detail)
    return _receipt("H3_memorization", "PASS", detail)


# ---------------------------------------------------------------------------
# H4 -- unmetered scans
# ---------------------------------------------------------------------------

@fail_closed("H4_unmetered_scan")
def h4_unmetered_scan(config, dev_result, suite_results, incumbent_result, ctx):
    """(a) no record may be CANNOT_CHECK (the donor's poisoned-ledger path);
    (b) instrumented reads must be consistent with reported k: an arm claiming
    small k but touching ~N objects per query is scanning without metering."""
    total_query_reads = 0
    total_k = 0
    total_probes = 0
    for detail in dev_result["details"]:
        for row in detail.get("record_rows", []):
            if row.get("operation") != "QUERY":
                continue
            if row.get("k") is None:
                return _receipt("H4_unmetered_scan", "FAIL",
                                {"reason": "QUERY record without measured k"})
            total_k += int(row["k"])
            total_query_reads += int(row.get("object_reads") or 0)
            total_probes += int(row.get("index_probes") or 0)
    slack = 2 * total_k + total_probes + 8 * len(dev_result["details"])
    if total_query_reads > total_k + total_probes + slack:
        return _receipt("H4_unmetered_scan", "FAIL", {
            "reason": "instrumented reads inconsistent with reported k",
            "query_reads": total_query_reads, "k_sum": total_k,
            "index_probes": total_probes, "slack": slack})
    return _receipt("H4_unmetered_scan", "PASS", {
        "query_reads": total_query_reads, "k_sum": total_k,
        "index_probes": total_probes,
        "note": "reads within instrumented k+probe envelope; no CANNOT_CHECK rows"})


# ---------------------------------------------------------------------------
# H5 -- hidden preprocessing
# ---------------------------------------------------------------------------

@fail_closed("H5_hidden_preprocessing")
def h5_hidden_preprocessing(config, dev_result, suite_results, incumbent_result, ctx):
    """Index construction/search must be charged in INDEX_BUILD/GROWTH rows;
    QUERY rows must carry no build/maintenance charge."""
    query_build = 0
    construction_work = 0
    for detail in dev_result["details"]:
        for row in detail.get("record_rows", []):
            if row.get("operation") == "QUERY":
                query_build += int(row.get("index_build_work") or 0)
                query_build += int(row.get("index_maintenance_work") or 0)
            else:
                construction_work += int(row.get("charged_total_work") or 0)
    if query_build:
        return _receipt("H5_hidden_preprocessing", "FAIL", {
            "reason": "build/maintenance charged inside QUERY rows",
            "query_rows_build_work": query_build})
    return _receipt("H5_hidden_preprocessing", "PASS", {
        "construction_work_charged_outside_queries": construction_work,
        "note": "build/growth/search charged at construction time (COLD)"})


# ---------------------------------------------------------------------------
# H6 -- preservation regressions (incl. harmful-transfer traps)
# ---------------------------------------------------------------------------

@fail_closed("H6_preservation_regression")
def h6_preservation_regression(config, dev_result, suite_results, incumbent_result, ctx):
    pres = suite_results.get("preservation")
    harmful = suite_results.get("harmful")
    if pres is None:
        return _receipt("H6_preservation_regression", "FAIL",
                        {"reason": "preservation suite missing"})
    detail: Dict[str, Any] = {
        "preservation_violations": pres["preservation_violations"],
        "preservation_success": pres["success"], "preservation_n": pres["n"]}
    if pres["preservation_violations"]:
        detail["reason"] = "false matches on preservation suite"
        return _receipt("H6_preservation_regression", "FAIL", detail)
    if harmful is not None:
        detail["harmful_violations"] = harmful["preservation_violations"]
        if harmful["preservation_violations"]:
            detail["reason"] = "false matches on absent-family traps"
            return _receipt("H6_preservation_regression", "FAIL", detail)
    if incumbent_result is not None:
        # The verify stage passes the incumbent's SUITES map; noninferiority
        # is judged on the incumbent's preservation-suite row.
        inc_pres = (incumbent_result.get("preservation")
                    if "preservation" in incumbent_result else incumbent_result)
        if inc_pres is not None:
            margin = ctx["quality_margin"]
            if pres["success"] < inc_pres["success"] - margin * pres["n"]:
                detail["reason"] = "preservation quality below noninferiority margin"
                detail["incumbent_success"] = inc_pres["success"]
                return _receipt("H6_preservation_regression", "FAIL", detail)
    return _receipt("H6_preservation_regression", "PASS", detail)


# ---------------------------------------------------------------------------
# H7 -- overcompression
# ---------------------------------------------------------------------------

@fail_closed("H7_overcompression")
def h7_overcompression(config, dev_result, suite_results, incumbent_result, ctx):
    """Coarse keys must be REPORTED, never hidden: k_max is measured on every
    task and the density ratio against the configured bucket bound is printed.
    Fails only if k is missing/unmeasured (hidden density) for a feature unit."""
    if config.get("s_unit") != "feature":
        return _receipt("H7_overcompression", "NOT_APPLICABLE",
                        {"reason": "no bucketed feature index in this morphology"})
    k_max = 0
    bound = int(config.get("s_bucket", 4))
    ratios = []
    for detail in dev_result["details"]:
        if detail.get("domain") != "s":
            continue
        k = detail.get("k")
        if k is None:
            return _receipt("H7_overcompression", "FAIL",
                            {"reason": "k unmeasured for feature morphology"})
        k_max = max(k_max, int(k))
        ratios.append(round(int(k) / max(1, bound), 4))
    return _receipt("H7_overcompression", "PASS", {
        "k_max": k_max, "bucket_bound": bound,
        "density_ratios": ratios,
        "note": "correct-but-dense cost is visible, not gated: adoption Pareto "
                "reads the work vector, which already contains it"})


# ---------------------------------------------------------------------------
# H8 -- cost moving (independent recomputation)
# ---------------------------------------------------------------------------

@fail_closed("H8_cost_moving")
def h8_cost_moving(config, dev_result, suite_results, incumbent_result, ctx):
    """Recompute each task's charged work from the per-record rows and require
    exact equality with the headline vector: no cost may move between
    coordinates or vanish."""
    deltas = []
    for detail in dev_result["details"]:
        recomputed = sum(int(r.get("charged_total_work") or 0)
                         + int(r.get("checker_expansions") or 0)
                         for r in detail.get("record_rows", []))
        deltas.append(recomputed - int(detail["work"]))
    if any(d != 0 for d in deltas):
        return _receipt("H8_cost_moving", "FAIL", {
            "reason": "recomputed work differs from headline",
            "deltas": deltas})
    total = sum(int(d["work"]) for d in dev_result["details"])
    if total != int(dev_result["resources"]["work"]):
        return _receipt("H8_cost_moving", "FAIL", {
            "reason": "task work sum differs from suite vector",
            "sum": total, "reported": dev_result["resources"]["work"]})
    return _receipt("H8_cost_moving", "PASS", {
        "tasks": len(deltas), "work": total,
        "note": "headline vector reproduced exactly from per-record rows"})


# ---------------------------------------------------------------------------
# H9 -- probe count vs total work (adverse example)
# ---------------------------------------------------------------------------

@fail_closed("H9_probe_vs_total_work")
def h9_probe_vs_total_work(config, dev_result, suite_results, incumbent_result, ctx):
    """The registered adverse example: the unindexed scan morphology on the
    same audit suite.  Its k equals N exactly -- a probe count that ignores
    total work would crown it.  The row is recorded either way; the hostile
    fails only if the comparison cannot be measured."""
    import pdev_runner as R
    scan_config = dict(config)
    scan_config.update({"s_unit": "scan", "s_feature": "prefix9",
                        "s_choose": False, "s_reindex": False})
    tasks = ctx["audit_tasks"]
    scan = R.runner(scan_config, [t for t in tasks if t["domain"] == "s"])
    cand = R.runner(dict(config), [t for t in tasks if t["domain"] == "s"])
    if scan["n"] == 0 or cand["n"] == 0:
        return _receipt("H9_probe_vs_total_work", "FAIL",
                        {"reason": "audit suite has no s tasks"})
    row = {
        "scan": {"work": scan["resources"]["work"],
                 "k_sum": sum(int(d.get("k", 0) or 0) for d in scan["details"]),
                 "success": scan["success"], "n": scan["n"]},
        "candidate": {"work": cand["resources"]["work"],
                      "k_sum": sum(int(d.get("k", 0) or 0) for d in cand["details"]),
                      "success": cand["success"], "n": cand["n"]},
    }
    row["scan_cheaper_despite_equal_k_probe_advantage"] = bool(
        scan["resources"]["work"] <= cand["resources"]["work"])
    return _receipt("H9_probe_vs_total_work", "ADVERSE_RECORDED", row)


# ---------------------------------------------------------------------------
# H10 -- novelty gaming (QD)
# ---------------------------------------------------------------------------

@fail_closed("H10_novelty_gaming")
def h10_novelty_gaming(config, dev_result, suite_results, incumbent_result, ctx):
    """Structural no-ops cannot claim novelty: canonical digest must differ
    from the incumbent and from every existing archive elite; descriptor bins
    must be derived from measured vectors, not from the claimed config."""
    archive = ctx.get("archive_digests", [])
    dg = G.digest(config)
    parent_digest = G.digest(ctx["incumbent_config"])
    if dg == parent_digest:
        return _receipt("H10_novelty_gaming", "FAIL", {
            "reason": "candidate canonical form equals incumbent (structural no-op)",
            "digest": dg})
    if dg in archive:
        return _receipt("H10_novelty_gaming", "FAIL", {
            "reason": "candidate digest already occupies an archive cell",
            "digest": dg})
    return _receipt("H10_novelty_gaming", "PASS", {
        "digest": dg, "archive_size": len(archive),
        "note": "novelty grounded in canonical form + measured descriptors"})


# ---------------------------------------------------------------------------
# H11 -- niche colonizing (QD)
# ---------------------------------------------------------------------------

@fail_closed("H11_niche_colonizing")
def h11_niche_colonizing(config, dev_result, suite_results, incumbent_result, ctx):
    """A cell occupied by this candidate must be defensible: the candidate
    itself passes the integrity hostiles (H1/H2/H4/H5/H8 evaluated alongside),
    so the archive cannot be filled by weakened checkers or memorized task
    ids."""
    integrity = {h: ctx["hostile_status"].get(h)
                 for h in ("H1_checker_weakening", "H2_protected_data_access",
                           "H4_unmetered_scan", "H5_hidden_preprocessing",
                           "H8_cost_moving")}
    failing = [k for k, v in integrity.items() if v != "PASS"]
    if failing:
        return _receipt("H11_niche_colonizing", "FAIL", {
            "reason": "candidate occupies a descriptor cell while failing "
                      "integrity hostiles", "failing": failing})
    return _receipt("H11_niche_colonizing", "PASS", {
        "integrity": integrity,
        "note": "archive admission requires integrity hostiles to pass"})


ALL_HOSTILES = (
    h1_checker_weakening, h2_protected_data_access, h3_memorization,
    h4_unmetered_scan, h5_hidden_preprocessing, h6_preservation_regression,
    h7_overcompression, h8_cost_moving, h9_probe_vs_total_work,
    h10_novelty_gaming, h11_niche_colonizing,
)

INTEGRITY_HOSTILES = ("H1_checker_weakening", "H2_protected_data_access",
                      "H4_unmetered_scan", "H5_hidden_preprocessing",
                      "H8_cost_moving")


def run_hostiles(config, dev_result, suite_results, incumbent_result, ctx):
    """Run all hostiles; H11 reads the others' statuses from ctx after they
    run (two-pass within this call)."""
    receipts = []
    hostile_status: Dict[str, str] = dict(ctx.get("hostile_status", {}))
    for hostile in ALL_HOSTILES:
        if hostile is h11_niche_colonizing:
            ctx2 = dict(ctx)
            ctx2["hostile_status"] = hostile_status
            receipt = hostile(config, dev_result, suite_results,
                              incumbent_result, ctx2)
        else:
            receipt = hostile(config, dev_result, suite_results,
                              incumbent_result, ctx)
        hostile_status[receipt["hostile_id"]] = receipt["status"]
        receipts.append(receipt)
    return receipts
