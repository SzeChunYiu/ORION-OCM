# A library earns on the search ledger and nowhere else (B15)

Date: 2026-09-14. Lane: machine-intelligence-morphogenesis-v1.
Witness: `gmi_microscope/program_library_witness.py`.
Receipt: `microscopes/results/STAGE_PROGRAM_LIBRARY_V1.json`.
Derived by a parallel worker. Witness and receipt md5 **independently
reproduced** on `laptop-billy` (exit 0, 0.1 s); 49 assertions; stdout and
receipt byte-identical across repeats.

## The delta, stated as a loss

B14 priced compositional closure on the **serving** ledger; B16 priced
compile-versus-search on the **serving** ledger. A retained chunk is a strict
loss on both:

| ledger | without chunk | with chunk |
|---|---:|---:|
| closure (functions reachable) | **209** | **209** — zero new |
| serving cost | **48 cells** | **64 cells** |

For all 24 candidate chunks the closure is unchanged *as a set*.

> A library adds nothing you could not already build, and costs more to serve.
> **It can only earn on the search ledger** — and that is the whole of B15.

The world is B14's `{rot, setb1, swap12}` carried from `{a,b}³` to `{a,b}⁴`,
**gated on reproducing B14's ladders exactly** (`[3,11,22,31,34,34]` and
`[3,3,3,3,3,3]`), so it is provably the same family rather than a lookalike.

## The paying window is bounded at both ends

A length-`ℓ` chunk turns depth `L` into `L − ℓ + 1` and raises branching 3 → 4.
It pays iff `N₄(L−ℓ+1) < N₃(L)`:

| chunk length | paying depths |
|---:|---|
| 2 | **[2, 5]** |
| 3 | **[3, 10]** |
| 4 | **[4, 14]** |

Too shallow and there is nothing to shorten; too deep and the extra branching at
every level outruns the levels saved.

> The program-length / search-burden relation has an **optimum**, not a monotone
> trade.

Checked against a measurement that knows nothing of that arithmetic: every
paying chunk has length 3, and all 8 length-2 chunks lose.

**Shortening is not helping.** 23 of 24 chunks shorten obligations they still
make *more expensive* — `rot+rot` shortens 150 and helps 87.

## Recurrence sets the tax base, not the usefulness

Only **1 of 24** chunks pays over the full 209-obligation corpus. But every
chunk pays on *some* corpus, and the break-even corpus size `n*` spans **51×**
across the 23 chunks whose ceiling is bracketed.

The twins are drawn **from chunks that lose over the full corpus**, at both
lengths, so nothing separates them but recurrence:

| chunk length | recurrence | `n*` |
|---:|---:|---:|
| 2 | 1 | **4** |
| 2 | 95 | **195** |
| 3 | 20 | **85** |
| 3 | 109 | **207** |

> Recurrence does not make a chunk useful — a one-use chunk pays on any corpus
> of ≤ 4. It sets **how many unrelated obligations the chunk can be taxed on
> before it stops paying.**

## Neutral recovery

The searcher gets only the move tables and the obligations' I/O tables — never a
short answer. 37 retention plans, machine-checked for forbidden vocabulary.

**"Store nothing" wins on 2 of 3 obligation sets and loses on the third**, where
8 plans beat it — so the loss is not one lucky candidate. Its winner
(`swap12+setb1+rot`) differs from the most frequent 2-run (`rot+rot`, 55), from
the most frequent 3-run (`rot+setb1+rot`, 33), **and** from the full-corpus
winner. A chooser handed the answer would have returned one of those.

## Scope

- One world, `|D| = 16`, `k = 3`, closure 209, depths 1–8. The chunk repertoire
  is 24 candidates over that generator set.
- Search burden is counted as nodes at branching 3 versus 4. The *window* and
  its two-sidedness are the result; its exact endpoints move with the branching
  model.
- `n*` for the single open-ceiling chunk is a **lower bound** — it ran out of
  taxed obligations inside this world.

**Falsifier.** Exhibit a chunk that enlarges the closure, or one that lowers
serving cost; or a paying window unbounded above; or a corpus on which no chunk
whatsoever pays.
