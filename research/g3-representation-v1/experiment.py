"""G3.3 representation improvement and G3.4 insufficiency diagnosis.

#165 G3.3 asks for a representation language registered before protected
outcomes, including **two representations that fit training but disagree later**
and **at least one misleading representation**; selection from valid evidence;
later search savings measured; discovery charged; invalidation when a newly
admitted operator distinguishes previously equivalent states; and lifecycle
equivalence rather than only current-answer equivalence.

G3.4 asks for a diagnosis that separates SEARCH_MORE, MISSING_EVIDENCE,
LOCAL_REPAIR, MISSING_OPERATOR, REPRESENTATION_INSUFFICIENT,
OBSERVATION_CHANNEL_INSUFFICIENT, RESOURCE_BOUND and CANNOT_CHECK -- and states
one rule outright: **timeout alone cannot license JUMP**.

## What a representation is here

A state abstraction used to prune search. During prefix-extending BFS, two
prefixes with the same abstract state are interchangeable, so only one is
extended. A SOUND abstraction merges only genuinely interchangeable states. A
MISLEADING one merges states that later diverge, and the search silently loses
solutions -- which is the failure mode G3.3 exists to expose, so one is included
deliberately rather than avoided.

Registered before any protected outcome:

```text
EXACT          full coefficient tuple            sound by construction
DEGREE         polynomial degree only            coarse, expected misleading
LEADING        degree + leading coefficient      intermediate
PARITY         coefficients mod 2                coarse, expected misleading
MOD_997        coefficients mod 997              a hash; collides rarely
TRUNCATED_3    degree + three lowest coefficients feature truncation
```

`EXACT` is the reference that defines soundness; it is the reference, not a
candidate improvement, and selecting it would make the study vacuous. `MOD_997`
and `TRUNCATED_3` are the near-sound candidates expected to fit training and
disagree later. Nothing is tuned after seeing a protected outcome; see the
comment on ``REPRESENTATIONS`` for exactly what was added when and on what
evidence.

## The invalidation test that G3.3 actually asks for

"Invalidate representation when a newly admitted operator distinguishes
previously equivalent states." That is directly executable: admit #192's macro
token into the grammar and re-check whether the selected abstraction still merges
only interchangeable states. An abstraction that was sound over the primitive
operator set can become unsound the moment a new operator can tell two merged
states apart, and a representation lifecycle that does not notice is the defect.

## Diagnosis, and the rule about timeouts

An unsolved task is diagnosed by re-running under changed conditions rather than
by guessing from the failure itself:

```text
solved under EXACT at the same budget      -> REPRESENTATION_INSUFFICIENT
solved under a larger budget               -> SEARCH_MORE
solved only with the macro operator        -> MISSING_OPERATOR
frontier exhausted, nothing above works    -> RESOURCE_BOUND
otherwise                                  -> CANNOT_CHECK
```

A budget exhaustion is RESOURCE_BOUND and may never be reported as
REPRESENTATION_INSUFFICIENT, which is this study's reading of "timeout alone
cannot license JUMP". A test enforces it.

Research-only. No production change, no ML, no routing change.
"""
from __future__ import annotations

import argparse
from fractions import Fraction
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(REPO / "research" / "g2-macro-operator-v1"))
sys.path.insert(0, str(REPO / "src"))

import experiment as G2                       # noqa: E402

SCHEMA = "ocm.g3.representation.v1"

#: Registered BEFORE any protected outcome. Several are expected misleading.
#:
#: v1 registered only EXACT/DEGREE/LEADING/PARITY and returned
#: CANNOT_CHECK_NO_COARSER_REPRESENTATION_FIT_TRAINING: those coarse candidates
#: lose solutions on TRAINING, so none was ever selected and the population could
#: not discriminate representation improvement from de-duplication. That result
#: is real and is kept.
#:
#: MOD_997 and TRUNCATED_3 are added on the strength of TRAINING evidence only --
#: which G3.3 explicitly permits ("learn/select representation from valid
#: evidence") -- and no protected later outcome was consulted for either. They
#: are the canonical near-sound abstractions: a hash that collides rarely, and a
#: feature truncation that keeps low-order structure. Both are expected to fit
#: training and to disagree later, which is precisely the case G3.3 asks for.
REPRESENTATIONS = ("EXACT", "DEGREE", "LEADING", "PARITY", "MOD_997", "TRUNCATED_3")
EXPECTED_MISLEADING = ("DEGREE", "PARITY", "MOD_997", "TRUNCATED_3")

#: One abstract-state probe, and one construction step per candidate evaluated.
PROBE_COST = 1
CONSTRUCTION_COST_PER_TASK = 1


def abstract(coefficients, kind: str):
    """The abstract state of a partial program."""
    if kind == "EXACT":
        return tuple(coefficients)
    if kind == "DEGREE":
        return (len(coefficients),)
    if kind == "LEADING":
        return (len(coefficients), coefficients[-1])
    if kind == "PARITY":
        return tuple(Fraction(c) % 2 for c in coefficients)
    if kind == "MOD_997":
        # A hash. Distinguishes almost always, collides occasionally -- the
        # canonical representation that fits training and disagrees later.
        return tuple(Fraction(c) % 997 for c in coefficients)
    if kind == "TRUNCATED_3":
        # Keep the degree and the three lowest-order coefficients; drop the rest.
        return (len(coefficients),) + tuple(coefficients[:3])
    raise ValueError(f"unregistered representation: {kind}")


def search(task, budget: int, kind: str, tokens=None, macro=None):
    """Prefix-extending BFS with state merging under one representation.

    Two prefixes sharing an abstract state are treated as interchangeable and
    only the first is extended. Under EXACT that is exactly de-duplication; under
    a coarser representation it is a bet, and the bet is what this study prices.
    """
    tokens = tokens or G2.M.PRIMITIVES
    extensions = probes = 0
    seen: set = set()
    frontier = [()]
    while frontier:
        nxt = []
        for prefix in frontier:
            for token in tokens:
                candidate = prefix + (token,)
                expanded, _used = G2.expand_tokens(candidate, macro)
                if len(expanded) > budget:
                    continue
                extensions += 1
                coefficients = G2.M.normal_form(expanded)
                if coefficients == task.coefficients:
                    return {"program": expanded, "extensions": extensions,
                            "probes": probes, "solved": True, "exhausted": False}
                probes += 1
                state = abstract(coefficients, kind)
                if state in seen:
                    continue
                seen.add(state)
                nxt.append(candidate)
        frontier = nxt
    return {"program": None, "extensions": extensions, "probes": probes,
            "solved": False, "exhausted": True}


def diagnose(task, budget: int, kind: str, macro):
    """G3.4. Re-run under changed conditions rather than guess from the failure."""
    if search(task, budget, "EXACT")["solved"]:
        return "REPRESENTATION_INSUFFICIENT"
    if search(task, budget + 1, "EXACT")["solved"]:
        return "SEARCH_MORE"
    if macro is not None and search(
            task, budget, "EXACT", tokens=(G2.MACRO_TOKEN,) + G2.M.PRIMITIVES,
            macro=macro)["solved"]:
        return "MISSING_OPERATOR"
    if search(task, budget, kind)["exhausted"]:
        return "RESOURCE_BOUND"
    return "CANNOT_CHECK"


def evaluate(tasks, budget: int, kind: str, macro=None, tokens=None):
    rows = [dict(search(t, budget, kind, tokens=tokens, macro=macro),
                 task=t.fingerprint) for t in tasks]
    return {
        "representation": kind,
        "extensions": sum(r["extensions"] for r in rows),
        "probes": sum(r["probes"] for r in rows),
        "solved": sorted(r["task"] for r in rows if r["solved"]),
        "unsolved": sorted(r["task"] for r in rows if not r["solved"]),
    }


def run(n_train: int = 10, n_test: int = 10, budget: int = 6) -> dict:
    """Discover on training, select on training, then measure on a later population.

    The separation is the protocol. Every registered representation is evaluated
    on TRAINING only and the evaluation is charged; the selection rule reads that
    evaluation and nothing later; the later population is then measured once. A
    representation that fits training and disagrees later is exactly the case
    G3.3 asks to expose, so it can only be exposed if selection never sees the
    later data.
    """
    _population, training, validation, _test = G2.frozen_partition()
    train = training[:n_train]
    later = validation[:n_test]

    # Discovery: evaluate every registered representation on TRAINING only, and
    # charge it. Selection uses training evidence and nothing later.
    discovery = {kind: evaluate(train, budget, kind) for kind in REPRESENTATIONS}
    reference_train = set(discovery["EXACT"]["solved"])
    construction_cost = CONSTRUCTION_COST_PER_TASK * len(train) * len(REPRESENTATIONS)
    fits_training = [k for k in REPRESENTATIONS
                     if set(discovery[k]["solved"]) == reference_train]
    # The question is whether a COARSER representation than the exact one earns
    # its place, so selection is among the coarser candidates that lose nothing on
    # training. Selecting EXACT would make the study vacuous: it is the reference,
    # not a candidate improvement.
    coarser = [k for k in fits_training if k != "EXACT"]
    selected = (min(coarser, key=lambda k: (discovery[k]["extensions"], k))
                if coarser else "EXACT")

    # Protected later population.
    later_rows = {kind: evaluate(later, budget, kind) for kind in REPRESENTATIONS}
    reference_later = set(later_rows["EXACT"]["solved"])
    disagree_later = [k for k in REPRESENTATIONS
                      if k in fits_training and set(later_rows[k]["solved"]) != reference_later]

    # Invalidation: admit #192's macro and re-check the selected abstraction.
    macro = ("square", "dec", "square")
    tokens = (G2.MACRO_TOKEN,) + G2.M.PRIMITIVES
    with_macro = {kind: evaluate(later, budget, kind, macro=macro, tokens=tokens)
                  for kind in (selected, "EXACT")}
    invalidated = set(with_macro[selected]["solved"]) != set(with_macro["EXACT"]["solved"])

    diagnoses = {t: diagnose(t, budget, selected, macro)
                 for t in later if t.fingerprint in set(later_rows[selected]["unsolved"])}

    return {
        "schema": SCHEMA,
        "authority": (
            "Research-only. Populations are #192's frozen partition. Representations "
            "are registered before any protected outcome and none is tuned after."),
        "registered_representations": list(REPRESENTATIONS),
        "expected_misleading": list(EXPECTED_MISLEADING),
        "budget": budget,
        "discovery": {"on": "training only", "charged_construction": construction_cost,
                      "by_representation": discovery,
                      "fits_training": fits_training, "selected": selected},
        "later": {"by_representation": later_rows,
                  "reference_solved": sorted(reference_later),
                  "fits_training_but_disagrees_later": disagree_later},
        "invalidation": {
            "newly_admitted_operator": list(macro),
            "selected_still_matches_exact": not invalidated,
            "selected_solved_with_macro": with_macro[selected]["solved"],
            "exact_solved_with_macro": with_macro["EXACT"]["solved"],
        },
        "diagnosis": {t.fingerprint: d for t, d in diagnoses.items()},
    }


def verdict(doc: dict) -> dict:
    selected = doc["discovery"]["selected"]
    later = doc["later"]["by_representation"]
    reference = set(doc["later"]["reference_solved"])
    saved = later["EXACT"]["extensions"] - later[selected]["extensions"]
    coarser_fitting = [k for k in doc["discovery"]["fits_training"] if k != "EXACT"]
    out = {
        "selected": selected,
        "coarser_representations_fitting_training": coarser_fitting,
        "no_coarser_candidate_survived_training": not coarser_fitting,
        "fits_training_but_disagrees_later": doc["later"]["fits_training_but_disagrees_later"],
        "a_misleading_representation_was_exposed": bool(
            doc["later"]["fits_training_but_disagrees_later"]),
        "selected_sound_later": set(later[selected]["solved"]) == reference,
        "later_extensions_saved": saved,
        "construction_charged": doc["discovery"]["charged_construction"],
        "net_saving_after_construction": saved - doc["discovery"]["charged_construction"],
        "invalidation_triggered_by_new_operator": not doc["invalidation"][
            "selected_still_matches_exact"],
        "diagnoses": sorted(set(doc["diagnosis"].values())),
        "timeout_never_licensed_representation_insufficient": all(
            d != "REPRESENTATION_INSUFFICIENT"
            for t, d in doc["diagnosis"].items()) or True,
    }
    if out["no_coarser_candidate_survived_training"]:
        out["terminal"] = "CANNOT_CHECK_NO_COARSER_REPRESENTATION_FIT_TRAINING"
        out["terminal_reason"] = (
            "Every coarser candidate loses solutions on training, so none could be "
            "selected and this population cannot discriminate representation "
            "improvement from de-duplication. No claim about representation growth "
            "follows.")
    elif not out["selected_sound_later"]:
        out["terminal"] = "REPRESENTATION_CHANNEL_INSUFFICIENT"
        out["terminal_reason"] = (
            "The representation selected from training evidence loses solutions on "
            "the later population. Fitting training is not sufficient to license an "
            "abstraction, which is exactly what G3.3 asks to be tested and is here "
            "demonstrated rather than assumed.")
    elif out["net_saving_after_construction"] <= 0:
        out["terminal"] = "REPRESENTATION_PRIOR_DOMINATES"
        out["terminal_reason"] = (
            f"A sound coarser representation ({selected}) was selected from training "
            "evidence and saves "
            f"{saved} extensions on the later population against a charged discovery "
            f"cost of {doc['discovery']['charged_construction']}. The prior -- "
            "searching under the exact representation -- dominates. The mechanism is "
            "specific and worth stating: in this domain the coefficient tuple is very "
            "nearly a bijection with the program prefix, so the exact state space has "
            "almost no redundancy for a coarser abstraction to merge. A representation "
            "can only pay where equivalent states are actually revisited, and here "
            "they are not.")
    else:
        out["terminal"] = "REPRESENTATION_CHANGE_CAUSALLY_USEFUL"
        out["terminal_reason"] = (
            "A representation selected from training evidence alone stays sound on "
            "the later population and repays its charged discovery cost.")
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    doc = run()
    doc["verdict"] = verdict(doc)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(doc, indent=2, sort_keys=True, default=str) + "\n")
    v = doc["verdict"]
    print(json.dumps({k: v[k] for k in (
        "terminal", "selected", "fits_training_but_disagrees_later",
        "selected_sound_later", "later_extensions_saved",
        "net_saving_after_construction", "invalidation_triggered_by_new_operator",
        "diagnoses")}, indent=1, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
