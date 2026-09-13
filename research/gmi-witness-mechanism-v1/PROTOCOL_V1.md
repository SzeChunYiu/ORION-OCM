# Fixed witness mechanism ablation V1

Status at registration: all graphs constructed; zero ecology calls.
Purpose: determine whether the recovered S1 DENSE-labelled witness requires
numeric dense coefficients, and test the implicated constant-key consumer.
This is a retrospective intervention on one recovered graph. It makes no
prospective prediction, search-distribution or population-frontier claim.

The matched parent is the untouched recovered, pruned historical graph and
the exact source at 5378c2b7f91f8fbc567764a2ee0c5ff6e256e814. Source semantics
are the primary mechanism reference, supplied in the companion recovery
archive: vm.py:94–126,153–223,285–304,367–405; core.py:170–187;
morph.py:89–109. No new architecture or general discovery claim is proposed.

CANDIDATES_V1.json is copied byte-for-byte from the prepared witness packet.
Arm order is original, zero_vector, variable_key. Original is the exact
14-node pruned graph. Zero replaces dense0 by INPUT(width1), NONLIN(fn1=NEG),
NONLIN(fn0=ReLU), redirecting its two outgoing edges to the last node.
Variable has exactly the same graph as zero except the last fn is 1=NEG.
Both replacements have 16 nodes. No other graph changes are permitted.

The dense output consists of parameter-name strings. Its only consumers are
EVIDENCE port0 and INSERT insert1 port1. EVIDENCE's forward operation emits
its store identifier; feedback populates that store from actual input and
target, not either incoming graph port. INSERT maps each vector element to
the bit getattr(v,"v",0)>0. Thus the dense strings produce key (0,) regardless
of the numeric dense cell value. The graph has no GRAD, LINEAR or AFFINE.
The admitted INPUT emits bits as values 0 or16. Negation then ReLU yields a
one-element zero vector; double negation instead yields the first input bit.
The latter is a varying-key control, not a guarantee that answers change.

Observational claim to test: identical complete served traces under the
11 declared contexts. Source analysis must examine actual consumers and
update order before any wider event-sequence claim. Full representation,
internal tape, raw state and resource equivalence are not presumed.
In particular changed program length, removed cell and new arithmetic cost
are measured; no cost-superiority claim follows from removing DENSE.

Run exactly 33 direct ecology evaluations, with fresh native VM state for
each: six historical interventions on E_smooth3 and five standard probes
E_smooth1,E_smooth3,E_sym3,E_sym5,E_wit1 for each graph. Historical intervention
order is standard,no_revoke,double_revoke,half_events,shuffled_events,
extra_unseen_feedback. B0_LOCAL_ADAPTIVE_TRANSDUCERS, seed0, original spec
and native protocol are unchanged. The historical last control provides
four unseen feedback examples; this six-control scope is not the current
seven-control bar. No search, pruning, tuning, replacement or retries.

Use the available recorded interpreter path, currently CPython3.11.14.
The historical patch/binary identity was not retained; this is a new
source-bound ablation, not proof of exact historical runtime identity.
REGISTRATION_V1.json binds code, candidates, this protocol, source archive,
source bindings, recovered witness and prior independent verification.

A passive subclass delegates every original update and preserves its return
value. It copies the effective INSERT key, vector element types and stores
after each insert. Native outputs remain untouched. At completion retain
final cells/stores/VM state, order, writes and operation counts. This adds
observation/serialization overhead only; it does not consume RNG or alter
the original primitive operations. The clean original response, including
ledger, must equal the prior independent original response in all contexts.

Each result retains full native traces, capability and measured lifecycle.
An error is a failed evaluation and is preserved; remaining registered calls
still run. Per-arm checks require minimum capability >=0.85, margin >=1
using frozen best constant0.8125 and FX_UNIT1/24, and at least three distinct
error-free final probe vectors. No DENSE carrier requirement is imposed on
the ablations. That is the mechanism being removed, not an outcome gate.

If zero preserves behavior and passes the historical bar, numeric DENSE
coefficients are unnecessary for this witness at that scope. If varying key
changes traces, the intervention identifies an effect of this changed key
channel within this graph. If it also matches, inspect channel use before
claiming causal necessity. If zero fails, identify the first divergence and
its stage without changing registered candidates or suppressing the result.

Costs: exactly 33 new ecology calls; zero search/calibration/atrophy calls.
Prior source acquisition and witness recovery are reused, explicitly
external costs from the companion packet, not charged a second time.
Per-call timers include passive capture; total function timers include
validation, extraction, comparisons and partial serialization, excluding
process startup and final receipt writing. An external /usr/bin/time record
covers process startup and final writing. Preparation, review and custody
copy costs remain outside those process measurements. This is a measured
software ledger and elapsed time, not a complete physical cost vector.

Run once with -I -B. A --preflight run validates all bindings, source imports,
typechecking and original identity with zero ecology calls. Results are
always retained regardless of whether the mechanism hypothesis succeeds.
