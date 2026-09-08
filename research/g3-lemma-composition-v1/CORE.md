# G3.1 lemma composition (smallest ordinary-cut pair)

**Terminal:** `TRAINING_PAIR_CUT_COMPOSITION_VERIFIED__NO_FRESH_COMPOSITION`

**G3.1 can be checked:** no. **G2.4:** still open.

The 0-premise `ssdifim` cut and the 0-premise `ssdifsym` cut both admit as ordinary `$p` on the pinned custodian prefix (same native check as #179). A reconstructed proof of the outer cut **invokes the inner cut identity** (`cut-ssdifim`), not the named whole theorem `ssdifim`. Removing the inner lemma rejects that proof. Inlining the inner body verifies but lengthens 64 → 80 tokens.

That is A-then-B composition on the **training pair** (ordinals 4127 then 4128, same subclass/difference neighbourhood). It is not disjoint-family G3.1, not an unseen A+B task, and not G2.4.

Held-out family after `pssdif`: 43,462 theorems. Zero cite both named parents. `NO_FRESH_COMPOSITION`.

The ordinary P1 parent already has named `ssdifim` / `ssdifsym` as **whole imported theorems**. Those statements are not the cuts. P1 proves the outer cut in 18 tokens via `ssdifim ex`.

[Result](RESULT.md) · [summary](SUMMARY.json) · [run](records/run-01/RESULT.json)
