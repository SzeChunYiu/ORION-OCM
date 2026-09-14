# When modelling another agent pays, and how deep it goes — I7 (#602)

Date: 2026-09-14. Status: **DERIVATION + EXACT WITNESS WITH TWO NEGATIVE TWINS**. Addresses the standing
gap the audit recorded for item 16 / I7: *"no derivation that other adaptive agents force models of their
goals, beliefs, intentions or reliability."*

An agent model is **retained state**, so it is charged like everything else and must pay for itself. That
is the whole approach; nothing about minds is assumed.

## 1. Modelling pays only under intermediate uncertainty

Two partner types, two actions, a signal of accuracy 0.85 about the type, model cost 0.4:

| prior on cooperative | fixed policy | with a model | model worth it? |
|---:|---:|---:|---|
| 0.1 | 1.000 | 0.600 | no |
| 0.3 | 1.000 | 0.795 | no |
| **0.5** | 1.000 | **1.225** | **yes** |
| **0.7** | 1.500 | **1.655** | **yes** |
| 0.9 | 2.500 | 2.100 | no |

> **An agent model pays only under intermediate uncertainty about the partner.** Near certainty in either
> direction, the fixed policy already does the right thing and the model is pure cost.

That is not a caveat — it is the derivation of *when* other agents force models, which is exactly what the
box asks. They force models when you are genuinely unsure about them, and not otherwise.

## 2. Two distinct negative twins

I7 asks for social negative twins where agent models are unnecessary. The witness produces **two, with
different mechanisms**:

* **Near-certainty** (priors 0.1 and 0.9 above) — the model is *redundant*: it would have to overturn an
  already-correct action to earn anything.
* **Uninformative partner** (signal accuracy 0.5, i.e. behaviour independent of us) — the model is
  *empty*: it costs **exactly 0.400 = its price** at every prior, and buys nothing.

The second is the cleaner control, because the loss is precisely the model's cost with no residual — which
is what "worthless" should look like when the accounting is right.

## 3. Recursive belief depth terminates on resources

Each level of "I think that you think…" costs 0.3 and yields diminishing returns:

| depth | cumulative gain | cost | net |
|---:|---:|---:|---:|
| 0 | 0.000 | 0.000 | 0.000 |
| 1 | 0.900 | 0.300 | 0.600 |
| **2** | 1.250 | 0.600 | **0.650** |
| 3 | 1.350 | 0.900 | 0.450 |
| 5 | 1.374 | 1.500 | −0.126 |

> **Optimal depth is 2, and the recursion terminates on resources rather than on being ill-founded.**

This matters because recursive belief is often treated as a regress to be stopped by fiat. Here it stops
for the same reason every other search stops in this corpus: **the next level does not pay for itself.**
It is the value-aware rule again — the fourth setting, after planning depth, replanning and retrieval.

## 4. Scope

**Derived:** the necessity condition for agent models, two negative twins, partner reliability as the
signal-accuracy parameter, hidden-goal inference as type inference, and the resource ceiling on recursive
depth.

**Not derived:** hidden-*belief* inference as distinct from hidden-goal; intention and action prediction;
cooperation-versus-competition regimes; and strategic deception. Four of I7's nine boxes remain.

**Assumptions:** two types, two actions, a single scalar signal accuracy, and a fixed per-level cost for
recursion. The diminishing-returns profile in §3 is **stipulated, not derived** — the *shape* of the
result (a finite optimum) follows from any diminishing profile plus a positive per-level cost, but the
specific optimal depth of 2 is a property of the numbers chosen and should not be quoted as a general
depth limit.

**Falsifier:** a partner distribution where an informative model loses at intermediate uncertainty, or a
cost structure with positive per-level price and diminishing gain where optimal depth is unbounded.
