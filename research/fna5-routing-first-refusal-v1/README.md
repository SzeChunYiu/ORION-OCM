# FNA-5 / D7 — non-neural routing first-refusal study (research-only)

Capsule for issue #214 work package FNA-5, deliverable FNA-D7 (aligned with #71).
Nothing here deploys anything; #71 stays `LEARNED_ROUTER_NOT_YET_AUTHORIZED`.

## Contents

- `PROTOCOL.md` — frozen protocol (read before outcomes existed)
- `FREEZE_FNA5_V1.json` — pre-outcome freeze with sha256 digests of the frozen code
- `fna5_world.py` — task world on the real `OperatorSpec` / `SolveOperatorIndex` surface
- `fna5_selectors.py` — arms A2..A6 (conventional parents first, neural last, diagnostic)
- `fna5.py` — driver; emits the receipt
- `test_fna5.py` — unittest harness-validity/control/charging/terminal checks
- `FREEZE_FNA5B_ADDENDUM_V1.json` + `fna5b.py` — revival pass 1 (negative-results
  directive): minimal-information A1B + perfect-router bound, own pre-declared mapping
- `FNA5B_RESULTS_V1.json` — revival receipt
- `FNA5_RESULTS_V1.json` / `FNA5_RESULTS_V1.md` — scored receipt and its reading
- `REPO_STATE.json` — base commit, disjointness audit, execution host

## Execution (all runs happen on the laptop, never the Mac)

The production `ocm` package requires Python >= 3.10 (`dataclass(slots=True)`); the
laptop's `a1_bench` conda env (3.10.19) satisfies this — the repo hook's own floor.
Capsule code itself is 3.8-syntax stdlib-only.

```bash
# 1. sync world + capsule + tests (Mac -> laptop)
rsync -av --delete \
  /Users/billy/Desktop/projects/ORION-OCM/ORION-OCM-wt/fna5-routing/src/ \
  billy-laptop:fna5-routing/src/
rsync -av \
  /Users/billy/Desktop/projects/ORION-OCM/ORION-OCM-wt/fna5-routing/research/fna5-routing-first-refusal-v1/ \
  billy-laptop:fna5-routing/capsule/

# 2. md5-verify what landed
ssh billy-laptop 'cd fna5-routing && md5 capsule/*.py capsule/PROTOCOL.md' 
md5 -r src/ocm/runtime/operator_index.py   # compare against laptop-side copies

# 3. tests (must be green before the scored run counts)
ssh billy-laptop 'cd fna5-routing/capsule && \
  PYTHONPATH=../src /home/billy/anaconda3/envs/a1_bench/bin/python3 -m unittest -v test_fna5'

# 4. scored run (full config, writes FNA5_RESULTS_V1.json)
ssh billy-laptop 'cd fna5-routing/capsule && \
  PYTHONPATH=../src /home/billy/anaconda3/envs/a1_bench/bin/python3 fna5.py \
  --out FNA5_RESULTS_V1.json'

# 5. pull the receipt back and verify
rsync -av billy-laptop:fna5-routing/capsule/FNA5_RESULTS_V1.json \
  /Users/billy/Desktop/projects/ORION-OCM/ORION-OCM-wt/fna5-routing/research/fna5-routing-first-refusal-v1/
ssh billy-laptop 'md5sum fna5-routing/capsule/FNA5_RESULTS_V1.json'
md5 -r /Users/billy/Desktop/projects/ORION-OCM/ORION-OCM-wt/fna5-routing/research/fna5-routing-first-refusal-v1/FNA5_RESULTS_V1.json

# 6. revival pass (negative-results directive; writes FNA5B_RESULTS_V1.json)
ssh billy-laptop 'cd fna5-routing/capsule && \
  PYTHONPATH=../src /home/billy/anaconda3/envs/a1_bench/bin/python3 fna5b.py \
  --out FNA5B_RESULTS_V1.json'
```
