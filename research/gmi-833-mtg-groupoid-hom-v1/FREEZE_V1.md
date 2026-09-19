# FREEZE_V1 — gmi-833-mtg-groupoid-hom-v1

Parent issue: SzeChunYiu/ORION-OCM#833. Programme comment: `5687604615` (headings are `###`).
`source_main`: `f1e150ea89d1e3422d5ab18ec9a61d36ff17c3e5`. Live comment sha256 at fetch: `bb5e9e8bb7b2a8f5e89d499d581ac7c63863a016bee5d371293eb1cf9c8ff5bb` (8570 chars, 61 open rows, 0 checked).
Row texts are pinned byte-exact in `research/gmi-833-mtg-map-v1/MTG_ROWS_V1.json`; the rows quoted below are copied from that file unchanged.
Parent receipts are pinned by path + git blob sha in `PARENT_PINS_V1.json` (sha256 `c30ad1ce5f594b66eac0b85344638f6ea4ef8be0091871987e094eec370bb99d`); prose in this package names parents by alias only.

## Claim ceiling

`GMI_833_MTG_REGISTERED_RELABELING_ACTION_ON_DERIVATION_RECORDS_AND_TYPED_HOM_COMPOSITION_AT_REGISTERED_FINITE_SCOPE`

Forbidden promotions: `UNIVERSAL_GRAMMAR_NEUTRALITY_PROVED`, `SEARCH_PRIOR_INVARIANCE_PROVED`, `REACHABILITY_INVARIANCE_PROVED`, `HOM_SETS_ISOMORPHIC_BEYOND_REGISTERED_RELABELINGS`, `DEVELOPMENTAL_EQUIVALENCE_PROVED`, `COMPLETE_GMI`.

## Rows this package may reconcile

Under the anchor quoted verbatim below:

> ### MTG-1 — Gauge/remint invariance

- [ ] Formalize semantics-preserving grammar/encoding remints as a groupoid/action on derivation records.

Under the anchor quoted verbatim below:

> ### MTG-2 — Transformation category

- [ ] Specify exact composition laws for semantic error, uncertainty, lifecycle resources, intervention contracts, and developmental reachability.
- [ ] Prove morphology-equivalent source/target remints induce isomorphic transform sets at the registered finite scope.

## Frozen objects

A **presentation** is `M=(X,x0,A,lambda,delta,rho)`: finite state set `X`, initial state `x0`, external action alphabet `A`, protected label map `lambda:X->L`, total deterministic transition law `delta:X x A->X`, and an exact nonnegative resource vector `rho in Q^3_{>=0}`. A **derivation record** is `D=(M,obs,hist)` where `obs` is the protected observation table of `M` on the registered input-word set `W` (every word over `A` of length at most 3), and `hist` is a finite sequence of operation tokens from a registered token alphabet `T` recording how `M` was derived.

The **registered relabeling group** is `G = Sym(X) x Sym(T)`. `(r,t)` acts on `D` by transporting every state-indexed component of `M` along `r` (as in parent P03) and renaming every history token along `t`; `obs` and `rho` are recomputed/left unchanged respectively. A **registered conclusion** is any of: the canonical fingerprint of `M`; the recomputed observation table; membership of `D` in the Pareto-minimal subset of a finite population of records; membership of `D`'s quotient class in a forward budget ball of a registered transform graph on quotient classes.

A **typed transform** is `T=(s,t,tau,eps,unc,rho,A,E,I,tier)`: source/target presentations, a total state map `tau:X_s->X_t`, exact semantic-distortion increment `eps>=0`, exact uncertainty interval `unc=[lo,hi]` with `0<=lo<=hi`, resource vector `rho`, assumption map `A`, evidence-kind set `E`, intervention contract `I` (the set of intervention labels the transform preserves), and developmental tier `tier in {STATIC, APPROX, EXACT}` ordered `STATIC < APPROX < EXACT`. Registered composition `U o T` (target of `T` = source of `U`, assumptions consistent): `tau` composes, `eps` adds, `unc` adds endpointwise, `rho` adds coordinatewise, `A` unions, `E` unions, `I` intersects, `tier` is the minimum. A target class registers a **required evidence-kind set**; a composite whose `E` lacks a required kind fails closed with `EVIDENCE_LOSS`.

## Frozen theorem targets

- `GRP-1` — `G` acts on derivation records: identity acts trivially, `(gh).D = g.(h.D)` for every ordered pair, inverses return the record; the action groupoid `G ⋉ Orbit(D)` has associative composition, identities and inverses. Checked exhaustively for `|X|=3`, `|T|=2` (12 group elements, 144 ordered pairs) on every record of the registered fixture population.
- `GRP-2` — every registered conclusion commutes with the action: the fingerprint, the recomputed observation table, Pareto-minimal membership and forward-ball membership are equal on the whole orbit. Recomputation is real: the relabeled presentation is executed again on `W`, so a neutral rename attached to any semantic mutation (label, transition, resource) is detected by an observation or fingerprint change. Null: 200 seeded random maps `X->X` that are not bijections or that carry a semantic mutation must yield `0/200` accepted as valid group elements.
- `GRP-3` (boundary, earned by counterexample) — the first-hit statistic of a fixed enumeration order over the population is **not** invariant under the action; representation invariance and search-order invariance are separated by an exact witness.
- `HOM-1` — the typed composition laws above are stated exactly; identities (`tau=id`, `eps=0`, `unc=[0,0]`, `rho=0`, empty `A`, neutral evidence, full `I`, tier `EXACT`) are two-sided identities and composition is associative on every composable triple of the fixture; the `tier` of a composite equals the tier recomputed from the composite `tau` against the registered update laws (so the minimum rule is not an overclaim).
- `HOM-2` — fail closed: assumption conflict, endpoint mismatch, negative `eps`/resource, malformed interval, missing ordinary evidence, and `EVIDENCE_LOSS` (a composite lacking a required evidence kind) each refuse rather than return a transform; hostiles for every branch, each with an `applicable` flag.
- `HOM-3` — for registered relabelings `r:M->M'`, `s:N->N'` of source and target, conjugation `tau |-> s o tau o r^-1` is a bijection `Hom(M,N) -> Hom(M',N')` that preserves every cost field and the recomputed tier; `Hom(M,N)` is the set of all total label-preserving state maps, enumerated exhaustively (`|X_N|^{|X_M|}` maps) for every ordered pair of fixture presentations and every relabeling pair.

Two materially independent routes: route A (executor) canonicalizes by minimum over state permutations and computes conclusions by direct definitions; route B (oracle, importing nothing from route A) checks equality of every conclusion across the explicitly enumerated orbit with its own interpreter, its own Pareto test, and its own Hom enumeration by index arithmetic.

## Frozen boundary

Nothing here proves invariance under grammar changes that alter description length or search geometry (parent P15 owns the counterexample), invariance of search reachability or cost, developmental equivalence, or Hom-set isomorphism beyond registered relabelings of the finite fixture.

## Order discipline

This freeze is committed **before** any executor, oracle, test, receipt, theorem note or workflow of this package exists. The freeze commit contains only `FREEZE_V1.md` and the pin/row JSON files named above. `git log` over this package must show this file in a commit strictly earlier than every implementation commit; the CI custody step checks that no post-freeze artifact exists at the freeze commit and degrades to a distinct `UNREACHABLE` state if the commit is not in the checkout, never to a pass.

## No neighboring row is earned here.

Only the rows quoted above may be reconciled by this package. Every other row of comment `5687604615`, every row of the #833 body, and every row of the other #833 comments remain untouched by this tranche.
