# FNA-3/D5 protocol — non-neural sequence/grammar parent suite

Work package: SzeChunYiu/ORION-OCM#214 FNA-3/D5 (functional absorption of
bounded sequence/grammar parents into OCM). All design authority lives in
`FREEZE_FNA3_V1.json` (frozen before any scored run; sha256 digests of
`fna3.py` / `test_fna3.py` recorded in the freeze under
`sha256_before_first_scored_run`). This file documents execution mechanics
and every implementation device declared by the freeze or its pre-run
amendments A1-A5.

## Execution environment

- All execution on host `billy` (billy-laptop, Python 3.8.10), stdlib only.
  Capsule rsynced from the worktree to `~/fna3-run/research/fna3-seqgrammar-parents-v1/`
  before the run; digests verified against the freeze pre-run and post-run;
  results rsynced back and md5-verified. No execution on the Mac mini.
- Budget cap 7200 s wall (amendment A4); recorded in results as
  `budget_respected`.
- Tests: `python3 test_fna3.py` — 23 tests, green on billy-laptop before the
  scored run.

## Worlds

- W1_PSA (synthetic): drifting probabilistic finite-state source, 6 states.
- W2_NESTED (synthetic): stochastic nesting grammar `S -> a S b` (p=0.72) |
  `S -> c` (0.28), depth truncated at D_MAX. **A5 (pre-run)**: the
  generator/oracle were corrected to the freeze-declared depth-first law —
  after `a` the innermost S decides a/c; after `c`/`b` the stack unwinds with
  deterministic `b`; depth cap forces `c`. Every depth-0 block is exactly
  `a^k c b^k`, k <= D_MAX. The oracle conditions on exact pending depth
  (max-suffix-sum, exact for balanced blocks) + phase, and matches the
  generator empirically (worst |emp-oracle| = 0.0057 at n=20000).
- W3_LEXICON (synthetic): 24 multi-char words (2-5 chars), Zipf frequencies,
  order-1 Markov word chain, deterministic word internals.
- W4_UD_CHAR / W5_UD_POS (real): UD EWT r2.14 custody corpus (sha256-gated
  against the frozen custody manifest; protected test split never touched).
  W4 = character stream; W5 = UPOS tag stream.

## Arms (P0 oracle, P1-P7 parents, P8 diagnostic)

- P0 ORACLE: exact generative distribution (world-specific). On UD worlds no
  oracle exists — P0 is absent there by design.
- P1 n-gram: Witten-Bell smoothing, order 8. - P2 PPM-C: order 8,
  no exclusion. - P3 CTW: KT/Dirichlet(1/2) leaf estimators, depth 12,
  Context-Tree-Weighting mixing `pw = 1/2 e^{pe} + 1/2 e^{pc}` (Willems,
  Shtarkov, Tjalkens 1995); full-depth contexts are pure-KT leaves; exact
  lgamma cache recompute on unobserve; counts-only state digest.
- P4 EM-HMM k=8: Baum-Welch, scope limited by A2 (n=16000 synthetic /
  n=20000 W5, 10 EM iterations). Spectral (HMM SVD) methods are
  CANNOT_CHECK_NO_STDLIB_SVD and are not silently substituted.
- P5 PCFG EM: frozen 8-rule template (r0 S->aT, r1 T->Sb, r2 S->c, five
  distractors), inside-outside EM (pull-formulation outside, lengths
  descending). Declared gift on W2 only: fit and score see depth-0
  constituent blocks; every other arm sees the raw stream. Fit uses the most
  recent 1500 blocks (A3) and skips blocks longer than 128 symbols (declared
  compute device; blocks are bounded by 2*D_MAX+1 so this binds only at
  D_MAX=48). Prefix probabilities: per-position probabilistic Earley charts
  (Stolcke 1995) over (alpha, beta) state pairs — predictor grows alpha by
  alpha*w, completer advances waiters by alpha(waiter)*beta(complete), each
  rule's own weight enters beta exactly at its completion; charts stabilised
  by seed-anchored Jacobi sweeps (tol 1e-14, cap 200); rho_k = alpha over
  terminal-pending states + complete root states; chain-rule conditionals are
  rho ratios (verified: prod of conditionals == inside sentence probability).
- P6 BPE(200)+PPM-4: deterministic merges fit on the train window (charged);
  word mode on W4 (whitespace), 8-char chunks on W3 (declared device); loss
  normalised per character (buffering lag inherent to the parent, declared).
- P7 kNN case memory: history-window nearest-neighbour voting.
- P8 LOGISTIC DIAGNOSTIC ONLY: single-layer softmax over one-hot last-4
  symbols, SGD, frozen epochs/lr. NO adoption authority. Positions before
  stream start contribute only the bias term.

## Metrics

Prequential predict-then-update scoring on protected tails; held-out
log-loss with 2^-20 eps floor; closure accuracy (uniform candidate closure
over last-24 history + actual, ACC_STRIDE=8 subsample per A1; P7 stride 8);
samples-to-oracle+0.05 on the sample ladder; full lifecycle cost (fit + score
work units + wall seconds, everything charged); revocation (retract last 256
observations; exact digest restore on online arms). Expressivity dial: W2
D_MAX in {8, 16, 32, 48}.

## Controls

Shuffle-equal-n null (seed 2140360) per world per arm (train window shuffled
by id permutation, same n); unigram floor per world; protected split
disjointness asserted in tests; custody sha256 gate on UD loads.

## Terminals

Only the terminals of #214 section 7 are emitted by `world_verdict` /
`evaluate_predictions`. NEGATIVE-RESULTS DIRECTIVE applies: every failing arm
is reported with one-stage failure attribution and a revival lever.

## File map

- `fna3.py` — worlds, arms, metrics, controls, main.
- `test_fna3.py` — 23-test battery (units + protocol invariants).
- `FREEZE_FNA3_V1.json` — frozen design + amendments + pre-run digests.
- `FNA3_RESULTS_V1.json` / `.md` — scored results and their reading.
- `REPO_STATE.json` — custody/base-commit provenance.
