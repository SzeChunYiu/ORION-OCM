"""Why does GRAD appear in no survivor? Proposed-and-rejected, or effectively never proposed?

Three outcomes with three different remedies:
  (a) rarely proposed            -> generator limitation
  (b) proposed but invalid       -> type/wiring limitation
  (c) proposed, valid, low score -> selection

Pure generator + evaluator probe. Reads nothing from the campaign and writes no campaign path.
"""
import json, random, sys, collections

from gmi_microscope import b1, ecology, morph, morphgen, smooth

N = int(sys.argv[1]) if len(sys.argv) > 1 else 4000
eco = sys.argv[2] if len(sys.argv) > 2 else "E_smooth3"
spec = ecology.REGISTRY[eco]; target = ecology.target_of(spec)
rng = random.Random(20260913)

seen = collections.Counter()
grad_graphs = []
g = morphgen.random_genotype(rng, steps=6)
for i in range(N):
    # the same proposal process b1.search uses: mutate a current genotype, occasionally restart
    if i % 50 == 0:
        g = morphgen.random_genotype(rng, steps=6)
    child, _ = morphgen.mutate(rng, g)
    kinds = {k for k, _ in child["nodes"].values()}
    seen["proposed"] += 1
    for k in kinds: seen["kind:" + k] += 1
    if "GRAD" in kinds:
        seen["with_GRAD"] += 1
        if len(grad_graphs) < 60: grad_graphs.append(child)
    g = child

print(f"proposals: {seen['proposed']}  containing GRAD: {seen['with_GRAD']} "
      f"({100.0*seen['with_GRAD']/max(1,seen['proposed']):.2f}%)")

valid = invalid = 0; caps = []
wired = collections.Counter()
for gg in grad_graphs:
    gid = [i for i, (k, _) in gg["nodes"].items() if k == "GRAD"]
    ins = collections.defaultdict(set)
    for a, b, pt in gg["edges"]:
        if b in gid: ins[b].add(pt)
    fully = sum(1 for i in gid if len(ins[i]) == 3)
    wired["grad_nodes"] += len(gid); wired["fully_wired"] += fully
    # does a GRAD output actually reach anything?
    consumed = sum(1 for a, b, pt in gg["edges"] if a in gid)
    wired["with_consumer"] += 1 if consumed else 0
    r = b1.evaluate(gg, target)
    if r is None: invalid += 1
    else: valid += 1; caps.append(r[0])

print(f"sampled GRAD graphs: {len(grad_graphs)}  valid phenotype: {valid}  invalid: {invalid}")
print(f"GRAD nodes: {wired['grad_nodes']}  fully wired (3/3 inputs): {wired['fully_wired']}  "
      f"graphs whose GRAD output is consumed: {wired['with_consumer']}")
if caps:
    caps.sort()
    print(f"capability of valid GRAD graphs: min {caps[0]:.4f}  median {caps[len(caps)//2]:.4f}  max {caps[-1]:.4f}  (theta 0.85)")
    print(f"reaching theta: {sum(1 for c in caps if c >= 0.85)} of {len(caps)}")
