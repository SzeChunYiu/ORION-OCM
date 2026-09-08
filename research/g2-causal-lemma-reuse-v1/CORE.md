# Causal lemma reuse (G2.4 successor)

**Terminal:** `NATIVE_ORDINARY_LEMMAS_ADMITTED_NO_HELD_OUT_INVOCATION`

The 22 unique `SCREENED_NEGATIVE_IN_DOMAIN` cuts from the syntax-revival replay
were compiled as ordinary Metamath `$p` (hypotheses as `$e` when present) and
natively checked against the pinned custodian prefix through `pssdif`.
**22/22 verified. 7 have zero hypotheses.** This is not yet
`CAUSAL_METHOD_REUSE_SUPPORTED`.

[Result](RESULT.md) · [summary](SUMMARY.json) · [admit](records/admit-01/ADMIT.json)

Held-out family: every `$p` after `pssdif` in set.mm (43,462 theorems).
The first 5,000 statements are not alpha-renames of the seven zero-premise
lemmas. `inssdif0` verifies from the prefix alone, so the ordinary parent already
has a proof of that first P1-closed target. A 4-decision finite-bank search
with a 9-formula bank did not invoke any cut lemma.

Not claimed: G2.4, novelty, or a journal residual.
