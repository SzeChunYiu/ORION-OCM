# One exposed task: implicit parent passes; explicit candidate calls time out

**`CANNOT_CHECK_CONSUMPTION`.** C returned a candidate and passed the original
primitive grammar and universal Z3 specification check. E0 and B each exhausted
the registered 20-second external envelope with empty stdout/stderr. Their assigned
rows remain in the denominator. Neither produced a returned body to inspect.

| Route | Candidate outcome | Native checker reached | Result |
| --- | --- | --- | --- |
| C: implicit primitive parent | Solution | C-spec: UNSAT / PASS | Checked answer |
| E0: full explicit primitives | External timeout, exit 124 | None | CANNOT_CHECK |
| B: E0 + exact acquired predicate | External timeout, exit 124 | None | CANNOT_CHECK_CONSUMPTION |

Three candidate commands were dispatched once; one of the four permitted Z3
obligations was reached. C's successful candidate and checker envelopes total
**0.228206754 s**. E0 and B consumed **20.009268306 s** and **20.011838971 s**
respectively. See [complete cost scopes](COSTS.md) and [numeric rows](COSTS.csv).
The ordinary implicit parent is sufficient for this exposed-task capability and
on-run service-work comparison: **`PARENT_SUFFICIENT`** for that narrow scope.

The responsible unresolved stage is the **shared explicit candidate interface**.
E0 failed without any learned helper, so the observed timeout does not require the
predicate's presence. These records do not locate the stall inside parsing, grammar
construction, native search, reconstruction or output. They do not show the predicate
is useless. No useful-learning, causal-search, OCM-specific residual or whole-lifetime
improvement has been established. The next step is a separately frozen phase
instrumentation diagnostic, [specified here](NEXT_DIAGNOSTIC.md), with no new induction.

## Custody and independent review

Prospective freeze: [issue #62 comment](https://github.com/SzeChunYiu/ORION-OCM/issues/62#issuecomment-5561648417),
commit `21a7fbcd154653e0ff00909a25d7dc2a5678fe56`. The exact manifest remains
`5f2f7386f9b9b10e9228522213002e34cf9241312819533f8132df8bc82e61a4`.

- Candidate seal: `ffb0537844e47ad90e94c809a5423cf8a708238ca96e8129933ebb529f9b605e`.
- Assessment seal: `23403ee223dacd8faef549e249f18621b5307561130ee886bd8758ab74f22e5a`.
- [Independent record audit](INDEPENDENT_RECORD_AUDIT.json) verified all 65 current
  source/environment/request bindings, all 20 candidate and 11 assessment members,
  exact request/launch matching, the C specification payload and root exit records.
- At audit time all six recorded PIDs were absent, with no surviving member of their
  four supervised process groups or sessions. This is current cleanup evidence;
  it does not reconstruct historical process-tree CPU or memory.

The audit invoked no native solver. Frozen sources, raw captures and graded receipts
remain unchanged. The first unexecuted preparation is still retained under
`preparation-history/eba6a712/`.

## Additive diagnostic correction

The frozen C-spec assessment contains `status=PASS`, `solver_result=unsat`, and the
stale diagnostic `reason="native return unavailable"`. Its raw Z3 stdout contains
PASS/UNSAT and no reason. `later_consumption_capture.decode_result` initializes that
reason before decoding and does not remove it when a successful return omits the
field. This is a presentation defect, not contradictory native evidence; no frozen
receipt has been rewritten. A separate source successor must clear the default
reason on successful decode and add a mocked regression test before its next use.
