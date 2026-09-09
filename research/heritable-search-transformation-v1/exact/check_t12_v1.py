#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""check_t12_v1.py -- finite-scope certificate for HST-T12 (pigeonhole recurrence).

Lane C of issue #233 (D4 limits). P2 witness ONLY: a passing run does not make T12
PROVED (the proof is the pigeonhole argument in proofs/LIMITS_V1.md); this script
exhaustively verifies the theorem's finite content over ALL closed deterministic
systems on n = 1..N states:

  for every total map f : S -> S and every initial state s0:
    (i)   the orbit s0, f(s0), ... revisits a state within |S|+1 states observed,
          i.e. first-repeat index j <= n (states s_0..s_j with s_j = s_i, i < j);
    (ii)  novelty (count of distinct states visited) saturates exactly at the first
          repeat and never grows after it;
    (iii) the eventual period p = j - i satisfies p <= n, and the pre-period i <= n.

Python 3.8 compatible (no match stmt, no PEP604 unions, no builtin generics).
Run on billy-laptop:  ssh billy-laptop 'python3 exact/check_t12_v1.py'
"""

from __future__ import print_function

import itertools
import json
import os
import sys

N = 4  # state-space sizes 1..4  (4^4 = 256 maps x 4 initial states; trivial runtime)


def orbit(f, s0, n):
    # deterministic orbit on finite S: stop at first repeat
    seq = [s0]
    pos = {s0: 0}
    t = 0
    cur = s0
    while True:
        cur = f[cur]
        t += 1
        if cur in pos:
            return seq, pos[cur], t  # first repeat: seq[i] == cur, i < t
        pos[cur] = t
        seq.append(cur)
        if t > n + 2:  # cannot happen if theorem holds; guard against runaway
            return seq, -1, t


def main():
    total_systems = 0
    total_initials = 0
    failures = []
    stats = {"max_first_repeat_index": 0, "max_period": 0, "max_preperiod": 0,
             "max_distinct_states": 0}
    for n in range(1, N + 1):
        S = list(range(n))
        for vals in itertools.product(S, repeat=n):  # every total map f: S->S
            f = dict(zip(S, vals))
            total_systems += 1
            for s0 in S:
                total_initials += 1
                seq, i, j = orbit(f, s0, n)
                # (i) first repeat within |S|+1 observed states: j <= n
                if not (0 <= i < j <= n):
                    failures.append(("T12-i", n, vals, s0, i, j))
                    continue
                p = j - i
                distinct = len(set(seq))
                # (ii) novelty saturation: continuing the orbit never adds new states
                seen = set(seq)
                cur = seq[-1]
                overflow = 0
                for _ in range(2 * n + 2):
                    cur = f[cur]
                    overflow += 0 if cur in seen else 1
                    seen.add(cur)
                if overflow != 0:
                    failures.append(("T12-ii", n, vals, s0, distinct, overflow))
                # (iii) pre-period i <= n, period p <= n, distinct <= n
                if not (i <= n and p <= n and distinct <= n):
                    failures.append(("T12-iii", n, vals, s0, i, p, distinct))
                stats["max_first_repeat_index"] = max(stats["max_first_repeat_index"], j)
                stats["max_period"] = max(stats["max_period"], p)
                stats["max_preperiod"] = max(stats["max_preperiod"], i)
                stats["max_distinct_states"] = max(stats["max_distinct_states"], distinct)
    result = {
        "checker": "check_t12_v1",
        "theorem": "HST-T12 finite-state literal open-endedness limit (finite scope)",
        "state_space_sizes": list(range(1, N + 1)),
        "total_maps_enumerated": total_systems,
        "total_initial_states_checked": total_initials,
        "checked_properties": [
            "first state repeat occurs within |S|+1 observed states (j <= n)",
            "novelty count saturates at first repeat (no new states afterwards)",
            "pre-period <= n and eventual period <= n; distinct states <= n",
        ],
        "observed_maxima_over_all_systems": stats,
        "failures": failures[:20],
        "failure_count": len(failures),
        "verdict": "PASS" if not failures else "FAIL",
    }
    out = json.dumps(result, indent=1, sort_keys=True)
    print(out)
    # location-independent (D8 finding 5): always next to this script
    cert_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                             "check_t12_v1.cert.json")
    with open(cert_path, "w") as fh:
        fh.write(out + "\n")
    sys.stderr.write("certificate written: %s\n" % cert_path)
    return 0 if not failures else 1


if __name__ == "__main__":
    sys.exit(main())
