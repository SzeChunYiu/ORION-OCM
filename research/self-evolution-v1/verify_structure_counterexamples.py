"""Exact elementary countermodels; not a synthetic self-evolution benchmark."""
from itertools import product
import json


def verify():
    cube = list(product((0, 1), repeat=3))
    anchored = [v for v in cube if sum(v) <= 2]
    assert all(v[0] * v[1] * v[2] == 0 for v in anchored)
    assert 1 * 1 * 1 != 0
    chains = []
    for n in (2, 4, 8, 16):
        def propagate(root):
            state = [root]
            for _ in range(n - 1):
                state.append(state[-1])
            return state
        before, after = propagate(0), propagate(1)
        assert sum(a != b for a, b in zip(before, after)) == n
        chains.append({"obligations": n, "edges": n - 1,
                       "affected": n, "affected_fraction": 1})
    parity = []
    for n in range(4, 11):
        checked = 0
        for xs in product((0, 1), repeat=n):
            separate = tuple(sum(xs[:i] + xs[i+1:]) % 2 for i in range(n))
            shared = tuple((sum(xs) % 2) ^ xs[i] for i in range(n))
            assert separate == shared
            changed = (1 - xs[0],) + xs[1:]
            outputs2 = tuple(sum(changed[:i] + changed[i+1:]) % 2 for i in range(n))
            assert sum(a != b for a, b in zip(separate, outputs2)) == n - 1
            checked += 1
        assert 2 * n - 1 < n * (n - 2)
        parity.append({"n": n, "states_checked": checked,
                       "affected_outputs": n - 1, "separate_xors": n * (n - 2),
                       "shared_xors": 2 * n - 1})
    return {"status": "EXACT_COUNTEREXAMPLES_VERIFIED",
            "claim": "elementary finite calibration; no OCM self-evolution outcome",
            "anchored_pairwise": {"indistinguishable_probes": len(anchored), "separating_input": [1, 1, 1]},
            "sparse_chains": chains, "dense_influence_shared_compute": parity}


if __name__ == "__main__":
    print(json.dumps(verify(), indent=2))
