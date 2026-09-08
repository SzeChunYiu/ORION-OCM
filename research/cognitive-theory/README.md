# research/cognitive-theory — theory-to-empirics registry

Issue: [#145](https://github.com/SzeChunYiu/ORION-OCM/issues/145), work package GUO-D1.
Empirical parent: [#143](https://github.com/SzeChunYiu/ORION-OCM/issues/143).
Publication constitution: [#144](https://github.com/SzeChunYiu/ORION-OCM/issues/144).

`THEORY_EMPIRICAL_REGISTRY_V1.md` is the readable view; the JSON beside it is the machine-readable
one. Both are generated from `registry_data.py`. Edit the source and re-run `python registry.py`;
CI regenerates them, so a hand-edited registry fails source custody.

No theory claim may enter manuscript prose without a row here, and every row names a concrete rung
of #143 capable of killing it.

## What this registry is for

It is written the unusual way round. Most theory registries are populated with statements someone
hopes to prove, and their status column stays `OPEN` for years. This one leads with the statements
the programme has already refuted, because those were the load-bearing ones and they turned out not
to be. Six of thirteen rows are `REFUTED`, two more are parent-owned or parent-sufficient, and one
is supported only at its declared scope. A registry whose refuted rows are missing is a wish list,
and a test in `test_registry.py` asserts that the killed rows outnumber the surviving ones.

## Rows worth reading first

- **TH-04** and **TH-09** are the two refutations that generated the current experiments. Leave-one-out
  attribution is incomplete, and flat surface fragments are the wrong level at which to look for
  reusable structure. Their successors, TH-05 and TH-10, are open and under test.
- **TH-06** is a construction-validity result rather than a claim about any system: a benchmark that
  plants a defect and labels the world by which defect was planted was wrong on nearly half of
  worlds, in both directions.
- **TH-08** is the only row currently supported, and only at its scope.

## Running

```
PYTHONPATH=research/cognitive-theory python -m pytest -q research/cognitive-theory
PYTHONPATH=research/cognitive-theory python research/cognitive-theory/registry.py
```

Stdlib only, Python 3.11+.
