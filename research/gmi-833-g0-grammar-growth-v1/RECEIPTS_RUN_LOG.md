# Receipts and run log (E8 / #897)

Per the standing compute rule, every execution below ran off the Mac mini
(worktree `/Users/billy/Desktop/projects/ORION-wt/w5-g0-ops` was used only for
editing and git/gh). Files were transferred with rsync/scp and sha256-verified
on both ends. No network calls to crypto/exchange platforms from any host.

## Hosts

| host | role | python | result |
|---|---|---|---|
| `billy-laptop` (laptop, 16 cores) | primary certificate run | 3.8.10, 3.9.x | receipts generated, byte-identical across versions/modes |
| `billy-old` (tailscale) | cross-version check + machinery probe | 3.14.4 | identical hashes; pip probe for REUSE_AUDIT_V1.md |

## Exact commands (as executed, 2026-09-16)

On `billy-laptop`, package rsynced to `~/w5-e8/ggpkg/` from the worktree:

```text
python3.8 -I -B  test_g0_grammar_growth_v1.py        # 35 tests OK
python3.8 -I -B  g0_grammar_growth_v1.py > /tmp/r_normal.json
python3.8 -I -O -B g0_grammar_growth_v1.py > /tmp/r_opt.json
cmp /tmp/r_normal.json /tmp/r_opt.json               # identical
cp /tmp/r_normal.json RESULT_V1.json
python3.8 -I -B  independent_oracle_v1.py > ORACLE_RESULT_V1.json   # exit 0
python3.8 -I -O -B independent_oracle_v1.py > /tmp/o_opt.json
cmp ORACLE_RESULT_V1.json /tmp/o_opt.json            # identical
python3.9 -I -B  g0_grammar_growth_v1.py > /tmp/r39.json
cmp /tmp/r_normal.json /tmp/r39.json                 # identical
python3.9 -I -B  test_g0_grammar_growth_v1.py        # 35 tests OK (incl. oracle agreement)
```

On `billy-old`, package rsynced to `/tmp/w5e8/` (home dir on that host is
ephemeral; /tmp used):

```text
python3 -I -B  g0_grammar_growth_v1.py > /tmp/r314.json
python3 -I -O -B g0_grammar_growth_v1.py > /tmp/r314o.json ; cmp  # identical
python3 -I -B  independent_oracle_v1.py > /tmp/o314.json
python3 -I -O -B independent_oracle_v1.py > /tmp/o314o.json ; cmp # identical
python3 -I -B  test_g0_grammar_growth_v1.py                        # OK
python3 -m pip index versions {pyribs,qdax,deap,hpbandster,dreamcoder,stitch,dream-coder}
```

## Seeds

The main certificate is fully deterministic (no RNG anywhere). The NULL-1
ensemble uses the 200 frozen seeds 0..199 from `FROZEN_FIXTURES_V1.json` with
the frozen integer hash `((s+1)·2654435761 mod 2^32) mod C(pool,size)`.

## Receipt hashes (sha256, verified laptop == billy-old == worktree == CI)

```text
bde6029b32374f04e74866f90bd01e9c0564d09d8db338f0039d6322eb980443  RESULT_V1.json
91328e12292414d3751779785125c0dc81cc3afa1bbffecaf1643e8c229df134  ORACLE_RESULT_V1.json
12acccf68dd5e02ac0521737bc8239f550600e80b87de3330beafa9a554921c6  FROZEN_FIXTURES_V1.json
```

## Summary numbers (full detail in RESULT_V1.json)

- terminal: `GMI_833_E8_GRAMMAR_GROWTH_HELDOUT_REUSE_GREEN_AT_REGISTERED_SCOPE`,
  all 17 receipt checks true.
- invention: `m1 -> a b` (o=11, gain 8), `m2 -> m1 m1` (o=4, gain 1), saturation
  stop, depth 2 of derived bound 23.
- H+ 12 targets: 50,052 -> 1,307 burdens, K=6, net −48,739.
- H− 12 targets: 538 -> 1,710 burdens, K=6, net +1,178 (regression preserved).
- THR-1: m1 (8, Δ=1, K=3) and m2 (13, Δ=1, K=3) both strict; aggregate 21 > 6.
- NULL-1: 200 seeds, 0 nulls beat the true library, best null −48,737, rank 1.
- κ-ablation {0..8}: m2 forms only at κ ∈ {0,1}; derived κ_primary = 1 (as
  frozen); H+ net stays negative in every row (worst −46,345 at κ=8).

## Reproduce anywhere (stock CPython ≥3.8, stdlib only)

```text
python -I -B  test_g0_grammar_growth_v1.py -v
python -I -B  g0_grammar_growth_v1.py        # stdout == RESULT_V1.json bytes
python -I -B  independent_oracle_v1.py       # stdout == ORACLE_RESULT_V1.json bytes
```
