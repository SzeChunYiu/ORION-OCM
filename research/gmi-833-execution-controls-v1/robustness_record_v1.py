#!/usr/bin/env python3
"""DerivationRobustnessRecord schema and fail-closed admission validator.

Issue #859 (child of #833 Section D), freeze `FREEZE_V1.md` (commit 3682a045).

This module is deliberately substrate-free and stdlib-only so that later
Section H/J derivation packages can import it by file path and validate their
own records.  It never imports the #901 substrate, the #855 auditor, or any
other module of this package.

A record carries one block per control:

    MATCHED_TWIN    D-X1  matched mechanism-removal twin
    ENCODING        D-X2  semantics-preserving alternate encodings
    SEARCH          D-X3  materially distinct search procedures
    SCALARIZATION   D-X4  raw Pareto relation plus positive scalarizations
    NO_SMUGGLING    #855  audit terminals for every compared arm

`validate_record` returns `ROBUST_AT_REGISTERED_D_CONTROLS_SCOPE` only when all
five admission conditions hold.  Every other outcome is fail-closed:
`CANNOT_ESTABLISH_D_ROBUSTNESS_<CONTROL>` naming the root failing control, with
the full ordered list of per-control typed terminals (never averaged, never
defaulted to clean).  The validator recomputes every decision it can from the
record's data (descriptor equality, bijection census, conclusion agreement,
Pareto set, scalar winners, wording compatibility); a declared terminal that
disagrees with the recomputation is itself a failure.

Exact arithmetic only: every rational is an `int` or a decimal string `a/b`;
a float anywhere in a numeric field makes the block malformed.
"""
from __future__ import annotations

from fractions import Fraction
import hashlib
import json
from typing import Any, Dict, List, Mapping, Sequence, Tuple

SCHEMA_ID = "GMI833DerivationRobustnessRecordV1"
VERDICT_SCHEMA_ID = "GMI833DerivationRobustnessVerdictV1"
ROBUST = "ROBUST_AT_REGISTERED_D_CONTROLS_SCOPE"
CANNOT_PREFIX = "CANNOT_ESTABLISH_D_ROBUSTNESS_"
CONTROL_ORDER = ("MATCHED_TWIN", "ENCODING", "SEARCH", "SCALARIZATION", "NO_SMUGGLING")

# per-control typed terminals -------------------------------------------------
CONTROL_MISSING = "CONTROL_MISSING"
CONTROL_MALFORMED = "CONTROL_MALFORMED"

MATCHED = "MATCHED_MECHANISM_TWIN"
UNMATCHED = "UNMATCHED_MECHANISM_TWIN"
TWIN_AUDIT_NOT_EVALUABLE = "TWIN_AUDIT_NOT_EVALUABLE"
TWIN_INTERPRETATION_UNSUPPORTED = "TWIN_INTERPRETATION_UNSUPPORTED"

ENC_ROBUST = "ENCODING_ROBUST_AT_REGISTERED_FINITE_SCOPE"
ENC_NOT_EQUIVALENT = "ENCODING_NOT_SEMANTICALLY_EQUIVALENT"
ENC_SENSITIVE = "ENCODING_SENSITIVE"
ENC_INSUFFICIENT = "ENCODINGS_INSUFFICIENT"
ENC_CONTRADICTS_CLAIM = "ENCODING_CONCLUSION_CONTRADICTS_CLAIM"

SEARCH_ROBUST = "SEARCH_ROBUST"
SEARCH_SENSITIVE = "SEARCH_SENSITIVE"
SEARCH_NOT_DISTINCT = "SEARCHERS_NOT_MATERIALLY_DISTINCT"
SEARCH_CONTRADICTS_CLAIM = "SEARCH_CONCLUSION_CONTRADICTS_CLAIM"

PARETO_OK = "PARETO_CONSISTENT_AT_REGISTERED_SCALARIZATIONS"
SCAL_SENSITIVE = "SCALARIZATION_SENSITIVE"
SCAL_INSUFFICIENT = "SCALARIZATIONS_INSUFFICIENT"
SCAL_INCONSISTENT = "SCALARIZATION_RECORD_INCONSISTENT"
COND_CONTRADICTED = "PRICE_CONDITIONAL_CLAIM_CONTRADICTED"
INVARIANT_CONTRADICTED = "FRONTIER_INVARIANT_CONTRADICTED"

NS_ADMISSIBLE = "NO_SMUGGLING_ADMISSIBLE"
NS_NOT_CLEAN = "NO_SMUGGLING_NOT_CLEAN"

PASS_TERMINALS = {
    "MATCHED_TWIN": MATCHED,
    "ENCODING": ENC_ROBUST,
    "SEARCH": SEARCH_ROBUST,
    "SCALARIZATION": PARETO_OK,
    "NO_SMUGGLING": NS_ADMISSIBLE,
}

# the frozen D-X1 non-K capacity descriptor (FREEZE_V1.md, D-X1)
DESCRIPTOR_COORDINATES = (
    "candidate_count",
    "primitive_envelope",
    "non_k_operator_inventory",
    "evaluator_id",
    "sequence_set",
    "budget",
    "tie_rule",
    "stopping_rule",
    "representable_k_free_behaviour_set",
)

# the frozen D-X3 difference-table axes (FREEZE_V1.md, D-X3 table)
DIFFERENCE_AXES = (
    "representation",
    "exploration_order",
    "pruning",
    "acceptance_termination",
    "completeness_proof",
    "search_cost_unit",
)
COMPLETE_COVERAGE_KINDS = ("EXHAUSTIVE_CONSTRUCTION", "ADMISSIBLE_BOUND", "OPTIMALITY_CERTIFICATE")
EXHAUSTIVE_KIND = "EXHAUSTIVE_CONSTRUCTION"
MIN_DIFFERING_AXES = 2

WORDINGS = ("PRICE_CONDITIONAL", "UNIVERSAL_WINNER", "FRONTIER_INVARIANT")

# #855 audit vocabulary (string constants only; the auditor is not imported)
NS_CLEAN = "CLEAN_AT_REGISTERED_AUDIT_SCOPE"
NS_SUBAUDITS = ("lexical", "semantic", "cost", "search", "evaluation", "ecology")
# Sensitivity findings that a registered D control evaluates are admissible
# ("evaluable"); every other non-clean finding is leakage and is not.
NS_ROUTED = {
    "cost": ("COST_PRIOR_SENSITIVE", ("SCALARIZATION_WINNER_REVERSAL",), "SCALARIZATION"),
    "search": ("SEARCH_PRIOR_SENSITIVE", ("ORDER_OR_TRAJECTORY_DEPENDENT_WINNER",), "SEARCH"),
}

SCHEMA: Dict[str, Any] = {
    "schema": SCHEMA_ID,
    "verdict_schema": VERDICT_SCHEMA_ID,
    "robust_terminal": ROBUST,
    "fail_closed_terminal_pattern": CANNOT_PREFIX + "<CONTROL>",
    "control_order": list(CONTROL_ORDER),
    "root_failure_rule": "the first control in control_order whose block is absent; otherwise the first control in control_order that fails",
    "admission_conditions": {
        "1": "MATCHED_TWIN: matched mechanism-removal twin valid and the outcome interpreted against it",
        "2": "ENCODING: at least two syntactically disjoint, semantics-equivalent encodings agree after canonical projection",
        "3": "SEARCH: two materially distinct complete searchers agree, or a verified exhaustive construction, and no registered searcher disagrees",
        "4": "SCALARIZATION: raw Pareto set plus at least two distinct strictly positive scalarizations do not contradict the wording",
        "5": "NO_SMUGGLING: every compared arm is clean, or carries only sensitivity findings routed to a registered control",
    },
    "record_fields": {
        "schema": "string == " + SCHEMA_ID,
        "record_id": "string",
        "claim": {
            "claim_id": "string",
            "mechanism": "string",
            "k_target_property": "string",
            "wording": list(WORDINGS),
            "scope": "string",
            "conclusion_by_world": "{world_id: [property, ...]}",
            "frontier_invariants": "[{invariant_id, if:{coordinate,op,value}, then:{coordinate,op,value}}]",
        },
        "controls": {
            "MATCHED_TWIN": {
                "positive_arm": "arm id (must appear in NO_SMUGGLING.arms)",
                "twin_arm": "arm id (must appear in NO_SMUGGLING.arms)",
                "descriptor_positive": {c: "json value" for c in DESCRIPTOR_COORDINATES},
                "descriptor_twin": {c: "json value" for c in DESCRIPTOR_COORDINATES},
                "operators_positive": "[operator]",
                "operators_twin": "[operator]",
                "twin_k_fingerprint_count": "int (must be 0)",
                "twin_k_target_realizable": "bool (must be false)",
                "positive_k_target_realized": "bool",
                "multiplicity_reweighting": "{reported: true, ...}",
                "outcome_positive_by_world": "{world_id: [property]}",
                "outcome_twin_by_world": "{world_id: [property]}",
                "interpretation": "K_DEPENDENCE_INTERPRETED_AGAINST_MATCHED_TWIN",
                "declared_terminal": "string",
            },
            "ENCODING": {
                "reference_census_size": "int",
                "encodings": "[{encoding_id, arm, surface_alphabet:[str], surface_id_pattern, census_size}] (>=2)",
                "bijection": "{domain_size, codomain_size, injective, surjective}",
                "projection_mismatches": "int (candidates whose canonical projection differs)",
                "resource_fingerprint_mismatches": "int",
                "decision_rule": "string",
                "conclusion_by_encoding": "{encoding_id: {world_id: {best, properties}}}",
                "declared_terminal": "string",
            },
            "SEARCH": {
                "probes": "[world_id]",
                "searchers": "[{searcher_id, difference_table:{axis:value}, coverage:{kind, verified}, search_cost, conclusion_by_world:{world_id:{best, properties}}, trace_digest_by_probe, acceptance_digest_by_probe}]",
                "declared_terminal": "string",
            },
            "SCALARIZATION": {
                "coordinates": "[name]",
                "raw_vectors": "[{point_id, vector:[rational], multiplicity, property}]",
                "pareto_set": "[point_id]",
                "scalarizations": "[{scalarization_id, weights:[rational], boundary_probe, winners:[point_id], claimed_properties:[property]}]",
                "declared_terminal": "string",
            },
            "NO_SMUGGLING": {
                "arms": "{arm_id: {terminal, subaudits:{lexical|semantic|cost|search|evaluation|ecology: {terminal, finding_kinds}}}}",
            },
        },
    },
    "difference_axes": list(DIFFERENCE_AXES),
    "descriptor_coordinates": list(DESCRIPTOR_COORDINATES),
    "complete_coverage_kinds": list(COMPLETE_COVERAGE_KINDS),
    "no_smuggling_routed_findings": {k: {"terminal": v[0], "finding_kinds": list(v[1]), "owning_control": v[2]} for k, v in sorted(NS_ROUTED.items())},
    "control_terminals": {
        "MATCHED_TWIN": [MATCHED, UNMATCHED, TWIN_AUDIT_NOT_EVALUABLE, TWIN_INTERPRETATION_UNSUPPORTED, CONTROL_MISSING, CONTROL_MALFORMED],
        "ENCODING": [ENC_ROBUST, ENC_NOT_EQUIVALENT, ENC_SENSITIVE, ENC_INSUFFICIENT, ENC_CONTRADICTS_CLAIM, CONTROL_MISSING, CONTROL_MALFORMED],
        "SEARCH": [SEARCH_ROBUST, SEARCH_SENSITIVE, SEARCH_NOT_DISTINCT, SEARCH_CONTRADICTS_CLAIM, CONTROL_MISSING, CONTROL_MALFORMED],
        "SCALARIZATION": [PARETO_OK, SCAL_SENSITIVE, SCAL_INSUFFICIENT, SCAL_INCONSISTENT, COND_CONTRADICTED, INVARIANT_CONTRADICTED, CONTROL_MISSING, CONTROL_MALFORMED],
        "NO_SMUGGLING": [NS_ADMISSIBLE, NS_NOT_CLEAN, CONTROL_MISSING, CONTROL_MALFORMED],
    },
}


class Malformed(ValueError):
    pass


# --------------------------------------------------------------------------
# exact helpers
# --------------------------------------------------------------------------
def rational(x: Any) -> Fraction:
    if isinstance(x, bool) or isinstance(x, float):
        raise Malformed("non-exact numeric value %r" % (x,))
    if isinstance(x, int):
        return Fraction(x)
    if isinstance(x, str):
        return Fraction(x)
    if isinstance(x, Fraction):
        return x
    raise Malformed("not a rational: %r" % (x,))


def canon(x: Any) -> Any:
    if isinstance(x, float):
        raise Malformed("float in canonical data")
    if isinstance(x, Fraction):
        return str(x)
    if isinstance(x, (list, tuple)):
        return [canon(v) for v in x]
    if isinstance(x, (set, frozenset)):
        return sorted(canon(v) for v in x)
    if isinstance(x, dict):
        return {str(k): canon(v) for k, v in x.items()}
    return x


def canonical_json(x: Any) -> str:
    return json.dumps(canon(x), sort_keys=True, indent=2, ensure_ascii=False) + "\n"


def compact_digest(x: Any) -> str:
    """16-hex sha256 of the compact canonical JSON form (the digest format
    used for canonical evaluation traces and acceptance sequences)."""
    raw = json.dumps(canon(x), sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]


def _need(block: Mapping[str, Any], keys: Sequence[str]) -> None:
    if not isinstance(block, dict):
        raise Malformed("block is not an object")
    missing = [k for k in keys if k not in block]
    if missing:
        raise Malformed("missing fields: %s" % ",".join(missing))


def _props(x: Any) -> Tuple[str, ...]:
    if not isinstance(x, (list, tuple)) or not all(isinstance(v, str) for v in x):
        raise Malformed("property set must be a list of strings")
    return tuple(sorted(set(x)))


def _conclusion_map(m: Any) -> Dict[str, Tuple[str, Tuple[str, ...]]]:
    if not isinstance(m, dict) or not m:
        raise Malformed("conclusion map must be a non-empty object")
    out = {}
    for w, v in m.items():
        _need(v, ("best", "properties"))
        out[str(w)] = (str(rational(v["best"])), _props(v["properties"]))
    return out


def _result(control: str, terminal: str, reasons: List[str], **extra: Any) -> Dict[str, Any]:
    r = {"control": control, "terminal": terminal, "passed": terminal == PASS_TERMINALS[control], "reasons": reasons}
    r.update(extra)
    return r


# --------------------------------------------------------------------------
# the five controls
# --------------------------------------------------------------------------
def _ns_arm_state(ns_block: Any, arm: str) -> str:
    """ABSENT | NOT_EVALUABLE | EVALUABLE_NOT_ADMISSIBLE | ADMISSIBLE."""
    if not isinstance(ns_block, dict) or not isinstance(ns_block.get("arms"), dict):
        return "ABSENT"
    a = ns_block["arms"].get(arm)
    if not isinstance(a, dict) or not isinstance(a.get("subaudits"), dict):
        return "ABSENT"
    subs = a["subaudits"]
    if any(k not in subs or not isinstance(subs[k], dict) for k in NS_SUBAUDITS):
        return "NOT_EVALUABLE"
    if any(str(subs[k].get("terminal", "")).startswith("CANNOT_AUDIT_") or "terminal" not in subs[k] for k in NS_SUBAUDITS):
        return "NOT_EVALUABLE"
    for k in NS_SUBAUDITS:
        t = subs[k]["terminal"]
        if t == NS_CLEAN:
            continue
        routed = NS_ROUTED.get(k)
        kinds = subs[k].get("finding_kinds")
        if routed is None or t != routed[0] or not isinstance(kinds, list) or not kinds or any(x not in routed[1] for x in kinds):
            return "EVALUABLE_NOT_ADMISSIBLE"
    return "ADMISSIBLE"


def evaluate_matched_twin(block: Any, ns_block: Any, check_declared: bool = True) -> Dict[str, Any]:
    c = "MATCHED_TWIN"
    if block is None:
        return _result(c, CONTROL_MISSING, ["block absent"])
    try:
        _need(block, ("positive_arm", "twin_arm", "descriptor_positive", "descriptor_twin",
                      "operators_positive", "operators_twin", "twin_k_fingerprint_count",
                      "twin_k_target_realizable", "positive_k_target_realized",
                      "multiplicity_reweighting", "outcome_positive_by_world",
                      "outcome_twin_by_world", "interpretation", "declared_terminal"))
        dp, dt = block["descriptor_positive"], block["descriptor_twin"]
        if not isinstance(dp, dict) or not isinstance(dt, dict):
            raise Malformed("descriptors must be objects")
        if set(dp) != set(DESCRIPTOR_COORDINATES) or set(dt) != set(DESCRIPTOR_COORDINATES):
            raise Malformed("descriptor coordinates differ from the registered set")
        if not isinstance(block["twin_k_fingerprint_count"], int) or isinstance(block["twin_k_fingerprint_count"], bool):
            raise Malformed("fingerprint count must be int")
        ops_p, ops_t = block["operators_positive"], block["operators_twin"]
        if not isinstance(ops_p, list) or not isinstance(ops_t, list):
            raise Malformed("operator inventories must be lists")
        out_p = {str(k): _props(v) for k, v in block["outcome_positive_by_world"].items()}
        out_t = {str(k): _props(v) for k, v in block["outcome_twin_by_world"].items()}
        if not out_p or set(out_p) != set(out_t):
            raise Malformed("twin outcomes must cover the same non-empty world set")
    except (Malformed, TypeError, ValueError, KeyError, AttributeError, ZeroDivisionError) as e:
        return _result(c, CONTROL_MALFORMED, [str(e)])

    capacity: List[str] = []
    for coord in DESCRIPTOR_COORDINATES:
        if canon(dp[coord]) != canon(dt[coord]):
            capacity.append("DESCRIPTOR_MISMATCH:" + coord)
    if block["twin_k_fingerprint_count"] != 0:
        capacity.append("K_FINGERPRINT_PRESENT_IN_TWIN")
    if block["twin_k_target_realizable"] is not False:
        capacity.append("K_TARGET_REALIZABLE_IN_TWIN")
    for op in sorted(set(map(str, ops_t)) - set(map(str, ops_p))):
        capacity.append("COMPENSATING_OPERATOR:" + op)
    rw = block["multiplicity_reweighting"]
    if not isinstance(rw, dict) or rw.get("reported") is not True:
        capacity.append("REWEIGHTING_NOT_REPORTED")
    audit: List[str] = []
    for arm in (block["positive_arm"], block["twin_arm"]):
        st = _ns_arm_state(ns_block, str(arm))
        if st in ("ABSENT", "NOT_EVALUABLE"):
            audit.append("NO_SMUGGLING_AUDIT_%s:%s" % (st, arm))
    differing = sorted(w for w in out_p if out_p[w] != out_t[w])
    interp: List[str] = []
    if block["positive_k_target_realized"] is not True:
        interp.append("K_TARGET_NOT_REALIZED_IN_POSITIVE_ARM")
    if not differing:
        interp.append("OUTCOME_IDENTICAL_IN_TWIN")
    if block["interpretation"] != "K_DEPENDENCE_INTERPRETED_AGAINST_MATCHED_TWIN":
        interp.append("INTERPRETATION_NOT_REGISTERED")
    if capacity:
        terminal, reasons = UNMATCHED, capacity + audit
    elif audit:
        terminal, reasons = TWIN_AUDIT_NOT_EVALUABLE, audit
    elif interp:
        terminal, reasons = TWIN_INTERPRETATION_UNSUPPORTED, interp
    else:
        terminal, reasons = MATCHED, []
    if check_declared and block["declared_terminal"] != terminal:
        reasons = reasons + ["DECLARED_TERMINAL_INCONSISTENT:%s" % block["declared_terminal"]]
        if terminal == MATCHED:
            terminal = TWIN_INTERPRETATION_UNSUPPORTED
    return _result(c, terminal, reasons, worlds_differing=len(differing))


def evaluate_encoding(block: Any, claim_props: Mapping[str, Tuple[str, ...]], check_declared: bool = True) -> Dict[str, Any]:
    c = "ENCODING"
    if block is None:
        return _result(c, CONTROL_MISSING, ["block absent"])
    try:
        _need(block, ("reference_census_size", "encodings", "bijection", "projection_mismatches",
                      "resource_fingerprint_mismatches", "decision_rule", "conclusion_by_encoding",
                      "declared_terminal"))
        encs = block["encodings"]
        if not isinstance(encs, list):
            raise Malformed("encodings must be a list")
        for e in encs:
            _need(e, ("encoding_id", "arm", "surface_alphabet", "surface_id_pattern", "census_size"))
            if not isinstance(e["surface_alphabet"], list) or not e["surface_alphabet"]:
                raise Malformed("surface alphabet must be a non-empty list")
        bij = block["bijection"]
        _need(bij, ("domain_size", "codomain_size", "injective", "surjective"))
        ref = block["reference_census_size"]
        pm, rm = block["projection_mismatches"], block["resource_fingerprint_mismatches"]
        for v in (ref, pm, rm, bij["domain_size"], bij["codomain_size"]):
            if not isinstance(v, int) or isinstance(v, bool):
                raise Malformed("census fields must be int")
        concl = {str(k): _conclusion_map(v) for k, v in block["conclusion_by_encoding"].items()}
    except (Malformed, TypeError, ValueError, KeyError, AttributeError, ZeroDivisionError) as e:
        return _result(c, CONTROL_MALFORMED, [str(e)])

    if len(encs) < 2:
        return _result(c, ENC_INSUFFICIENT, ["FEWER_THAN_TWO_ENCODINGS"])
    ids = [str(e["encoding_id"]) for e in encs]
    if len(set(ids)) != len(ids) or set(ids) != set(concl):
        return _result(c, CONTROL_MALFORMED, ["encoding ids and conclusion keys differ"])
    reasons: List[str] = []
    for i in range(len(encs)):
        for j in range(i + 1, len(encs)):
            a, b = encs[i], encs[j]
            if set(map(str, a["surface_alphabet"])) & set(map(str, b["surface_alphabet"])):
                reasons.append("ALPHABETS_OVERLAP:%s|%s" % (a["encoding_id"], b["encoding_id"]))
            if a["surface_id_pattern"] == b["surface_id_pattern"]:
                reasons.append("SURFACE_ID_PATTERN_SHARED:%s|%s" % (a["encoding_id"], b["encoding_id"]))
    if reasons:
        return _result(c, ENC_INSUFFICIENT, ["ENCODINGS_NOT_SYNTACTICALLY_DISJOINT"] + reasons)
    eq: List[str] = []
    if bij["injective"] is not True:
        eq.append("MAP_NOT_INJECTIVE")
    if bij["surjective"] is not True:
        eq.append("MAP_NOT_SURJECTIVE")
    if bij["domain_size"] != ref:
        eq.append("MAP_DOMAIN_%d_NE_CENSUS_%d" % (bij["domain_size"], ref))
    if bij["codomain_size"] != ref:
        eq.append("MAP_CODOMAIN_%d_NE_CENSUS_%d" % (bij["codomain_size"], ref))
    for e in encs:
        if e["census_size"] != ref:
            eq.append("CENSUS_%s_%d_NE_%d" % (e["encoding_id"], e["census_size"], ref))
    if pm != 0:
        eq.append("PROJECTION_MISMATCHES:%d" % pm)
    if rm != 0:
        eq.append("RESOURCE_FINGERPRINT_MISMATCHES:%d" % rm)
    if eq:
        terminal, reasons = ENC_NOT_EQUIVALENT, eq
    else:
        first = concl[ids[0]]
        sens = []
        for other in ids[1:]:
            if set(concl[other]) != set(first):
                sens.append("WORLD_SETS_DIFFER:%s" % other)
                continue
            for w in sorted(first):
                if concl[other][w] != first[w]:
                    sens.append("CONCLUSION_DIFFERS:%s:%s" % (other, w))
        if sens:
            terminal, reasons = ENC_SENSITIVE, sens
        else:
            bad = sorted(w for w in claim_props if w not in first or first[w][1] != claim_props[w])
            if bad or not claim_props:
                terminal, reasons = ENC_CONTRADICTS_CLAIM, ["WORLD:" + w for w in bad] or ["EMPTY_CLAIM"]
            else:
                terminal, reasons = ENC_ROBUST, []
    if check_declared and block["declared_terminal"] != terminal:
        reasons = reasons + ["DECLARED_TERMINAL_INCONSISTENT:%s" % block["declared_terminal"]]
        if terminal == ENC_ROBUST:
            terminal = ENC_CONTRADICTS_CLAIM
    return _result(c, terminal, reasons)


def _pair_distinctness(a: Mapping[str, Any], b: Mapping[str, Any], probes: Sequence[str]) -> Dict[str, Any]:
    axes = [x for x in DIFFERENCE_AXES if a["difference_table"][x] != b["difference_table"][x]]
    ta, tb = a["trace_digest_by_probe"], b["trace_digest_by_probe"]
    aa, ab = a["acceptance_digest_by_probe"], b["acceptance_digest_by_probe"]
    trace_diff = [p for p in probes if ta[p] != tb[p]]
    reencoding = (not trace_diff) and all(aa[p] == ab[p] for p in probes)
    distinct = len(axes) >= MIN_DIFFERING_AXES and bool(trace_diff) and not reencoding
    return {"pair": [a["searcher_id"], b["searcher_id"]], "declared_axes_differing": axes,
            "probes_with_trace_difference": len(trace_diff), "reencoding": reencoding, "distinct": distinct}


def evaluate_search(block: Any, claim_props: Mapping[str, Tuple[str, ...]], check_declared: bool = True) -> Dict[str, Any]:
    c = "SEARCH"
    if block is None:
        return _result(c, CONTROL_MISSING, ["block absent"])
    try:
        _need(block, ("probes", "searchers", "declared_terminal"))
        probes = [str(p) for p in block["probes"]]
        ss = block["searchers"]
        if not isinstance(ss, list) or not probes:
            raise Malformed("searchers must be a list and probes non-empty")
        for s in ss:
            _need(s, ("searcher_id", "difference_table", "coverage", "search_cost", "conclusion_by_world",
                      "trace_digest_by_probe", "acceptance_digest_by_probe"))
            if not isinstance(s["difference_table"], dict) or set(s["difference_table"]) != set(DIFFERENCE_AXES):
                raise Malformed("difference table must carry exactly the registered axes")
            _need(s["coverage"], ("kind", "verified"))
            for key in ("trace_digest_by_probe", "acceptance_digest_by_probe"):
                if not isinstance(s[key], dict) or any(p not in s[key] for p in probes):
                    raise Malformed("digest map must cover every probe")
        concl = [_conclusion_map(s["conclusion_by_world"]) for s in ss]
        if len({s["searcher_id"] for s in ss}) != len(ss):
            raise Malformed("duplicate searcher id")
    except (Malformed, TypeError, ValueError, KeyError, AttributeError, ZeroDivisionError) as e:
        return _result(c, CONTROL_MALFORMED, [str(e)])
    if not ss:
        return _result(c, CONTROL_MISSING, ["no searcher registered"])

    complete = [i for i, s in enumerate(ss) if s["coverage"]["kind"] in COMPLETE_COVERAGE_KINDS and s["coverage"]["verified"] is True]
    ref = complete[0] if complete else 0
    disagreements = []
    for i, s in enumerate(ss):
        if set(concl[i]) != set(concl[ref]):
            disagreements.append("WORLD_SETS_DIFFER:%s" % s["searcher_id"])
            continue
        for w in sorted(concl[ref]):
            if concl[i][w] != concl[ref][w]:
                disagreements.append("DISAGREES:%s:%s" % (s["searcher_id"], w))
    pairs = []
    for x in range(len(complete)):
        for y in range(x + 1, len(complete)):
            pairs.append(_pair_distinctness(ss[complete[x]], ss[complete[y]], probes))
    exhaustive = [ss[i]["searcher_id"] for i in complete if ss[i]["coverage"]["kind"] == EXHAUSTIVE_KIND]
    distinct_pairs = [p for p in pairs if p["distinct"]]
    if disagreements:
        terminal, reasons = SEARCH_SENSITIVE, disagreements
    elif not distinct_pairs and not exhaustive:
        terminal = SEARCH_NOT_DISTINCT
        reasons = ["NO_MATERIALLY_DISTINCT_COMPLETE_PAIR_AND_NO_EXHAUSTIVE_CONSTRUCTION"]
        reasons += ["REENCODING:%s|%s" % tuple(p["pair"]) for p in pairs if p["reencoding"]]
        reasons += ["TOO_FEW_DIFFERING_AXES:%s|%s" % tuple(p["pair"]) for p in pairs if len(p["declared_axes_differing"]) < MIN_DIFFERING_AXES]
    else:
        bad = sorted(w for w in claim_props if w not in concl[ref] or concl[ref][w][1] != claim_props[w])
        if bad or not claim_props:
            terminal, reasons = SEARCH_CONTRADICTS_CLAIM, ["WORLD:" + w for w in bad] or ["EMPTY_CLAIM"]
        else:
            terminal, reasons = SEARCH_ROBUST, []
    if check_declared and block["declared_terminal"] != terminal:
        reasons = reasons + ["DECLARED_TERMINAL_INCONSISTENT:%s" % block["declared_terminal"]]
        if terminal == SEARCH_ROBUST:
            terminal = SEARCH_CONTRADICTS_CLAIM
    return _result(c, terminal, reasons, distinctness=pairs, exhaustive_searchers=exhaustive)


def _dominates(u: Sequence[Fraction], v: Sequence[Fraction]) -> bool:
    return all(a <= b for a, b in zip(u, v)) and any(a < b for a, b in zip(u, v))


def pareto_ids(vectors: Mapping[str, Sequence[Fraction]]) -> List[str]:
    keys = sorted(vectors)
    return [k for k in keys if not any(_dominates(vectors[j], vectors[k]) for j in keys if j != k)]


def _lcm(a: int, b: int) -> int:
    x, y = a, b
    while y:
        x, y = y, x % y
    return a // x * b


def argmin_ids(vectors: Mapping[str, Sequence[Fraction]], weights: Sequence[Fraction]) -> List[str]:
    """Exact weighted-sum argmin; values are scaled to integers by the (positive)
    common denominator, which preserves the order exactly."""
    den = 1
    for w in weights:
        den = _lcm(den, Fraction(w).denominator)
    for v in vectors.values():
        for x in v:
            den = _lcm(den, Fraction(x).denominator)
    wi = [int(Fraction(w) * den) for w in weights]
    vals = {k: sum(a * int(Fraction(x) * den) for a, x in zip(wi, v)) for k, v in vectors.items()}
    lo = min(vals.values())
    return sorted(k for k, v in vals.items() if v == lo)


def _check_invariant(inv: Mapping[str, Any], coords: Sequence[str], vec: Sequence[Fraction]) -> bool:
    def holds(cond: Mapping[str, Any]) -> bool:
        x = vec[list(coords).index(cond["coordinate"])]
        val = rational(cond["value"])
        op = cond["op"]
        if op == "lt":
            return x < val
        if op == "le":
            return x <= val
        if op == "eq":
            return x == val
        if op == "ge":
            return x >= val
        if op == "gt":
            return x > val
        raise Malformed("unknown invariant op %r" % op)
    return (not holds(inv["if"])) or holds(inv["then"])


def evaluate_scalarization(block: Any, claim: Mapping[str, Any], check_declared: bool = True) -> Dict[str, Any]:
    c = "SCALARIZATION"
    if block is None:
        return _result(c, CONTROL_MISSING, ["block absent"])
    try:
        _need(block, ("coordinates", "raw_vectors", "pareto_set", "scalarizations", "declared_terminal"))
        coords = [str(x) for x in block["coordinates"]]
        if not coords or len(set(coords)) != len(coords):
            raise Malformed("coordinates must be distinct and non-empty")
        vectors: Dict[str, Tuple[Fraction, ...]] = {}
        prop: Dict[str, str] = {}
        for rv in block["raw_vectors"]:
            _need(rv, ("point_id", "vector", "multiplicity", "property"))
            v = tuple(rational(x) for x in rv["vector"])
            if len(v) != len(coords) or any(x < 0 for x in v):
                raise Malformed("raw vector shape/sign")
            if not isinstance(rv["multiplicity"], int) or rv["multiplicity"] < 1:
                raise Malformed("multiplicity must be a positive int")
            if rv["point_id"] in vectors:
                raise Malformed("duplicate point id")
            vectors[str(rv["point_id"])] = v
            prop[str(rv["point_id"])] = str(rv["property"])
        if not vectors:
            raise Malformed("no raw vectors")
        scals = []
        for s in block["scalarizations"]:
            _need(s, ("scalarization_id", "weights", "boundary_probe", "winners"))
            w = tuple(rational(x) for x in s["weights"])
            if len(w) != len(coords) or any(x < 0 for x in w):
                raise Malformed("weights must be nonnegative and match coordinates")
            scals.append((s, w))
        wording = claim.get("wording")
        if wording not in WORDINGS:
            raise Malformed("unknown wording")
        invariants = claim.get("frontier_invariants", [])
        if not isinstance(invariants, list):
            raise Malformed("frontier invariants must be a list")
    except (Malformed, TypeError, ValueError, KeyError, AttributeError, ZeroDivisionError) as e:
        return _result(c, CONTROL_MALFORMED, [str(e)])

    front = pareto_ids(vectors)
    if sorted(map(str, block["pareto_set"])) != front:
        return _result(c, SCAL_INCONSISTENT, ["PARETO_SET_MISDECLARED"])
    positive = [(s, w) for s, w in scals if s["boundary_probe"] is not True and all(x > 0 for x in w)]
    distinct_weights = {w for _, w in positive}
    if len(distinct_weights) < 2:
        return _result(c, SCAL_INSUFFICIENT, ["FEWER_THAN_TWO_DISTINCT_STRICTLY_POSITIVE_SCALARIZATIONS:%d" % len(distinct_weights)])
    reasons: List[str] = []
    observed: Dict[str, Tuple[str, ...]] = {}
    for s, w in scals:
        win = argmin_ids(vectors, w)
        if sorted(map(str, s["winners"])) != win:
            reasons.append("WINNERS_MISDECLARED:%s" % s["scalarization_id"])
        observed[str(s["scalarization_id"])] = tuple(sorted({prop[k] for k in win}))
    for s, w in positive:
        if any(k not in front for k in argmin_ids(vectors, w)):
            reasons.append("POSITIVE_SCALARIZATION_PICKED_DOMINATED:%s" % s["scalarization_id"])
    if reasons:
        return _result(c, SCAL_INCONSISTENT, reasons)
    pos_sets = sorted({observed[str(s["scalarization_id"])] for s, _ in positive})
    reversal = len(pos_sets) > 1
    try:
        inv_fail = [str(inv["invariant_id"]) for inv in invariants
                    if not all(_check_invariant(inv, coords, vectors[k]) for k in front)]
    except (Malformed, TypeError, ValueError, KeyError, AttributeError) as e:
        return _result(c, CONTROL_MALFORMED, [str(e)])
    if wording == "UNIVERSAL_WINNER" and reversal:
        terminal = SCAL_SENSITIVE
        reasons = ["POSITIVE_WEIGHTS_REVERSE_WINNER:" + "|".join(",".join(p) for p in pos_sets)]
    elif wording == "PRICE_CONDITIONAL" and any(
            "claimed_properties" not in s or _props(s["claimed_properties"]) != observed[str(s["scalarization_id"])]
            for s, _ in scals):
        terminal = COND_CONTRADICTED
        reasons = ["CLAIM_MISPREDICTS:%s" % s["scalarization_id"] for s, _ in scals
                   if "claimed_properties" not in s or _props(s["claimed_properties"]) != observed[str(s["scalarization_id"])]]
    elif inv_fail:
        terminal, reasons = INVARIANT_CONTRADICTED, ["INVARIANT:" + x for x in inv_fail]
    elif wording == "FRONTIER_INVARIANT" and not invariants:
        terminal, reasons = INVARIANT_CONTRADICTED, ["NO_INVARIANT_REGISTERED"]
    else:
        terminal, reasons = PARETO_OK, []
    if check_declared and block["declared_terminal"] != terminal:
        reasons = reasons + ["DECLARED_TERMINAL_INCONSISTENT:%s" % block["declared_terminal"]]
        if terminal == PARETO_OK:
            terminal = SCAL_INCONSISTENT
    return _result(c, terminal, reasons, pareto_set=front, positive_scalarizations=len(positive),
                   distinct_positive_weight_vectors=len(distinct_weights), winner_reversal=reversal,
                   invariants_holding=[str(inv["invariant_id"]) for inv in invariants if str(inv["invariant_id"]) not in inv_fail])


def evaluate_no_smuggling(block: Any, referenced_arms: Sequence[str]) -> Dict[str, Any]:
    c = "NO_SMUGGLING"
    if block is None:
        return _result(c, CONTROL_MISSING, ["block absent"])
    if not isinstance(block, dict) or not isinstance(block.get("arms"), dict) or not block["arms"]:
        return _result(c, CONTROL_MALFORMED, ["arms must be a non-empty object"])
    arms = sorted(set(map(str, block["arms"])) | set(map(str, referenced_arms)))
    reasons = []
    states = {}
    for arm in arms:
        st = _ns_arm_state(block, arm)
        states[arm] = st
        if st != "ADMISSIBLE":
            reasons.append("%s:%s" % (arm, st))
    return _result(c, NS_NOT_CLEAN if reasons else NS_ADMISSIBLE, reasons, arm_states=states)


# --------------------------------------------------------------------------
# the admission theorem, executed
# --------------------------------------------------------------------------
def validate_record(record: Any) -> Dict[str, Any]:
    if not isinstance(record, dict) or record.get("schema") != SCHEMA_ID:
        return {"schema": VERDICT_SCHEMA_ID, "terminal": CANNOT_PREFIX + "RECORD_SCHEMA",
                "failing_controls": ["RECORD_SCHEMA"], "control_terminals": {}, "reasons": {}}
    claim = record.get("claim")
    try:
        _need(claim, ("claim_id", "mechanism", "k_target_property", "wording", "scope", "conclusion_by_world"))
        if claim["wording"] not in WORDINGS:
            raise Malformed("unknown wording")
        claim_props = {str(w): _props(v) for w, v in claim["conclusion_by_world"].items()}
        if not claim_props:
            raise Malformed("empty claim")
    except (Malformed, TypeError, ValueError, KeyError, AttributeError) as e:
        return {"schema": VERDICT_SCHEMA_ID, "terminal": CANNOT_PREFIX + "CLAIM",
                "failing_controls": ["CLAIM"], "control_terminals": {}, "reasons": {"CLAIM": [str(e)]}}
    controls = record.get("controls")
    if not isinstance(controls, dict):
        controls = {}
    ns = controls.get("NO_SMUGGLING")
    referenced = []
    mt = controls.get("MATCHED_TWIN")
    if isinstance(mt, dict):
        referenced += [str(mt.get("positive_arm")), str(mt.get("twin_arm"))]
    enc = controls.get("ENCODING")
    if isinstance(enc, dict) and isinstance(enc.get("encodings"), list):
        referenced += [str(e.get("arm")) for e in enc["encodings"] if isinstance(e, dict)]
    results = [
        evaluate_matched_twin(mt, ns),
        evaluate_encoding(enc, claim_props),
        evaluate_search(controls.get("SEARCH"), claim_props),
        evaluate_scalarization(controls.get("SCALARIZATION"), claim),
        evaluate_no_smuggling(ns, referenced),
    ]
    failing = [r["control"] for r in results if not r["passed"]]
    missing = [r["control"] for r in results if r["terminal"] == CONTROL_MISSING]
    if not failing:
        terminal = ROBUST
    else:
        terminal = CANNOT_PREFIX + (missing[0] if missing else failing[0])
    return {
        "schema": VERDICT_SCHEMA_ID,
        "record_id": record.get("record_id"),
        "terminal": terminal,
        "failing_controls": failing,
        "control_terminals": {r["control"]: r["terminal"] for r in results},
        "reasons": {r["control"]: r["reasons"] for r in results if r["reasons"]},
        "conditions": {
            "1_matched_twin_interpreted": results[0]["passed"],
            "2_encodings_agree_after_projection": results[1]["passed"],
            "3_distinct_searchers_or_exhaustive_agree": results[2]["passed"],
            "4_pareto_and_positive_scalarizations_consistent": results[3]["passed"],
            "5_no_smuggling_admissible_all_arms": results[4]["passed"],
        },
        "details": {r["control"]: {k: v for k, v in r.items() if k not in ("control", "terminal", "passed", "reasons")}
                    for r in results},
    }


# --------------------------------------------------------------------------
# validate-the-checker-first: a substrate-free toy record and its corruptions
# --------------------------------------------------------------------------
def _toy_record() -> Dict[str, Any]:
    worlds = {"w1": ["A"], "w2": ["B"]}
    concl = {"w1": {"best": "8", "properties": ["A"]}, "w2": {"best": "8", "properties": ["B"]}}
    desc = {k: "same" for k in DESCRIPTOR_COORDINATES}
    ns_arm = {"terminal": NS_CLEAN, "subaudits": {k: {"terminal": NS_CLEAN, "finding_kinds": []} for k in NS_SUBAUDITS}}
    table1 = {"representation": "raw", "exploration_order": "enumeration", "pruning": "none",
              "acceptance_termination": "full_scan", "completeness_proof": "construction", "search_cost_unit": "evaluations"}
    table2 = {"representation": "compressed", "exploration_order": "bound_sorted", "pruning": "admissible_bound",
              "acceptance_termination": "incumbent", "completeness_proof": "admissibility", "search_cost_unit": "evaluations"}
    return {
        "schema": SCHEMA_ID,
        "record_id": "TOY_POSITIVE",
        "claim": {"claim_id": "toy", "mechanism": "k", "k_target_property": "t", "wording": "PRICE_CONDITIONAL",
                  "scope": "toy", "conclusion_by_world": worlds,
                  "frontier_invariants": [{"invariant_id": "I", "if": {"coordinate": "x", "op": "lt", "value": "2"},
                                           "then": {"coordinate": "y", "op": "eq", "value": "4"}}]},
        "controls": {
            "MATCHED_TWIN": {"positive_arm": "P", "twin_arm": "N", "descriptor_positive": dict(desc),
                             "descriptor_twin": dict(desc), "operators_positive": ["op"], "operators_twin": ["op"],
                             "twin_k_fingerprint_count": 0, "twin_k_target_realizable": False,
                             "positive_k_target_realized": True, "multiplicity_reweighting": {"reported": True},
                             "outcome_positive_by_world": {"w1": ["A"], "w2": ["B"]},
                             "outcome_twin_by_world": {"w1": ["B"], "w2": ["B"]},
                             "interpretation": "K_DEPENDENCE_INTERPRETED_AGAINST_MATCHED_TWIN",
                             "declared_terminal": MATCHED},
            "ENCODING": {"reference_census_size": 2,
                         "encodings": [{"encoding_id": "e1", "arm": "P", "surface_alphabet": ["0", "1"], "surface_id_pattern": "q#", "census_size": 2},
                                       {"encoding_id": "e2", "arm": "P2", "surface_alphabet": ["a", "b"], "surface_id_pattern": "W#", "census_size": 2}],
                         "bijection": {"domain_size": 2, "codomain_size": 2, "injective": True, "surjective": True},
                         "projection_mismatches": 0, "resource_fingerprint_mismatches": 0,
                         "decision_rule": "SEMANTIC_ARGMIN_SET",
                         "conclusion_by_encoding": {"e1": concl, "e2": concl}, "declared_terminal": ENC_ROBUST},
            "SEARCH": {"probes": ["w1", "w2"], "declared_terminal": SEARCH_ROBUST,
                       "searchers": [
                           {"searcher_id": "s1", "difference_table": table1, "coverage": {"kind": EXHAUSTIVE_KIND, "verified": True},
                            "search_cost": {"evaluations": 2}, "conclusion_by_world": concl,
                            "trace_digest_by_probe": {"w1": "t1", "w2": "t1"}, "acceptance_digest_by_probe": {"w1": "a1", "w2": "a2"}},
                           {"searcher_id": "s2", "difference_table": table2, "coverage": {"kind": "ADMISSIBLE_BOUND", "verified": True},
                            "search_cost": {"evaluations": 1}, "conclusion_by_world": concl,
                            "trace_digest_by_probe": {"w1": "t2", "w2": "t3"}, "acceptance_digest_by_probe": {"w1": "a3", "w2": "a4"}}]},
            "SCALARIZATION": {"coordinates": ["x", "y"],
                              "raw_vectors": [{"point_id": "a", "vector": ["1", "4"], "multiplicity": 1, "property": "A"},
                                              {"point_id": "b", "vector": ["4", "1"], "multiplicity": 1, "property": "B"},
                                              {"point_id": "c", "vector": ["4", "4"], "multiplicity": 1, "property": "B"}],
                              "pareto_set": ["a", "b"],
                              "scalarizations": [{"scalarization_id": "w1", "weights": ["4", "1"], "boundary_probe": False, "winners": ["a"], "claimed_properties": ["A"]},
                                                 {"scalarization_id": "w2", "weights": ["1", "4"], "boundary_probe": False, "winners": ["b"], "claimed_properties": ["B"]}],
                              "declared_terminal": PARETO_OK},
            "NO_SMUGGLING": {"arms": {"P": ns_arm, "N": ns_arm, "P2": ns_arm}},
        },
    }


def self_test() -> Dict[str, bool]:
    """The validator must pass its no-alarm toy and fire on each toy corruption
    before it is trusted on a real record."""
    import copy
    out: Dict[str, bool] = {}
    base = _toy_record()
    v = validate_record(base)
    out["toy_positive_is_robust"] = v["terminal"] == ROBUST and v["failing_controls"] == []
    for ctl in CONTROL_ORDER:
        r = copy.deepcopy(base)
        del r["controls"][ctl]
        out["toy_delete_" + ctl.lower() + "_fails_closed"] = validate_record(r)["terminal"] == CANNOT_PREFIX + ctl
    r = copy.deepcopy(base)
    r["controls"]["MATCHED_TWIN"]["descriptor_twin"]["budget"] = "half"
    out["toy_descriptor_mismatch_unmatched"] = validate_record(r)["control_terminals"]["MATCHED_TWIN"] == UNMATCHED
    r = copy.deepcopy(base)
    r["controls"]["ENCODING"]["bijection"]["injective"] = False
    out["toy_noninjective_map_not_equivalent"] = validate_record(r)["control_terminals"]["ENCODING"] == ENC_NOT_EQUIVALENT
    r = copy.deepcopy(base)
    r["controls"]["SEARCH"]["searchers"][1]["conclusion_by_world"] = {"w1": {"best": "8", "properties": ["B"]}, "w2": {"best": "8", "properties": ["B"]}}
    out["toy_disagreeing_searcher_sensitive"] = validate_record(r)["control_terminals"]["SEARCH"] == SEARCH_SENSITIVE
    r = copy.deepcopy(base)
    r["claim"]["wording"] = "UNIVERSAL_WINNER"
    out["toy_universal_wording_sensitive"] = validate_record(r)["control_terminals"]["SCALARIZATION"] == SCAL_SENSITIVE
    r = copy.deepcopy(base)
    r["controls"]["NO_SMUGGLING"]["arms"]["N"] = {"terminal": "AUDIT_NOT_CLEAN", "subaudits": dict(
        base["controls"]["NO_SMUGGLING"]["arms"]["N"]["subaudits"], lexical={"terminal": "LEXICAL_LEAKAGE", "finding_kinds": ["LEXICAL"]})}
    out["toy_lexical_leak_not_clean"] = validate_record(r)["control_terminals"]["NO_SMUGGLING"] == NS_NOT_CLEAN
    r = copy.deepcopy(base)
    r["controls"]["SCALARIZATION"]["raw_vectors"][0]["vector"] = [float(1), "4"]  # a runtime float: the hostile input
    out["toy_float_rejected"] = validate_record(r)["control_terminals"]["SCALARIZATION"] == CONTROL_MALFORMED
    r = copy.deepcopy(base)
    r["controls"]["SEARCH"]["declared_terminal"] = SEARCH_SENSITIVE
    out["toy_declared_terminal_inconsistency_fails"] = validate_record(r)["control_terminals"]["SEARCH"] != SEARCH_ROBUST
    out["toy_wrong_schema_fails_closed"] = validate_record({"schema": "other"})["terminal"] == CANNOT_PREFIX + "RECORD_SCHEMA"
    return out


if __name__ == "__main__":
    print(canonical_json(self_test()), end="")
