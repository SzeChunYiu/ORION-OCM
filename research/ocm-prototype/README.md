# Shared-vessel development pilot

This pilot sends taught language interpretation and polynomial-program synthesis
through the existing `OCMRuntime.solve` / `SV.solve` loop. Both domains share one
persistent KSO field, the full three-operator catalogue and explicit host checked
admission. The mechanism uses no Transformer or LLM.

Scientific ownership and executable next-study protocol:
[#69 architecture](https://github.com/SzeChunYiu/ORION-OCM/issues/69),
[#73 prototype](https://github.com/SzeChunYiu/ORION-OCM/issues/73),
[#50 thesis](https://github.com/SzeChunYiu/ORION-OCM/issues/50),
[#62 experience](https://github.com/SzeChunYiu/ORION-OCM/issues/62),
[#42 domain execution](https://github.com/SzeChunYiu/ORION-OCM/issues/42).

## Run on a Linux test host

Follow [G1 operating instructions](G1_CORE.md#operate-on-a-compute-host) for
dependencies and scoped tests. Hosted client/native controls use their separate
[qualification instructions](hosted_reference/README.md).

The study uses real subprocesses and a fresh temporary state directory. To retain
an individual receipt, call `vessel_pilot.run_study(Path(FRESH_DIRECTORY))` with
`research/ocm-prototype` on the Python path and serialize the returned dictionary.
An existing populated study directory is refused to avoid mixing lifetimes.

## What is implemented

- `vessel_state.py`: acquired language and generator data in the existing ledger.
- `vessel_ops.py`: credited donor proposals and fixed host checker bindings.
- `vessel_pilot.py`: one unchanged executive plus explicit checked admission.
- `vessel_study.py`: interleaved domains, process reload and support lifecycle.
- `vessel_parents.py`: independently executed direct parser and finite catalogue.
- `test_shared_vessel.py`: integration and refusal regressions.

The arithmetic catalogue enumerates every program through length four; build and
storage are charged. Generator withdrawal changes eligibility, while previously
independently checked mathematical truths can remain valid.

## Scope and evidence

The [registered receipt](results/shared-vessel-20260906.json) passes 20 controls
across 16 fresh query processes; the [test report](results/shared-vessel-tests-20260906.xml)
records 53 passing tests. The direct donors are parent-sufficient at this tiny
capability scope. The [evidence manifest](results/shared-vessel-evidence-20260906.json)
binds these records, the independent source review and the hosted pilot manifest.

This is a trusted-host engineering gate for governed donor orchestration.
The parser and arithmetic search perform domain work as disclosed operators.
The source-bound checker fixture does not establish isolation from arbitrary
Python operators, constitutional immutability, minimality, or external-action
permission. Domain priors include the supplied transitive semantic template,
lexical/construction lessons, arithmetic primitives, search algorithms and checks.

Wall/CPU/storage observations are separate from existing logical cost proxies.
Global navigation, hashing and persistence remain. There is no sparse-cognition,
compression-utility, continued-acquisition-after-restart, or efficiency claim.
The current language object aggregates all six lexical supports, so it does not
establish locality within the language domain. Teaching precedes the probes;
there is no before/after acquisition contrast. A tiny finite grammar is
insufficient for meaningful LLM comparability.

`results/hosted-comparator-20260906/` preserves a separate two-request GPT-5.5/high
file-memory/tool development pilot. It includes prompts, schemas, public tool,
responses, memory, raw events, corrections and a hash manifest. Its tasks, tool
and process envelope differ from this OCM run: do not compute a head-to-head
quality or speed ratio. It demonstrates a usable strong hosted reference route;
it is not a protected or matched comparison. The provider backend snapshot and
pretraining/energy costs are unavailable.

Detailed hypotheses, strongest parents, protected splits, falsifiers and the
paper claim/figure decisions live in the owner issues, not a second local roadmap.
