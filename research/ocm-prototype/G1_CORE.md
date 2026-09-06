# G1 donor attachment — read first

**Current verdict: G1_NOT_ADMITTED.** The same vessel completes a frozen stream
of 100 supplied-token syntax cases and five public CLIA tasks. Its 100 selected
trees exactly match the native donor, and both arms pass all five program checks.
`PARENT_SUFFICIENT` explains capability at this development scope. Strong hosted
comparison and an OCM-specific benefit remain open.

Owners: [#73](https://github.com/SzeChunYiu/ORION-OCM/issues/73) prototype,
[#69](https://github.com/SzeChunYiu/ORION-OCM/issues/69) architecture,
[#50](https://github.com/SzeChunYiu/ORION-OCM/issues/50) thesis,
[#62](https://github.com/SzeChunYiu/ORION-OCM/issues/62) lifetime learning,
[#42](https://github.com/SzeChunYiu/ORION-OCM/issues/42) domains,
[#38](https://github.com/SzeChunYiu/ORION-OCM/issues/38) acceptance.
Detailed hypotheses, experiments and negative terminals stay in those issues.

## What is implemented

- `g1_vessel.py`: the same production `OCMRuntime.solve` / `SV.solve`, with both
  donor descriptors offered on every query. Per-run bindings identify the core source.
- `g1_field.py`: ordinary field objects, ledger persistence and a model archive.
  Archive bytes count as persistent state. Setup refuses model/plan mismatch.
- `clia_*.py`: ADOPT cvc5 proposals and separate Z3 checking; ADAPT a small
  S-expression grammar/type/binding gate. All five public specifications are in
  `clia_fixtures/`, including upstream custody and grammar adaptation.
- `udpipe_donor.py`: ADOPT UDPipe1, with a forms-only JSON adapter. This trained
  tagger/feedforward parser is the syntax mechanism donor in O; it is not Pi.
- `syntax_contract.py`: ADOPT official CoNLL18 structural loading. Gold scoring
  is external and never an interactive checker available to an arm.

`status=ADMITTED` plus a non-null `admitted_id` denotes final host admission.
`solve_status=ANSWER` alone is insufficient. Failed rechecks expose no accepted
`answer`; any raw proposal is explicitly diagnostic.

Syntax admission means **model M emitted structurally valid tree T on input X**.
It uses an observation atom and OBSERVATION certificate. It does not certify
gold accuracy, semantic truth, communication, or an epistemic superiority.
Generic `runtime.compose` is outside this adapter: its current certificate
provenance requires separate review before observations can feed proof claims.

CLIA admission means a candidate fits the declared grammar and Z3 returned
`unsat` for the negation of the public universal specification. Search is
performed by cvc5 over its implicit CLIA space; independent grammar checking
restricts accepted outputs identically for every arm. Native explicit-grammar
search was tried and its time-bound failure and failed revival are retained.

## Operate on a compute host

```sh
python -m pip install -e . -r research/ocm-prototype/requirements-g1.txt
python -m pytest research/ocm-prototype -q
```

For direct synthesis, import `load_task` from `clia_tasks`, `propose` from
`clia_solver`, and `check` from `clia_checker`. Pass the complete bound task to
both APIs. Checker `unknown`, missing dependencies and timeouts are CANNOT_CHECK.

`g1_vessel.worker(state_directory, command)` accepts host actions:
`setup` (model path and training manifest), `query` (typed request), and
`revoke`/`reinstate` (a list of complete evidence identifiers).
Syntax requests are `{kind: syntax, tokens: [...]}`; CLIA requests are
`{kind: clia, task: load_task(id)}`. No gold or checker selector is accepted.

Model withdrawal is coarse, covering a whole trained model version. It does not
prove training-example deletion or local neural unlearning. Unit syntax stubs
and invalid-model CLIA smoke fixtures are explicitly not language evidence.

## Evidence and remaining claims

Raw public development records are in `results/g1-20260906/`; each carries
source/input bindings. Query wall time excludes process startup/replay;
external capture receipts measure those separately and include terminated child
CPU. Dense field navigation, full ledger replay, both checks, archive hashing
and reload remain charged. No sparse or whole-lifetime efficiency claim follows.

The scalar parameter count of the binary UDPipe model remains CANNOT_CHECK;
model/package bytes and the actual non-Transformer architecture are separate
accounting quantities. No new controller or theory is introduced here.

## Trained and matched development evidence

- [Trained donor CORE](results/g1-trained-donor-20260906/CORE.md): complete TRAIN-only provenance, both training attempts and frozen 290 direct evaluation.
- [Matched comparison CORE](results/g1-matched-20260906/CORE.md): external gold scores, all 105 native/OCM outcomes and measured startup/replay/check/persistence costs.
- [Frozen public stream](results/g1-matched-plan-v1/plan.json): 105 items in five alternating-order chunks, bound before model outputs.
- `capture_g1_matched.py` executes that stream with separate persistent states; `grade_g1_matched.py` scores afterward using an explicitly supplied, hash-bound DEV file. Neither actor imports the grader.

The matched panel has 77.904% base LAS and 32/100 exact trees in both arms; the
original OCM run uses 127.735 s recorded CPU versus 6.852 s native. These are
shared-host descriptive results, not protected comparability or an efficiency
advantage. The diagnosed admission/replay cost is owned by issue #72.
