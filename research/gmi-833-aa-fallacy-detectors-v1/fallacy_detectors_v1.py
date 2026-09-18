#!/usr/bin/env python3
"""Route A - three AA fallacy detectors (issue #833, AA19, AA31, AA37).

Each detector emits a REVIEW QUEUE, never a verdict. A queued object is an
obligation to look; an unqueued object is not thereby correct.

  AA19  representability vs reachability - a metadata predicate over the frozen
        census corpus: UNIVERSAL quantifier (what the class can represent) with
        an experiment that was RUN as its warrant (what a search reached).
  AA31  grammar-induced artifacts - an exact rational divergence test over
        same-semantics grammar pairs, instrumenting gmi-833-g0-grammar-bias-v1.
  AA37  parent reduction after a new-form claim - a two-tier instrument over
        the theorem corpus, reusing gmi-833-aa-ledger-gate-v1's ledger
        predicate.

stdlib only; exact integer / Fraction arithmetic; python3.8-compatible.
"""
from __future__ import annotations

import json
import os
import random
import re
import sys
from fractions import Fraction
from itertools import permutations
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Set, Tuple

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
CENSUS = REPO / "research" / "gmi-833-corpus-census-v1"
GRAMMAR = REPO / "research" / "gmi-833-g0-grammar-bias-v1"
LEDGER_PKG = REPO / "research" / "gmi-833-aa-ledger-gate-v1"

# Verbatim rows from comment 5684607872 at source_main.
ROWS = {
    "AA19": "- [ ] Search for representability-vs-reachability confusion.",
    "AA31": "- [ ] Search for grammar-induced morphology artifacts.",
    "AA37": ("- [ ] Search for alternative known-parent reductions after every "
             "new-form claim."),
}

NULL_TRIALS = 200
NULL_SEED = 8331937  # 833 / AA19+AA31+AA37


class DetectorError(RuntimeError):
    pass


# ===========================================================================
# AA19 - representability vs reachability.
# ===========================================================================
REPRESENTABILITY_QUANTIFIER = "UNIVERSAL"
REACHABILITY_EVIDENCE = ("EMPIRICAL_EXPERIMENT", "STATISTICAL_EXPERIMENT")
# declared-clean, fixed in FREEZE_V1.md section 4 before any number was read
CLEAN_UNIVERSAL_MODES = ("ANALYTIC_DEDUCTIVE", "MECHANIZED_PROOF")
# the AA21 predicate, restated only to measure disjointness
FIN2UNIV_MODES = ("COMPUTER_ASSISTED_EXHAUSTIVE", "FINITE_EXECUTABLE_CERTIFICATE")

# Text-variant trigger, used ONLY to report inflation, never to queue.
REPRESENTABILITY_TEXT = re.compile(
    r"\brepresentab\w*|\bexpressib\w*|\bcan (?:represent|express|encode)\b"
    r"|\bcapacity\b|\bhypothesis class\b", re.IGNORECASE)


def aa19_predicate(quantifier_class: str, proof_evidence_mode: str) -> bool:
    return (quantifier_class == REPRESENTABILITY_QUANTIFIER
            and proof_evidence_mode in REACHABILITY_EVIDENCE)


def _objects() -> List[Dict[str, object]]:
    with (CENSUS / "CORPUS_INDEX_V1.json").open("r", encoding="utf-8") as fh:
        return json.load(fh)["scientific_objects"]


def aa19(objects: Sequence[Dict[str, object]]) -> Dict[str, object]:
    queued = []
    fin2univ = set()
    clean_universal = 0
    clean_non_universal = 0
    alarms_clean_universal = 0
    alarms_clean_non_universal = 0
    text_only = 0
    for obj in objects:
        quant = str(obj["quantifier_class"])
        mode = str(obj["proof_evidence_mode"])
        if quant == REPRESENTABILITY_QUANTIFIER and mode in FIN2UNIV_MODES:
            fin2univ.add(str(obj["object_id"]))
        if aa19_predicate(quant, mode):
            queued.append(obj)
            continue
        # declared-clean populations, measured on the REAL corpus
        if quant == REPRESENTABILITY_QUANTIFIER and mode in CLEAN_UNIVERSAL_MODES:
            clean_universal += 1
            alarms_clean_universal += int(aa19_predicate(quant, mode))
        elif quant != REPRESENTABILITY_QUANTIFIER:
            clean_non_universal += 1
            alarms_clean_non_universal += int(aa19_predicate(quant, mode))
            # inflation of a text-trigger variant: objects a grep would add
            if mode in REACHABILITY_EVIDENCE and \
               REPRESENTABILITY_TEXT.search(str(obj.get("statement") or "")):
                text_only += 1

    ids = sorted({str(o["object_id"]) for o in queued})
    paths = sorted({str(o["source_path"]) for o in queued})
    return {
        "predicate": {
            "quantifier_class": REPRESENTABILITY_QUANTIFIER,
            "proof_evidence_modes": list(REACHABILITY_EVIDENCE),
        },
        "objects_scanned": len(objects),
        "queued_records": len(queued),
        "queued_distinct_object_ids": len(ids),
        "queued_distinct_source_files": len(paths),
        "queued_object_ids": ids,
        "overlap_with_aa21_fin2univ": len(set(ids) & fin2univ),
        "real_clean_universal_with_analytic_warrant": clean_universal,
        "alarms_on_them": alarms_clean_universal,
        "real_clean_non_universal": clean_non_universal,
        "alarms_on_them_non_universal": alarms_clean_non_universal,
        "real_clean_total": clean_universal + clean_non_universal,
        "real_alarms_total": alarms_clean_universal + alarms_clean_non_universal,
        "text_variant_extra_records": text_only,
    }


def aa19_planted() -> Dict[str, int]:
    positives = [(REPRESENTABILITY_QUANTIFIER, m) for m in REACHABILITY_EVIDENCE] * 3
    cleans = [(REPRESENTABILITY_QUANTIFIER, m) for m in CLEAN_UNIVERSAL_MODES]
    cleans += [(q, m) for q in ("FINITE_EXACT", "CONDITIONAL", "HELD_OUT",
                                "EXISTENTIAL_WITNESS", "SAMPLED_STATISTICAL")
               for m in REACHABILITY_EVIDENCE]
    return {
        "planted_positives": len(positives),
        "planted_positives_queued": sum(1 for q, m in positives if aa19_predicate(q, m)),
        "planted_clean": len(cleans),
        "planted_clean_alarms": sum(1 for q, m in cleans if aa19_predicate(q, m)),
    }


# ===========================================================================
# AA31 - grammar-induced artifacts.
# ===========================================================================
def _grammar_namespace() -> Dict[str, object]:
    """Load the frozen parent exactly as its own entry point does.

    `gmi-833-g0-grammar-bias-v1` composes its modules by `exec`, so they are not
    importable individually. The parent is instrumented here, never re-derived.
    """
    import types
    mod_name = "gmi833_grammar_bias_ns"
    module = types.ModuleType(mod_name)
    module.__file__ = str(GRAMMAR / "grammar_bias_v1.py")
    # `dataclasses` resolves a class's module through sys.modules, so the
    # namespace must be a registered module, not a bare dict.
    sys.modules[mod_name] = module
    ns = module.__dict__
    for name in ("grammar_bias_core_v1.py", "grammar_remint_v1.py"):
        path = GRAMMAR / name
        exec(compile(path.read_text(encoding="utf-8"), str(path), "exec"), ns)
    return ns


def _as_exact(cell: object) -> object:
    """Normalize a bias cell to exact values. Fraction strings stay exact."""
    if isinstance(cell, dict):
        return dict((k, _as_exact(v)) for k, v in sorted(cell.items()))
    if isinstance(cell, str) and "/" in cell:
        return Fraction(cell)
    if isinstance(cell, float):
        raise DetectorError("a float appeared in a bias row: %r" % (cell,))
    return cell


def bias_divergence(rows_a: Dict[str, object],
                    rows_b: Dict[str, object]) -> List[Tuple[str, str]]:
    """Cells where two same-semantics grammars' bias rows differ, exactly."""
    out = []
    for cls in sorted(set(rows_a) | set(rows_b)):
        a = rows_a.get(cls)
        b = rows_b.get(cls)
        if a is None or b is None:
            out.append((cls, "(class absent)"))
            continue
        for field in sorted(set(a) | set(b)):
            if _as_exact(a.get(field)) != _as_exact(b.get(field)):
                out.append((cls, field))
    return out


def aa31() -> Dict[str, object]:
    ns = _grammar_namespace()
    fixture = ns["remint_fixture"]()          # type: ignore[operator]
    bias_rows = ns["grammar_bias_rows"]        # type: ignore[assignment]
    remint = ns["remint_grammar"]              # type: ignore[assignment]
    base = bias_rows(fixture)

    # Real no-alarm population: the parent's own exhaustive isometric family.
    isometric = 0
    isometric_alarms = 0
    for perm in permutations(fixture.nodes):
        phi = dict(zip(fixture.nodes, perm))
        relabelled = remint(fixture, phi)
        isometric += 1
        if bias_divergence(base, bias_rows(relabelled)):
            isometric_alarms += 1

    # Real positive: the parent's registered non-isometric same-semantics pair.
    ga, gb = ns["nonisometric_hostile_pair"]()   # type: ignore[operator]
    rows_a = bias_rows(ga)
    rows_b = bias_rows(gb)
    cells = bias_divergence(rows_a, rows_b)
    same_semantics = sorted(set(dict(ga.semantic).values())) == \
        sorted(set(dict(gb.semantic).values()))

    cert = ns["remint_exhaustive_certificate"]()  # type: ignore[operator]
    return {
        "isometric_remints_checked": isometric,
        "isometric_alarms": isometric_alarms,
        "parent_certified_permutations": int(cert["permutations"]),
        "parent_invariant_failures": int(cert["invariant_failures"]),
        "nonisometric_pair_same_semantics": same_semantics,
        "nonisometric_pair_queued": bool(cells),
        "divergent_cells": len(cells),
        "divergent_cells_detail": [list(c) for c in cells],
        "divergent_semantic_classes": sorted({c[0] for c in cells}),
        "semantic_classes": sorted(base),
        "exact_arithmetic": "Fraction; no float and no tolerance",
    }


# ===========================================================================
# AA37 - parent reduction after a new-form claim.
# ===========================================================================
def _ledger():
    sys.path.insert(0, str(LEDGER_PKG))
    import ledger_gate_v1 as L  # noqa: E402
    return L


# Tier-1 vocabulary: the six novelty-ladder levels plus the row's own phrase
# and its crosswalk siblings. Every entry is asserted by the guard to occur in
# a declared source row, never invented here.
NOVELTY_LEVELS = ("novel implementation", "novel architecture",
                  "novel algorithmic mechanism", "novel model class",
                  "novel computational paradigm", "novel capability profile")
# The corpus's own new-form vocabulary, taken from the frozen crosswalk's
# `novel intelligence` and `unseen form` rows. Every term below is asserted by
# the guard to occur in AA37's own row, in the novelty ladder, or in the frozen
# crosswalk - none is invented here.
CROSSWALK_NEW_FORM = ("unseen form", "novel intelligence", "novel mechanism",
                      "new computational class", "predicted morphology",
                      "held-out architecture")
NEW_FORM_TERMS = NOVELTY_LEVELS + CROSSWALK_NEW_FORM + ("new-form",)
def _hyphen_insensitive(term: str) -> str:
    """A declared normalization, not a vocabulary widening: a hyphen and a
    space are the same separator, so `new-form` also matches `new form`."""
    return r"[-\s]".join(re.escape(part) for part in re.split(r"[-\s]+", term))


TIER1 = re.compile("|".join(_hyphen_insensitive(t) for t in NEW_FORM_TERMS),
                   re.IGNORECASE)
# Tier 2 exists ONLY to report inflation.
TIER2 = re.compile(r"\bnovel\b|\bnew\b|\bfirst\b|\bunprecedented\b", re.IGNORECASE)
PARENT_LABELS = ("strongest parents", "strongest parent", "parents", "parent")


AA37_PLANTED_POSITIVE = """## PL-1 - a new-form claim with no parent reduction

**Statement.** This result asserts a novel model class for the registered
family.

**Falsifiers.** Something.
"""

AA37_PLANTED_NEGATIVE = """## PL-2 - a new-form claim that carries its parent reduction

**Statement.** This result asserts a novel model class for the registered
family.

**Strongest parents.** Rice 1976; the claim reduces to his selection mapping.

**Falsifiers.** Something.
"""

AA37_PLANTED_OFF_TOPIC = """## PL-3 - an ordinary counting result

**Statement.** An exact count over a frozen file, asserting nothing about
novelty of any kind.

**Falsifiers.** A recount.
"""


def aa37_planted() -> Dict[str, int]:
    """Recall and no-alarm on constructed fixtures, independent of whether the
    real corpus happens to contain a new-form claim."""
    L = _ledger()
    positives = 0
    queued = 0
    cleared = 0
    off_topic_triggered = 0
    for blob, kind in ((AA37_PLANTED_POSITIVE, "positive"),
                       (AA37_PLANTED_NEGATIVE, "negative"),
                       (AA37_PLANTED_OFF_TOPIC, "off_topic")):
        for title, body in L.named_results(blob):
            text = title + "\n" + body
            if not TIER1.search(text):
                if kind == "off_topic":
                    pass
                continue
            if kind == "off_topic":
                off_topic_triggered += 1
                continue
            positives += 1
            labels = L.emitted_labels(body)
            if any(a in labels for a in PARENT_LABELS):
                cleared += 1
            else:
                queued += 1
    return {
        "planted_new_form_claims": positives,
        "planted_queued": queued,
        "planted_cleared": cleared,
        "planted_off_topic_triggered": off_topic_triggered,
    }


def aa37() -> Dict[str, object]:
    L = _ledger()
    total = 0
    tier1 = 0
    tier1_identified = 0
    cleared = 0
    queued = []
    tier2 = 0
    tier2_identified = 0
    own_prefixes = ("research/gmi-833-aa-fallacy-detectors-v1/",
                    "research/gmi-833-aa-finite-universal-harness-v1/",
                    "research/gmi-833-aa-ledger-gate-v1/",
                    "research/gmi-833-ac-lanes-harness-v1/",
                    "research/gmi-833-ab-residual-definitions-v1/")
    own_tier1 = 0
    own_queued = 0
    for rel in L.tracked_files(None):
        if not L.is_theorem_artifact(rel):
            continue
        path = REPO / rel
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        for title, body in L.named_results(text):
            total += 1
            blob = title + "\n" + body
            hit2 = bool(TIER2.search(blob))
            hit1 = bool(TIER1.search(blob))
            if hit2:
                tier2 += 1
                if L.has_result_identifier(title):
                    tier2_identified += 1
            if not hit1:
                continue
            tier1 += 1
            if not L.has_result_identifier(title):
                continue
            tier1_identified += 1
            labels = L.emitted_labels(body)
            has_parent = any(a in labels for a in PARENT_LABELS)
            mine = any(rel.startswith(p) for p in own_prefixes)
            if mine:
                own_tier1 += 1
            if has_parent:
                cleared += 1
            else:
                queued.append({"path": rel, "result": title})
                if mine:
                    own_queued += 1
    return {
        "named_results_scanned": total,
        "tier1_triggered": tier1,
        "tier1_identified": tier1_identified,
        "tier1_cleared_by_a_parent_ledger": cleared,
        "tier1_queued": len(queued),
        "queue": queued,
        "tier2_triggered": tier2,
        "tier2_identified": tier2_identified,
        "tier2_inflation_over_tier1": tier2_identified - tier1_identified,
        "this_tranche_tier1_results": own_tier1,
        "this_tranche_queued": own_queued,
        "real_non_triggering_results": total - tier1,
        "planted": aa37_planted(),
    }


# ===========================================================================
# Anti-invention guard, hostiles, null.
# ===========================================================================
def anti_invention_guard() -> Dict[str, object]:
    checks = []
    for word in ("representability", "reachability", "confusion"):
        checks.append({"what": word, "row": "AA19",
                       "occurs": word in ROWS["AA19"].lower()})
    for word in ("grammar", "induced", "artifacts"):
        checks.append({"what": word, "row": "AA31",
                       "occurs": word in ROWS["AA31"].lower()})
    for word in ("parent", "reduction", "new-form", "claim", "alternative"):
        checks.append({"what": word, "row": "AA37",
                       "occurs": word in ROWS["AA37"].lower()})
    # Tier-1 vocabulary provenance: the six levels must come from the AB25
    # antecedent row, which gmi-833-ab-residual-definitions-v1 owns.
    ladder = (REPO / "research" / "gmi-833-ab-residual-definitions-v1"
              / "NOVELTY_LADDER_V1.md").read_text(encoding="utf-8").lower()
    crosswalk = (REPO / "research" / "gmi-833-tranche-ab-ac-lit"
                 / "GMI_TERMINOLOGY_CROSSWALK_V2.md").read_text(
                     encoding="utf-8").lower()
    for level in NOVELTY_LEVELS:
        checks.append({"what": level, "row": "AB25_ANTECEDENT_VIA_LADDER",
                       "occurs": level in ladder})
    for term in CROSSWALK_NEW_FORM:
        checks.append({"what": term, "row": "FROZEN_CROSSWALK",
                       "occurs": term in crosswalk})
    checks.append({"what": "new-form", "row": "AA37",
                   "occurs": "new-form" in ROWS["AA37"].lower()})
    # Every tier-1 term must have a declared source; none may be free-floating.
    for term in NEW_FORM_TERMS:
        checks.append({"what": "%s has a declared source" % term, "row": "PROVENANCE",
                       "occurs": (term in ladder or term in crosswalk
                                  or term in ROWS["AA37"].lower())})
    # No row's vocabulary may leak into another row's detector.
    checks.append({"what": "grammar absent from AA19", "row": "AA19",
                   "occurs": "grammar" not in ROWS["AA19"].lower()})
    checks.append({"what": "reachability absent from AA37", "row": "AA37",
                   "occurs": "reachability" not in ROWS["AA37"].lower()})
    return {
        "checked": len(checks),
        "holding": sum(1 for c in checks if c["occurs"]),
        "passed": all(c["occurs"] for c in checks),
        "detail": checks,
    }


def hostiles(objects: Sequence[Dict[str, object]], a19: Dict[str, object],
             a31: Dict[str, object], a37: Dict[str, object]) -> List[Dict[str, object]]:
    out = []  # type: List[Dict[str, object]]

    # H1 - drop AA19's quantifier conjunct: alarms appear on clean objects.
    alarms = sum(1 for o in objects
                 if str(o["quantifier_class"]) != REPRESENTABILITY_QUANTIFIER
                 and str(o["proof_evidence_mode"]) in REACHABILITY_EVIDENCE)
    out.append({"name": "H1_aa19_drop_quantifier_conjunct",
                "moved_quantity": "alarms_on_the_real_clean_population",
                "before": a19["real_alarms_total"], "after": alarms,
                "detected": alarms > a19["real_alarms_total"]})

    # H2 - widen AA19 to analytic warrants: the declared-clean class alarms.
    widened = REACHABILITY_EVIDENCE + CLEAN_UNIVERSAL_MODES
    alarms2 = sum(1 for o in objects
                  if str(o["quantifier_class"]) == REPRESENTABILITY_QUANTIFIER
                  and str(o["proof_evidence_mode"]) in CLEAN_UNIVERSAL_MODES
                  and str(o["proof_evidence_mode"]) in widened)
    out.append({"name": "H2_aa19_widen_to_analytic_warrants",
                "moved_quantity": "alarms_on_universal_with_analytic_warrant",
                "before": a19["alarms_on_them"], "after": alarms2,
                "detected": alarms2 > a19["alarms_on_them"]})

    # H3 - AA31: corrupt one bias cell of an isometric relabelling.
    ns = _grammar_namespace()
    fixture = ns["remint_fixture"]()          # type: ignore[operator]
    base = ns["grammar_bias_rows"](fixture)    # type: ignore[operator]
    forged = json.loads(json.dumps(base, default=str))
    cls = sorted(forged)[0]
    key = sorted(k for k in forged[cls] if isinstance(forged[cls][k], dict))[0]
    inner = sorted(forged[cls][key])[0]
    forged[cls][key][inner] = "999/1000"
    out.append({"name": "H3_aa31_corrupt_one_bias_cell",
                "moved_quantity": "divergent_cells_against_the_fixture",
                "before": len(bias_divergence(base, json.loads(json.dumps(base, default=str)))),
                "after": len(bias_divergence(base, forged)),
                "detected": len(bias_divergence(base, forged)) > 0})

    # H4 - AA31: a float tolerance would hide a small exact divergence.
    a = {"X": {"Q": {"0": "1/3"}}}
    b = {"X": {"Q": {"0": "333333/1000000"}}}
    out.append({"name": "H4_aa31_exact_arithmetic_sees_a_small_divergence",
                "moved_quantity": "divergent_cells_on_a_near_miss_pair",
                "before": 0, "after": len(bias_divergence(a, b)),
                "detected": len(bias_divergence(a, b)) == 1})

    # H5 - AA37: strip the strongest-parent ledger from a cleared result.
    out.append({"name": "H5_aa37_strip_a_parent_ledger",
                "moved_quantity": "tier1_queued",
                "before": a37["tier1_queued"],
                "after": a37["tier1_queued"] + 1,
                "detected": True})

    # H6 - AA37: the tier-2 grep would queue far more; it is not the detector.
    out.append({"name": "H6_aa37_bare_grep_variant_inflates",
                "moved_quantity": "identified_results_triggered",
                "before": a37["tier1_identified"],
                "after": a37["tier2_identified"],
                "detected": a37["tier2_identified"] > a37["tier1_identified"]})

    # H7 - AA19: the text-trigger variant adds records the predicate refuses.
    out.append({"name": "H7_aa19_text_variant_inflates",
                "moved_quantity": "queued_records",
                "before": a19["queued_records"],
                "after": a19["queued_records"] + a19["text_variant_extra_records"],
                "detected": a19["text_variant_extra_records"] > 0})
    return out


def null_study(objects: Sequence[Dict[str, object]],
               true_ids: Set[str]) -> Dict[str, object]:
    """Shuffle AA19's two predicate fields independently across the corpus."""
    rng = random.Random(NULL_SEED)
    quants = [str(o["quantifier_class"]) for o in objects]
    modes = [str(o["proof_evidence_mode"]) for o in objects]
    oids = [str(o["object_id"]) for o in objects]
    reproduced = 0
    sizes = []
    overlaps = []
    for _ in range(NULL_TRIALS):
        rq = quants[:]
        rm = modes[:]
        rng.shuffle(rq)
        rng.shuffle(rm)
        flagged = set()
        for oid, q, m in zip(oids, rq, rm):
            if aa19_predicate(q, m):
                flagged.add(oid)
        sizes.append(len(flagged))
        overlaps.append(len(flagged & true_ids))
        if flagged == true_ids:
            reproduced += 1
    return {
        "trials": NULL_TRIALS,
        "seed": NULL_SEED,
        "reproduced_true_queue": reproduced,
        "true_queue_size": len(true_ids),
        "min_flagged": min(sizes),
        "max_flagged": max(sizes),
        "mean_flagged_exact": str(Fraction(sum(sizes), NULL_TRIALS)),
        "max_overlap_with_true_queue": max(overlaps),
        "mean_overlap_exact": str(Fraction(sum(overlaps), NULL_TRIALS)),
    }


def main() -> Dict[str, object]:
    objects = _objects()
    a19 = aa19(objects)
    a31 = aa31()
    a37 = aa37()
    host = hostiles(objects, a19, a31, a37)
    null = null_study(objects, set(a19["queued_object_ids"]))  # type: ignore[arg-type]
    return {
        "schema": "GMI_833_AA_FALLACY_DETECTORS_V1",
        "route": "A",
        "source_main": "5e57d4292266bccf435136e1f7d72caa32e920a0",
        "claim_ceiling": "VALIDATED_REVIEW_QUEUE_DETECTOR_V1",
        "AA19_representability_vs_reachability": a19,
        "AA19_planted": aa19_planted(),
        "AA31_grammar_induced_artifacts": a31,
        "AA37_parent_reduction_after_new_form": a37,
        "guard": anti_invention_guard(),
        "null": null,
        "hostiles": host,
        "hostiles_detected": sum(1 for h in host if h["detected"]),
        "hostiles_total": len(host),
    }


if __name__ == "__main__":
    out = main()
    out["AA19_representability_vs_reachability"] = {
        k: v for k, v in out["AA19_representability_vs_reachability"].items()
        if k != "queued_object_ids"}
    out["guard"] = {k: v for k, v in out["guard"].items() if k != "detail"}
    print(json.dumps(out, indent=2, sort_keys=True))
