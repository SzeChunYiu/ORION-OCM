# GMI #833 compact axiom and finite consistency core v1

Status: **LOCAL FORMAL CLOSURE — RELATIVE FINITE-MODEL CONSISTENCY ONLY**

## 1. Compact basis and derivation envelope

`AXIOMS_V1.json` registers exactly ten typed axioms/definition principles:
typed domains, implementation-independent behavioral specification, registered
process totality, protected-response equivalence, developmental relations,
raw resource vectors, architecture-independent capability, tagged uncertainty,
query-relative abstention, and explicit scope tags.

These are a compact basis for the **registered mathematical core vocabulary**,
not premises from which empirical facts follow. `DERIVATION_MAP_V1.json` gives
ten exact constructions and every dependency:

- behavioral specification and protected-response quotient;
- developmental reachability;
- morphology/mechanism equivalence and its legacy machine-species quotient;
- capability regions and ceilings;
- typed uncertainty and identified-query semantics;
- scientific claim scope.

The map imports the already merged, stronger packages from PRs #837, #847,
#850, and #853. It does not re-prove or reclaim them. Every dependency token is
checked against the ten axioms, four imports, or ten registered definitions,
and every imported result must retain its exact green terminal/verdict.

Empirical validity, real-system capabilities, universal grammar completeness,
prospective success, independent replication, and ontological completeness are
explicitly non-derivable without new evidence.

## 2. Concrete finite model

The model has states `{s0,s1}`, actions `{toggle,hold}`, observations `0,1`, and
the total transition table

`toggle(s0)=s1, toggle(s1)=s0, hold(si)=si`.

It has an external `REPORT_STATE` acceptance relation, a three-coordinate
nonnegative resource vector, a typed resource-labeled developmental edge, a
versioned/provenanced feasible uncertainty object, all four query dispositions,
and valid theorem scope tags. Its protected-response quotient has two singleton
classes. The executable checker evaluates one named predicate for each axiom;
all ten are true.

## 3. Relative consistency theorem

**Theorem AC-1.** The registered ten-axiom finite core is satisfiable in the
ordinary semantics of finite sets, relations, integer resource vectors, and
finite strings.

**Proof.** The concrete interpretation above assigns every sort and symbol.
`axiom_core_v1.py` evaluates the exact ten predicates and returns
`axioms_satisfied=10`. The committed deterministic receipt fixes the model and
result. Therefore this interpretation is a model of the registered finite core.
QED.

**Corollary (relative non-contradiction).** Assuming the ordinary finite
set/integer semantics and a sound consequence relation, the registered core
cannot derive both a sentence and its negation: a model cannot satisfy both.

This does **not** prove consistency of the metatheory, arbitrary future
extensions, unrestricted set theory, unbounded self-reference, or all text in
the repository. Each extension needs a new model, conservativity proof, or
other appropriate argument.

## 4. Hostiles and recursive gap

Four mutations independently delete a transition, make a resource negative,
erase a scope tag, and conflate the uncertainty kind; the corresponding axiom
predicate fails in normal and optimized Python. The deterministic receipt also
fails on any result drift.

Independent hostile theorem review remains explicitly open, so the closure
level is `LOCALLY_CLOSED`, never `HOSTILE_CLOSED`.
