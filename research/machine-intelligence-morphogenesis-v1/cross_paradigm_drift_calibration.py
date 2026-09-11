from fractions import Fraction


def exact_constant_drift_hitting_time(initial_potential: Fraction, drift: Fraction) -> Fraction:
    if initial_potential <= 0:
        return Fraction(0, 1)
    if drift <= 0:
        raise ValueError("drift must be positive")
    return initial_potential / drift


def calibration_rows():
    # Program search: unsolved-indicator potential is 1; one proposal succeeds
    # with probability q, so exact additive drift is q and E[T] = 1/q.
    program = {
        "FAST_X": (Fraction(1), Fraction(1, 4)),
        "FAST_Y": (Fraction(1), Fraction(1, 16)),
    }

    # Bayesian toy: potential is remaining log-odds gap to the posterior
    # threshold; each registered observation supplies exactly 2 units.
    bayes = {
        "PRIOR_PLUS": (Fraction(4), Fraction(2)),
        "PRIOR_MINUS": (Fraction(8), Fraction(2)),
    }

    # Quadratic-GD toy: potential is a registered log-error gap; each step
    # contracts it by exactly 2 units in the chosen coordinate system.
    neural = {
        "FAST_X": (Fraction(8), Fraction(2)),
        "FAST_Y": (Fraction(36), Fraction(2)),
    }

    families = {
        "program_search": program,
        "bayesian_update": bayes,
        "quadratic_gradient": neural,
    }

    out = {}
    for family, rows in families.items():
        out[family] = {
            name: {
                "initial_potential": str(phi),
                "drift": str(delta),
                "predicted_hitting_time": str(exact_constant_drift_hitting_time(phi, delta)),
            }
            for name, (phi, delta) in rows.items()
        }
    return out


if __name__ == "__main__":
    import json
    print(json.dumps(calibration_rows(), indent=2, sort_keys=True))
