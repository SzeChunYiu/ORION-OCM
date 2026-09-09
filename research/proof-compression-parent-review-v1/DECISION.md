# Donor decision and next qualification

Adopt the established compression mechanism and wrap its input/output boundary.
The first implementation should reuse pinned `terms_dagsav/4`, or the closely related
`term_dag_compression/3` when explicit proof parameters must be propagated. Keep an
unchanged donor process as the reference; a Python port is an adaptation needing parity,
not a new algorithm. [CD Tools](http://cs.christophwernhard.com/cdtools/)

## What the papers establish for this decision

The 2026 pipeline deduplicates generated proof terms, shares repeated subterms, ranks
factors by save-value then formula size/height, and removes redundant MGTs. PSP omits
some proof terms. Its 13 highlighted lemma settings were selected from 100 test runs;
they do not supply our frozen held-out result. App. A preserves the correspondence
between proof parameters and ordered clause-body positions during implication-form
conversion. These are strong reusable parents, with their original scope retained.
[Wernhard 2026, §§4–6 and App. A](https://arxiv.org/html/2602.15511v2)

The 2025 framework already treats a library as grammar-compressed proof terms and
provides parameterized TreeRePair, nonlinear compression and MGT-based reduction.
A nonlinear grammar's MGT can be more restricted or undefined even when the expanded
term has an MGT. Exact expansion preservation alone therefore does not license an
arbitrary generalized theorem. [Wernhard–Zombori 2025, §§2–5](https://arxiv.org/html/2505.12305v1)

## Reuse boundaries

The [source map](SOURCE-MAP.md) identifies actual entry points. Reuse the pure
compression modules with an explicitly registered input forest. Do not consult
`thgen_dagsav.pl` unchanged: its load directives import generated POI data, and its
launcher reads historical SGCD run files. Those are external acquisition data, not
permitted implicit OCM training inputs.

For the first adapter preserve ordered typed proof ports, leaf/ordinary assertion
identity, formula-variable identity, native syntax witnesses and origin dependency
closure. Structural sharing must never combine evidence or authority merely because
terms match. Preserve an exact reconstruction map and immutable preimage before
Prolog's unification/numbering operations mutate term variables.

Ordinary open proof cuts require an explicit essential-parameter context. The small
`factorized_ds_mgts/4` expects a representation expanding to ground D-terms; it is not
the generic typed open-cut checker. The parameterized grammar/Horn-MGT interfaces
are closer donors. Keep inferred MGT and admitted native statement separate.

CD Tools already contains syntax/DV completion, but its documentation marks inference
of additional variables/DV for new-theorem insertion as unfinished. Its native wrapper
replaces an existing labelled theorem. Reuse those algorithms where suitable while
retaining OCM's issued fresh claim, exact trusted prefix, typed substitutions, every
applied rule's DV constraints and current evidence/authorization checks. This review
has not established that the donor accepts our current restricted frames.

## Smallest separate qualification

1. Freeze one authored native proof forest plus its permitted ordinary library and
   dependency closure; published examples are development-only. Qualify extraction
   and exact re-expansion against the unchanged donor, using repeated ordered ports,
   an alias case and a finite acyclic input. Reject malformed/cyclic inputs explicitly.
2. Compile one mechanically obtained supported cut to an ordinary derived `$p` with
   explicit essential/floating context, and independently check the exact new claim.
   Include wrong-port and wrong-type/scope controls. A pure data control cannot stand
   in for native acceptance. An existing ordinary alias is a valid interface witness,
   with acquisition eligibility still empty.
3. If a port/adaptation is necessary, compare all candidates, expansions, stated score
   units and deterministic ties to the pinned donor on the same input. Do not require
   byte-identical internal variable names; require a reversible bijection and exact
   native output binding. Preserve every discrepancy and refusal.

Only after that interface works should an opportunity audit open registered training
records. Keep the full demonstrated-theorem parent, the same proper cuts admitted as
ordinary lemmas, and any OCM-specific retention/revision treatment equally equipped.
Freeze family/chronological exclusions before evaluation; exclude the target's own
assertion and prohibited derived shortcuts. Imported theorem reuse is not acquired-cut
benefit. Do not replace an all-alias result with a hand-injected nonalias candidate.

## Cost and policy choices

Keep the donor's representation cost separate from abstract rule-tree actions, shared
DAG nodes and fully emitted native proof labels. `dagsav_cd` uses edge size; on binary
D-terms this rescales the paper's inner-node score by two, but that equivalence fails
for arbitrary-arity native applications. A changed scoring unit is an explicit adapter
choice. Compression gain proposes a candidate; future solving benefit warrants retention.

Charge conversion, donor/runtime startup, full input pass, compilation, sorting,
subsumption, native checking, storage and later use/revision. Reference occurrences
in a grammar are not independent support episodes. A finite search that stops under
PSP, trimming or a resource bound has not proved semantic non-existence.

Prefer the fixed symbolic save-value path initially. The separate 2023 repository's
`model.py` imports PyTorch and GCN code even for its linear class; do not import it.
An eventual explicit non-neural selection policy needs its own implementation contract,
matched comparison and dependency qualification. No neural component is adopted here.

Readiness is **source available, adapter and execution qualification pending**. No
current OCM opportunity count, generalization, native success, speedup or novelty follows
from this review. Neither the full dependency closure nor a runnable donor installation
was qualified. No additional miner or grammar expansion is justified before this test.
