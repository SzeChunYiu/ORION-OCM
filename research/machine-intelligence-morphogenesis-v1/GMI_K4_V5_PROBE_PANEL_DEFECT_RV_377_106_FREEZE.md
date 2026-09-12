# RV-377-106 — FREEZE: the DG-10 measurement panel cannot separate its own reference laws

Frozen BEFORE the repair run. Nothing below may be edited after the run;
outcomes are appended verbatim in the adjudication commit.

## 1. What was received

`gmi/k4-dg10-hardening-v5` (head `bd875488`, 21 commits) responds to the two
findings recorded in PR #445: it derives the K4 `state_scales_with` /
`serve_scales_with` axes from *measured* resource traces instead of copying
them out of the candidate token (DG-10), and it repairs the three hostile
tests that died on the no-admissible-candidate early return.

The design is right. A candidate carries two independently selected integer
resource expressions; the public axis labels are recovered only by executing
each expression on a fixed probe panel and matching the numeric trace against
the preregistered reference laws, with `UNCLASSIFIED_*_LAW` fallbacks.

## 2. The defect

`gmi_k4_resource_native_v4.py` raises on **import**, at its own self-check:

```
File ".../gmi_k4_resource_native_v4.py", line 125, in <module>
    raise AssertionError("state measurement panel aliases reference laws")
```

Every importer is affected — `gmi_k4_search_v4.py`, `gmi_k4_search_v5.py`,
`gmi_k4_null_frontier_v5.py`, `test_gmi_k4_resource_native_v4.py` — and because
pytest fails at *collection*, the branch's entire suite is blocked, not merely
the K4 tests. The 8 newest commits (null-aware K4 V5, its freeze JSON, the
LUNARC sizing, the beacon, the aggregate, the renderer/submitter) are therefore
built on a module that has never once executed.

### Root cause (mechanical, not environmental)

`_probe_env(i)` assigns every resource variable

```python
env = {v: 2 + ((j * 7 + i * 11) % 13) for j, v in enumerate(_RESOURCE_VARS)}
```

where `j` is the variable's index in the sorted variable list. There are **39**
variables but the modulus is **13**. Since 7 is invertible mod 13, `j*7 mod 13`
depends only on `j mod 13`, so the variables at indices `j`, `j+13` and `j+26`
receive *identical* values. The `i*11` term shifts every variable by the same
amount, so no probe can ever break the tie: the aliasing holds simultaneously on
all 19 probes. Only `search_branch`, `window` and `rank` escape, because they are
explicitly overridden afterwards.

Measured consequence on the received code:

- 39 resource variables collapse to **16** distinct value-traces
- 22 `STATE_REFERENCE` laws collapse to **16** distinct signatures
- 21 `SERVE_REFERENCE` laws collapse to **19** distinct signatures

Colliding state pairs: `n_retained_sections`/`n_hypotheses`,
`n_records`/`hidden_width`, `n_constraints`/`kernel_size`,
`program_size`/`edge_features`, `state_dim`/`dynamics_model_size`,
`corpus_size`/`score_model_size`. Colliding serve pairs:
`n_retained_sections`/`n_hypotheses`, `policy_size`/`sequence_length`.

This is not cosmetic. The entire DG-10 argument is that the axis label is
*recovered by measurement* rather than carried in the token. A panel that
cannot separate 6 of 22 state laws does not recover the label; it would have
mislabelled silently had the self-check not been there. The self-check is the
one part of this module that worked, and it is what makes the lane's own claim
auditable. Credit where due — it fired correctly.

### A second leak the self-check does not cover

The module builds `STATE_SIG_TO_LABEL` from `STATE_REFERENCE` only, then asserts
only reference-vs-reference injectivity. It never checks the **distractors**.
On the received panel, `STATE_DISTRACTORS[1] = V("positions")` aliases the
reference law `dynamics_model_size = V("dynamics")`, so a candidate selecting a
deliberate non-target law would be reported as having hit a frozen target
coordinate. That is the DG-10 failure mode in reverse — a leak *into* the answer
key rather than out of it — and it is currently unguarded.

## 3. Minimal justified change

Raise the probe modulus above the variable count, keeping the multiplier coprime
to it, and add the missing distractor guard. Nothing else in the module changes:
no reference law is added, removed or rewritten, no candidate generation or
ranking is touched, the probe count stays 19.

```python
_PROBE_MOD = 41   # prime, > len(_RESOURCE_VARS) == 39
env = {v: 2 + ((j * 7 + i * 11) % _PROBE_MOD) for j, v in enumerate(_RESOURCE_VARS)}
```

plus a fourth assertion: no `STATE_DISTRACTORS` / `SERVE_DISTRACTORS` element may
carry a signature present in the corresponding reference table.

## 4. Frozen predictions

| id | prediction | falsifier |
|----|-----------|-----------|
| P1 | With `_PROBE_MOD = 41`, `gmi_k4_resource_native_v4` imports with no assertion. | any assertion on import |
| P2 | All 39 resource variables receive distinct value-traces; all 22 state and all 21 serve reference laws receive distinct signatures. | any collision |
| P3 | No distractor aliases any reference law, so the new fourth assertion passes as written rather than needing the distractor set changed. | a distractor collision forcing an edit to `*_DISTRACTORS` |
| P4 | **The V4/V5 test files will show at least one further failure beyond the import error.** A module this size that has never executed is not correct on first run. | the V4/V5 tests pass first time |
| P5 | The 245 tests green before this merge stay green; the fix changes no result outside the K4 V4/V5 line. | any previously-green test turns red |

P4 is the prediction that costs something. It is stated against the Codex lane's
work and against the convenient outcome. If P4 is falsified — if the whole V4/V5
stack runs clean the moment the panel is widened — that is recorded as a win for
the lane, not quietly dropped.

## 5. What this does NOT do

This repairs the *instrument*. It does not adjudicate DG-10. Whether the measured
axes actually break the family bijection is a separate question, answerable only
after the module runs, and is not claimed here.

No RED result is touched. No earlier failure is rewritten.
