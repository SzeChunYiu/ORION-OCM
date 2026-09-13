"""Finite inference countermodels; not candidate generation or ecology execution."""
from fractions import Fraction as F
from copy import deepcopy
from records_v1 import ECOLOGIES, require


def archive(candidates, cost_bin):
    """Faithful MAP-Elites insertion on supplied, already-evaluated records."""
    cells = {}
    paid = F(0)
    for name, score, cost, feature in candidates:
        require(cost >= 0, "nonnegative supplied evaluation cost")
        paid += cost
        key = (feature, cost_bin(cost))
        if key not in cells or score > cells[key][1]:
            cells[key] = (name, score, cost)
    return sorted(v[0] for v in cells.values()), paid


def controls(data):
    task = "E_fresh4"
    members = ("gradient_net_h2", "gradient_net_h4")
    observed = {name: data["results"][task]["rows"][name]["min_over_six"]
                for name in members}
    worlds = [{"observations": deepcopy(data), "extra_score": extra}
              for extra in (F(0), F(1))]
    require(all(w["observations"] == data for w in worlds), "all observed fields preserved")
    maxima = [max(*observed.values(), w["extra_score"]) for w in worlds]
    require(maxima[0] < maxima[1], "fixed-task rows do not fix family supremum")
    # Both abstract extensions retain all observations, adding one permitted unknown score.
    weak_niche_baseline, possible_score = F(7, 8), F(15, 16)
    hypothetical_margin = 24 * (possible_score - weak_niche_baseline)
    require(possible_score >= F(85, 100) and hypothetical_margin >= 1, "niche countermodel")
    # Nearest-four-decimal reporting can conceal a margin below one.
    printed_q, printed_b = F("0.9688"), F("0.9271")
    true_q, true_b = F("0.968751"), F("0.927149")
    half_unit = F(1, 20000)
    require(abs(printed_q - true_q) < half_unit and abs(printed_b - true_b) < half_unit,
            "same rounded displayed scores")
    require(24 * (printed_q - printed_b) > 1 and 24 * (true_q - true_b) < 1,
            "rounding control")
    candidates = [("cheap", F(4, 5), F(1), "same"),
                  ("expensive", F(9, 10), F(100), "same")]
    old, old_paid = archive(candidates, lambda cost: 0)
    split, split_paid = archive(candidates, lambda cost: int(cost >= 10))
    same_bin, _ = archive(candidates, lambda cost: int(cost >= 1000))
    require(old == ["expensive"] and split == ["cheap", "expensive"]
            and same_bin == old and old_paid == split_paid == 101, "archive control")
    # Uniform sampling of three representations is not uniform sampling of two denotations.
    denotations = ("A", "A", "B")
    representation_mass = F(denotations.count("A"), len(denotations))
    semantic_mass = F(1, len(set(denotations)))
    require(representation_mass != semantic_mass, "pushforward distribution")
    return {
        "completion_fixed_task": task,
        "completion_observed_members": {k: str(v) for k, v in observed.items()},
        "all_observed_fields_preserved": all(w["observations"] == data for w in worlds),
        "completion_scope": "PARTIAL_SCORE_REGISTER_ADMITTING_AN_UNMEASURED_MEMBER",
        "same_observed_rows_possible_family_maxima": [str(v) for v in maxima],
        "hypothetical_nonweak_baseline_admissible_score": {
            "baseline": str(weak_niche_baseline), "score": str(possible_score),
            "declared_24_scaled_margin": str(hypothetical_margin), "realized_learner": False},
        "rounding_control": {"printed_margin_model": str(24 * (printed_q - printed_b)),
                             "compatible_below_one": str(24 * (true_q - true_b)),
                             "model": "HYPOTHETICAL_LINEAR_MARGIN_AND_NEAREST_DECIMAL"},
        "archive": {"old": old, "distinct_cost_bins": split, "same_cost_bin": same_bin,
                    "paid_before_insertion_each": str(old_paid),
                    "candidate_evaluations_executed": 0},
        "representation_vs_semantic_mass": [str(representation_mass), str(semantic_mass)],
        "search_prefix_visits": {"grammar_width": 4, "grammar0": [min(b, 2401) for b in (16, 2401)],
                                "grammar1": [min(b, 32) for b in (16, 2401)],
                                "empty_evidence_scoring_calls": 0,
                                "endpoint_ratio": str(F(2401, 16)),
                                "scope": "SOURCE_DERIVED_LOOP_COUNT_NO_VM_EXECUTION"},
    }
