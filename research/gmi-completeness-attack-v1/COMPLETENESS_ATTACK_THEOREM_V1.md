# GMI Completeness Attack Theorem v1

**Issue**: #602 Section J2 (also supports #592 domain-basis hardening)  
**Burden class**: `E1_CONSTANT_FACTOR`  
**Claim ceiling**: finite obligation catalogue under a frozen native-size vector — **not** ontological completeness of machine intelligence.

## Domain basis under test

| Di | Registered name | Frozen native size |
|----|-----------------|--------------------|
| D1 | coefficient_function_field | parameter_count ≤ 8 |
| D2 | exemplar_memory_indexed | record_count ≤ 8 |
| D3 | probabilistic_belief | support_size ≤ 8 |
| D4 | symbolic_rule_program | symbol_count ≤ 8 |
| D5 | search_deliberative_frontier | frontier_width ≤ 8 |
| D6 | dynamical_state_controller | state_dimension ≤ 8 |
| D7 | collective_distributed_population | component_count ≤ 8 |
| D8 | morphogenetic_self_rewriting | morph_depth ≤ 4 |

## Catalogue

Deterministic finite catalogue `O`:

1. **ATOMIC** — `ATOMIC_Di_demand_k` for each Di and `k ∈ {1..12}` (96 obligations).
2. **PAIR** — for every unordered pair `{Di,Dj}`:
   - `PAIR_FACTOR_Di_Dj` (factorizable product succeeds within budget),
   - `PAIR_FAIL_Di_Dj` (non-factorizable; product reduction fails) (56 obligations).
3. **HIGHER** — eight selected triples plus `HIGHER_OPEN_FULL_BASIS_RESIDUE` (9 obligations).

`|O| = 96 + 56 + 9 = 161`.

## Predicates

- **Alone-meet**: Di meets `o` iff `o` is ATOMIC with support `{Di}` and `demand(Di) ≤ B(Di)`.
- **Product-meet** (`Di⊗Dj⊗…`): support ⊆ admitted domains, `factorizable=True`, and every support demand fits its frozen burden.
- **Pairwise reduction failure**: neither alone-meets, support exactly `{Di,Dj}`, and product-meet fails.
- **Higher-order uncaptured**: coupling HIGHER, no pairwise product meets it, and the full simple product fails.

## Theorems

### T1 — Per-domain unmet witnesses (J2 boxes 1–8)

For every `i ∈ {1..8}`, the set

\[
U_i = \{ o \in O \mid \text{Di does not alone-meet } o \}
\]

is nonempty. Explicit first witnesses are returned by `first_unmet_witness(Di)`.

Alone coverage (exact):

\[
\mathrm{cov}(D_i) = \frac{B(D_i)}{|O|}
\]

so D1–D7 each cover `8/161` and D8 covers `4/161`.

### T2 — Pairwise reduction failures (J2 box 9)

There are exactly `C(8,2) = 28` pairwise reduction-failure witnesses — one `PAIR_FAIL_Di_Dj` per unordered pair. Each satisfies the failure predicate above.

### T3 — Higher-order combinations (J2 box 10)

Every HIGHER obligation in the catalogue (9 total) is uncaptured by simple pairwise composition. In particular `HIGHER_OPEN_FULL_BASIS_RESIDUE` remains open under the full basis product.

### T4 — Bounded completeness on ATOMIC∩budget (J2 box 11)

Let

\[
O_{\mathrm{atomic}}^{\le B}
= \{ o \in O \mid o\text{ ATOMIC},\ \mathrm{demand}(\mathrm{supp}(o)) \le B(\mathrm{supp}(o)) \}.
\]

Then `|O_atomic^{≤B}| = 7·8 + 4 = 60`, and every such obligation is alone-met by its unique support domain:

\[
\frac{|\{o \in O_{\mathrm{atomic}}^{\le B} : \text{met}\}|}{|O_{\mathrm{atomic}}^{\le B}|} = 1 = \frac{60}{60}.
\]

### T5 — Union coverage and open regions (already-checked J2 residue)

Union coverage under alone-meet ∨ factorizable product:

\[
\mathrm{cov}(\cup_i D_i) = \frac{60 + 28}{161} = \frac{88}{161}.
\]

Open-region fraction:

\[
1 - \frac{88}{161} = \frac{73}{161}
\]

(all 28 `PAIR_FAIL` + 9 HIGHER + 36 over-budget ATOMIC). These are explicit open regions, not a global-completeness claim.

## Limitations

- Scope is the declared catalogue and frozen `B`, not all conceivable cognitive obligations.
- “Product composition” is the registered simple-composition baseline; richer joint operators are out of scope and would need separate J3/J4 treatment.
- E2/E3 burden classes are not claimed.
