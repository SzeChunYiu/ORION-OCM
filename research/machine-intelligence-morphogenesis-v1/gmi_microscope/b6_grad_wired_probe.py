"""Is the learner family INCAPABLE, or merely UNREACHABLE under this generator?

The probe showed GRAD is proposed often (10.4% of proposals), always yields a valid
phenotype, always wires its three inputs -- and its OUTPUT is never consumed, so it
computes an update that goes nowhere and confers no advantage.

This takes those same graphs and performs the second mutation by hand: wire the GRAD
output into a VEC-consuming port. If wired GRAD graphs reach theta, the family is capable
and the negative is a search/grammar result. If they do not, the negative is about the
family itself.
"""
import random, collections
from gmi_microscope import b1, ecology, morph, morphgen

eco = "E_smooth3"
spec = ecology.REGISTRY[eco]; target = ecology.target_of(spec)
rng = random.Random(20260913)

def vec_ports(g, exclude):
    out = []
    for i, (k, _) in g["nodes"].items():
        if i in exclude: continue
        for pt, t in enumerate(morph.KINDS[k][1]):
            if t == morph.VEC: out.append((i, pt))
    return out

dangling_caps, wired_caps = [], []
n_wired = n_seen = 0
g = morphgen.random_genotype(rng, steps=6)
for i in range(6000):
    if i % 50 == 0: g = morphgen.random_genotype(rng, steps=6)
    child, _ = morphgen.mutate(rng, g); g = child
    gid = [i2 for i2, (k, _) in child["nodes"].items() if k == "GRAD"]
    if not gid: continue
    n_seen += 1
    consumed = any(a in gid for a, b, pt in child["edges"])
    r0 = b1.evaluate(child, target)
    if r0 is not None: dangling_caps.append(r0[0])
    if consumed or n_wired >= 120: continue
    # hand-perform the second mutation: point one VEC port at the GRAD output
    ports = vec_ports(child, set(gid))
    if not ports: continue
    import json as _j
    w = _j.loads(_j.dumps(child))
    b, pt = rng.choice(ports)
    w["edges"] = [e for e in w["edges"] if not (e[1] == b and e[2] == pt)]
    w["edges"].append((gid[0], b, pt))
    r1 = b1.evaluate(w, target)
    if r1 is not None:
        wired_caps.append(r1[0]); n_wired += 1

def summ(name, caps):
    if not caps:
        print(f"{name}: none valid"); return
    caps = sorted(caps)
    print(f"{name}: n={len(caps)} min {caps[0]:.4f} median {caps[len(caps)//2]:.4f} "
          f"max {caps[-1]:.4f} | reaching theta 0.85: {sum(1 for c in caps if c >= 0.85)}")

print(f"GRAD-bearing graphs seen: {n_seen}")
summ("GRAD dangling (as the generator makes them)", dangling_caps)
summ("GRAD wired by hand (the second mutation)   ", wired_caps)
