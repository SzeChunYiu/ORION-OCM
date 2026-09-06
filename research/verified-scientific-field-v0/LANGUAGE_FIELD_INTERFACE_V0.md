# LANGUAGE_FIELD_INTERFACE_V0

Status: **research interface candidate** for #93 / #52 / #43–#45.  
Purpose: harden how LLM-like communication can emerge over the same General Epistemic Field used by science/math/coding without turning language into a second cognition core.

## 1. Core position

Language is a bidirectional interface and a learned competence family over `F_t`:

```text
utterance
   ↓ L_in
candidate field interpretations / proposals
   ↓ Π + O over F
intended communicative state
   ↓ L_out
candidate utterance
   ↓ reverse-read + commit gate
external language act
```

The internal field is not assumed to be English, token sequences, or one universal logical form.

## 2. Input interface

Candidate contract:

```text
L_in(
    utterance,
    language_scope,
    dialogue_context,
    available_field_view,
    budget
) -> InterpretationSet
```

`InterpretationSet` contains zero or more candidates, each with:

```text
field_delta / meaning representation
referent candidates
construction / lexeme derivation
warrant/evidence ids
scope
speaker/source authority
unknown obligations
resource receipt
```

Required outcomes include the existing M3 classes:

```text
INTERPRETED
AMBIGUOUS
UNKNOWN_LEXEME
UNKNOWN_CONSTRUCTION
NEEDS_CONTEXT
CONTRADICTION
CANNOT_CHECK
```

No top-k or model score converts AMBIGUOUS into INTERPRETED.

## 3. Output interface

Candidate contract:

```text
L_out(
    intended_field_obligations,
    dialogue_context,
    language_scope,
    style/register constraints,
    budget
) -> SurfaceCandidateSet
```

A candidate records:

```text
utterance
realizer identity/version
intended semantic digest or obligations
style/register metadata
inference/training resource receipt
```

A realizer may be symbolic, construction-based, recurrent, SSM-based, neural, retrieval-assisted, or another parent.

Its role is **surface communication**, not epistemic authority.

## 4. Reverse-read gate

Before external commitment:

```text
u = L_out(intent)
I = L_in(u)
```

The gate must establish that at least one recovered interpretation satisfies the intended obligations and that no protected semantic coordinate has been lost or strengthened.

Required checks where applicable:

```text
entity/referent identity
predicate/event structure
negation
quantity
modality
scope
speaker/report status
uncertainty / epistemic marker
correspondence/warrant references
requested speech act
```

A generated sentence that sounds better but changes one of these fails.

The gate is not a claim that semantic parsing is perfect. If reverse-read itself is ambiguous or unavailable, the candidate may be refused or sent for another realization attempt.

## 5. No renderer intelligence laundering

Hostile test:

The renderer receives only a deliberately incomplete intended meaning but enough conversational/world context to infer a plausible answer.

Forbidden behavior:

```text
renderer injects missing factual proposition
```

Required behavior:

```text
render only supplied intended obligations
or return REALIZATION_INSUFFICIENT
```

This separates linguistic fluency from cognition attributed to `F/O/Π`.

## 6. Language objects inside the field

Current M3 structures are first-right-of-refusal:

```text
Lexeme / Sense
MorphRule
Construction
MeaningGraph / representation
Dialogue evidence
Speaker commitment
```

For the general-field framing these are ordinary scoped field/procedure objects plus language registry metadata.

Do not duplicate a scientific/world proposition merely because it has several linguistic realizations.

Instead link language forms/constructions to the relevant field representation through explicit correspondence objects where justified.

## 7. No perfect interlingua assumption

A `MeaningGraph` is a current language representation, not constitutional proof that all cognition has one canonical graph.

Required cases:

- one utterance has several candidate meanings;
- one meaning has many paraphrases;
- one phrase is only partially grounded;
- one representation loses distinctions required by another query;
- a metaphor/idiom is not compositionally recoverable from literal lexical mappings;
- a domain concept has no established language correspondence yet.

The system must preserve mapping status rather than force all cases into exact one-to-one translation.

## 8. Dialogue as transient field view

Current `DialogueWorkspace` may remain an implementation structure, but architecturally it should be understood as a materialized/transient view over field state:

```text
current turns
active commitments
entities/referents
pending questions
conversation goals
local discourse salience
```

It is not a second epistemic universe.

If persisted separately, it must carry field/evidence identities and invalidate on relevant revision.

## 9. Clarification is a `DISTINGUISH` instance

Given interpretation alternatives `I1...In`, a clarification question is valuable only if its possible answers change a downstream obligation/action.

Abstractly:

```text
DISTINGUISH(alternatives, allowed_questions, cost, target_query)
```

Language-specific implementation chooses a human-usable question.

This shares a control contract with scientific experiment selection while retaining distinct domain probe generators and response semantics.

## 10. Learning language over the field

The learning ladder remains #52-owned:

```text
lexemes/senses
morphology
constructions
form→meaning
meaning→form
discourse/reference
clarification/explanation
style/register
acquisition strategies
```

The General Epistemic Field contributes:

```text
shared identity
warrant/scope/revision
operator reuse
representation correspondence
active-state navigation
cross-domain context
```

It does not by itself solve grammar induction or surface fluency.

## 11. LLM-like speaking target

Evaluate two distinct questions:

### Q-LANG-CAPABILITY

Can the system reach useful/open-domain conversational quality comparable to strong LLM-based systems at a registered scope?

### Q-LANG-ARCHITECTURE

How much language-specific parametric/statistical machinery remains necessary once non-linguistic knowledge, long-term memory, explicit procedures and epistemic control live outside the surface model?

Do not infer Q-LANG-ARCHITECTURE from a capability result.

## 12. Comparator ladder

At minimum where feasible:

```text
fixed templates
learned construction grammar / grammar-based realizer
retrieval/template memory
small recurrent realizer
small SSM realizer
small seq2seq/other compact neural realizer
strong Transformer realizer
strong LLM + memory/tools full conversational parent
```

Every model gets the same intended semantic input and permitted external field access for causal comparison.

For open-domain end-to-end comparison, the LLM parent receives equivalent memory/tool powers.

## 13. Metrics

Separate:

```text
semantic round-trip success
protected-coordinate preservation
reference accuracy
clarification correctness/value
held-out compositionality
correction/revocation locality
fluency
human preference if authorized
response task success
parameter count/bytes
training data/information
training compute
inference compute
active field k
field reads
language-state bytes
```

Fluency must never hide semantic or authority failures.

## 14. Hard negative terminals

```text
FIXED_LANGUAGE_PRIOR_DOMINATES
LANGUAGE_FIELD_INTERFACE_SUPPORTED
COMPOSITIONAL_LANGUAGE_ONLY
OPEN_DOMAIN_FLUENCY_NOT_REACHED
PARAMETRIC_LANGUAGE_CORE_DOMINATES
REVERSE_READ_TOO_WEAK
UNIVERSAL_INTERLINGUA_ORACLE
PARENT_LANGUAGE_SYSTEM_SUFFICIENT
LANGUAGE_CORE_FORK_REQUIRED
CANNOT_CHECK_<reason>
```

A negative terminal does not refute the General Epistemic Field as a substrate for other domains; it scopes the language bridge.
