# Cross-domain cognitive transfer v1

**Terminal:** `CROSS_DOMAIN_TRANSFER_SUPPORTED_AT_REGISTERED_SCOPE`

Issue [#165](https://github.com/SzeChunYiu/ORION-OCM/issues/165) §7 / P6. Owners #143, #145, #151, #93.

A source polynomial method is frozen as the typed operator `apply-fragment`. A typed correspondence maps *compose learned fragment* onto *compose learned rewrite* without recording any target solution. On a reminted 4-cell ribbon-rewrite domain — exact tape equality, not polynomial identity — that transferred operator reduces held-out search work versus reset OCM and versus a task-specific miner. Removing the source method restores reset search. An unrelated color-naming table shows no usefulness. A harmful fragment lengthens search.

## Frozen protocol (before target access)

1. Freeze source method identity: `(square, dec, square)` as `apply-fragment` from `src/ocm/learning/methods.py` blob `50323a33418b8ef8bb6500ddeba4b9d1f795e9e3`.
2. Freeze typed correspondence [`correspondence.json`](correspondence.json).
3. Verify that file does not contain target tapes, task fingerprints, or color answers.
4. Remint target tokens: tape `{kel, mora}`, operators `{plait, nick, braid, knot}`. These are disjoint from `{inc, dec, double, square}`.
5. Then load target tasks.

## Domains

| Arm | Domain | Checker |
|---|---|---|
| Source | rational univariate polynomials | coefficient identity |
| Target | 4-cell ribbon rewrite | exact tape equality |
| Unrelated | color-name table | exact name match |

The target is not the polynomial grammar with renamed tokens. `plait` reverses a tape, `nick` flips cell 0, `braid` rotates, `knot` swaps the first two cells. Validation is `start` rewritten to `goal`, not a polynomial normal form.

Role correspondence (not a solution word): `nonlinear_wrap → plait`, `local_shift → nick`. Instantiated transfer fragment: `(plait, nick, plait)`.

## Comparisons

- **Reset OCM:** no live procedure; primitive token BFS.
- **Task-specific OCM:** proper fragments mined from the disjoint distance-4 train stratum, then admitted and restarted.
- **Transfer OCM:** correspondence-instantiated fragment admitted with source-method support, then restarted.
- **kNN/prototype parent:** nearest distance-4 donor by Hamming on `(start, goal)`; copy its shortest program or fall back to primitive. Neural libraries are absent → `CANNOT_CHECK_NEURAL`.
- **Unrelated:** transfer a 3-step numeric prefix into color-name enumeration; no shared sequential structure.
- **Harmful:** `(braid, braid, braid)` as a first-class token.
- **Ablation:** revoke source-method evidence; transferred procedure is not live; search equals reset task-by-task.

## Registered population

Complete finite Cayley strata of the 16 tapes, not a post-hoc subset:

- train: all 34 pairs at primitive distance 4
- test: all 16 pairs at primitive distance 5
- max expanded length 6

## Measured (this host)

| Arm | Attempts | vs reset |
|---|---:|---|
| Reset OCM | 9892 | — |
| Transfer `(plait, nick, plait)` | 6100 | 12/16 strict wins, fragment used on 12 |
| Task-specific `(plait, nick)` | 6536 | better than reset, worse than transfer |
| kNN/prototype | 9892 | 0 prototype hits; not sufficient |
| Harmful `(braid, braid, braid)` | 13522 | 14/16 longer |
| Source-method ablation | 9892 | equals reset task-by-task |
| Unrelated color-naming | 60 vs 36 | `NO_BENEFIT` |

Neural parent: `CANNOT_CHECK_NEURAL` (no torch/tensorflow/sklearn/jax). Study wall ≈ 0.12 s.

## What is not claimed

- No OCM architecture residual: ordinary serving of the same transferred fragment matches OCM.
- No claim from reusing the polynomial Python API on renamed tokens.
- No general cross-domain intelligence, language transfer, or neural-parent comparison.
- Scope is this ribbon-rewrite ecology and this correspondence.

## Run

```sh
python -B -m unittest discover -s research/cross-domain-transfer-v1 -p 'test_*.py' -v
python -B research/cross-domain-transfer-v1/experiment.py --out research/cross-domain-transfer-v1/RESULT.json
```
