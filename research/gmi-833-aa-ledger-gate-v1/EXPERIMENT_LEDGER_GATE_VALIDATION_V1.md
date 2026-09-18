# Experiment ledger — ledger-gate recall, no-alarm and failure demonstration

Schema: `GMI_EXPERIMENT_LEDGER_V1`. Package `gmi-833-aa-ledger-gate-v1`,
issue #833, row AA06. Experiment: establish that the ratcheting ledger gate
detects a non-compliant new result, raises no alarm on compliant input, and
**can actually fail** — the defect that made the terminology gate it succeeds
vacuous was that its checks ran under `|| true`.

**Leakage.** The fixture corpora are generated into a temporary directory
outside `research/`, so a deliberately broken fixture can never be picked up by
the repository-wide census and inflate the measured debt. The gate under test
is the same function CI calls, with `--scan-root` pointed at the fixture and
`--baseline` at the fixture's own frozen state; no code path exists only for
the test. The fixture baseline is written from the clean fixture before the
break is applied, so the break cannot be pre-absorbed.

**Search space.** Four fixture corpora, fixed in advance: (1) clean — one
theorem artifact whose single named result emits all four ledgers; (2) the same
corpus with one new non-compliant result appended; (3) the same corpus with an
existing compliant result's ledger removed (regression); (4) a decoy — a result
whose prose contains the words "assumption", "depends", "falsify" and "parent"
in running text but carries no block-leading ledger label. Nothing is sampled
and no fixture was added after seeing a result.

**Cost model.** Each fixture is a handful of kilobytes; the whole validation is
milliseconds and runs inside the test module on every CI invocation, so the
"the gate can fail" claim is re-established on every run rather than asserted
once in prose.

**Evaluation.** The outcome is the gate's own exit code and violation list. The
clean corpus must exit **0** with zero violations; corpora (2) and (3) must exit
**non-zero** and name the missing ledgers and the violation kind
(`NEW_RESULT_MISSING_LEDGER`, `COMPLIANT_RESULT_REGRESSED`); corpus (4) must
exit non-zero with the decoy's result named — a prose mention is not an
emission. A gate that passed corpus (4) would be measuring word frequency, not
ledger emission.

**Sampling bias.** The fixtures are constructed, not sampled, so they carry
exactly the bias of their author — which is why they are not the only evidence.
The same predicate is run over the whole 329-file corpus in
`EXPERIMENT_LEDGER_CORPUS_CENSUS_V1.md`'s experiment, where the no-alarm case
is the real one: at baseline the gate reports **0** violations against its own
frozen baseline while the debt it discloses is 2345 non-compliant results. A
gate that fires on work a lane did not do is a gate that gets switched off, so
the corpus debt is ratcheted, never retroactively charged.
