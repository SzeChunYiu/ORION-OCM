# PR551 current GRAD diagnosis correction — GRC-1–6

Snapshot: `7328d5b3b0a5111fd43c3e277679faf0edeee1bb`, after
`320bfb64bc7e3187470c641d07f869464258aec1` (two probes) and
`712552096634331d294fda933a89557094ca037b` (freeze appendix).
The baseline is `2d23c5834d1eff8555761273a5952c9f35191688`.
This corrects interpretation of new unmerged claims; it preserves the accepted
B6 consumer census, all historical measurements and both original probe scripts.
[Exact archived source](SOURCE_BINDINGS_V1.json) binds18 files at this snapshot.

All paths below are relative to `research/machine-intelligence-morphogenesis-v1/`.
The new claims are in `GMI_B6_DEVELOPMENTAL_MORPHOGENESIS_RV_377_180_FREEZE.md`
lines778–820 and `GMI_LEARNER_ADMISSIBILITY_MAP_V1.md`.
Mature parent: reverse accumulation follows the backward dependency graph,
then updates parameter state; see [Baydin et al., JMLR2018](https://jmlr.org/papers/volume18/17-468/17-468.pdf),
§3.2/Fig.1. This is a mechanism reference, not certification that this
fixed-point VM implements every derivative correctly or a new learning method.

## GRC-1 — CORRECTED: no outgoing GRAD edge does not mean no effect

The probe's predicate is literally `any(a in gid for a,b,pt in edges)`.
It inspects the forward return channel, whereas native GRAD acts through state.

- `gmi_microscope/vm.py:82–90,153–158`: forward nodes run first; all update
  nodes run afterward during feedback and are skipped during queries.
- `vm.py:287–296`: ports0/1/2 supply parameter-cell names, taped prediction
  and target. With valid values it computes an adjoint, writes named cells
  when its recorded gradient is nonzero, and returns `None`.
- `vm.py:140–151,167–185,344–375`: LINEAR/AFFINE read those cells; feedback
  builds the local tape. A later query can therefore change with no outgoing
  GRAD edge. Invalid ports, zero recorded gradient, rounding and clipping can
  still prevent a change; structural presence does not prove activity.

The existing `zoo.gradient_net` has no edge sourced from either GRAD node10/11.
Its architecture already refutes the claimed outgoing-edge necessity.
The nominal VEC return type in `morph.KINDS` is not an operational vector:
the runtime branch returns `None`.

The registered [one-input native control](CONTROL_PROTOCOL_V1.md), executed once,
uses DENSE(width1), INPUT(width1), LINEAR, OUTPUT, TARGET and GRAD(lr1), with
no GRAD output edges. Seed0; query1, feedback target0, query1. The dense cell
and answer both change fixed-point8→7. [Complete raw output](GRAD_SIDE_EFFECT_CONTROL_V1.json)
retains the graph, source/binary identities, schedule, cell/store states and
ledger snapshots. Charges are desc12, exec6 for both queries, upd13, ver/rev0
in the authored B0 ledger. This is not an ecology, capability or physical-cost run.

## GRC-2 — CORRECTED: the sampled denominator and search process

`b6_grad_probe.py:21–52` advances an unselected random walk, restarting every
50 iterations. It evaluates only the first60 GRAD-bearing visits, not all417
reported visits. The prose “every one a valid phenotype with all three ports”
is therefore unsupported for417. The static generator's typecheck also permits
unbound ports; validity does not imply all three semantic GRAD inputs exist.

This is the same mutation operator, not the full `b1.search` proposal law:
B1 chooses an archive parent, uses20% crossover, canonical-deduplicates scored
placements and keeps descriptor elites. The probe sets `g=child` regardless
of capability and can count unchanged/repeated genotypes. Its417/4000 is a
claimed visit-presence fraction for this probe, not a campaign introduction
rate, a unique-genotype count or an independent population estimate.
Size uses node-count buckets; adding GRAD may cross a bucket. Drift may also
change through its writes. “Same archive cell as parent” is not automatic.

## GRC-3 — CORRECTED: the hand-wiring probe is not a rescue test

`b6_grad_wired_probe.py:36–50` inserts a GRAD→VEC edge but native GRAD supplies
no value through that edge. Forward consumers run before update nodes, so this
can replace a valid input with missing data. It does not enable the state
update channel identified above. Failure is not evidence against the family.

Its two summary distributions are not a matched comparison: `dangling_caps`
includes every valid GRAD-bearing visit before filtering; `wired_caps`
includes only up to120 successful modified evaluations. It neither retains
per-pair effects nor summarizes exactly the corresponding unchanged120 graphs.
The wiring choice consumes the same RNG as later mutations, so even its
original-graph sequence diverges from the first probe after the first choice.
The source docstring's “negative is about the family itself” is withdrawn.

## GRC-4 — Retained records, missing new execution custody

The exact baseline→snapshot diff adds only two probe scripts and the
admissibility-map document and modifies the freeze appendix: no new raw result
file, sampled genotype set, complete capability table, command or runtime
binding is introduced by those three commits. Both probe scripts print
aggregates and retain no genotype/output/ledger packet. The claimed417/4000,
0/60 and120-graph statistics are thus not independently verified by this audit.
No generator, ecology or capability experiment was rerun.

The explicitly cited older
`microscopes/results/STAGE_NN_NONNN_PACKET_RV_377_210_old.json` is preserved.
It covers E_cr4/E_sym5/E_wit1 under the six-member V2 intervention family,
not the new six-ecology V1 table. Its registered E_wit1 h3/lr1 row has V2
minimum0.8542 and margin3.502, versus the new V1 table's0.8646/3.751.
The E_sym5 h3/lr2 row has minimum0.8333 and is belowθ. These retained
configuration-specific records remain evidence at their declared family;
they do not authenticate an independent new run or the other four map rows.
V1 extra-feedback leaks scoring inputs, and historical E_parity is the
identity0..15 target; both are disclosed in the pinned `ecology.py`.

## GRC-5 — CORRECTED: a finite registry failure is not a causal diagnosis

Even if the new table is accurate, four authored configurations failing does
not choose capability over grammar/search as the cause of failure to discover
an arbitrary coefficient learner. It cannot explain the entire43-run corpus,
and four configurations are not a complete family. Retain only the stated
configuration/target/intervention observations; withhold the causal ranking.

The proposed “no room above the constant” mechanism is not established:
the largest displayed baseline0.875 leaves0.125 capability to1, i.e.3 units
under the declared `FX_UNIT=1/24`, exceeding the1-unit margin requirement.
The map's “everywhere within±0.4” also conflicts with its E_sym5 margin+0.998.
The two inequalities are simply `cap>=θ` and `cap>=baseline+1/24`;
their failure does not identify why an optimizer failed.
Rounded summaries must not be silently promoted to exact margins.

## GRC-6 — Confirmed local adjoint defect, not a campaign claim

`vm.py:145–148` places `("param",name)` on the multiplication result `pv`.
`_backprop:357–359` then accumulates `pv.grad` as the parameter gradient,
while the factor `xv.v` is applied only to the separate weight Val.
For a one-weight product at input0, output is identically0 for every weight.
With target16, the authored tape nonetheless assigns parameter adjoint−16:
the parameter marker bypasses the zero input multiplier.

The separately predeclared [zero-input control](ZERO_INPUT_ADJOINT_PROTOCOL_V1.md)
confirmed exactly this behavior in one native feedback call: adjoint−16,
dense8→9, query0→0, despite exact zero parameter sensitivity.
[Full raw output](ZERO_INPUT_ADJOINT_CONTROL_V1.json) preserves the reachable
Val tape before/after the original adjoint call and the Machine tape, cells,
outputs and ledger. Its passive observer makes no Machine operation or RNG
call and returns the original adjoint unchanged. Charges again are desc12,
exec6 and upd13 in B0. The earlier x1/target0 control is the nonzero-input
no-alarm; neither record is an ecology, capability or numerical-optimization run.

Smallest prospective semantic repair: attach the marker to the weight Val
before traversing its product edge, and remove it from `pv`. Validate zero/
unit/nonunit inputs, repeated weights and bias paths against an independent
declared chain-rule oracle. Any such change needs a versioned VM/receipt;
historical learner scores cannot be overwritten or inferred for that repair.
The accepted no-outgoing-edge countercontrol does not certify this adjoint.

## Disposition

The output-edge inactivity mechanism,417-valid generalization, paired-wiring
interpretation and capability-not-search causal conclusion are CORRECTED.
New probe counts remain unverified retrospective claims pending source-bound
raw custody. The older explicit V2 positive row is retained at its own scope.
A sound next diagnostic records valid parameter names, tape-to-cell adjoints,
actual writes, and subsequent response effects on the same saved graphs.
It must distinguish each stage and include the existing zero-output-edge zoo
parent as a no-alarm control; it cannot start with the rejected edge predicate.
