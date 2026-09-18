# Section H family-gate soundness theorems v1

## Scope and notation

Let `J` be the eleven requirements written above the named family rows in Issue
#833 Section H. Although earlier summaries sometimes call these “ten gates,”
the source sentence has eleven coordinates when “lower bound where possible” is
counted explicitly. Let a scope be

```text
sigma = (family row, grammar, ecology, budget, freeze, protected interface).
```

A certificate is `(j, status, sigma)` for `j in J`. Every gate accepts `PASS`.
The lower-bound coordinate also accepts `NOT_APPLICABLE_PROVED`; an unsupported
claim that no lower bound is possible is not accepted.

These theorems formalize the checklist's evidentiary rule. They do not establish
any one family gate.

## FGS-1 — fail-closed conjunction theorem

Define `Eligible(B, sigma)` to hold exactly when:

1. `B` contains exactly one certificate for every `j in J`;
2. every certificate has scope `sigma`; and
3. every certificate has an accepted status.

Then a row is eligible if and only if the eleven accepted, same-scope
certificates are present.

### Proof

The forward direction follows by eliminating each conjunct in the definition of
`Eligible`. The reverse direction follows by introducing their conjunction.
Duplicates, unknown gate names, absent gates, failed gates, and incompatible
scopes violate at least one conjunct and therefore fail closed. `□`

No gate is redundant under this policy. For each `j`, assign every other gate a
valid certificate and omit (or fail) `j`. The bundle satisfies all other gate
predicates while `Eligible` is false. The checker constructs all eleven
single-missing and all eleven single-failed hostiles. This is logical
independence of the policy coordinates, not a claim that their empirical
measurements are statistically independent.

## FGS-2 — scope-gluing no-go

Certificates indexed by scopes `sigma_j` prove gate predicates at those scopes.
Absent a registered transport theorem from `sigma_j` to a target `sigma*`, they
cannot be composed into `Eligible(B, sigma*)` unless every `sigma_j = sigma*`.

### Proof

Suppose one gate certificate has `sigma_k != sigma*`. Make a countermodel in
which its predicate is true at `sigma_k` and false at `sigma*`, while all other
target-scope predicates are true. Every submitted certificate remains true at
its own scope, but the target conjunction is false. Therefore cross-scope
composition is invalid without an additional transport premise. `□`

The executable hostile changes only the budget field, once per gate, while all
ten other certificates remain at the target scope. All eleven glued bundles are
rejected. Grammar, ecology, freeze, family row, and protected-interface drift
are covered by the same equality argument.

## FGS-3 — finite-evidence non-promotion theorem

For every nonempty finite binary observation prefix
`a=(a_0,...,a_B)`, there are total functions `f,g:N->{0,1}` such that

```text
f(i) = g(i) = a_i  for every i <= B,
f(B+1) = 0,
g(B+1) = 1.
```

### Proof

Set both functions to the observed values through `B`. Set `f(i)=0` for every
later index. Set `g(B+1)=1` and `g(i)=0` for `i>B+1`. Both are total, agree on
all evidence, and disagree at the first unobserved case. `□`

Consequently, bounded evidence alone does not logically entail behavior at an
unobserved real-scale point. A scaling law, structural invariant, continuity
assumption, or direct real-scale test can add the missing premise; the theorem
does not say that transfer is impossible. It says transfer is not earned by the
finite observations alone. The checker exhausts all 510 prefixes through bound
7, while the proof covers every finite bound.

## FGS-4 — observational family non-identifiability theorem

There exist distinct hidden organizations with identical protected response
profiles on every finite binary word.

### Proof

Organization `A` has one hidden state and emits the current input symbol.
Organization `B` has two hidden states, toggles state after every input, and
also emits the current input symbol. By induction on word length, both response
traces equal the input word. Their hidden state cardinalities are one and two,
so the organizations are distinct. Hence the map from hidden organization to
this protected response profile is not injective. `□`

This blocks a family-identity inference from operational equivalence alone. It
does not block a scoped post-hoc family mapping when additional structural
observables and the evaluation prior are disclosed. The executable census
checks all 511 words through length 8; the step-definition proof is unbounded.

## FGS-5 — remint and independent-oracle controls

Gate and family labels are independently reminted by domain-separated SHA-256
identifiers. Reconstructing the gate bundle through the reminted IDs preserves
eligibility, showing that the result depends on the gate relation rather than
English identifier spelling.

The primary implementation uses typed certificates and exact scope records. A
source-separated oracle uses an eleven-bit mask and scope-code tuples. Both
agree on the complete bundle, all single-missing gates, all single-scope glues,
510 finite-prefix witnesses, and 511 visible words.

## FGS-6 — reconciliation consequence

This package furnishes no family-specific gate certificate. Therefore it closes
zero named rows. It also leaves the aggregate obstruction-census row to PR #987.
The machine-readable reconciliation preview contains no mutations and records
all 43 named rows with `close: false`.

## Strongest parents and novelty boundary

- Conjunction introduction/elimination and indexed predicates own FGS-1/FGS-2.
- Underdetermination by finite data and elementary diagonal extensions own
  FGS-3.
- Observational equivalence, automata minimization, and latent-variable
  non-identifiability own FGS-4.

The contribution is not a new theorem in logic or automata theory. It is an
exact, executable application of these parent facts to the Section H closure
contract, including scope custody and a no-op reconciliation artifact.

## Falsifiers and forbidden extrapolations

The formal result fails if the checker accepts a missing/failed/incompatible
certificate, if a purported continuation pair differs inside the observed
prefix or not after it, if the two hidden organizations expose different
protected responses, or if any reconciliation mutation is emitted.

The result does not prove any named family recovered or unrecoverable; it does
not supply held-out prediction, independent-team replication, or real-scale
validation; and it does not override a future registered transport theorem.
