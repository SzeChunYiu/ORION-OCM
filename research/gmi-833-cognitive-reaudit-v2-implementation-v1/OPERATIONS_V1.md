# Operations — Section-M hierarchy/planning/causal re-audit v1

Compute on **billy-old / laptop-billy**, never the Mac mini. From the repo root:

```bash
python3 -I -B  research/gmi-833-cognitive-reaudit-v2-implementation-v1/executor_v1.py
python3 -I -O -B research/gmi-833-cognitive-reaudit-v2-implementation-v1/executor_v1.py
python3 -I -B  research/gmi-833-cognitive-reaudit-v2-implementation-v1/test_reaudit_v1.py -v
python3 -I -O -B research/gmi-833-cognitive-reaudit-v2-implementation-v1/test_reaudit_v1.py -v
python3 -I -B  research/gmi-833-cognitive-reaudit-v2-implementation-v1/replay_v1.py | cmp - research/gmi-833-cognitive-reaudit-v2-implementation-v1/RESULT_V1.json
python3 -I -O -B research/gmi-833-cognitive-reaudit-v2-implementation-v1/replay_v1.py | cmp - research/gmi-833-cognitive-reaudit-v2-implementation-v1/RESULT_V1.json
```

Both executor modes must write a byte-identical `RESULT_V1.json`; the isolated
replay (a fresh subprocess with the same flags) must reproduce it byte-for-byte
and the `replay` command must equal the committed `RESULT_V1.json`.  The
executor itself re-runs both replayable legacy packages (`hierarchy`, `causal`)
in isolation (`-I -B [-O]`) and requires byte-exact reproduction of their
committed `RECEIPT_V1.json` files.  Any mismatch raises `ValueError`
(non-zero exit); a red result is explicit, never a silent pass.

Stdlib only; exact `Fraction` arithmetic; no float literal appears in any
package source file (enforced by a test and by CI).  Parent blobs are pinned
in `MANIFEST_V1.json` and re-checked at run time; the in-package
`FREEZE_V1.md` is a byte-identical copy of the canonical freeze
(sha256 `5f457a7f2fa6af1fce554e29e90df4ee3afd58c1cd6656418fcdfbde76bd3e2c`).

## Expected numbers

- planning: hostile `k=1/8` myopic EVC `-1/8` stops, Bellman continues with
  `V*(root)=3/4`, two-step plan net value `+1/4`; clean `k=1` stops; `k=1/4`
  tie choice set `{stop,t1,t2}`; 144 full-policy enumerations match `V*`;
  myopic META-3 scope 13/35 with disagree witness `S={3,5}`.
- hierarchy: lifecycle 3060/3032/1233; greedy countermodel cost 2 vs source
  greedy 3; hierarchy-loses workload solver cost 2; register census 384 cases /
  3456 executions; parsing census 1008 cases / 3136 parses.
- causal: census n=1..6 (1716 models at n=6; 27,018 joint-law comparisons;
  4,032 attainment checks); observation-equivalent pairs with different PN;
  incompatible evidence refused; identified constant-on-fiber control; faithful
  graphs do not orient (3/4 vs 1/2); undefined conditioning distinct refusal.

## Commit / PR discipline

Implementation artifacts must postdate the freeze commit
`cb6d6a590535e8660559b143cbe32308a880c482` in git order (CI freeze-custody
step enforces it).  This repo has no required-checks branch protection, so the
PR head's CI must reach `conclusion=success` before a squash merge.
