# M2-P4 stage 3 — scorer validation (precondition met)

`M2P4_STAGE3_FREEZE_V1.json` makes one thing a precondition of the scored run: the registered
scorer must first reproduce a **known answer on real data**. If it did not, the scorer would be
wrong and the study would stop here. It did.

## What was run

`m2p4_score_dryrun.sbatch` on LUNARC, job **3602070**, exit **0:0**.

Inputs are M2-P2's eight worlds — `PARENT_GF_D4` from the `_gf` runs, `RESET` from the `_ocm5`
runs — assembled into the `m2p4_*_scored` layout the scorer globs. These are the data behind the
independent pre-freeze calibration (LUNARC 3599978), reproduced once already by M2-P3 (3600816),
so the expected answer was fixed before this run and not read off it.

The job prints the sha256 of the scorer it is about to execute, so the artifact under test
identifies itself in its own log: `e09c02d4050791767dc72323ef3bb1d3e50cc402352761ca0e3211666e647261`
— the sha bound in the stage-3 registration, verified identical on both sides before staging.

## Result

| world | n | ratio−1 | Holm | passes 50% bar |
|---|---|---|---|---|
| hc01-binary-ladder | 46 | −0.9277 | 0.00080 | yes |
| hc02-square-shift | 447 | −0.8184 | 0.00080 | yes |
| hc03-shift-runs | 303 | −0.9033 | 0.00080 | yes |
| hc05-long-form | 55 | −0.8755 | 0.00080 | yes |
| hc06-decoy-pair | 146 | −0.9467 | 0.00080 | yes |
| **hc08-drawn-lot-b** | 55 | −0.5987 | 0.15678 | **no** |
| hc09-negative-ladder | 58 | −0.8778 | 0.00080 | yes |
| hc10-quartic-climb | 163 | −0.8194 | 0.00080 | yes |

k = **7/8**, median ratio−1 = **−0.8766**, precondition significant in every world.

All six registered checks passed: `k_passing==7`, `worlds_scored==8`, `hc08_present`,
`hc08_fails`, `median~-0.877`, `no_point_prediction`.

`hc08_present` is in that list deliberately. Without it, a staging bug that silently dropped hc08
would leave 7 worlds that all pass — and "the failing world did not fail" would read as
agreement. The check asserts the world was actually scored before asserting how it scored.

The validation script exits **3** on disagreement and non-zero on a crash, so "could not check"
can never be recorded as "checked and fine".

## Isolation, checked rather than asserted

The sbatch writes only into its own `tmp_scoredry_m2p4`. That is a claim about the script, so it
was also measured: M2-P3's `tmp_scoredry` was fingerprinted before and after the run.

| | before | after |
|---|---|---|
| inode | 1035087118464 | 1035087118464 |
| mtime | 1789164773 | 1789164773 |
| content digest | `e14ab12e…` | `e14ab12e…` |

Unchanged in all three. `tmp_scoredry_m2p4` is a separate inode (1054414471296) holding its own
eight world directories. No M2-P3 or M2-P4 run data was read for writing, renamed, or reused.

## What this does and does not establish

It establishes that the scorer computes the registered statistic correctly on data whose answer
was already known. It says **nothing** about M2-P4's own worlds: these are M2-P2's band-2–3
worlds, and the median here is not comparable to one from a band-3–4 tiling. The scored run
remains unrun and its outcome unknown.
