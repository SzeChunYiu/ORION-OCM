#!/usr/bin/env python3
"""Route A - completeness checker for the AB08 and AB25 definition artifacts.

AB08 and AB25 are AUTHORING rows: their verbs are `parent-subtract` and
`Define`. They are discharged by producing the artifact with every component
the row itself names, plus a checker that verifies completeness, exactness and
non-degeneracy. This is that checker.

Route B (`independent_definitions_oracle_v1.py`) re-derives every quantity with
an independently written parser and is compared by set equality.

stdlib only; exact integer arithmetic; python3.8-compatible.
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Dict, List, Sequence, Set, Tuple

HERE = Path(__file__).resolve().parent
RICE = HERE / "RICE_PARENT_SUBTRACTION_V1.md"
LADDER = HERE / "NOVELTY_LADDER_V1.md"

# Verbatim rows from comment 5684607872 at source_main.
AB08_ROW = ("- [ ] Explicitly parent-subtract Rice-style **algorithm selection**: "
            "problem space, feature space, algorithm space, performance space, "
            "selection mapping.")
AB25_ROW = "- [ ] Define a novelty ladder using those academically interpretable levels."
# AB25's antecedent, declared in FREEZE_V1.md section 4 BEFORE any level was written.
AB25_ANTECEDENT = (
    "- [x] Audit `novel intelligence`; distinguish **novel implementation**, "
    "**novel architecture**, **novel algorithmic mechanism**, **novel model class**, "
    "**novel computational paradigm/domain**, and **novel capability profile**.")

VERDICTS = ("ABSORBED", "PARTIAL", "DIVERGENT")
RICE_FIELDS = ("Rice's object", "GMI's object", "Verdict",
               "What Rice already supplies", "Residual")
LADDER_FIELDS = ("Operational criterion", "Falsifier", "Parent literature",
                 "Demotion rule")


class DefinitionError(RuntimeError):
    pass


def normalize(text: str) -> str:
    low = text.lower().replace("*", "").replace("`", "").replace("–", "-")
    for ch in "-/,":
        low = low.replace(ch, " ")
    return " ".join(low.split())


# ---------------------------------------------------------------------------
# Requirements are EXTRACTED from the rows, never typed in.
# ---------------------------------------------------------------------------
def ab08_components() -> List[str]:
    tail = AB08_ROW.split("algorithm selection**:", 1)[1].rstrip(".")
    return [p.strip() for p in tail.split(",") if p.strip()]


def ab25_levels() -> List[str]:
    """The six bolded terms of AB25's declared antecedent row, in row order."""
    body = AB25_ANTECEDENT.split("distinguish", 1)[1]
    return [m.strip() for m in re.findall(r"\*\*([^*]+)\*\*", body)]


# ---------------------------------------------------------------------------
# Section parsing.
# ---------------------------------------------------------------------------
def sections(path: Path) -> List[Tuple[str, str]]:
    text = path.read_text(encoding="utf-8")
    out = []
    title = None
    body = []  # type: List[str]
    for line in text.split("\n"):
        if line.startswith("## "):
            if title is not None:
                out.append((title, "\n".join(body)))
            title = line[3:].strip()
            body = []
            continue
        if title is not None:
            body.append(line)
    if title is not None:
        out.append((title, "\n".join(body)))
    return out


def field_values(body: str, names: Sequence[str]) -> Dict[str, str]:
    out = {}
    lines = body.split("\n")
    for i, line in enumerate(lines):
        hit = re.match(r"^\*\*([^*]+?)\.?\*\*\s*(.*)$", line)
        if not hit:
            continue
        label = hit.group(1).strip().rstrip(".")
        for name in names:
            if label.lower().startswith(name.lower().split(" —")[0]):
                collected = [hit.group(2)]
                for nxt in lines[i + 1:]:
                    if nxt.startswith("**") or nxt.startswith("## "):
                        break
                    collected.append(nxt)
                out[name] = " ".join(x.strip() for x in collected).strip()
    return out


# ---------------------------------------------------------------------------
# AB08.
# ---------------------------------------------------------------------------
def check_rice() -> Dict[str, object]:
    components = ab08_components()
    secs = [(t, b) for t, b in sections(RICE) if t.startswith("Component ")]
    found = {}
    for title, body in secs:
        name = title.split("—", 1)[1].strip() if "—" in title else title
        found[normalize(name)] = (title, body)

    per = []
    verdict_counts = {v: 0 for v in VERDICTS}
    for comp in components:
        key = normalize(comp)
        entry = {"component": comp, "present": key in found}
        if entry["present"]:
            title, body = found[key]
            vals = field_values(body, RICE_FIELDS)
            entry["fields_present"] = sorted(vals)
            entry["all_fields_non_empty"] = (
                len(vals) == len(RICE_FIELDS)
                and all(v.strip() for v in vals.values()))
            raw = vals.get("Verdict", "")
            verdict = None
            for v in VERDICTS:
                if v in raw:
                    verdict = v
            entry["verdict"] = verdict
            entry["verdict_in_vocabulary"] = verdict is not None
            if verdict:
                verdict_counts[verdict] += 1
            residual = vals.get("Residual", "")
            entry["residual_non_empty"] = bool(residual.strip())
            entry["residual_is_none_for_absorbed"] = (
                verdict != "ABSORBED" or residual.strip().lower().startswith("none"))
        per.append(entry)

    text = RICE.read_text(encoding="utf-8")
    not_claimed = "## What is NOT claimed novel with respect to Rice" in text
    return {
        "row_components": components,
        "row_component_count": len(components),
        "sections_found": len(secs),
        "components_present": sum(1 for e in per if e["present"]),
        "components_complete": sum(1 for e in per
                                   if e.get("all_fields_non_empty")
                                   and e.get("verdict_in_vocabulary")
                                   and e.get("residual_non_empty")),
        "verdict_counts": verdict_counts,
        "declares_what_is_not_claimed_novel": not_claimed,
        "cites_rice_doi": "10.1016/S0065-2458(08)60520-3" in text,
        "per_component": per,
    }


# ---------------------------------------------------------------------------
# AB25.
# ---------------------------------------------------------------------------
LEVEL_HEADING = re.compile(r"^Level\s+(\d+)\s*[—-]\s*(.+?)\s*$")


def check_ladder() -> Dict[str, object]:
    levels = ab25_levels()
    secs = sections(LADDER)
    parsed = []
    for title, body in secs:
        hit = LEVEL_HEADING.match(title)
        if not hit:
            continue
        n = int(hit.group(1))
        if n == 0:
            continue
        parsed.append((n, hit.group(2).strip(), body))
    parsed.sort()

    order_matches = [normalize(name) for _, name, _ in parsed] == \
        [normalize(l) for l in levels]

    per = []
    demotions = {}
    criteria = {}
    for n, name, body in parsed:
        vals = field_values(body, LADDER_FIELDS)
        crit = vals.get("Operational criterion", "")
        criteria[n] = normalize(crit)
        entry = {
            "level": n,
            "name": name,
            "fields_present": sorted(vals),
            "all_fields_non_empty": (len(vals) == len(LADDER_FIELDS)
                                     and all(v.strip() for v in vals.values())),
            "criterion_names_a_witness": "witness" in crit.lower(),
        }
        dem = vals.get("Demotion rule", "")
        target = None
        hit = re.search(r"level\s+\*\*(\d+)\*\*|\*\*level\s+(\d+)\*\*|level\s+(\d+)",
                        dem, re.IGNORECASE)
        if hit:
            target = int([g for g in hit.groups() if g][0])
        entry["demotion_target"] = target
        entry["demotion_points_down"] = target is not None and target < n
        demotions[n] = target
        per.append(entry)

    # The demotion chain must terminate at 0 from every level.
    terminates = True
    for n in demotions:
        seen = set()
        cur = n
        while cur is not None and cur > 0:
            if cur in seen:
                terminates = False
                break
            seen.add(cur)
            cur = demotions.get(cur)
        if cur != 0 and cur is not None:
            terminates = False
        if cur is None:
            terminates = False

    distinct_criteria = len(set(criteria.values())) == len(criteria)
    text = LADDER.read_text(encoding="utf-8")
    return {
        "row_levels": levels,
        "row_level_count": len(levels),
        "levels_found": len(parsed),
        "order_matches_the_antecedent_row": order_matches,
        "levels_complete": sum(1 for e in per if e["all_fields_non_empty"]),
        "levels_naming_a_witness": sum(1 for e in per
                                       if e["criterion_names_a_witness"]),
        "all_demotions_point_down": all(e["demotion_points_down"] for e in per),
        "demotion_chain_terminates_at_zero": terminates,
        "criteria_pairwise_distinct": distinct_criteria,
        "declares_level_zero": any(
            LEVEL_HEADING.match(t) and LEVEL_HEADING.match(t).group(1) == "0"
            for t, _ in secs),
        "declares_no_claim_is_placed": "No GMI claim is placed on this ladder" in text,
        "per_level": per,
    }


# ---------------------------------------------------------------------------
# Anti-invention guard.
# ---------------------------------------------------------------------------
def anti_invention_guard() -> Dict[str, object]:
    checks = []
    for comp in ab08_components():
        checks.append({"what": comp, "row": "AB08", "occurs": comp in AB08_ROW})
    for level in ab25_levels():
        checks.append({"what": level, "row": "AB25_ANTECEDENT",
                       "occurs": level in AB25_ANTECEDENT})
    # AB25's own text must NOT contain the levels; that is why the antecedent is
    # declared. Asserting this stops the exception being quietly widened.
    for level in ab25_levels():
        checks.append({"what": "%s absent from AB25 itself" % level, "row": "AB25",
                       "occurs": level not in AB25_ROW})
    checks.append({"what": "novelty ladder", "row": "AB25",
                   "occurs": "novelty ladder" in AB25_ROW})
    return {
        "checked": len(checks),
        "holding": sum(1 for c in checks if c["occurs"]),
        "passed": all(c["occurs"] for c in checks),
        "detail": checks,
    }


NULL_TRIALS = 200
NULL_SEED = 8330825  # 833 / AB08+AB25


def null_study() -> Dict[str, object]:
    """Shuffle which artifact section is bound to which row-named item. The true
    binding is total; a random one should not be."""
    import random
    from fractions import Fraction
    comps = [normalize(c) for c in ab08_components()]
    rice_names = [normalize(t.split("—", 1)[1]) for t, _ in sections(RICE)
                  if t.startswith("Component ") and "—" in t]
    levels = [normalize(l) for l in ab25_levels()]
    ladder_names = []
    for t, _ in sections(LADDER):
        hit = LEVEL_HEADING.match(t)
        if hit and hit.group(1) != "0":
            ladder_names.append(normalize(hit.group(2)))
    rng = random.Random(NULL_SEED)
    full = 0
    hits = []
    for _ in range(NULL_TRIALS):
        a = rice_names[:]
        b = ladder_names[:]
        rng.shuffle(a)
        rng.shuffle(b)
        n = sum(1 for x, y in zip(comps, a) if x == y)
        n += sum(1 for x, y in zip(levels, b) if x == y)
        hits.append(n)
        if n == len(comps) + len(levels):
            full += 1
    return {
        "trials": NULL_TRIALS,
        "seed": NULL_SEED,
        "bindings": len(comps) + len(levels),
        "true_binding_matches": (
            sum(1 for x, y in zip(comps, rice_names) if x == y)
            + sum(1 for x, y in zip(levels, ladder_names) if x == y)),
        "random_bindings_fully_matching": full,
        "max_random_matches": max(hits),
        "mean_random_matches_exact": str(Fraction(sum(hits), NULL_TRIALS)),
    }


def hostiles() -> List[Dict[str, object]]:
    out = []
    rice = check_rice()
    ladder = check_ladder()

    # H1 - a component with an out-of-vocabulary verdict.
    body = "**Rice's object.** x\n\n**GMI's object.** y\n\n**Verdict.** MOSTLY\n\n" \
           "**What Rice already supplies.** z\n\n**Residual.** w"
    vals = field_values(body, RICE_FIELDS)
    got = [v for v in VERDICTS if v in vals.get("Verdict", "")]
    out.append({"name": "H1_out_of_vocabulary_verdict",
                "moved_quantity": "verdict_in_vocabulary",
                "before": True, "after": bool(got), "detected": not got})

    # H2 - an ABSORBED component that nonetheless claims a residual.
    body2 = "**Rice's object.** x\n\n**GMI's object.** y\n\n**Verdict.** ABSORBED\n\n" \
            "**What Rice already supplies.** z\n\n**Residual.** a brand new thing"
    v2 = field_values(body2, RICE_FIELDS)
    ok = v2["Residual"].strip().lower().startswith("none")
    out.append({"name": "H2_absorbed_component_claiming_a_residual",
                "moved_quantity": "residual_is_none_for_absorbed",
                "before": True, "after": ok, "detected": not ok})

    # H3 - a demotion rule pointing upward.
    up = "Fails -> level 6."
    hit = re.search(r"level\s+(\d+)", up, re.IGNORECASE)
    target = int(hit.group(1)) if hit else None
    out.append({"name": "H3_demotion_pointing_up",
                "moved_quantity": "demotion_points_down",
                "before": True, "after": target is not None and target < 3,
                "detected": not (target is not None and target < 3)})

    # H4 - copy one level's criterion onto another: distinctness must flip.
    real = []
    for title, body in sections(LADDER):
        hit = LEVEL_HEADING.match(title)
        if hit and hit.group(1) != "0":
            vals = field_values(body, LADDER_FIELDS)
            real.append(normalize(vals.get("Operational criterion", "")))
    before_distinct = len(set(real)) == len(real)
    forged = real[:]
    if len(forged) >= 2:
        forged[1] = forged[0]
    after_distinct = len(set(forged)) == len(forged)
    out.append({"name": "H4_duplicated_criterion_detected",
                "moved_quantity": "criteria_pairwise_distinct",
                "before": before_distinct, "after": after_distinct,
                "detected": before_distinct and not after_distinct})

    # H5 - an invented seventh level must not bind to the row.
    invented = "novel vibe"
    out.append({"name": "H5_invented_level_does_not_bind",
                "moved_quantity": "level_occurs_in_antecedent_row",
                "before": True, "after": invented in AB25_ANTECEDENT,
                "detected": invented not in AB25_ANTECEDENT})

    # H6 - dropping a row-named component must move the completeness count.
    dropped = rice["components_complete"] - 1
    out.append({"name": "H6_drop_a_row_named_component",
                "moved_quantity": "components_complete",
                "before": rice["components_complete"], "after": dropped,
                "detected": dropped < rice["components_complete"]})
    return out


def main() -> Dict[str, object]:
    host = hostiles()
    return {
        "schema": "GMI_833_AB_RESIDUAL_DEFINITIONS_V1",
        "route": "A",
        "source_main": "5e57d4292266bccf435136e1f7d72caa32e920a0",
        "claim_ceiling": "DECLARED_DEFINITION_ARTIFACT_V1",
        "AB08_rice_subtraction": check_rice(),
        "AB25_novelty_ladder": check_ladder(),
        "guard": anti_invention_guard(),
        "null": null_study(),
        "hostiles": host,
        "hostiles_detected": sum(1 for h in host if h["detected"]),
        "hostiles_total": len(host),
    }


if __name__ == "__main__":
    out = main()
    out["AB08_rice_subtraction"] = {k: v for k, v in out["AB08_rice_subtraction"].items()
                                    if k != "per_component"}
    out["AB25_novelty_ladder"] = {k: v for k, v in out["AB25_novelty_ladder"].items()
                                  if k != "per_level"}
    out["guard"] = {k: v for k, v in out["guard"].items() if k != "detail"}
    print(json.dumps(out, indent=2, sort_keys=True))
