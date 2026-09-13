# Completed static validation

Executed on billy-laptop with CPython 3.12.13, using isolated mode and disabled
bytecode writes. This is exact synthetic arithmetic and packet custody only;
no ecology, search, training, timing experiment or physical measurement ran.

- 25 focused tests passed normally and 25 passed with optimization:
  17 mathematical/interface controls and 8 custody controls.
- The normal and optimized checker outputs are byte-identical, preserved in
  RECEIPT_V1.json. It retains the complete numerical payload.
- Independent absorbing-chain equations and explicit path execution check
  128 depth-three common policy trees under two kernels (256 executions),
  each with a fixed proper continuation after the depth-three prefix.
- Positive controls include paid trap rescue, model-dependent selected actions,
  fee-aware selection, complete observed-charge state, and convex row mixtures.
- Hostile controls include unseen traps, cost error despite two proper models,
  lost terminal identity, coverage without certification, certification-selected
  confidence failure, missing data-averaged integrability, malformed arithmetic,
  and a noncontractive certificate.
- Full packet membership, hidden extras, nonregular files, parent mutation,
  symlink substitution, changed numeric output, late source changes and a
  self-consistent rehashed manifest mutation are checked.
- Semantic peer independently accepted WTT1–4 and the finite model/oracle;
  no mathematical novelty or general-quantifier census is claimed.

Exact test execution metadata is in VALIDATION_RECEIPT_V1.json. The recorded
executable digest identifies this run; another binary is not claimed identical.

From this directory, the tests are:

    python3 -I -B -m unittest discover -s . -p 'test_*_v1.py'
    python3 -I -O -B -m unittest discover -s . -p 'test_*_v1.py'

The complete published payload is replayed using:

    python3 -I -B replay_v1.py
    python3 -I -O -B replay_v1.py

Raw copied theorem parents are preserved byte-for-byte from their pinned
commit. Neither exact checks nor passing replay authenticate confidence
coverage, support, sufficient state, physical access or adequacy semantics.
