# Compressed dynamical state, and when the update can be affine (B9)

Date: 2026-09-14. Lane: machine-intelligence-morphogenesis-v1.
Witness: `gmi_microscope/state_space_witness.py`.
Receipt: `microscopes/results/STAGE_STATE_SPACE_V1.json`.
Executed on `laptop-billy`; receipt md5-verified. Reproduced in CI.

`GMI_FINITE_STATE_DERIVATION_V1.md` established that the minimal number of
states is the quotient index, and that recurrent state beats carrying history
once the history exceeds `|Q|`. That leaves the question this family is actually
about: having got `|Q|` states, **how cheaply can the update be written?**

## Compression is a counting fact; affine update is not

`|Q|` distinctions fit in `⌈log₂|Q|⌉` bits — always. Whether the *transition* is
affine in that encoding is a separate question, answered by searching **every**
code assignment and **every** GF(2) matrix and bias, not by inspecting the
table for structure.

| obligation | \|Q\| | one-hot | bits | affine update |
|---|---:|---:|---:|---|
| `parity_b` | 2 | 2 | 1 | ✅ |
| `count_b_mod4` | 4 | 4 | 2 | ✅ |
| **`ends_with_ab`** | **4** | 4 | **2** | **✗** |

> A compressed state is always available. An **affine** update is not.

**`ends_with_ab` is the instructive negative.** It has the *same* state count as
the mod-4 counter and the *same* 2-bit encoding, and yet **no assignment of
codes** makes its update affine. Its transitions are not invertible — several
states go to the same successor on `b` — and an affine map over GF(2) with a
fixed matrix cannot merge states and still separate them later.

That pair is the whole result: identical in every resource coordinate, separated
only by transition structure.

## Long horizon: state against attention against explicit memory

| length `n` | state (work) | attention (work) | memory (storage) |
|---:|---:|---:|---:|
| 8 | 8 | 36 | 8 |
| 16 | 16 | 136 | 16 |
| 64 | **64** | **2080** | 64 |

State storage stays at **2 bits** at every length, while explicit memory grows
to 64 slots and attention's work grows quadratically.

> The state-space advantage is not that it is cleverer. It is that a fixed state
> is the only one of the three whose cost **does not grow with the horizon** —
> and it buys that by *discarding* everything the quotient says is not needed,
> which is exactly what the other two decline to do.

**That is also its limit.** Where the obligation's quotient is infinite or grows
with `n`, there is no fixed state to compress into, and attention or memory is
not a worse choice but the only one. This witness does not exhibit such an
obligation, so that half is **stated and not shown**.

## Neutral recovery in a long-sequence ecology

Candidates are described by what they carry between symbols and what they do per
symbol. No state-space, recurrence or attention macro appears.

| length `n` | fixed carry + O(1)/symbol | carry everything | cheapest |
|---:|---:|---:|---|
| 8 | **10** | 44 | fixed carry |
| 64 | **66** | 2144 | fixed carry |

The cheapest shape carries a fixed number of bits and does constant work per
symbol. That object — a small state advanced once per input — is a state-space
model, selected by cost from a description that never names one.

**Stated honestly**: the fixed carry wins at *every* length tested, so this
recovery shows what is **selected**, not a crossover. A crossover would need an
obligation whose quotient grows with `n`, and this witness does not construct
one. The claim is correspondingly narrower than the neutral recoveries in B16
and B13, where both shapes win somewhere.

## Scope

- Three obligations with `|Q| ≤ 4`, binary alphabet. Affine realizability is
  searched over all injective code assignments and all GF(2) matrices at that
  width — exhaustive for these sizes, not a general algorithm.
- Affinity is tested over GF(2) only. A machine allowed a larger ring (`Z₄`, say)
  might realize transitions this search rejects, so `✗` means *not affine over
  GF(2) at this width*, not *not linear in any sense*.
- The cost model charges attention one visit per earlier symbol and memory one
  slot per symbol. The *orderings* are the result; the constants are not.
- Box 4 of B9 ("compare against attention and explicit memory") is answered on
  **work and storage**, not on expressiveness. An attention machine can express
  obligations a fixed state cannot, and that comparison is not made here.

**Falsifier.** Exhibit a code assignment making `ends_with_ab` affine over GF(2)
at width 2; or an obligation with a finite quotient where a fixed state does
more work than revisiting the whole history.
