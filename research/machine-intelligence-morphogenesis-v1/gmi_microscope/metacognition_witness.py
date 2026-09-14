"""I6: confidence as a decision-relevant object, and what calibration actually requires.

Confidence is not intrinsically valuable -- it earns its cost only by CHANGING AN ACTION.
With an abstain option and costs (wrong = W, abstain = A, right = 0), the optimal policy is

    answer iff  (1 - p) * W  <  A     i.e.   p > 1 - A/W

so confidence is decision-relevant exactly where it can cross that threshold.

The sharp consequence under test: if only the CROSSING matters, then miscalibration FAR from
the threshold should cost almost nothing, while miscalibration NEAR it should be expensive.
Calibration would then be a LOCAL requirement, not a global one.

Exact expectation over a discretised confidence distribution. Non-vacuity asserted.
"""
import json

W, A = 10.0, 3.0
THRESH = 1 - A / W                      # answer iff true p > 0.7
BINS = [(i + 0.5) / 20 for i in range(20)]   # 20 confidence bins, true accuracy = bin centre

def policy_cost(reported):
    """reported: map from true p -> reported confidence. Decide with reported, pay with true."""
    tot = 0.0
    for p in BINS:
        r = reported(p)
        if r > THRESH: tot += (1 - p) * W      # answered: pay W when wrong
        else:          tot += A                # abstained
    return tot / len(BINS)

perfect = policy_cost(lambda p: p)

def skew(p, lo, hi, delta):
    """distort confidence by delta, but only inside [lo, hi]"""
    return min(1.0, max(0.0, p + delta)) if lo <= p <= hi else p

print("threshold: answer iff confidence > %.2f   (W=%.0f, A=%.0f)" % (THRESH, W, A))
print("perfectly calibrated cost: %.4f\n" % perfect)
print("%-34s %-10s %s" % ("miscalibration region", "cost", "excess over perfect"))
rows = []
for name, lo, hi in (("far below threshold  [0.00,0.40]", 0.0, 0.40),
                     ("near threshold       [0.60,0.80]", 0.60, 0.80),
                     ("far above threshold  [0.90,1.00]", 0.90, 1.00)):
    for delta in (+0.15, -0.15):
        c = policy_cost(lambda p, lo=lo, hi=hi, d=delta: skew(p, lo, hi, d))
        rows.append({"region": name, "delta": delta, "cost": round(c, 4),
                     "excess": round(c - perfect, 4)})
        print("%-34s %-10.4f %+.4f   (delta %+.2f)" % (name, c, c - perfect, delta))

near = max(r["excess"] for r in rows if "near" in r["region"])
far = max(r["excess"] for r in rows if "far" in r["region"])
print("\nworst excess NEAR the threshold : %+.4f" % near)
print("worst excess FAR from threshold : %+.4f" % far)
nonvac = abs(near - far) > 1e-9
print("regions differ (non-vacuous): %s" % nonvac)
if nonvac:
    print("=> calibration is a LOCAL requirement: it matters only where confidence can cross the")
    print("   decision threshold. Far from it, a badly wrong confidence costs %.4f." % far)
json.dump({"schema": "MetacognitionCalibrationV1", "W": W, "A": A, "threshold": THRESH,
           "perfect_cost": perfect, "rows": rows, "worst_near": near, "worst_far": far,
           "non_vacuous": nonvac},
          open("microscopes/results/STAGE_METACOGNITION_V1.json", "w"), indent=1, sort_keys=True)
print("written")
