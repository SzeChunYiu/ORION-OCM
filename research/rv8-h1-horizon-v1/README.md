# RV-8 — the H1 library-acquisition horizon

FNA-4 established that a learned library beats the incumbent **per task** at 16 tasks,
and **projected** break-even at ~6,123 tasks. That is a 380× extrapolation, so
`LIBRARY_ACQUISITION_EXCEEDS_LATER_SAVINGS` was PROJECTED, NOT OBSERVED. This study runs
the horizon on a `(horizon × same-family-mix)` grid to convert it into an observation or
refute it.

The lever question is closed — the admission rule is the failing stage, the lever was
applied, and a classical stdlib-only parent (Stitch + misfire nogoods + CEGIS) holds
`PARENT_SUFFICIENT_FOR_EXPERIENCE_CONSOLIDATION_AT_REGISTERED_SCOPE`. This is a scale
question.

## Files

| file | what it is |
|---|---|
| `RV8_PROTOCOL.md` | the frozen protocol — axes, arms, gates, endpoints, predictions, limitations |
| `RV8_FREEZE.json` | digests and salts recorded before any scored cell |
| `rv8_horizon.py` | the runner: `preflight`, `replicate`, `cell` |
| `rv8_analyse.py` | the analysis, declared in the freeze commit before any result exists |
| `probe_cost.py` | post-preflight sizing probe (SLURM `--time` and launch order only) |

The world, solver, learners, arms and cost model are **imported** from
`research/functional-neural-absorption-v1/fna4_library_synthesis/`, never copied. Every
cost term FNA-4 charges is still charged.

## Running it

```
python3 rv8_horizon.py replicate  <out>     # frozen-receipt determinism gate
python3 rv8_horizon.py preflight  <out>     # harness + acquisition gates, library pickle
python3 rv8_horizon.py cell <i>   <out>     # one (arm, mix, composition, seed) stream
python3 rv8_analyse.py <out>
```

984 cells. Off-Mac only; LUNARC `lu48` under account `lu2026-2-51`, no network from the
cluster. Cells dump progressively every 4,096 tasks, so a timed-out cell still yields an
honestly-labelled prefix.

## Run state and how to resume

The scored array runs on LUNARC and outlives any one session. Everything lives under
`/projects/hep/fs12/scratch/scyiu-rv8` (NOT `/home`, which is over quota):

```
out/RV8_REPLICATION.json    gate 3 receipt
out/RV8_PREFLIGHT.json      gates 1-2 receipt + null profiles + library digest
out/RV8_COSTPROBE.json      measured per-task cost, for --time sizing only
out/RV8_LIBRARIES.pkl       the 13 acquired libraries; every cell checks its sha256
out/cells/cell_NNNNN.json.gz   one per cell, rewritten every 4,096 tasks
logs/feeder.log             what the submit feeder has done
```

To resume after any interruption:

```bash
ssh lunarc
BASE=/projects/hep/fs12/scratch/scyiu-rv8
pgrep -f rv8_feeder.py || (cd $BASE/repo/research/rv8-h1-horizon-v1 &&
  setsid nohup python3 rv8_feeder.py $BASE/out > $BASE/logs/feeder.stdout 2>&1 &)
```

The feeder is idempotent: it skips cells already marked `complete`, submits only what is
missing, respects lu48's `MaxSubmitJobs=300` (staying at 240 to leave the sibling lane
room), and retries a timed-out cell once before letting its recorded prefix stand.

Then, on whatever is present:

```bash
python3 rv8_analyse.py $BASE/out     # writes out/RV8_ANALYSIS.json
python3 rv8_verify.py  $BASE/out     # independent recomputation, must agree
python3 rv8_report.py  $BASE/out     # renders RV8_REPORT.md
```

A partial grid is analysable: every surface row records `horizon_reached_max` and
`all_seeds_complete`, so an incomplete cell is never read as a complete one.

Operational facts, so no one rediscovers them: `nuc` rejects this project despite
`AllowAccounts=ALL` (submit-plugin rule); `lu48` works with an explicit
`-A lu2026-2-51`; there is no default account; `/home` has a per-user quota that `df`
does not show.
