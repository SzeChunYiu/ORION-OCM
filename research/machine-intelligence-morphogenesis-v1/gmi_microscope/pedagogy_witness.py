"""I8's remaining boxes: demonstration selection, learner questioning, pedagogy-aware inference.

All three are the same object as the acquisition stopping rule, moved across the cut:

  * TEACHER  chooses which demonstration to send. TDA-1 splits candidates by test; a teacher
    splits the LEARNER's hypothesis set by demonstration. The best demonstration is the one
    minimising worst-case remaining ambiguity -- TDA-1 with the teacher paying the cost.
  * LEARNER  chooses which question to ask. Identical, with the learner paying.
  * PEDAGOGY-AWARE inference: a learner who knows the teacher is CHOOSING helpfully can infer
    more from the same demonstration than one treating it as a random sample. Testable: does
    the pedagogic posterior beat the random-sample posterior, and by how much?

Exact enumeration over a finite hypothesis space.
"""
import itertools, json

# 8 hypotheses, each a response map on 4 inputs
HYPS = [tuple(int(b) for b in format(i, "03b")) + (0,) for i in range(8)]
HYPS = [h[:3] + ((h[0] ^ h[1]),) for h in HYPS]          # 4th output determined, keeps some pairs tied
INPUTS = range(4)

def split_by(demo_input, hyps):
    """partition hypotheses by the output they predict at this input"""
    parts = {}
    for h in hyps:
        parts.setdefault(h[demo_input], []).append(h)
    return parts

def worst_remaining(demo_input, hyps):
    return max(len(v) for v in split_by(demo_input, hyps).values())

print("(a) TEACHER: which demonstration to give (TDA-1 across the cut)")
print("  %-8s %-28s %s" % ("input", "partition sizes", "worst-case remaining"))
best_in, best_w = None, None
for i in INPUTS:
    parts = split_by(i, HYPS); w = worst_remaining(i, HYPS)
    if best_w is None or w < best_w: best_w, best_in = w, i
    print("  %-8d %-28s %d" % (i, sorted(len(v) for v in parts.values()), w))
print("  best demonstration: input %d, worst case %d of %d hypotheses remain" % (best_in, best_w, len(HYPS)))

print("\n(b) LEARNER: which question to ask -- identical computation, learner pays")
print("  the ordering over inputs is the same, so teacher choice and learner choice")
print("  are ONE rule differing only in who is charged:", [worst_remaining(i, HYPS) for i in INPUTS])

print("\n(c) PEDAGOGY-AWARE INFERENCE")
# random-sample learner: teacher picks an input uniformly
# pedagogic learner: teacher picks the input that best discriminates the TRUE hypothesis
def posterior_size(true_h, pedagogic):
    if pedagogic:
        # teacher picks the input minimising the learner's remaining set given the true answer
        best = None
        for i in INPUTS:
            rem = len(split_by(i, HYPS)[true_h[i]])
            if best is None or rem < best: best = rem
        return best
    # random: average over inputs
    return sum(len(split_by(i, HYPS)[true_h[i]]) for i in INPUTS) / len(list(INPUTS))

ped = [posterior_size(h, True) for h in HYPS]
rnd = [posterior_size(h, False) for h in HYPS]
mean_p, mean_r = sum(ped) / len(ped), sum(rnd) / len(rnd)
print("  mean hypotheses remaining after ONE demonstration")
print("    random-sample learner : %.3f" % mean_r)
print("    pedagogic learner     : %.3f" % mean_p)
print("    pedagogy is worth %.3f hypotheses (%.0f%% tighter)" % (mean_r - mean_p, 100 * (1 - mean_p / mean_r)))
print("  strictly better on %d of %d true hypotheses" % (sum(1 for a, b in zip(ped, rnd) if a < b), len(HYPS)))

json.dump({"schema": "PedagogyWitnessV1", "n_hypotheses": len(HYPS),
           "teacher_worst_case": {i: worst_remaining(i, HYPS) for i in INPUTS},
           "best_demonstration_input": best_in, "best_worst_case": best_w,
           "pedagogic_mean": mean_p, "random_mean": mean_r,
           "strictly_better_count": sum(1 for a, b in zip(ped, rnd) if a < b)},
          open("microscopes/results/STAGE_PEDAGOGY_V1.json", "w"), indent=1, sort_keys=True)
print("written")
