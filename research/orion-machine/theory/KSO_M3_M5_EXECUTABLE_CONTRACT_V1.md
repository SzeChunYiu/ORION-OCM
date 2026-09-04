# KSO M3–M5 executable contract V1

Status: **controlled-domain mechanism package**.  
Parent: #284 · M0/M1 branch #295 · M2 branch #298.  
Branch: `research/ocm-kso-m3-m5-20260904`.

This artifact advances the first executable Knowledge-Space Object beyond retrieval/solving into
**learning**, **governed self-representation change**, and a **codec/chat boundary**. It does not
establish open-domain learning, human-level language, novelty, architectural superiority, or
frontier mathematical discovery.

## 1. M3 — learning a reusable procedure rather than an endpoint

### 1.1 Registered finite problem

Let

\[
D=\{00,01,10,11\},
\qquad
\mathcal H=\{f:D\to\{0,1\}\}.
\]

Thus \(|\mathcal H|=2^4=16\). The registered target for the calibration is AND,

\[
f_\wedge=(0,0,0,1).
\]

The learner does not receive a hidden target object except through the registered channel
interface. Its state after observations \(E\) is the exact version space

\[
V(E)=\{h\in\mathcal H:\forall(x,y)\in E,\ h(x)=y\}.
\]

A procedure is admitted only when \(|V(E)|=1\). This rule forbids a guessed completion.

### 1.2 Five channels

The channels implement the directive literally but with different information contracts.

- **Instruction** supplies a complete registered finite rule/table. It is checked on all four
  inputs before it becomes a procedure.
- **Demonstration** supplies input/output examples. The learner admits a procedure only when the
  examples leave one hypothesis.
- **Interaction** exposes only a query API. The learner chooses a deterministic minimax version-
  space split and pays one query per answer.
- **Experimentation** evaluates the procedure in the finite sandbox on every input and earns an
  exact closure certificate.
- **Feedback** supplies endpoint success/failure only. It may update utility metadata but is
  **non-warranting** and cannot create a live procedure.

On the full 16-function class, no learner can identify an arbitrary function with fewer than four
binary output bits in the worst case. The registered AND run therefore uses four instruction
coordinates / demonstrations / adaptive queries / experiments. This is a calibration, not a
sample-complexity advantage claim.

### 1.3 M3 theorems

**M3-T1 — version-space soundness.** If `learn_*` emits a procedure \(p\), every registered
observation is satisfied by \(p\). Proof: the emitted table is the unique member of \(V(E)\).

**M3-T2 — uniqueness completeness on the finite class.** If \(|V(E)|=1\), the learner emits that
unique function. If \(|V(E)|>1\), it emits `GAP_AMBIGUOUS`. This is immediate from the exact
enumeration defining `version_space`.

**M3-T3 — no endpoint laundering.** Feedback cannot produce a `LearnedProcedure`, regardless of
the endpoint verdict. M0 admission independently converts feedback atoms to the zero warrant
profile, so they cannot enable a warranted composition.

**M3-T4 — compositional reuse.** After learning \(f\), the lesson is not replayed in evaluation.
The learned primitive is reused in the held-out programs `IDENTITY(f(x))`, `NOT(f(x))`, and
`XOR_A(f(x),x)`. Four inputs × three programs = 12 checks. All four warranting channels score
12/12; feedback scores 0/12 because no procedure exists.

**M3-T5 — lifecycle correction.** Let evidence identity \(e\) warrant procedure \(p\). For every
held-out composition \(C[p]\),

\[
e\in R \Longrightarrow C[p]\text{ is not executable as warranted knowledge}.
\]

In the registered run each warranting channel moves 12/12 → 0/12 under revocation and returns to
12/12 after reinstatement. This is the finite procedure-level realization of the M0 exact-share/RCL
rule.

### 1.4 M0 integration

Each M3 learning receipt is passed through the existing M0 `admit` transaction with a typed
`COMPOSITION` edge connecting the new procedure to the procedure library. Instruction,
demonstration, interaction and experimentation remain warranted. Feedback is admitted
unwarranted. No separate weaker acquisition semantics is introduced.

Terminal: `M3_EXACT_GAP_LEARNING_GREEN`.

Non-consequence: this does not show efficient open-domain procedure induction or language learning.

---

## 2. M4 — a governed Jump from a witnessed expressive ceiling

### 2.1 Incumbent representation

The incumbent family is the eight affine Boolean functions

\[
f(a,b)=c_0\oplus c_1a\oplus c_2b,\qquad c_i\in\{0,1\}.
\]

Every affine truth table has even parity across the four inputs:

\[
f(00)\oplus f(01)\oplus f(10)\oplus f(11)=0.
\]

AND has truth table `(0,0,0,1)`, whose parity is 1. Therefore AND is not in the affine family. The
checker also enumerates all eight candidates and records a distinguishing input for each. This is
an exact `EXPRESSIVE_CEILING`, not a low score.

Affine functions are closed under affine substitution/composition, so J0 parameter changes and J1
local affine composition cannot manufacture the missing non-affine term.

### 2.2 Competing Jumps

Two admissible proposals are constructed through the repository's existing
`orion_v2.jump.JumpTrigger` / `JumpProposal` objects.

**J3 representation transition**

\[
\phi(a,b)=(1,a,b)
\quad\mapsto\quad
\phi'(a,b)=(1,a,b,ab).
\]

Then

\[
AND(a,b)=0\oplus0a\oplus0b\oplus1(ab).
\]

All eight old affine functions embed with the new coefficient \(c_3=0\), so the old repertoire is
preserved exactly. Dropping the fourth feature is an exact rollback to the incumbent family.

**J5 operator invention** adds AND as a primitive Boolean operator. It also solves the task, but is
a higher Jump.

ORION's `minimum_level` therefore chooses J3. A bad feature `a xor b` is exhaustively rejected;
`POOR_SCORE` is not an admissible Jump trigger; and any lower-level sufficient repair cancels the
Jump.

Terminal: `M4_FINITE_GOVERNED_JUMP_GREEN`.

This is a finite mechanism calibration. The #284 inherited 84-world V1 Jump benchmark remains
unrun in this lane and must not be conflated with this terminal.

---

## 3. M5 — codec-independent controlled chat

M5 tests whether language can sit at the boundary rather than secretly act as the solver.

Two independently written codecs are registered.

Text:

`teach AND where 00=0 01=0 10=0 11=1`

JSON:

`{"kind":"teach","name":"AND","table":[0,0,0,1]}`

Both map to the same canonical `TeachCommand`; the evidence identity is derived from that canonical
command, not from surface wording.

Likewise, `solve NOT AND on 11` and its JSON equivalent map to the same `SolveCommand`.

### 3.1 Translator invariance

For equivalent codec inputs \(c_1,c_2\),

\[
H(\eta_{c_1}(x))=H(\eta_{c_2}(x)),
\]

where \(H\) is the canonical command digest. Independent machines receiving the two lesson
encodings produce equal procedure digests, equal evidence identities, and equal answers.

The codec is forbidden from supplying an `answer`/`result` field. Such a request is rejected as
`CODEC_ATTEMPTED_TO_SUPPLY_ANSWER`.

### 3.2 Executable conversation

```text
> solve NOT AND on 11
GAP_UNKNOWN_PROCEDURE

> teach AND where 00=0 01=0 10=0 11=1
Learned AND as a warranted reusable procedure.

> {"kind":"solve","name":"AND","combinator":"NOT","input":[1,1]}
Result: 0.

> revoke AND
REVOKED

> solve NOT AND on 11
GAP_REVOKED_PROCEDURE

> {"kind":"reinstate","name":"AND"}
REINSTATED

> solve XOR_A AND on 11
Result: 0.
```

`reference/kso_demo_v1.py --interactive` exposes the same state machine for manual use.

Terminal: `M5_CONTROLLED_CODEC_CHAT_GREEN`.

Non-consequence: the grammar is intentionally tiny. This is a boundary/invariance proof of concept,
not fluent natural language.

---

## 4. Current executable ladder

| milestone | status after this package | meaning |
|---|---|---|
| M0 | GREEN upstream | mathematical + frozen substrate checks |
| M1 | GREEN on #295 branch | KSO populated on exact ME-X1 worlds |
| M2 | PARENT_SUFFICIENT on #298 branch | KSO solves 50/50 and ties the strongest faithful ceiling |
| M3 | `M3_EXACT_GAP_LEARNING_GREEN` | learns reusable procedure through four warranting channels |
| M4 | `M4_FINITE_GOVERNED_JUMP_GREEN` | exact ceiling triggers minimum sufficient representation Jump |
| M5 | `M5_CONTROLLED_CODEC_CHAT_GREEN` | two-codec controlled conversation with learning/revocation |
| M6 | **NOT_RUN** | genuine frontier-math/proof-assistant pilot still required |

M3–M5 are controlled finite calibrations. They matter because the code now demonstrates the
mechanical cycle the programme previously only described, but they do not establish that the same
mechanisms scale to natural language, broad knowledge, or research-level mathematics.

---

## 5. Strongest-parent subtraction

Nothing in this package should win by renaming existing theory.

- M3's finite version-space learning is classical exact learning / active learning territory.
- M3's procedure-library reuse collides with program/library learning and DreamCoder/LILO-class
  systems.
- The warrant/lifecycle gate is inherited from M0/RCL/ATMS rather than re-claimed.
- M4's affine feature lift is elementary representation engineering; graph rewriting and Jump
  governance are the ORION integration layer.
- M5's parser/renderer separation is an interface architecture; controlled codec invariance is a
  systems property, not a new theory of language.

The remaining major scientific question is therefore no longer "can the pieces execute?" in this
controlled setting. They can. It is whether a **single scalable KSO** can acquire rich procedures,
navigate a large learned space, perform useful Jumps, and learn its language interface while
matching or exceeding the strongest equally provisioned parent product.

---

## 6. Why M6 is not marked green

A frontier-mathematics claim needs all of the following at minimum:

1. a genuinely nontrivial/open formal target fixed before outcome access;
2. a proof-assistant kernel/checker available and independently replayable;
3. a KSO populated with the relevant mathematical knowledge without importing the target proof;
4. a witnessed obstruction before any Jump;
5. a prospectively specified J-level transformation and predicted consequences;
6. proof/counterexample results bound as new atoms with exact provenance;
7. strongest theorem-search/retrieval parent at matched information and compute;
8. an independent replay/review.

No finite Boolean toy can substitute for that evidence. M6 remains `NOT_RUN` rather than receiving
a false green.
