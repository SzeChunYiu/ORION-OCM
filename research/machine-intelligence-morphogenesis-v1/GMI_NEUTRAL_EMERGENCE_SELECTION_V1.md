# What neutral search selects for, measured — memory yes, gradient no, attention no

Date: 2026-09-13. Addresses checklist items 35 (neutral emergence: reward only task performance, classify
structure afterward), 6 (derive memory systems), 23 (derive learning laws), 5 (derive attention).

Nothing in the search rewards any architectural property. The archive selects on capability and fills
cells by descriptor. So comparing **how often the generator proposes a primitive** against **how often it
survives into archives** isolates selection from supply.

## Method

* **Proposal prevalence**: 4 000 genotypes drawn through the same `morphgen.mutate` chain `b1.search`
  uses, counting the fraction of graphs containing each kind.
* **Survivor prevalence**: all 677 archive cells across the eleven `RV-377-180` source receipts, same
  measure.

## Result

| kind | proposed | survives | ratio | reading |
|---|---:|---:|---:|---|
| `INSERT` (store write) | 0.103 | 0.644 | **6.25×** | **strongly selected for** |
| `DENSE` | 0.219 | 0.623 | 2.84× | *confounded — see below* |
| `NEAREST` (retrieval) | 0.294 | 0.693 | **2.36×** | **strongly selected for** |
| `PROGRAM` | 0.322 | 0.421 | 1.31× | mildly for |
| `VERIFY` | 0.707 | 0.727 | 1.03× | neutral |
| `SCORESELECT` | 0.291 | 0.261 | 0.90× | slightly against |
| `ABSTAIN` | 0.924 | 0.742 | **0.80×** | **selected against** |
| `GRAD` (gradient update) | 0.104 | 0.050 | **0.48×** | **selected against** |
| `GATE` | 0.115 | 0.043 | **0.37×** | **strongly against** |

**The `DENSE` row is excluded from every claim below.** Carrier kinds change the archive's descriptor, so
they occupy their own cells and are structurally guaranteed representation. `DENSE`, `TABLE`, `KVSTORE`
and `PROGRAM` are carriers; `INSERT`, `NEAREST`, `ABSTAIN`, `GATE`, `VERIFY` and `GRAD` are not, so their
enrichment or depletion cannot be explained by cell structure.

## What this establishes

**Memory is derived, not assumed (item 6).** The two most strongly selected non-carrier primitives are a
store **write** (6.25×) and a **retrieval** (2.36×). Nothing rewards memory; task performance alone
enriches both ends of a store-and-retrieve loop by large factors. This is the cleanest emergence result
in the corpus, and it is consistent with every other memory finding today — memory admissible on a quarter
of the construction space, the exhibited coefficient recovery turning out to be a key-value machine.

**Gradient learning is selected against (item 23).** `GRAD` is depleted to 0.48×. Combined with today's
other measurements — 33 of 34 gradient-bearing archive cells wire the parameter block into the update law,
only 8 route it back out, none is admissible, and no registered gradient net is admissible on any tested
ecology — the picture is consistent: this ecology class does not reward gradient updating, so neutral
search discards it.

**Attention does not emerge here, and item 5's own antecedent explains why.** `GATE` (0.37×) and
`SCORESELECT` (0.90×) are both depleted, so no selective-processing structure is being favoured. Item 5
predicts attention from *limited computation plus excessive possible information*. These ecologies present
sixteen inputs over sixteen events — there is **no information overload**, so the antecedent is not
satisfied and the absence of attention is what the item predicts rather than a failure of it. **Testing
item 5 requires an ecology where the input space exceeds the compute budget**, which this construction
does not provide. That is a concrete, named gap in the *ecology set*, not in the theory.

**Abstention is selected against (bears on item 14).** `ABSTAIN` is proposed in 92 % of genotypes and
survives in 74 %. Declining to answer is not rewarded under this scoring, which charges capability over all
inputs. So the corpus's metacognitive primitive exists but is under negative selection here — again a
property of the ecology's scoring, not evidence that metacognition is underivable.

## Scope

One construction, one basis, pooled across eleven source archives on five ecologies. Prevalence is measured
as "fraction of graphs containing the kind", not as a count of instances. Archive cells are best-in-cell
rather than globally best, which is what makes them the right population for a selection measure.
