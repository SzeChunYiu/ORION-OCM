# L1 meaning-graph bound v1 — historical exact canonicalization

Issue [#165](https://github.com/SzeChunYiu/ORION-OCM/issues/165) L1 boxes:

- meaning graphs beyond historical small bound
- exact canonicalization / explicit bound

L1 linguistic G2 v1/v2/v3 recorded `meaning_graphs_beyond_bound =
CANNOT_CHECK_MICROWORLD_SMALL` because those capsules never produced a
graph with more than three nodes. This capsule **does not retune** those
studies and does not overwrite their `RESULT.json` (nor v4 if present).

**L2/L3 stay locked. No corpus-scale N1. No neural net.**

## Independent historical bound (not invented)

Production `src/ocm/language/meaning.py` defines

```text
MAX_EXACT_CANONICAL = 7
```

Exact `canonical(g)` enumerates colour-class vertex orderings only for
`|V| ≤ 7`. Larger fragments raise `CannotCheck`. That cutoff is independently
recorded in:

- `docs/theorems/OCM_LANGUAGE_OBLIGATION_REGISTRY_V1.json` KS-T34
- `research/l0-bootstrap-audit-v1` inventory `G5_canonical_max`
- `tests/m3/test_meaning_graph.py`

This capsule **raises that finite bound as the measurement standard**. It
does not invent a second node cap. If that constant were absent, the honest
terminal would be `CANNOT_CHECK_NO_HISTORICAL_BOUND`.

There is no independent historical **edge** bound. None is invented.

## What is measured

Production `ocm.language` graphs on a planted microworld:

1. Required M3 `example_meanings()`.
2. `microworld.generate()` corpus.
3. `interpret()` under production `seed_constructions()` + bootstrap lexicon.
4. A planted recursive stacked-adjective NP family (production
   `Construction` / `match_constructions` / `interpret`, new salt, new
   adjectives). This is the mechanism that can grow `|V|` past 7 — not a
   salt of v1–v3.

If any production-pipeline graph has `|V| > MAX_EXACT_CANONICAL`, the
terminal is `GRAPH_BOUND_EXCEEDED_AT_SCOPE`. Production `canonical()` and
therefore `interpret()` fail closed on those graphs.

## Exact canonicalization at the bound

- `|V| = 7`: production `canonical` succeeds and is relabel-invariant.
- `|V| = 8` identical colours: production `canonical` raises `CannotCheck`.
- WL-1 is not canonical (existing C6 vs 2·C3 collision witness).

## Honest bound raises (mechanisms, not salts)

Production already contains a second exact labeller for **trees**:
`ocm.language.meaning_tree.canonical_any` (Aho–Hopcroft–Ullman). Digests at
or below 7 nodes stay the MEG-24 SHA-256; above the bound, trees get a
`tree:` digest. This capsule measures that mechanism on a finite explicit
tree size (16). It does not claim an infinite bound.

The historical node cutoff is a **work** cutoff: worst-case 7 identical
colours is `7! = 5040` orderings. Restating the bound as “colour-class
permutation count ≤ 5040” (same enumerator, no `|V|` gate) is the same
algorithm. Distinct-colour graphs beyond 7 then canonicalize; 8 identical
colours still fail (`8! > 5040`). Worst-case node count is unchanged.
Production `canonical()` is **not** patched; `src/` is not edited. The
restated bound is recorded, not silently adopted as the production cutoff.

Typical clause graphs with both roles and modifiers are **not** trees, so
AHU does not rescue the planted stacked-NP clause.

## Valid terminals

```text
GRAPH_BOUND_EXCEEDED_AT_SCOPE
GRAPHS_INSIDE_HISTORICAL_BOUND_AT_SCOPE
CANNOT_CHECK_NO_HISTORICAL_BOUND
```

## Run

```sh
python3 -B -m unittest discover -s research/l1-meaning-graph-bound-v1 -p 'test_*.py' -v
python3 -B research/l1-meaning-graph-bound-v1/experiment.py research/l1-meaning-graph-bound-v1/RESULT.json
```
