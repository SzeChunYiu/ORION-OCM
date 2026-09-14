# Demonstration selection, learner questioning, and pedagogic inference — I8 (#602)

Date: 2026-09-14. Status: **DERIVATION + EXACT WITNESS, WITH THE DEGENERATE CASE AS A SCOPE RESULT**.
Closes the three remaining boxes of I8. The other four are in `GMI_TEACHING_AND_CULTURE_THEOREM_V1.md`.

## 1. All three are one rule, moved across the cut

`TDA-1` selects an acquisition test by splitting the candidate set and minimising worst-case remaining
ambiguity. The same computation answers all three boxes:

| box | who splits what | who pays |
|---|---|---|
| **demonstration selection** | the teacher splits the *learner's* hypothesis set | teacher |
| **active learner questioning** | the learner splits its own hypothesis set | learner |
| **pedagogic inference** | the learner reasons that the split was *chosen*, not sampled | — |

## 2. Witness

Eight hypotheses over five inputs, deliberately asymmetric so demonstrations differ in value:

| demonstration | partition | worst case remaining |
|---|---|---:|
| input 0 | 3, 5 | **5** |
| input 1 | 3, 5 | **5** |
| input 2 | 2, 6 | 6 |
| input 3 | 1, 7 | 7 |
| input 4 | 1, 7 | 7 |

**Teacher and learner rank the demonstrations identically** — one rule, differing only in who is charged.
The best demonstration leaves 5 of 8 hypotheses in the worst case; the worst leaves 7.

**Pedagogic inference is warranted, and by a wide margin:**

| learner | mean hypotheses remaining after one demonstration |
|---|---:|
| treats the demonstration as a random sample | **5.200** |
| knows the teacher *chose* it | **2.500** |

> **52 % tighter, and strictly better on 8 of 8 true hypotheses.** Knowing the demonstration was selected
> rather than sampled more than halves the remaining ambiguity, without any extra data.

I8's box asks for pedagogy-aware inference *"if warranted"*. On this evidence it is.

## 3. The failed first attempt is the scope condition

The first witness used a **symmetric** hypothesis space — every input split it 4/4. There, all
demonstrations are equally good, the teacher's choice is arbitrary, and **pedagogy is worth exactly
0.000 hypotheses, strictly better on 0 of 8.**

That is not a bad test to discard; it is the scope condition:

> **Pedagogy pays only when demonstrations differ in discriminative value. In a symmetric hypothesis space
> a pedagogic learner has no advantage over one assuming random sampling, because there is nothing in the
> teacher's choice to read.**

The witness now asserts non-vacuity — that the demonstrations differ — and refuses to report a claim
otherwise. That guard exists because this is the **fifth** witness in this lane to have been vacuous on
first construction.

## 4. Scope

**Derived:** demonstration selection and learner questioning as one splitting rule; the value of pedagogic
inference; and the condition under which that value is zero.

**Assumptions:** a finite shared hypothesis space known to both parties, a cooperative teacher, and
noiseless demonstrations. A teacher with different beliefs about the learner's hypothesis set would choose
differently, and the learner's pedagogic inference would then be miscalibrated — an interesting failure
mode not explored here.

**Falsifier:** an asymmetric space where the pedagogic learner does no better than the random-sample
learner, or where teacher and learner rankings diverge.

## 5. I8 status — all seven boxes

| box | where |
|---|---|
| observational learning value | teaching theorem — `C − U` per learner |
| imitation when copying beats rediscovery | teaching theorem — `S → 0`, threshold `n > 1` |
| sender-cost/receiver-benefit law | teaching theorem — `n > 1 + S/(C−U)` |
| negative twin where cost exceeds benefit | teaching theorem — `U ≥ C`, never beneficial |
| **demonstration selection by a teacher** | **here** |
| **active learner questioning** | **here** |
| **pedagogy-aware inference** | **here** — warranted, 52 % tighter, and zero in symmetric spaces |
