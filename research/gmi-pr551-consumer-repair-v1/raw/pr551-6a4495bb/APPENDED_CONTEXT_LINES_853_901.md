
### `Z8`'s gradient-absence claim is RETRACTED — two defects in my own scanner

The other lane's `research/gmi-b6-consumer-census-v1/` corrects the `Z8` section above on two counts.
Both verified independently here before acceptance, and both are worse than stated.

**Defect 1 — the consumer whitelist was wrong, and partly fictional.** I tested for numeric consumers
`{DOT, LINEAR}`. `AFFINE` is `("T", (vec, vec), vec, ("width",))` — a parameter-consuming transform of the
same shape as `LINEAR` — and I omitted it, even though it appears in consumer lists I printed and read.
Worse, **`DOT` is not a kind in this IR at all.** I built the whitelist from a source *comment* ("dot
product of input with a DENSE parameter vector", which describes `LINEAR`) rather than from `morph.KINDS`.
So the test checked one real kind and one that does not exist. Their count of six parameter-port
adjacencies in those 17 rows, against my two, is the corrected figure.

**Defect 2 — the scope was arm receipts, and I wrote it as the searched population.** My scan covered
`final_best_genotypes` and `first_admissible` graphs from the arm receipts: best-per-carrier elites and
one admissible machine per arm. That is a tiny, heavily selected slice. Scanning the **source archives**
instead:

> **34 of 677 archive cells contain `GRAD`**, across 9 of the 11 source archives.

So "`GRAD` appears in none of 70 searched graphs" was true of my sample and false as the claim I drew
from it. Gradient-bearing machines survive into archives routinely, at about 5 % of cells. **"Search
never assembles the gradient primitive" is retracted.** (The other lane reports eight such graphs in five
retained archives; scanning the live archives finds 34 in nine — same correction, larger scope.)

These are the two failure modes this programme's own rules name — validate a checker on real data before
trusting it, and justify the scope of an absence claim rather than inferring it from whatever the search
returned.

### What the gradient cells actually look like, now that they are counted

| | count |
|---|---|
| `GRAD`-bearing archive cells | **34** |
| with `DENSE` feeding the `GRAD` input | **33 of 34** |
| with the `GRAD` **output consumed** by anything | **8 of 34** |
| reaching θ = 0.85 on the archive's standard capability | **0 of 34** |

The structural story therefore survives its retraction in a **weaker and more precise** form. The
generator does assemble `DENSE → GRAD` constantly — 33 of 34 cells wire the parameter block into the
update law, which is the hard half of a learner. What is missing is the other end: only 8 of 34 route
the update *back out*, and the best of those consumers is a `LOOKUP`, not a predictor. And none of the 34
reaches θ even on the permissive standard-only reading, let alone the six-intervention bar.

So the corrected statement is: **gradient machines are assembled and retained; none of the retained ones
is admissible.** That is consistent with the independent row measurement above — no registered
`gradient_net` is admissible on these ecologies either — and it reaches the same place by a route that no
longer depends on a claim of absence.
