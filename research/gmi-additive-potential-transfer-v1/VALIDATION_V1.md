# Completed exact validation

Executed on billy-laptop with CPython 3.12.13, isolated mode and disabled bytecode
writes. No ecology/search/training campaign, timing experiment or physical
measurement was executed.

- 33 focused tests passed normally and 33 passed with optimization:
  25 mathematical/interface controls and 8 custody controls.
- Full normal/optimized checker payloads are byte-identical and preserved in
  RECEIPT_V1.json; validation execution details are retained separately.
- 28 exact rational countable-row checks validate the polynomial formula
  implementation. The theorem, not these finite points, covers every countable
  state and real parameter in the supplied interval.
- Independent exact 16-step prefix execution supplies three bounded intervals
  for infinite-horizon expected costs. These are analytic model calculations.
- Doubling/kill controls retain nonvanishing upper-envelope expectations while
  actual cost tails vanish; the signed-potential control falsifies removal of
  nonnegativity using the same killed operator.
- Independent absorbing-chain equations and explicit paths evaluate 128
  depth-three common policies under two kernels, 256 model executions, with
  a fixed proper continuation afterward.
- Positive controls cover WTT embedding, mixed initial laws, data-selected
  policies, charged setup fees, complete observed-charge state, optional
  terminal certificates and convex joint transition/charge mixtures.
- Adverse controls cover an unseen trap, zero-cost nontermination, insufficient
  work/error reserves, terminal-label loss, signed/nonzero-terminal potentials,
  independent recombination of transition and charge extrema, uncertified
  coverage, comparator expansion and data-averaged nonintegrability.
- Eight custody controls include real-unit no-alarm, full numeric payload
  mutation, copied-parent drift, hidden/nonregular entries, symlinks, late
  source mutation and self-consistent manifest rebinding during the worker.

From this directory:

    python3 -I -B -m unittest discover -s . -p 'test_*_v1.py'
    python3 -I -O -B -m unittest discover -s . -p 'test_*_v1.py'
    python3 -I -B replay_v1.py
    python3 -I -O -B replay_v1.py

The recorded executable digest identifies the actual validation run. A replay
on another binary is not a claim of binary identity. Whole-payload replay checks
this mathematical packet's source/content consistency, not the physical truth
of confidence coverage, sufficient state, action access or adequacy.
