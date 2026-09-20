"""Exact robust model comparison over declared independent quality/cost intervals."""
from fractions import Fraction


def rational(x):
    if isinstance(x, bool) or not isinstance(x, (int, Fraction)):
        raise ValueError("exact rational values required")
    return Fraction(x)


def certify_winner(intervals, tradeoff):
    """Return a unique winner valid over the entire interval box, else UNKNOWN.

    Each value is (quality_lower, quality_upper, cost_lower, cost_upper).
    Intervals are supplied evidence premises, not inferred from source code.
    """
    tradeoff = rational(tradeoff)
    if tradeoff < 0 or not isinstance(intervals, dict) or not intervals:
        raise ValueError("nonnegative tradeoff and nonempty mapping required")
    bounds = {}
    for name, raw in intervals.items():
        if not isinstance(name, str) or not name or not isinstance(raw, (tuple, list)):
            raise ValueError("nonempty candidate names and four-field records required")
        if len(raw) != 4:
            raise ValueError("quality/cost interval requires four fields")
        qlo, qhi, clo, chi = map(rational, raw)
        if qlo > qhi or clo < 0 or clo > chi:
            raise ValueError("unordered interval or negative cost")
        bounds[name] = (qlo - tradeoff * chi, qhi - tradeoff * clo)
    winners = [name for name, (lo, _) in bounds.items()
               if all(name == other or lo > hi for other, (_, hi) in bounds.items())]
    if len(winners) > 1:
        raise ValueError("inconsistent interval certificate")
    return {"status": "CERTIFIED" if winners else "UNKNOWN",
            "winner": winners[0] if winners else None, "bounds": bounds}
