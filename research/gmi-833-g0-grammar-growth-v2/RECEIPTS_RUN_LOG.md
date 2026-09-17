# Receipts and run log — grammar-growth tranche 2 (#897 follow-up)

Per the standing compute rule, every execution below ran off the Mac mini
(worktree `/Users/billy/Desktop/projects/ORION-wt/w5-g0-ops` used only for
editing and git/gh). Files were transferred with rsync/scp and sha256-verified
on both ends. No network calls to crypto/exchange platforms from any host.

## Hosts

| host | role | python | result |
|---|---|---|---|
| `billy-laptop` (laptop, 16 cores, shared with 3 other lanes) | design probes, full certificate, oracle, tests | 3.8.10, 3.9.x | receipts byte-identical across versions/modes; 32/32 tests; oracle all_ok |

## Design probes (pre-freeze, off-Mac)

Three probe rounds (`probe2.py`, `probe2b.py`, `probe2c.py`, executed on
`billy-laptop` only, never committed — they are design tooling for the frozen
fixtures, superseded by the package tests): round 1 falsified the initial
hand-derived depth-3 corpus design (programs of (ab)^4 give only depth 2) and
located the L8f18/f19 witness; round 2 established the depth-4/5 attempt
corpora's actual depth-3 saturation, the trap corpora, the tier tables, the
exec formula checks, and the suite constraint checks; round 3 verified the
final frozen corpora, suites, κ grids, f* brackets, utility-gate behaviour on
all corpora, and the exec previews. Every frozen expectation in
`FROZEN_FIXTURES_V2.json` is a probed value with an honest-failure clause.

## Exact commands (as executed, 2026-09-16/17)

On `billy-laptop`, package rsynced to `~/w5-t2/research/` mirroring the repo
layout (v1 package alongside v2, as the v2 module imports it):

```text
python3 -I -B  test_g0_grammar_growth_v2.py -v   # 32 tests OK
python3 -I -B  g0_grammar_growth_v2.py > RESULT_V2.json
python3 -I -O -B g0_grammar_growth_v2.py > /tmp/r_opt.json
cmp RESULT_V2.json /tmp/r_opt.json               # identical
python3 -I -B  independent_oracle_v2.py > ORACLE_RESULT_V2.json   # exit 0
python3 -I -O -B independent_oracle_v2.py > /tmp/o_opt.json ; cmp # identical
python3.9 -I -B g0_grammar_growth_v2.py > /tmp/r39.json
cmp RESULT_V2.json /tmp/r39.json                 # identical
```

Full receipt runtime ~20 s; oracle ~1.3 s.

## Incident log (honest, both defects found and fixed before ship)

1. The oracle initially used combinadic (colex) unranking against v1's
   lexicographic materialized enumeration — HUNR-1 smoke caught it; fixed to
   lexicographic unranking in both implementations.
2. `trace_depth` initially hardcoded `m*` macro names, mis-scoring the ADM-ALT
   `d*`-named diagnostic as depth 1 — smoke caught; made name-generic.
3. The first committed-candidate oracle run stalled (>30 min) with wrong
   monster-integer exec values: `lstar, hit = burden(...)` unpacked the return
   pair `(burden_number, program)` incorrectly, so `lstar` became the burden
   count (~10^4-10^5) and the full-length geometric sums exploded. Direct
   staged timing on the laptop isolated the block; fixed to
   `_, hit = burden(...); lstar = len(hit)`. The main receipt was never
   affected (its exec DP unpacks correctly and was independently verified
   against naive enumeration by HEXEC-1 and the pre-freeze probes). Post-fix
   oracle: all_ok, 1.3 s.

## Seeds

The main certificate is fully deterministic (no RNG anywhere). NULL-2 uses the
200 frozen seeds 0..199 from `FROZEN_FIXTURES_V2.json` with the frozen hash
`((s+1)·2654435761 mod 2^32) mod C(pool,size)` and lexicographic unranking
(HUNR-1-verified against materialized enumeration on feasible pools).

## Receipt hashes (sha256, generated on billy-laptop, verified == worktree)

```text
bc81e7757962132f0418119a8d8799719f41da3d280541c724493df7e9eb4514  FROZEN_FIXTURES_V2.json
fdb3bef78bec3e211a39cf39aa3dd534014de33c0692c8d72651f1ad812104fd  RESULT_V2.json
b4218cf156f1af793717301186a07ea9fc094ebf7bd0b64ba55526ead4481690  ORACLE_RESULT_V2.json
```

## Summary numbers (full detail in RESULT_V2.json)

- terminal `GMI_833_E8_TRANCHE2_GREEN_AT_REGISTERED_SCOPE`, all 33 receipt
  checks true, oracle `all_ok` (traces, tier rows, h2h nets, exec grid +
  breakeven 164, nulls, κ*).
- formation: c3 depth 3 (m3=(m2,m2), gain 1, saturation), c4/c5 designed for
  depth 4/5 stop at depth 3 (T7 dominance); family ceiling fn5/8/12 depth 1,
  fl8/fl16 depth 2; ADM-ALT diagnostic depth 7/9; economics f*=19/50/115
  (strict), κ*=1/4/4.
- compounding (c3, charged): T1 1712→732→1296→2098, T2 1.97e9→7683408→4130→7652,
  T3 3.15e16→1.22e11→20616→1350; H− 429→771→1257→1911; aggregate net
  −31,501,345,179,969,279; 0/200 nulls better (rank 1) on c3/c4/c5.
- head-to-head: v1ref/c4/c5 ties (−48739 on v1ref); c3 compression better by
  14,939 (shallow V) / tie (deep V); trap1 utility −19,433 vs compression
  −12,892 (0/200 vs 52/200 nulls beating); trap3 compression +43,897
  (regression vs primitive) vs utility −17,348 (= null-ensemble min).
- exec: flagship H+ net −395,484/−393,054/−388,194 at ρ=1/2/4, H− preserved,
  break-even ρ†=164; 19/200 exec-nulls beat the recursive library (rank
  cost-fragility, mechanism: flat abab=5 ops vs recursive m2=7 ops); all
  verdict signs agree count-vs-exec.

## Reproduce anywhere (stock CPython ≥3.8, stdlib only)

```text
python -I -B  test_g0_grammar_growth_v2.py -v
python -I -B  g0_grammar_growth_v2.py        # stdout == RESULT_V2.json bytes
python -I -B  independent_oracle_v2.py       # stdout == ORACLE_RESULT_V2.json bytes
```
