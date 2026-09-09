# G2.2 donor / library-learning parent boxes

Issue [#165](https://github.com/SzeChunYiu/ORION-OCM/issues/165) G2.2 still
unchecked: Stitch-style library learning, DreamCoder-class abstraction,
anti-unification, grammar induction, e-graph / rewrite-derived abstraction,
program compression, domain-native method induction, and a strong conventional
parent on the **same** primitive library `{inc, dec, double, square}`, each
with `ADOPT / ADAPT / GENERALIZE / REJECT / OPEN`, origin identity,
prior-information charge, integration cost, and residual after subtraction.

## What is already known (not retuned)

`research/g2-acquisition-economics-v1/` already asked whether a corpus scan can
replace the 9,010,526-attempt utility tournament. Compression / Stitch-style
**FAILED the argmax**. SEARCH_AWARE **succeeded**.

| selector | ρ with utility | chose | utility rank | acquisition |
|---|---:|---|---:|---:|
| `FREQUENCY` | +0.101 | `dec square` | 13 / 16 | 16 token ops |
| `COMPRESSION_PER_TOKEN` | +0.269 | `dec square` | 13 / 16 | 4,608 token ops |
| `MDL_COMPRESSION` | +0.518 | `dec square` | 13 / 16 | 4,608 token ops |
| **`SEARCH_AWARE`** | **+0.531** | **`square dec square`** | **1 / 16** | 4,608 token ops |
| *tournament* | — | `square dec square` | 1 / 16 | **9,010,526 attempts** |

```text
square dec square (tournament and SEARCH_AWARE)   test saving  +275,329
dec square        (every compressor)              test saving  -609,213
```

That is an **argmax failure, not a correlation failure**. The missing term is
grammar widening, countable in closed form (depth-7 word count, 4 primitives,
budget 7): primitives 21,845; + length-2 macro 30,348 (+39%); + length-3 23,451
(+7%). This capsule **cites that receipt** and refuses to retune it. The
9-million-attempt tournament is **not rerun**. Importing the receipt is stronger.

## What this capsule adds

Tiny **research parents** that instantiate the *idea* of those systems on the
same ecology, without pip-installing DreamCoder, Stitch, or egg:

| G2.2 box | Tiny parent | object | disposition |
|---|---|---|---|
| Stitch-style library learning | per-token corpus compressor | `dec square` | **REJECT** |
| DreamCoder-class abstraction | one MDL sleep, no wake/recognition | `dec square` | **REJECT** |
| anti-unification | LGG of two training programs + pair vote | `dec square` | **REJECT** |
| grammar induction | count of right-linear productions | `dec square` | **REJECT** |
| e-graph / rewrite-derived abstraction | hashcons + `inc∘dec = id` saturate | `dec square` | **REJECT** |
| program compression | MDL description length | `dec square` | **GENERALIZE** (scan → search-aware MDL) |
| domain-native method induction | #192 fragment miner / frequency | `dec square` | **GENERALIZE** (keep mining, change admission) |
| strong conventional parent, same library | SEARCH_AWARE | `square dec square` | **ADOPT** (tournament twin: **ADAPT**) |

Full Stitch / DreamCoder / egg runtimes remain `OPEN` / `CANNOT_CHECK` as
software; the tiny parents are what earn the compare boxes.

Each parent is charged:

- **origin identity** — which parent proposed the fragment
- **prior-information** — the 48 verified training programs and `{inc,dec,double,square}`
- **integration cost** — grammar-width delta at depth 7 (length-2 costs +8,503 words; length-3 costs +1,606)
- **residual after subtraction** — what remains once that parent is granted

Validation utility is **looked up** in the frozen tournament table. Fragments
outside the frozen 16-candidate pool are `OPEN` on utility: the tournament is
not rerun to score them.

## Terminal

```text
CONVENTIONAL_LIBRARY_PARENTS_SUBORDINATE_TO_SEARCH_AWARE
```

ADOPT SEARCH_AWARE. REJECT compression / Stitch / DreamCoder-class as a
selection objective. GENERALIZE the scan. That **earns** the G2.2 compare boxes
without claiming OCM invented library learning. SEARCH_AWARE is a conventional
parent.

Not a new G2.4 causal-reuse positive. Not a production change.

## Run

```sh
python3 -B -m unittest discover -s research/g2-abstraction-parents-v1 -p 'test_*.py' -v
python3 -B research/g2-abstraction-parents-v1/experiment.py --out research/g2-abstraction-parents-v1/RESULT.json
```
