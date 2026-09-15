# GMI terminology crosswalk — foundations v1

| term in #833 / legacy work | exact meaning in this tranche | boundary / non-equivalence |
|---|---|---|
| behavioral specification | extensional map `A* -> O*` induced by a deterministic state | not an implementation object and not an evidence checklist |
| obligation | claim-governance tuple with premises, inference, evidence, falsifier, dependencies, status | not synonymous with behavior |
| state | an element of an abstract carrier `S` | does not imply vector, graph node, memory slot, latent, or neural activation |
| future-behavior equivalence | equality of emitted output traces for every finite action suffix | deterministic exact equality only in v1 |
| minimal sufficient state | quotient class under future-behavior equivalence, minimal among exact deterministic abstractions | not statistical sufficiency under stochastic sampling |
| Myhill–Nerode | right-language indistinguishability for DFA prefixes/states | recovered as a deterministic accept/reject specialization; not claimed as novel |
| bisimulation | stepwise matching relation | coincides with exact behavior in deterministic total transition/output systems; diverges from plain trace equivalence under nondeterminism |
| predictive state | state represented by predictions of future tests/observations | PSR/computational-mechanics extensions are literature parents, not proved stochastic equivalence here |
| architecture-prior-free | no preselected named architecture family, with invariance to architecture relabeling and a complete residual-prior ledger | explicitly **not** prior-free or assumption-free |
| prior | non-evidential basis that constrains representation, architecture/operator, search, ecology, or evaluation | a disclosed prior may be justified; disclosure is not disproof |
| proof | analytic derivation from stated premises | finite enumeration is a reconstruction/hostile check, not a universal proof |
| finite check | exhaustive or sampled computation on an explicitly bounded surface | cannot by itself establish an unbounded universal claim |
| closure | evidence target for the declared scope has been met | not ontological completeness and not permission to close stronger descendants |
| Pareto/resource result | imported strongest-parent result #805 | not reproved or newly claimed here |
| uncertainty composition | imported strongest-parent result #765 | not reproved or newly claimed here |
| theorem typing | imported strongest-parent result #797 | not reproved or newly claimed here |
