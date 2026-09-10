# Clause to module binding — reuse audit for EB-F0

Companion to `PARENT_LEDGER.md`. That file records the **literature** parents
(Price, Moran, Pearl, Maynard Smith & Szathmáry, the HST rows). This file
records the **in-repo machinery** parents: which existing module already
implements each contract clause, and where a module is close but not
sufficient.

Rule, from the operator's reuse-first directive: never reimplement mature
machinery. Audit first, self-build only the project-specific residual. Where a
module is close but not sufficient, say exactly what is missing rather than
forking it.

Every module below was read at signature level before being bound. None was
copied, and none was forked.

## Binding table

| # | clause | module | provides | sufficiency |
|---|---|---|---|---|
| §1 | `C` immutability | `oracle/c_immutability.py` | `constitution_snapshot`, `genome_touches_c`, `check_c_immutable`, `selftest` asserting both directions | SUFFICIENT_MECHANISM, needs C-registry adapter — gap **G1** |
| §2 | kernel factorization | *none* | — | SELF_BUILT: `WORLD_STATE_AND_DYNAMICS_V1` + `AMEND_1` |
| §3 | assay noninterference | *none* | — | SELF_BUILT: `check_noninterference.py`, gap **G2** on run binding |
| §4 | cross-ecotype transport | `oracle/d26_adapters.py`, `oracle/d26_operators.py` | per-domain adapters behind four abstract drivers; `run_operator`/`run_d26` transfer matrix; `sem_equal_exact` returning `(equal, status)` so CANNOT_CHECK survives the call | SUFFICIENT_PATTERN — gap **G3** |
| §5 | behavioural coarse-graining | `oracle/behaviour_sig.py` | `behaviour_signature` dedups on BEHAVIOUR not genotype nor structure; `SigCost` reports yield and price separately | SUFFICIENT_MECHANISM — gap **G4** |
| §5/§10 | Pareto over incomparable levels | `oracle/objectives4.py` | `dominates_k` with per-objective sense, `pareto_front_k`, `partition_checkable` keeping CANNOT_CHECK structurally distinct from checked-and-fine | **SUFFICIENT** |
| §7 | evolvability `Ev`, `τ_U` | `oracle/evolvability.py` | `evolvability(...)` with provenance and charged measurement, `governed_step` comparing like with like, `shuffle_null` equal-n null, `redundancy_check`, `cap_bin` | SUFFICIENT_MECHANISM — gap **G5** |
| §7/§9 | frozen future tasks `U_t` | `oracle/future_family.py` | `mint_key(role)`, `keys_record`, `assert_disjoint_from_t3` | SUFFICIENT_MECHANISM — gap **G6** |
| §9 | burden vector `B_*` | `oracle/burden.py` | `B_own` decomposition, `lambda_bytes` byte rent, `RejectLedger` that only ever grows, `b_full` | SUFFICIENT — gap **G7** |
| §9 | CONTINUED vs RESET bridge | `oracle/d27_lineage.py` | `run_arm`, `_knockout` with guaranteed restore, `knockout_attribution`, `signature_with_controls` requiring the related family to improve **and** the unrelated control not to, `b_future_cognition`, `first_useful_epoch` | SUFFICIENT_MECHANISM — gap **G8** |
| §16 | freeze/amendment chain | `research/hsg-semantic-execution-v1/verify_freeze_chain.py` | newest-amendment resolution, `prior_manifest_sha256_observed` cross-file rule, distinct exit codes | SUFFICIENT_PATTERN — gap **G9** |

## Gaps — what the existing modules cannot cover

**G1 — `c_immutability` is name-membership plus digest, not a dependency graph.**
`genome_touches_c` tests whether a genome *names* a C-owned constant, and
`check_c_immutable` compares a before/after digest. Both are correct for §1.
Neither is an ancestor closure over a write graph, so neither can serve §3. A
digest detects that protected state *changed*; it does not detect that
protected state was *read* by a selection-relevant kernel. Leakage into
selection is a read-path property. Additionally `C_OWNED_NAMES`, `GENOME_FIELDS`
and `constitution_snapshot` are bound to the Form Oracle's own modules
(`evaluation.lifetime`, `evaluation.invariants`, `morphology.schema`); the
biosphere needs its own C-owned name registry wired into the same gate. Reuse
the gate, supply a new registry. Do not fork.

**G2 — the noninterference check is over the DECLARED graph, not the run.**
`check_noninterference.py` proves the declared factorization has no path from
protected names to selection. It cannot prove the declaration matches the
executing simulator. Strongest available claim is
`DECLARED_GRAPH_NONINTERFERENCE`, not `RUN_NONINTERFERENCE`. Binding the graph
to the executing kernels — deriving it from code rather than asserting it
alongside — is EB-F0-X's residual. BIO-T1 already carries the matching
assumptions, "graph complete for protected outputs" and "no hidden side
channel", so the gap is registered rather than hidden.

**G3 — D26 adapters cover three fixed Form Oracle domains.**
`ObsAdapter`, `AbsAdapter` and `AlgAdapter` serve observation, systems-block
abstraction and algebra. An ecotype adapter for evolved biosphere organisms
does not exist. The four abstract drivers and the `(equal, status)` return
convention transfer unchanged; only the adapter is new.

**G4 — `behaviour_signature` is per-form, not per-macrostate.**
The signature is over one form's `(ev, gates, descriptors)`. §5 needs a
signature over a `φ_L` macrostate so that two groups solving the same problem
differently are one behaviour. The quantisation and canonical-JSON discipline
transfer; the payload does not.

**G5 — `Ev` is per-genome, not per-population-measure.**
`evolvability(genome, ...)` computes descendant mass on `U` for one genome.
§7 also needs `Ev` over `μ_t` and `τ_U` as a hitting time in the biosphere
kernel rather than in the Form Oracle's governed-step process. `shuffle_null`
and `redundancy_check` transfer unchanged and should be reused verbatim, since
"is evolvability just capability wearing another name" is exactly the falsifier
§7 needs.

**G6 — held-out disjointness is anchored to the Form Oracle's T3.**
`assert_disjoint_from_t3` asserts disjointness against one specific battery. A
biosphere target `T` needs its own disjointness anchor. `mint_key` and
`keys_record` transfer unchanged.

**G7 — the burden vector is missing two buckets.**
`burden.py` covers `B_acquire`, `B_exec`, `B_verify`, `B_revise`, `B_self` and
byte rent. §9's vector also names `maintenance` and `human_external_input`.
Neither has a bucket. `RejectLedger`'s non-netting discipline is the right
carrier for both and should be extended rather than replaced.

**G8 — knockout is over inherited store fields, not channels.**
`_knockout(fields, snapshots)` wipes named fields of the inheritable store with
a guaranteed restore. §4 needs the same discipline applied to a *channel*:
knocking out `I_h`, `I_o` or `I_pub` while leaving organisms and inheritance
intact. The patch-and-restore pattern transfers; the target does not.

**G9 — the CI freeze verifier is directory-scoped.**
`verify_freeze_chain.py` resolves `DIR` from its own `__file__`, so
`.github/workflows/freeze-chain.yml` checks `research/hsg-semantic-execution-v1/`
only and will not check this directory. The resolution rule, the
`prior_manifest_sha256_observed` cross-file convention and the distinct exit
codes are the pattern to copy. A sibling verifier for this directory is
EB-F0-X's residual, or a follow-up amendment here.

## What this lane may claim

Reuse audit performed before any self-build; nine clauses bound to existing
modules; three clauses self-built as the project-specific residual (kernel
factorization, noninterference check, hostile no-alarm pairing). No module was
forked. Every gap above is a named residual with an owner, not a silent
omission.
