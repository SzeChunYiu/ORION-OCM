# Evolvability Theory synthetic falsification lane

This directory supports:

- historical V0: `docs/spec/MACHINE_EPISTEMICS_EVOLVABILITY_THEORY_V0.md`
- current steering theory V0.2: `docs/spec/MACHINE_EPISTEMICS_EVOLVABILITY_THEORY_V0_2.md`

Status: **E2 exploratory synthetic only.** Nothing here establishes that current OCM has a self-evolution advantage, beats neural systems, or beats AutoML/open-ended-search parents.

Run:

```bash
python research/evolvability-theory-v0/synthetic_evolvability.py \
  --output /tmp/SYNTHETIC_RESULTS_V0_2.json
```

Committed outputs:

- `SYNTHETIC_RESULTS_V0.json` — historical V0 output.
- `SYNTHETIC_RESULTS_V0_2.json` — current V0.2 output.
- `LITERATURE_COLLISION_MATRIX_V0_2.md` — strongest-parent subtraction for the revised theory.

V0.2 pressures five claims:

1. **diagnosis value:** discriminating probes help only when the search they remove exceeds their information/resource cost;
2. **factorization phase boundary:** sparse/stable coupling can improve the quality/resource frontier while dense coupling/drift erase the advantage;
3. **self-identifiability:** Fano's inequality creates a lower bound on diagnostic information, so oracle-ablation and real-failure settings cannot share a claim without accounting for information channel strength;
4. **self-intervention learning:** resolved self-interventions can make future diagnosis much cheaper, but a direct probabilistic parent can match/beat the explicit self-graph, especially on compositional faults;
5. **stepping stones:** strict monotonic local self-improvement can be trapped; a shadow archive improves reachability, but a conventional broader-search parent dominates the naive archive in the registered deceptive fixture.

The revised theory therefore uses the triad:

```text
κ = effective cognitive coupling / locality
Ω = self-identifiability per diagnostic cost
χ = effective repair-search space
```

and asks whether developmental experience moves a persistent machine toward a regime with lower future acquisition and self-change cost.

Strongest-parent closure remains open. Real OCM studies must compare against active diagnosis/causal discovery, direct empirical/probabilistic self-models, AutoML/program repair, MARS-style reflective credit assignment, DGM/open-ended archives, learned abstraction/library parents, and adaptive neural/Transformer systems under #144.
