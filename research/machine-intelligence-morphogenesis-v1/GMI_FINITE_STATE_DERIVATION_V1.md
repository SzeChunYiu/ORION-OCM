# Finite-state machines, derived rather than assumed (B2)

Date: 2026-09-14. Lane: machine-intelligence-morphogenesis-v1.
Witness: `gmi_microscope/finite_state_witness.py`.
Receipt: `microscopes/results/STAGE_FINITE_STATE_V1.json`.
Executed on `laptop-billy`; receipt md5-verified. Reproduced in CI.

The developmental quotient theorem says the coarsest response-preserving
quotient is the unique minimal representation. Specialised to obligations over
**sequences**, that quotient *is* the Nerode congruence. So the minimal
automaton is not a modelling choice imported from automata theory — it is what
the quotient theorem already says, read on a sequential ecology.

No automaton is assumed anywhere below. Obligations are given only as "what
response does this history demand"; everything else is computed by exhaustive
enumeration.

## 1–2. Minimal state, and a tight lower bound

| obligation | \|Q\| | stateless suffices |
|---|---:|---|
| `constant` | 1 | yes |
| `last_symbol` | 2 | yes |
| `parity_b` | 2 | no |
| `count_b_mod3` | 3 | no |
| `ends_with_ab` | 3 | no |

The lower bound is a **fooling set**: pairwise-inequivalent prefixes, each pair
separated by an *exhibited* continuation. Any machine merging two of them would
answer identically on that continuation, and one answer would be wrong. Every
pair is separated for every obligation, and the fooling set's size equals the
quotient index.

## 3. The upper bound meets it

The machine is built straight from the quotient — states are classes,
transitions are where a class goes when a symbol arrives — then replayed on
every string up to length 8. It reproduces the obligation exactly, using
precisely `|Q|` states.

> Lower bound and upper bound coincide on every obligation, so the quotient
> index is the **exact** state cardinality, derived and not assumed.

## 4. When a stateless policy fails

A stateless policy sees only the current symbol. Best achievable accuracy:

| obligation | stateless accuracy |
|---|---:|
| `constant` | **1.0000** |
| `last_symbol` | **1.0000** |
| `ends_with_ab` | 0.7515 |
| `count_b_mod3` | 0.6673 |
| `parity_b` | **0.5029** |

Parity collapses to chance — the classic result, here as a consequence rather
than an example.

> **Stateless suffices exactly when the obligation is a function of the current
> symbol alone.** It fails whenever the quotient separates two prefixes that end
> in the *same* symbol, which is what makes state necessary rather than
> convenient.

## 5. Recurrent state versus carrying explicit history

Recurrent state costs `|Q|` once. Explicit history costs the length retained,
which grows with the sequence. For `count_b_mod3` (`|Q| = 3`):

| sequence length | 1 | 2 | **3** | 4 | 8 | 16 |
|---|---|---|---|---|---|---|
| cheaper | history | history | **tie** | state | state | state |

> **The crossover sits at `|Q|` itself.** Recurrent state pays exactly once the
> history it replaces is longer than the number of distinctions that history was
> ever used to make.

That is the same shape as PVR-3: retained structure earns its keep only past a
break-even fixed by what it replaces.

## 6. Neutral recovery, by brute force

**A first version of this section was vacuous** and is recorded here because
the failure is instructive: it asked a helper for the cheapest `k`, and the
helper returned the quotient index it had been handed. That is a restatement
wearing the costume of a search.

It is replaced by exhaustive enumeration over **actual machines** — every
transition table and every accept assignment, for each `k` in turn. The search
is told only *does this meet the obligation*, never what the index is.

| obligation | brute-force `k` | quotient index | match |
|---|---:|---:|---|
| `parity_b` | 2 | 2 | ✅ |
| `count_b_mod3` | 3 | 3 | ✅ |
| `ends_with_ab` | 3 | 3 | ✅ |
| `constant` | 1 | 1 | ✅ |
| `last_symbol` | 2 | 2 | ✅ |

And the direction that actually proves minimality — **no machine with one fewer
state works**, shown by exhausting all of them:

| obligation | states tried | any machine works |
|---|---:|---|
| `parity_b` | 1 | **no** |
| `count_b_mod3` | 2 | **no** |
| `ends_with_ab` | 2 | **no** |
| `last_symbol` | 1 | **no** |

> A search told only "meet the obligation, pay for states" returns exactly the
> minimal automaton, and no cheaper machine exists at all. Finite-state control
> is what the accounting **selects**, not what was inserted.

## Scope

- Binary alphabet; strings to length 9 for the quotient, 6 for the brute-force
  search. The witness checks that this horizon separates the registered
  obligations, but a longer-memory obligation would need a longer horizon.
- The brute-force enumeration is capped at 3 million machines and refuses to
  claim beyond what it enumerated, so `|Q| > 3` obligations are excluded from
  section 6 rather than asserted.
- Five obligations, chosen to span index 1 to 3 and to include two that are
  stateless-solvable. They are not a sample of any natural distribution.
- Myhill–Nerode is the parent here and is not re-proved; what is shown is that
  the GMI quotient, defined without reference to automata, lands on it.

**Falsifier.** Exhibit an obligation where the quotient index and the smallest
brute-force machine differ, or one where a stateless policy achieves perfect
accuracy while the quotient separates two same-ending prefixes.
