#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""check_t13_v1.py -- finite-scope certificate for HST-T13 (prefix-extension).

Lane C of issue #233 (D4 limits). P2 witness ONLY (the proof is the explicit
construction in proofs/LIMITS_V1.md §T13). Universe U_n = {0..n-1}; n = 3.
A prefix rho = (rho_0..rho_T) is DETERMINISM-CONSISTENT iff no i<j<T has
rho_i == rho_j but rho_{i+1} != rho_{j+1}. For EVERY prefix of length 1..4 over
U_3, enumerate ALL total maps f : U_3 -> U_3 consistent with the prefix and verify:

  (1) every determinism-consistent prefix has >= 1 consistent system whose
      post-prefix orbit adds NO state unseen in the prefix  -> bounded continuation
      (Case-A construction S_b / trivial in Case B);
  (2) Case A (all prefix states distinct) AND unused state exists (m < n):
      >= 1 consistent system whose post-prefix orbit visits a fresh state
      -> novelty continuation (Case-A construction S_n);
  (3) Case B (prefix repeats a state): NO consistent system has post-prefix
      novelty -- the observed repeat forces periodicity (strengthens the ceiling);
      Case A with m == n: same-universe novelty impossible (Expansion Lemma);
  (4) determinism-INCONSISTENT prefixes admit exactly zero consistent systems.

Python 3.8 compatible. Run on billy-laptop.
"""

from __future__ import print_function

import itertools
import json
import sys

N = 3
MAX_LEN = 4


def consistent_with(f, rho):
    for t in range(len(rho) - 1):
        if f[rho[t]] != rho[t + 1]:
            return False
    return True


def prefix_consistent(rho):
    for i in range(len(rho) - 1):
        for j in range(i + 1, len(rho) - 1):
            if rho[i] == rho[j] and rho[i + 1] != rho[j + 1]:
                return False
    return True


def post_prefix_fresh(f, rho):
    # states on the orbit from rho_T (followed to its repeat) not seen in the prefix
    pre = set(rho)
    cur = rho[-1]
    seen = set([cur])
    while True:
        cur = f[cur]
        if cur in seen:
            break
        seen.add(cur)
    return len(seen - pre)


def main():
    U = list(range(N))
    failures = []
    counts = {"prefixes_total": 0, "prefixes_consistent": 0,
              "prefixes_inconsistent": 0, "consistent_systems_total": 0,
              "caseA_simple_path": 0, "caseB_self_repeating": 0,
              "novelty_continuation_prefixes": 0, "expansion_boundary_prefixes": 0}
    for L in range(1, MAX_LEN + 1):
        for rho_t in itertools.product(U, repeat=L):
            rho = list(rho_t)
            counts["prefixes_total"] += 1
            if not prefix_consistent(rho):
                counts["prefixes_inconsistent"] += 1
                any_consistent = False
                for vals in itertools.product(U, repeat=N):
                    f = dict(zip(U, vals))
                    if consistent_with(f, rho):
                        any_consistent = True
                        break
                if any_consistent:                      # (4) must have zero systems
                    failures.append(("T13-4", rho))
                continue
            counts["prefixes_consistent"] += 1
            m = len(set(rho))
            caseA = (m == len(rho))                     # all states distinct
            if caseA:
                counts["caseA_simple_path"] += 1
            else:
                counts["caseB_self_repeating"] += 1
            has_bounded = False
            has_novelty = False
            for vals in itertools.product(U, repeat=N):
                f = dict(zip(U, vals))
                if not consistent_with(f, rho):
                    continue
                counts["consistent_systems_total"] += 1
                if post_prefix_fresh(f, rho) > 0:
                    has_novelty = True
                else:
                    has_bounded = True
            if not has_bounded:                          # (1) always
                failures.append(("T13-1", rho))
            if caseA and m < N:                          # (2) novelty must exist
                if not has_novelty:
                    failures.append(("T13-2", rho))
                counts["novelty_continuation_prefixes"] += 1
            else:                                        # (3) novelty must NOT exist
                if has_novelty:
                    tag = "T13-3-caseB" if not caseA else "T13-3-expansion"
                    failures.append((tag, rho))
                counts["expansion_boundary_prefixes"] += 1
    result = {
        "checker": "check_t13_v1",
        "theorem": "HST-T13 no finite trajectory proves unbounded future novelty "
                   "(finite scope, U_3, all prefix lengths 1..4, all 3^3 maps)",
        "verified": [
            "(1) every consistent prefix admits a zero-post-prefix-novelty system",
            "(2) simple-path prefixes with an unused universe state admit a "
            "post-prefix-novelty system",
            "(3) self-repeating prefixes admit NO novelty system; exhausted-"
            "universe simple paths admit none in-universe (Expansion Lemma)",
            "(4) determinism-inconsistent prefixes admit zero consistent systems",
        ],
        "counts": counts,
        "failures": failures[:20],
        "failure_count": len(failures),
        "verdict": "PASS" if not failures else "FAIL",
    }
    out = json.dumps(result, indent=1, sort_keys=True)
    print(out)
    with open("exact/check_t13_v1.cert.json", "w") as fh:
        fh.write(out + "\n")
    sys.stderr.write("certificate written: exact/check_t13_v1.cert.json\n")
    return 0 if not failures else 1


if __name__ == "__main__":
    sys.exit(main())
