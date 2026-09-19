# AE9 parent-ownership disclosure

Assimilation-first: the parent work below is absorbed and credited, and the
residual contribution of this tranche is stated afterwards. **Nothing in the
list is claimed novel.**

## Strongest parents

| parent | what it owns | citation |
|---|---|---|
| Emergent-ability phenomenology | the observation being audited: sharp apparent onsets of capability with scale | Wei, Tay, Bommasani, Raffel, Zoph, Borgeaud et al., *Emergent Abilities of Large Language Models*, TMLR 2022. arXiv:2206.07682 |
| The metric-artifact mechanism | that a discontinuous or strongly nonlinear scoring rule applied to a smoothly improving underlying quantity manufactures an apparent sharp emergence | Schaeffer, Miranda, Koyejo, *Are Emergent Abilities of Large Language Models a Mirage?*, NeurIPS 2023. arXiv:2304.15004 |
| Grokking | delayed generalization long after training performance saturates | Power, Burda, Edwards, Babuschkin, Misra (2022). arXiv:2201.02177 |
| Grokking as internal reorganization | that the delayed generalization coincides with the formation of an internal structure | Nanda, Chan, Lieberum, Smith, Steinhardt, ICLR 2023. arXiv:2301.05217 |
| Representational-geometry measurement | measuring representational structure on real neural systems, which this tranche deliberately does **not** do | Kriegeskorte, Mur, Bandettini, Frontiers in Systems Neuroscience 2:4 (2008), doi:10.3389/neuro.06.004.2008; Raghu, Gilmer, Yosinski, Sohl-Dickstein, NIPS 2017, arXiv:1706.05806; Kornblith, Norouzi, Lee, Hinton, ICML 2019, arXiv:1905.00414 |
| Partition-based comparison | the pair-counting metric on set partitions and its metric properties | Meila, Journal of Multivariate Analysis 98(5):873-895 (2007), doi:10.1016/j.jmva.2006.11.013 |
| Usable and computationally bounded information | that the content of a representation is relative to a decoder class and a budget | Xu, Zhao, Song, Stewart, Ermon, ICLR 2020. arXiv:2002.10689 |
| Boolean junta learning | exact junta arity, essential variables, and the hardness of parity for low-arity readouts | Mossel, O'Donnell, Servedio, JCSS 69(3):421-434 (2004), doi:10.1016/j.jcss.2004.04.002; O'Donnell, *Analysis of Boolean Functions*, CUP 2014, doi:10.1017/CBO9781139814782 |

## What is NOT claimed novel

- That an apparent sharp emergence can be an artifact of the scoring rule.
- That grokking exists, or that it coincides with internal reorganization.
- That representational structure can be compared by partition metrics.
- That usable information depends on the decoder class and its budget.
- That parity is hard for readouts of low junta arity.
- Any statement whatever about a real neural system.

## The residual

The parents own every mechanism used here. What this tranche adds is small,
exact, and machine-checked:

1. **One roster on which all three readings of `emergence` coexist and are
   separated by a discrete quantity.** The thresholded-metric artifact, the
   phase-like reorganization and the grokking-like delay are instantiated on a
   single registered finite construction, and the line between them is drawn on
   structural invariants — `CELLS`, `INVARIANCE`, `READOUT_ARITY` — which take
   values in finite discrete sets. The artifact and the transition are
   therefore separated by an integer, not by a threshold on a graded quantity
   and not by an argument.

2. **Architecture-independence proved in both directions rather than
   asserted.** Equality of markers under equal partitions is structural, and is
   also witnessed on two materially different learners; exact invariance under
   arbitrary injective re-encoding of the code set is exhibited; and
   non-degeneracy — that a genuine change of partition always moves a marker —
   is established unconditionally through the partition metric and exhibited on
   all `15` pairs of the registered family. The second direction is what stops
   the markers from being degenerate constants.

3. **An exactly linear underlying curve.** The Schaeffer, Miranda and Koyejo
   mechanism is usually shown on an approximately smooth curve. Here the
   underlying per-step increments are all exactly `1/32`, spread exactly `0`,
   so the knee in the `k = 8` transform — last-over-first increment ratio
   exactly `6352865779/536158029` — is provably entirely an artifact of the
   transform, with no residual curvature to argue about.

4. **A classifier validated on real roster data in both directions, with its
   false alarms diagnosed rather than suppressed.** Recall `3/3`, no alarm on
   the clean smooth trajectory *or* on its knee-bearing transformed curve, and
   a `200`-trial randomized null through the identical pipeline reporting `5`
   firings: `1` diagnosed genuine positive at magnitude `2/7` and `4` false
   alarms at magnitude `1/7`, each listed individually, against a planted
   witness magnitude of `2/7`.

5. **An explicit statement of what the construction cannot reach.** The four
   AE9 measurement rows need a real neural training run and stay open with a
   named instrument each.

## What would overturn this

A representation-change quantity that is architecture-independent in the sense
defined here yet distinguishes two learners inducing the same partition; a
registered trajectory on which the structural invariants move without any
change in exact accuracy at the same step, or the converse; a false alarm in
the null at magnitude `2/7` or above; or a demonstration that the registered
pool and held-out set are not disjoint.
