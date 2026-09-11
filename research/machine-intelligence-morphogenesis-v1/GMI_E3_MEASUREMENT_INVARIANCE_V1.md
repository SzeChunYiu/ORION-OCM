# GMI E3 measurement invariance v1

Status: **formal bridge from GMI-v1 to heterogeneous real-domain measurement**.

Refs #233 #377 #369 #46 #208.

---

# 1. The trap this file forbids

A cross-domain theory can become meaningless if it forces heterogeneous capabilities into arbitrary common units.

Examples of invalid moves:

```text
1 Lean theorem = 1 coding task
kernel proof success = same epistemic quantity as passing tests
100 proof-state expansions = 100 shell commands
one average score across math + code chosen after outcomes
```

GMI-v1 does not require any of these.

The invariant object is the **form of the measurement**, not equality of domain units.

---

# 2. Common form

For deployed developmental system `(M,d,D)` and ecology `E`, retain:

\[
\mathcal A_{M}(E\mid d,D)
=\{(Q_E,\mathbf B):\text{reachable under legal development}\}
\]

and

\[
\mathcal F_M(E\mid d,D)=Pareto(\mathcal A_M(E\mid d,D)).
\]

The capability coordinate vector `Q_E` is **ecology-specific**.

Examples:

Math:

```text
statement correspondence
kernel-verified target theorem
verified registered sublemmas
dependency/axiom validity
```

Code:

```text
build success
protected behavior/test success
regression invariants
requirements discharged
false-completion absence
```

The raw resource schema is shared where coordinates have the same physical/operational meaning; domain-native receipts remain separate coordinates.

---

# 3. Generality across heterogeneous ecologies

Let the registered ecology family contain math and code members:

\[
\mathfrak E=\mathfrak E_{math}\cup\mathfrak E_{code}.
\]

A deployed system's profile is still:

\[
\mathcal I_{(M,d,D)}:E\mapsto\mathcal F_M(E\mid d,D).
\]

No conversion between theorem correctness and code-test correctness is needed.

Family-wide dominance is checked **within each ecology's declared coordinates**.

A strict claim that system A is more general than B over `Eset` requires A to be no worse under every registered ecology comparison and better somewhere according to the prospectively registered comparison semantics.

If the domain coordinate systems are not comparable enough for a cross-domain Pareto claim, report the vector of per-ecology relations instead of manufacturing a total order.

---

# 4. Optional scalarization

A scalar cross-domain score is allowed only if, before protected outcomes, the experiment declares:

```text
ecological sampling measure mu
per-ecology utility/admissibility mapping u_E
resource price/utility mapping where needed
failure/censoring treatment
```

Then a distributional question can be asked.

Different `mu` or `u_E` may reverse rankings. That is a property of the question being asked, not a contradiction in GMI.

The first E3 study should **not** make a headline scalar across math and code. Report domain profiles and cross-domain invariance first.

---

# 5. Reliability is part of capability, not an omitted nuisance

For each task family, report at least:

```text
admissible success probability / coverage
false-success probability
partial-verified-progress probability where applicable
CANNOT_CHECK / ASSAY_DEFECT rate
```

A faster system with materially lower verified coverage does not automatically dominate a slower reliable system.

The frontier must represent the capability/reliability difference rather than average burden only over successes.

---

# 6. Censoring / unsolved tasks

Unsolved or timed-out tasks remain observations.

Minimum rules:

```text
retain resources consumed up to censoring
retain terminal reason
report solved/admissible coverage separately
never compute mean burden over successful tasks only and call it overall burden
```

Possible registered analyses include:

```text
budgeted success probability
restricted mean burden up to fixed censoring horizon
survival/time-to-admissible-result analysis
Pareto comparison at fixed coverage
```

Choose before protected outcomes.

For formal mathematics, `no proof found` is not `false theorem`.

For code, `test failure` may be candidate failure or assay defect depending on evaluator validity.

---

# 7. Developmental comparisons require matched starting obligations

RESET and CONTINUED comparisons must use the same target obligations and verifier semantics.

The treatment difference is developmental state/history, not a different target formulation.

Math-specific caution:

```text
continued arm must not receive a stronger/easier formal statement
```

Code-specific caution:

```text
continued arm must not receive extra protected tests, gold patch hints or privileged repository metadata
```

---

# 8. History can alter the frontier in several ways

A developmental effect may appear as:

```text
higher verified coverage at same budget
lower burden at same verified coverage
better reliability / fewer false completions
lower maintenance/revision cost
better retention/plasticity under later tasks
```

K1 additionally requires a pre-solution causal change to cognition-generation on fresh targets.

Therefore:

```text
frontier improvement != automatically K1
K1 != automatically K2
```

---

# 9. Cross-domain theory acceptance criterion

The E3 semantic/measurement transfer succeeds if:

1. both domains instantiate the same developmental situation/state semantics;
2. morphology fields retain the same meanings;
3. external verification remains outside learner authority;
4. raw burden/resource accounting obeys the same rules;
5. capability differences are represented through ecology-specific coordinates rather than theory forks;
6. RESET/CONTINUED/K0/K1/K2/K3 retain exactly the same definitions;
7. failures/censoring are preserved under one policy family.

Terminal:

```text
GMI_E3_MEASUREMENT_FORM_INVARIANT_ACROSS_MATH_CODE
```

Failure terminal:

```text
GMI_THEORY_REVISION_REQUIRED_<semantic_or_measurement_reason>
```

---

# 10. Claim ceiling

This measurement invariance is a **theory/application property**, not evidence that any machine is generally intelligent.

Empirical GMI claims require actual domain-owner executions on prospectively protected tasks.
