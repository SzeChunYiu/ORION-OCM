"""Correct the D27 ceiling counts, and state the signature the way it reads.

TWO CORRECTIONS, both to prose rather than to any measurement. The receipt
FO_D27_AGGREGATE.json was right throughout; what was quoted off it was not.

1. THE CEILING WAS REPORTED AS EXCEPTIONLESS AND IT IS NOT.
   Reported: "present in 240 of 240 forms below reset capability 0.636,
   absent in 0 of 219 above 0.659". The buckets say 240 of 243 at or below
   0.636, with three exceptions, and 0 of 237 at or above 0.659.

   The 219 was a different quantity entirely: the number of NON-ADVANTAGED
   forms among the 459 that persist at all. It is not the size of the
   above-threshold set, and putting it there conflated two counts.

   The three exceptions sit at reset capability 0.500 (n=2) and 0.614 (n=1).
   At those n they are plausibly noise and it is fair to say so, but "240 of
   240" asserts there are none, and there are three.

2. THE SIGNATURE RUNS THE WRONG WAY, WHICH IS STRONGER THAN ABSENT.
   Reported as "0 of 480", which reads as insufficient power. The measurement
   is more than that: the mean relative burden drop on the UNRELATED control
   is 0.019433 against 0.013474 on the prospectively frozen RELATED family.
   The control improves MORE than the family development is supposed to have
   prepared for. And 155 of 480 forms show an equivalent gain on the unrelated
   control, which disqualifies the signature independently wherever it might
   otherwise have looked present.

   So the developmental amortisation pattern does not merely fail to reach
   significance. What little burden reduction exists is a general effect that
   favours unrelated tasks slightly more than related ones.
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)


def main() -> int:
    agg = json.load(open(os.path.join(ROOT, "results",
                                      "FO_D27_AGGREGATE.json")))
    b = agg["boundary_by_reset_capability"]
    low = {k: v for k, v in b.items() if float(k) <= 0.636}
    high = {k: v for k, v in b.items() if float(k) >= 0.659}
    n_low = sum(v["n"] for v in low.values())
    a_low = sum(v["n_advantaged"] for v in low.values())
    n_high = sum(v["n"] for v in high.values())
    a_high = sum(v["n_advantaged"] for v in high.values())
    exceptions = {k: v for k, v in low.items()
                  if v["n_advantaged"] < v["n"]}
    sig = agg["b_future_cognition_signature"]

    rec = {
        "correction_id": "FO_D27_BOUNDARY_AND_SIGNATURE_CORRECTION_V1",
        "corrects": "prose quoted off FO_D27_AGGREGATE.json, not the receipt",
        "created_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "receipt_unchanged": True,
        "ceiling": {
            "withdrawn": ("present in 240 of 240 forms below reset capability "
                          "0.636, absent in 0 of 219 above 0.659"),
            "correct": ("present in %d of %d forms at or below 0.636, absent "
                        "in %d of %d at or above 0.659"
                        % (a_low, n_low, a_high, n_high)),
            "n_at_or_below_0_636": n_low,
            "n_advantaged_at_or_below": a_low,
            "n_at_or_above_0_659": n_high,
            "n_advantaged_at_or_above": a_high,
            "exceptions_below_threshold": {
                k: {"n": v["n"], "n_advantaged": v["n_advantaged"]}
                for k, v in sorted(exceptions.items(), key=lambda kv: float(kv[0]))},
            "exception_note": ("three forms, at reset capability 0.500 (n=2) "
                               "and 0.614 (n=1); plausibly noise at those n, "
                               "but they exist and the earlier phrasing "
                               "asserted they did not"),
            "where_219_came_from": ("the count of NON-ADVANTAGED forms among "
                                    "the 459 that persist at all; not the "
                                    "size of the above-threshold set"),
            "bucket_totals_sum_to": sum(v["n"] for v in b.values()),
            "still_a_sharp_ceiling": True,
        },
        "signature": {
            "withdrawn_framing": ("reported as '0 of 480', which reads as "
                                  "insufficient power"),
            "correct_framing": ("the pattern runs the wrong way: mean relative "
                                "burden drop is LARGER on the unrelated "
                                "control than on the prospectively frozen "
                                "related family"),
            "n_signature_present": sig["n_signature_present"],
            "n_checked": sig["n_checked"],
            "mean_relative_drop_related": sig["mean_relative_drop_related"],
            "mean_relative_drop_unrelated": sig["mean_relative_drop_unrelated"],
            "mean_relative_drop_harmful": sig["mean_relative_drop_harmful"],
            "n_equivalent_gain_on_unrelated": sig[
                "n_equivalent_gain_on_unrelated"],
            "reading": ("what little burden reduction exists is a general "
                        "effect that slightly favours unrelated tasks; it is "
                        "not developmental amortisation failing to reach "
                        "significance"),
        },
        "unchanged_and_verified": {
            "carrier": agg["carrier_counts"],
            "attribution_mean": agg["attribution_mean"],
            "n_forms": agg["n_forms"],
        },
    }
    out = os.path.join(ROOT, "results", "FO_D27_BOUNDARY_CORRECTION.json")
    blob = json.dumps(rec, indent=1, sort_keys=True, default=str)
    with open(out, "w") as fh:
        fh.write(blob + "\n")
    sys.stderr.write("correction sha256 %s\n"
                     % hashlib.sha256((blob + "\n").encode()).hexdigest())
    print(json.dumps({"ceiling": rec["ceiling"]["correct"],
                      "exceptions": list(exceptions),
                      "drop_related": sig["mean_relative_drop_related"],
                      "drop_unrelated": sig["mean_relative_drop_unrelated"]},
                     sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
