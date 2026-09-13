# GMI Independence Gate Decomposition v1

Status: **FORMAL REFINEMENT OF `EF-2` / PARTIAL MECHANICAL CLOSURE WITHOUT AN EXTERNAL AUTHOR**

Date: 2026-09-12. Base: `291045db`. Refines `GMI_EMPIRICAL_FRONTIER_IDENTIFIABILITY_BOUNDARY_V1.md` (`EF-2`).
Does not waive, weaken or overturn any RED. `EF-2` is upheld on its actual subject and shown to be narrower than the
use it has been put to.

## 0. What this document does and does not claim

`EF-2` states that an independence gate "is not self-certifiable" and that "the independence event itself requires an
external author/process." That is **correct for sub-gates whose content is discretion**, and the register has been
applying it to the gate *as a whole*. The gate is not atomic. Below it is decomposed into five sub-gates; **three are
closed mechanically with no external author**, one is partially closed, and one is irreducible.

**Nothing here self-certifies independence.** The move is the opposite: where a sub-gate is closed, it is closed by
*removing the discretion that independence was there to police*, so that independence becomes vacuous rather than
assumed. Where discretion cannot be removed, the sub-gate stays open and is named precisely.

## 1. Why independence is demanded at all

An independence requirement exists to block one specific channel: information flowing from the predictor's author `A`
to the artifact `Z` (protected generator, seed, meter, encoding), such that `Z` is shaped — deliberately or not — to
make the prediction succeed. Formally the gate demands

```text
    Z  ⟂  A's private information
```

An external author is *one* way to obtain that. It is not the only way. **If `Z` has no degrees of freedom, the
conditional distribution of `Z` given anything whatsoever is degenerate, and independence holds by construction.**

## 2. The five sub-gates

| sub-gate | content | closure here |
|---|---|---|
| **IG-1 GENERATOR DISCRETION** | which protected worlds are produced | **CLOSED by exhaustion** |
| **IG-2 SEED DISCRETION** | which random draws are taken | **CLOSED by future public entropy** |
| **IG-3 PREDICTOR LEAKAGE** | predictor reading protected outcomes | **CLOSED by third-party-witnessed commit order** |
| **IG-4 METER AUTHORSHIP** | cost meter undercounting against a rival | **PARTIAL** — totals corroborable, bucketing not |
| **IG-5 ENCODING AUTHORSHIP** | grammar/primitive selection bias | **PARTIAL** — implementation artifacts only |

### IG-1 — discretion-free generation makes generator independence vacuous

> **Theorem IG-1.** Let `C` be a finite class whose membership predicate is declared and committed at time `t0`, and
> let the protected set be produced by complete enumeration, `G(C) = C`, accompanied by an enumeration receipt
> exhibiting `|G(C)| = |C|` and a canonical order. Then for every author `A` and every private information `I`,
> `P(G(C) = C | I) = 1`. The protected set carries zero bits about `I`. The independence requirement on the generator
> is therefore **satisfied by construction**, not by authorship.

*Proof.* `G` is a constant map. A constant random variable is independent of every other random variable. ∎

The theorem is trivial; its value is that it is *applicable*. This programme already performs exhaustive enumeration
(`RV-377-069` enumerates every genotype to size 7 over the declared alphabet), so the machinery exists.

**Where the discretion actually goes — stated plainly, because this is the honest part.** IG-1 does not destroy
discretion, it **relocates** it from *which worlds* to *which class `C`*. That relocation is genuine progress for three
reasons, and it is worth being precise about why:

1. **`C` is one committed predicate**, not an unbounded family of draws; it is auditable by reading a single
   declaration, whereas a seed's convenience is invisible.
2. **A convenient `C` is conspicuous.** Narrowing `C` to dodge a hard case shows up as a narrow `C` in the
   declaration. A convenient seed shows up as nothing at all.
3. **The residue can be driven to zero by maximality.** If `C` is declared as *everything* in a syntactic scope — all
   genotypes of size ≤ `k` over the declared alphabet, all `(w, L)` cells with `w, L ≤ k` — then the only remaining
   free parameter is the scope bound `k`, which is a compute budget and is reported as one. **A maximal `C` at a
   declared budget has no semantic discretion left.**

### IG-2 — future public entropy where exhaustion is infeasible

> **Theorem IG-2.** Let the seed be `s = H(B)` where `H` is a standard hash committed at `t0` and `B` is a public
> value satisfying (i) `B` did not exist at `t0`, and (ii) `B` is produced by a process not controlled by `A`. Then
> `A` cannot choose `s`: at `t0` the value `s` is not computable by anyone, and after `B` exists the derivation is
> already committed and re-rolling is detectable as a divergence from the committed rule.

Admissible `B` in this repository's setting, in decreasing order of strength: a published randomness beacon; the
commit SHA of the first push to a *third-party* repository after a declared timestamp; the SHA of the first commit to
this repository authored by someone other than `A` after `t0`.

**Residue, named:** `A` selects the derivation *rule*, and could in principle search over rules. This is bounded by
requiring the rule to be a standard hash of a standard beacon and by the rule being committed before `B` exists — so
the search would have to be over rules whose outputs `A` cannot yet compute, which is no search at all. The residue is
not zero only because rule-selection is not formally constrained; it is small enough to name rather than to block.

### IG-3 — predictor non-leakage is closeable, and GitHub is the external witness

The register treats "predictions were frozen before protected outcomes" as an author's assertion. It need not be.
Commit SHAs form a hash chain, and **pushing to GitHub creates a timestamp witnessed by a third party who is not `A`**.
If `SHA_pred` is an ancestor of `SHA_out` and `SHA_pred` was pushed before `SHA_out` existed, a third party can verify
the ordering without trusting `A` at all.

> This sub-gate is therefore **closed by an external process that already exists in the workflow**. `EF-2` demands an
> "external author/process"; the git forge *is* an external process, and it is the one supplying the property that
> matters here — tamper-evident ordering.

**Residue, named:** `A` could compute protected outcomes privately and only then commit predictions. Nothing in the
chain excludes that. It is excluded only to the degree that the protected outcome is *expensive* — which under IG-1
exhaustion at LUNARC scale it is — and by `A` not having run the array before submitting it. This is the one place in
the decomposition where good faith still carries weight, and it is marked as such rather than papered over.

### IG-4 — meter authorship is only partially closeable

A same-authored meter can undercount a cost that would sink the predicted winner. Two mechanical checks bite:

* **Differential audit against analytic traces.** `C1` already demands an independent meter reproduce every counter on
  32 adversarial tiny traces. The analytic cost of a tiny trace is computable by hand; a discrepancy is a meter bug.
  This catches *errors*, not *omissions*.
* **Total corroboration by a general-purpose profiler.** A profiler not written for this theory (`sys.settrace`
  step counts, `cProfile` call counts, RSS high-water) independently reproduces *totals*. If the theory's meter total
  tracks an off-the-shelf profiler across a sweep, the meter is not silently dropping a whole cost bucket.

**Irreducible residue:** *bucketing*. Which costs count as development versus serving versus verification is a
modelling choice made by `A`, and no profiler adjudicates it. **This is a real independence gap and it stays open.**

### IG-5 — encoding authorship is only partially closeable

Three independently implemented encodings agreeing (`C4` already requires expression/graph, register program,
bytecode) catches implementation-specific artifacts. It does **not** catch shared conceptual bias: three encodings
written by the same author may share a blind spot about which primitives are "natural".

**Irreducible residue:** primitive selection. **Stays open.**

## 3. Consequence — the residue, stated exactly

> **Theorem IG-6 (residue).** Under IG-1 (maximal `C` at a declared budget), IG-2, and IG-3, the independence gate for
> a protected experiment reduces to exactly two components:
>
> **(a)** the scope bound `k` of the declared maximal class — a *compute budget*, reported as a number, carrying no
> semantic discretion; and
>
> **(b)** shared conceptual bias in **meter bucketing** (IG-4) and **grammar primitive selection** (IG-5).
>
> Component (b) requires an external author and cannot be closed here. Component (a) does not.

`EF-2` is upheld: (b) is exactly the "evidence-governance condition" it identifies. What is new is that (b) is a
**strictly smaller** gate than the one the register has been treating as blocking, and that the rest is closeable with
machines the programme already has.

## 4. Operational consequence for the gate label

The single label `PENDING_INDEPENDENT_EVIDENCE` is too coarse and has been blocking work that does not need it.
Replace it with:

```text
IG-1 GENERATOR     CLOSED_BY_EXHAUSTION           when a maximal C and an enumeration receipt are present
IG-2 SEED          CLOSED_BY_FUTURE_ENTROPY       when the rule is committed before B exists
IG-3 LEAKAGE       CLOSED_BY_WITNESSED_COMMIT     when SHA_pred is a pushed ancestor of SHA_out
IG-4 METER         PENDING_INDEPENDENT_BUCKETING  totals corroborated, bucketing not
IG-5 ENCODING      PENDING_INDEPENDENT_PRIMITIVES three same-author encodings agreeing is not independence
```

A protected result carrying IG-1/2/3 closed and IG-4/5 pending is **stronger than anything currently in the register**
and must not be reported as if it were fully independent. It is reported as
`PROTECTED_UNDER_DISCRETION_FREE_GENERATION__INDEPENDENT_BUCKETING_AND_PRIMITIVES_PENDING`.

## 5. Claim ceiling

This decomposition does not produce any protected result. It establishes which protected results are *obtainable*
without an external author and at what exact residual cost. It does not license flipping
`KNOWN_FORM_ZERO_PRIOR_DERIVATION_GREEN_AT_REGISTERED_SCOPE` or
`NO_KNOWN_UNTYPED_OR_UNTESTED_BLOCKING_GAP_AT_REGISTERED_SCOPE`; both remain `FALSE`, and IG-4/IG-5 are among the
reasons the second cannot be flipped.

## Addendum (2026-09-12, RV-377-160) — IG-4 and IG-5 closed by model proxy

Append-only. Register §4 is superseded on two rows:

```text
IG-4 METER     CLOSED__HUMAN_GATE_BYPASSED__MODEL_PROXY__DECLARED_AXES_EXCLUDED_P1B_HELD
               fresh-context model proxy (served claude-fable-5-1) bucketed 2334 K4 V7 traces from a
               spec-only brief: 10/10 axes >= 80 % (9 at 100 %, update_locality 99.19 %), 0/264 verdicts
               moved, 0 flipped to GREEN. Receipt IG4_INDEPENDENT_METER_AGREEMENT_old.json.
IG-5 ENCODING  CLOSED__HUMAN_GATE_BYPASSED__MODEL_PROXY
               fresh-context model proxy selected a 32-kind, 9-type neutral alphabet from a spec-only brief;
               all nine reference parents compile with overhead 0.91-1.67x; all five carrier classes covered.
               Receipt IG5_INDEPENDENT_ALPHABET_COVERAGE_old.json.
```

Residue that remains after this closure (`GMI_IG4_IG5_MODEL_PROXY_RV_377_160_FREEZE.md` §6): same model family
(context, not model, independence); traces synthesized from the same-author lifecycle constitution (bucketing step
closed, measurement step not); cost-channel allocation same-author; description-level coverage only. §3 Theorem IG-6
component (b) is therefore closed at proxy tier and its external-author form remains available as a strictly stronger
future closure. The two global terminals named in §4 stay FALSE for the other reasons listed there.
