# Executed witness readout

One frozen attempt on 2026-09-06, 17:07:21.839437–17:07:22.467817 UTC; outer exit 0.
Raw terminal: WITNESS_QUALIFICATION_PASS. Five assigned/five completed.

| Case | Native result | Recorded evidence |
| --- | --- | --- |
| Saved subtraction vs h1-h0 | UNSAT | Exact witnessed identity |
| Saved integer predicate vs h0<=0 | UNSAT | Exact witnessed identity |
| Wrong subtraction orientation | SAT | h0=0,h1=1 |
| Shifted integer threshold | SAT | h0=1 |
| Real reinterpretation | NOT_RUN | Int-signature refusal before native entry |

Four actual native Z3 entries; zero compression/normalization/discovery calls.
The two SAT results are intended negative controls, not passed equalities.
The type refusal does not classify the Real identity.

## Recorded costs

| Measurement | Value | Scope |
| --- | ---: | --- |
| Root outer elapsed | 0.628380 s | Start before launch through observed completion |
| Supervisor wall | 0.597495309 s | Includes pre/post source binding |
| Child launch/wait/cleanup | 0.364991825 s | Existing process envelope |
| Caller body wall | 0.283748603 s | Starts after top-level imports |
| Caller self CPU | 0.003895254 s | Caller body only, excludes native children/import CPU |
| Caller peak RSS | 20552 KiB | Process high-water including imports |

| Native probe | Worker wall(s) | Worker CPU(s) | Worker peak RSS(KiB) |
| --- | ---: | ---: | ---: |
| saved_subtraction | 0.032314623 | 0.032295590 | 52416 |
| saved_integer_predicate | 0.031930494 | 0.031920694 | 55884 |
| wrong_subtraction_orientation | 0.032764030 | 0.032746418 | 58064 |
| shifted_integer_threshold | 0.033173339 | 0.033166046 | 57856 |

These nested wall observations are not additive. Per-worker CPU excludes parent and
process-startup work outside the worker timer; RSS values are separate high-water marks.
Total process-tree CPU/RSS, energy and whole-lifetime acquisition cost remain UNKNOWN.
Previous acquisitions, inductions and normalizations are external recorded history.
No runtime saving, learned-usefulness, transfer or OCM advantage was tested.

## Identity

Original seal: 761a0e1e70d6811009979ebe13af657abf7ac9534657c6ade9bd145ebebda83f.
Frozen manifest: 672ed29cdb66957b087349caae3dfac206358aa8250e56b2cff032953a992c5b.
All 27 seal members and 69 frozen bindings matched during publication inspection.
No source or scientific authority was promoted by this evidence-only packaging.
