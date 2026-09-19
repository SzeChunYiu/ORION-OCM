# FREEZE AMENDMENT 01 — `gmi-833-aa-logical-form-register-v1`

Status: committed with the implementation, **before any receipt exists**.
`FREEZE_V1.md` is not edited. Every item below is a disclosed refinement made
while validating the frozen rules on the real corpus; none widens a claim.
Where an item corrects a false-positive class the object that exposed it is
named.

## A. Tokenization and grammar (FREEZE section 5)

1. **`<MATH>` in the relational lexicon.** Display math is replaced by the
   single token `<MATH>` as frozen, which erases the `=` / `<=` / `>=` a
   sentence such as "The exact time to move from q_0 to q_1 is `\[T=…\]`"
   carries. The EQ cue list therefore also contains `is <MATH>` / `are
   <MATH>` and the bare word `exactly`; LE adds `upper bound`, `never
   increase/exceed`, `not exceed`; GE adds `lower bound`, `requires at
   least`. Nothing else is added to any lexicon.
2. **Sentence boundaries.** A sentence that ends in display math has no
   period; a break is inserted after `<MATH>`/`<CODE>` when the next word is a
   capitalised sentence opener (`If`, `Then`, `Thus`, `Therefore`, `For`,
   `The`, …), at ` --- ` rules and at ` - ` / ` * ` list bullets. Without
   this, "A global assignment exists iff `<MATH>` If it exists, …" parsed as
   one iff with a two-sentence right side.
3. **Anchored prefix rules first.** R7/R8 anchored at the sentence start
   (`For every V, S`, `There exists V such that S`) and the `Under/Given/
   Assuming H, S` hypothesis peel are applied before R1–R6, so that the
   unanchored trailing variant `Y if X` cannot cut a sentence that opens with
   a quantifier. The anchored R1–R6 forms cannot begin with `For every`, so
   no rule of section 5 is displaced.
4. **Context + if/then.** `C, if X, then Y` (a leading context clause, as in
   IC-2 "For an invertible linear mixture …, if at most one component is
   Gaussian, then …") folds `C` as a hypothesis and parses `If X, then Y`;
   the trailing-`if` variant is skipped whenever the sentence contains
   `then`. Without this IC-2 was cut at the wrong `if`.
5. **R5 `requires` is a necessity only when its object is a condition.**
   "Encoding every task independently requires `<MATH>` bits" (EM-3) is a
   quantity bound, not `Y -> X`; the right side may not open with `<MATH>`,
   a digit, `at least/most`, `exactly`, `only`, `zero/one/two`, `no more`,
   `fewer/more`, `by`. EM-3 was a false ROLE_SWAP alarm under the frozen
   wording.
6. **R6 variants.** `It suffices to X`, `A sufficient condition for Y is X`
   (-> `X -> Y`) and `A necessary condition for Y is X` (-> `Y -> X`) are
   spelled out; they are the section-5 R5/R6 shapes in their other common
   surface order.
7. **`conclusion_prefix`.** Each form records, next to the folded `prefix`,
   the prefix contributed by the conclusion sentence alone.

## B. Warrant column (FREEZE section 6)

8. **Opening assumption only.** A first-sentence fallback for the proof
   literal was tried on the corpus and produced **6/6 false CONVERSE alarms**
   (AM-1, ER-2, KF-16.1, NR-3, TC-1, ID-2 — every one a direct proof whose
   first sentence works with the objects named in the consequent). The
   literal is therefore exactly the frozen opening assumption (`Suppose |
   Assume | Let | Given | If | Fix | Consider | Take X`) and nothing else.
9. **Proof-label sub-classification.** `Derivation consequence` /
   `Derivation notes` subsections are interpretation, not proofs (KF-6, KF-17,
   KF-20, KF-21 carry only those) and are not warrants; a `Construction`
   subsection is the proof of an existential and is one. `exactly when`,
   `iff`, `if and only if` join the second-direction markers.
10. **AA16 cue is discriminating only on the conclusion prefix.** When the
    `forall` comes from a `Let` hypothesis the variable is fixed before the
    proof starts, so a proof that opens by constructing the witness is
    consistent with forall-exists and the proof-first cue says nothing
    about order. KF-4 ("Let p != q … There exists a binary decision problem
    …", proof "Set v = p − q … Define …") was the false positive. The cue is
    read only when the conclusion sentence's own prefix is mixed; otherwise
    the object needs a hand warrant.
11. **Relative polarity, contrapositive-aware.** A warrant assuming the
    negated consequent is a contrapositive proof of `A -> B`, not a converse;
    verdicts are: aligned-left & same polarity = direct; aligned-right &
    opposite polarity = contrapositive; aligned-right & same polarity =
    CONVERSE; aligned-left & opposite polarity = INVERSE. This is the
    section-7 wording made exact.
12. **Hand warrants are content-anchored.** A hand warrant names the assumed
    side at registration time; the executor stores the *content* of that
    side (atom text and polarity) and re-aligns it against the current
    matrix by token overlap. A side *label* travelling with a planted swap
    can never detect the swap: under label anchoring H3 and H6 were vacuous
    (0/15 and 0/16 detected). A hand warrant whose assumed side is pure
    `<MATH>` has no content to align and is `UNALIGNED`, not evaluable
    (PS-2, EG-3, IB-1, IB-3, QD-1).

## C. Hand registration (FREEZE section 5.1)

13. **Second, warrant-only hand sample.** The frozen hand sample (seed 833,
    40 objects) is drawn from `FORM_UNAVAILABLE` and cannot supply warrants
    to machine-registered conditionals. A second sample of **20** objects
    (seed **834**, same LCG) is drawn from the pool: machine-registered,
    applicable to AA16/AA17/AA18, not machine-evaluable, carrying a proof or
    falsifier block — plus **every** AA16-applicable object. For these the
    form stays machine; only the warrant is read by hand. The pool is
    computed from the machine register state and is not cherry-picked.
14. **Hand warrant sources.** When a note carries no proof block the hand
    warrant may cite the result's own package receipt or checker by path and
    blob (EA-3: `GRAND_GMI_EPISTEMIC_RECEIPT_V1.json` blob `3c02d155…`,
    `strict_adaptive_advantage: 576`), or inline argument sentences that the
    form parse dropped as trailing (QS-1, LLS-3); the source is recorded in
    the entry. An object with nothing outside its statement to read is
    refused (`NO_WARRANT_BYTES`, CC-T2), never guessed.
15. **Reader verdicts.** Every hand entry carries `hand_verdict`: `CLEAN`
    (stated form and warrant consistent; the object belongs to the no-alarm
    set) or `QUEUE_EXPECTED` (the reader found the warrant short of the
    stated form; a real-data positive that must be queued). DL-3 is the one
    `QUEUE_EXPECTED` entry: an `iff` whose block proves the identity and
    argues neither direction of the equality case. The frozen clause "the
    hand set raises 0 alarms" is read over the `CLEAN` subset.

## D. Null (FREEZE section 9)

16. **Permutation over the whole registered set.** A permutation of the
    warrant column *within* the evaluable set of AA20/AA22 leaves the
    agreeing count invariant (the statistic counts clean evidence modes on
    OPT/CAUSAL atoms, a multiset property) — a null that cannot move is not
    a null. Warrants (machine and hand) are therefore permuted over the whole
    registered population, so an object may receive an unavailable or
    unaligned warrant and drop out of the evaluable set. The per-row
    statistics are reported; AA20/AA22 per-row nulls are expected to be
    weak for the same multiset reason and their weakness is disclosed rather
    than hidden in the pooled figure.

## E. Route agreement (FREEZE section 10)

17. **Form equality** between the routes means canonical-structure equality:
    identical prefix quantifier kinds in order, identical matrix tree
    (connectives and rel classes) and identical content-token sequences per
    atom; the `scope` string is compared separately and reported. Queue
    equality is exact on `(key, kind)`.

## F. Custody

- `s6_instruction_followed: true` — no frozen clause is overridden; items
  5, 8, 10 and 12 remove false-positive classes found on real data before
  any receipt was written, items 13–15 extend the hand work to a declared,
  seeded class, item 16 replaces a vacuous null with one that can move.
- `audit_shape_disclosed: PRE_RECEIPT_AMENDMENT`.
