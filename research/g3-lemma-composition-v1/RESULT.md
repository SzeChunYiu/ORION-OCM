# Smallest G3 composition on admitted ordinary-cut lemmas

Pinned prefix: `CUSTODIAN-PREFIX.mm` sha256
`b12e2bac9f6fe8a6fda972d74dbfb21c2e85cd86040fd447c685c693ae0af1cd`
(1,806,915 bytes, last `$p` is `pssdif`). Checker: vendor `mmverify.py`.
Native calls this run: 6.

## Methods (already-admitted cuts)

| Role | Training root | Cut identity | Statement |
|---|---|---|---|
| A | `ssdifim` (ordinal 4127) | `cut-ssdifim` | `|- ( B = ( V \ A ) -> ( V \ ( V \ A ) ) = ( V \ B ) )` |
| B | `ssdifsym` (ordinal 4128) | `cut-ssdifsym` | `|- ( A C_ V -> ( B = ( V \ A ) -> A = ( V \ B ) ) )` |

Both are 0-premise `SCREENED_NEGATIVE_IN_DOMAIN` cuts. Both native-verify as ordinary `$p`. Neither statement equals the named P1 theorem of the same label.

The published outer-cut proof is `… ssdifim ex` (18 tokens): it cites the **named whole** `ssdifim`, which is already in P1.

## Training-pair composition (invocation is real)

Rebuilt outer proof uses `dfss4` / `eqcom` / `sylbb` / `sylan9eq` / `ex` and **`cut-ssdifim`**. It does not mention named `ssdifim`. Native result: `NATIVE_VERIFIED` (64 tokens).

| Arm | Terminal | Proof tokens | Cites |
|---|---|---:|---|
| P1 original outer (`ssdifim ex`) | `NATIVE_VERIFIED` | 18 | named whole `ssdifim` |
| Composed outer | `NATIVE_VERIFIED` | 64 | inner cut `cut-ssdifim` |
| Ablate inner cut | `NATIVE_REJECTED` (`No statement information found for label cut-ssdifim`) | 64 | broken |
| Inline inner body (`difeq2 eqcomd`) | `NATIVE_VERIFIED` | 80 | neither cut nor named `ssdifim` |

Ablation of A breaks the composed B proof. Inlining A lengthens B. That is causal dependence of this outer derivation on the inner cut identity.

## Fresh task

Held-out `$p` after `pssdif`: 43,462.

| Named parent in a later proof | Count | Example |
|---|---:|---|
| `ssdifim` only | 1 | `frgrwopregbsn` (friendship graph) |
| `ssdifsym` only | 1 | `zarcls` (Zariski) |
| both | 0 | — |

No held-out theorem needs both **cut** identities. Combined target of the composed proof is the training outer cut itself, so it is not absent from training.

**`NO_FRESH_COMPOSITION`.**

## P1 parent comparison

Named wholes already on the prefix:

```text
ssdifim  |- ( ( A C_ V /\ B = ( V \ A ) ) -> A = ( V \ B ) )
ssdifsym |- ( ( A C_ V /\ B C_ V ) -> ( B = ( V \ A ) <-> A = ( V \ B ) ) )
```

Those are imported library facts, not the extracted cuts. P1 is parent-sufficient for proving the outer cut without admitting any cut. Composition here is a reconstruction of one training cut from another, not a residual over the library parent.

## G3.1 / G2.4

G3.1 requires disjoint families, an unseen A+B task, actual use of **both** learned identities on that task, and A-only / B-only / both ablations. This run has a real A-inside-B invocation on the training pair and an A-removal break. It does not have disjoint B, a fresh task, or use of the outer identity as a lemma on a third goal.

**G3.1 cannot be checked.** Do not issue `METHOD_COMPOSITION_SUPPORTED`.

G2.4 remains open. Same-family training-pair composition is not fresh-task causal reuse.

## Reproduction

```sh
python3 research/g3-lemma-composition-v1/compose.py
python3 -m unittest research/g3-lemma-composition-v1/test_composition.py
```

Requires `/tmp/orion-native/CUSTODIAN-PREFIX.mm` and `/tmp/orion-native/set.mm`.
