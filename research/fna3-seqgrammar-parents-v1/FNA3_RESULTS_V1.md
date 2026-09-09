# FNA-3/D5 results V1 — where bounded sequence/grammar parents break

Artifact: `FNA3_RESULTS_V1.json` (59646 bytes, md5 b4ef3fad…) — single scored
run on billy-laptop (host `billy`, Python 3.8.10, stdlib only), wall 7028.3 s
under the 7200 s cap (A4). Design authority `FREEZE_FNA3_V1.json`, frozen
before the run; pre-run amendments A1-A7; ONE post-run correction A8 (UD
shuffle-null scored an empty window; recomputed on the same host, 2622.7 s —
details below, invalid entries preserved in the JSON). Tests 23/23 green
before the run and re-run after A8.

## Verdicts (terminals from #214 §7 only)

| World | Verdict | Best parent | Gap (bits/sym) |
|---|---|---|---|
| W1_PSA (sparse order-3 PSA) | PARENT_SUFFICIENT_FOR_NEXT_SYMBOL_PREDICTION | P3 CTW | -0.00002 (n=1000 already) |
| W2_NESTED (stochastic nesting) | REPRESENTATION_INSUFFICIENT | P3 CTW | 0.0684 |
| W3_LEXICON (24-word Markov) | REPRESENTATION_INSUFFICIENT | P3 CTW | 0.3517 |
| W4_UD_CHAR (real English chars) | CANNOT_CHECK_ORACLE_ABSENT_REAL_CORPUS | P6 BPE+PPM (2.593 bpc) | n/a |
| W5_UD_POS (real UPOS stream) | CANNOT_CHECK_ORACLE_ABSENT_REAL_CORPUS | P1 n-gram (0.602) | n/a |

## Where each parent breaks (attribution -> revival lever)

- P1 n-gram WB o8 — breaks on SPARSE CONTEXTS + SMOOTHING BIAS (W1: gap 0.106
  at n=64000, still 0.283 at 16k; the order-3 PSA's rare branches are exactly
  representable yet Witten-Bell backoff never stops paying). Lever: context
  merging (CTW-style weighting) rather than backoff — absorbed by P3.
- P2 PPM-C o8 — breaks the same way, worse (W1 gap 0.305): escape-C weights
  recency over exact sparse contexts. Lever: same as P1.
- P3 CTW d12 — sufficient on W1 (first parent class to hit the oracle
  threshold at the LADDER MINIMUM n=1000; |gap| < 3e-5). Breaks on DEPTH
  (W2 gap 0.068) and on MULTI-CHAR LEXEMES (W3 gap 0.352): a context tree
  cannot represent "position inside a word" without splitting every word
  across 2-5 contexts. Lever (declared, not run): variable-length units ->
  the P6 composition.
- P4 EM-HMM k8 — runs at declared scope (A2: n=16000) and never leads on any
  world; weighted-automaton state cannot encode stack depth (W2) or lexicon
  identity (W3). Spectral learner: CANNOT_CHECK_NO_STDLIB_SVD. Lever: richer
  state -> literally the grammar parents.
- P5 PCFG-EM (frozen 8-rule template, block gift) — the cleanest negative:
  on W2 it RANKS better than every other arm AND better than the oracle
  itself (closure accuracy 0.917 vs oracle 0.838) yet loses 7.9 bits/sym on
  log-loss (8.44 vs 0.496). One-stage attribution: JOINT-likelihood EM on an
  ambiguous template (S->SS distractor) inflates block probability while
  destroying the CONDITIONAL magnitudes the metric scores (mass pumped into
  continuation predicts a/c after `c` where truth is deterministic `b`).
  Fit data makes it WORSE (2.12 -> 4.79 -> 8.47 bits at n=1k/4k/16k): the
  EM optimum diverges from the evaluation objective as ambiguity gets
  resolved. Lever: conditional/objective-matched training (minimum-description
  or discriminative rule weighting), or dropping ambiguous distractors —
  both are new-mechanic work, not tuning; the parent AS BOUNDED does not
  own calibrated next-symbol prediction on its own grammar's language.
- P6 BPE(200)+PPM-4 — WINS the real character world (2.593 bpc vs 2.866 CTW /
  2.905 n-gram) but REFUTES R3 on W3 (1.092 vs PPM 1.056): chunk-mode BPE on
  2-5-char words with shared internals splits the wrong units and pays
  buffering lag. Break = merge inventory is frequency-driven, not
  lexicon-driven. Lever: lexicon-aware merge objective.
- P7 kNN case memory — breaks everywhere real (W4: 7.48 bpc, 7.4e9 work
  units, 33 bytes state): exact-window retrieval has no generalization
  across unseen windows. Lever: distance-weighted soft matching = the
  kernel/nadaraya direction, out of the bounded set.
- P8 logistic (DIAGNOSTIC ONLY) — never beats the best online parent on any
  world (R4 confirmed on W5: online parents 0.602-1.448 vs P8 0.653);
  a linear map over the last 4 symbols is the floor the parents clear.

## Expressivity dial (W2 D_MAX 8/16/32/48, n=64000)

| D_MAX | oracle | P1 gap | P2 gap | P3 gap | P5 gap |
|---|---|---|---|---|---|
| 8 | 0.4887 | 0.109 | 0.121 | 0.035 | 7.80 |
| 16 | 0.4956 | 0.138 | 0.151 | 0.069 | 7.88 |
| 32 | 0.4957 | 0.138 | 0.151 | 0.068 | 7.95 |
| 48 | 0.4957 | 0.138 | 0.151 | 0.068 | 7.95 |

The finite-context break (P3 0.035 -> 0.068) appears by D_MAX=16 and then
SATURATES: with p_open=0.72 the depth tail beyond 16 is exponentially rare,
and D32/D48 sampled identical streams (all five arms bit-identical). The
expressivity deficit of finite-context parents on nesting is structural
(counting depth needs unbounded state) but its magnitude at this source is
capped by the tail mass — the dial honestly measures 8->16, not beyond.

## Data efficiency (samples-to-oracle+0.05)

Only P3 CTW ever reaches the oracle threshold, and only on W1 (n=1000, the
ladder minimum). Every other parent on every world stays off-threshold at
the ladder maximum (64000): P1 best-case gap 0.106 (W1), P7 worst 1.23
(W3). P4/P5/P8 are batch arms — threshold crossed by none.

## Real corpus (custody-gated, protected test only)

- W4 chars (n=1M train / 100k scored, 111+1 sentinel alphabet, 2 OOV subs):
  P6 2.593 < P3 2.866 < P1 2.905 < P2 3.283 << P7 7.485 bpc.
- W5 POS (n=254k / 122557 scored, 19 tags): P1 0.602 < P3 0.608 < P2 0.621
  < P8 0.653 (diag) < P7 1.448.
- Lifecycle at W4 max n: P1 n-gram needs 736 MB persistent state (order-8
  tables) vs P2 53 MB, P3 211 MB, P6 2.6 KB, P7 33 B; fit walls 615-663 s
  (P6 27 s, P7 0.6 s). The strongest char parent is also 3 orders of
  magnitude lighter than the count-table arms.

## Controls

- Shuffle-equal-n null (seed 2140360), degradation bits (shuffled - normal):
  W1 +0.19..+0.42, W2 +0.72..+1.28, W3 +1.88..+5.60, W4 +1.89..+6.22,
  W5 +3.03..+9.25 — every arm on every world passes (R5 confirmed, 23/23
  cases). A8 note: the seven UD entries in the run artifact were 0.0
  (empty-window defect, replaced post-run with values above; originals
  preserved under post_run_corrections.A8). Consistency check: CTW's
  shuffled W4 loss (4.7599) equals the unigram floor (4.7599) to 4 decimals
  — a shuffled-trained universal model collapses to the unigram, as theory
  says.
- Unigram floors (bits/sym): W1 1.553, W2 1.477, W3 2.757, W4 4.760,
  W5 3.634. Every scored arm beats its world's floor.
- Revocation (retract 256): P1/P2 exact digest restore in ~1 ms (~250x
  faster than refit); P3 restores EXACTLY but its lgamma cache recompute
  makes retraction 62x SLOWER than a refit (25.97 s vs 0.42 s) — exact
  online revocation is economical only for plain count arms; P4/P5/P8 pay
  full refit semantics (P5: 28.1 s).

## Predictions ledger (registered pre-execution)

- R1 (CTW early, n-gram closes by 64k) REFUTED — CTW early confirmed
  (gap 0.001 at 16k), but WB n-gram never closes on the sparse PSA
  (0.106 at 64k, trend ~1/n, off-threshold past the ladder).
- R2 (finite-context parents break at D48, PCFG closes) REFUTED — the
  finite-context break is real but saturates by D16 (and D32==D48 streams
  identical); PCFG-EM fails catastrophically (see P5 above) instead of
  closing.
- R3 (BPE+PPM beats PPM on W3) REFUTED — 1.092 vs 1.056.
- R4 (online parents beat the logistic diagnostic on W5) CONFIRMED.
- R5 (shuffle null degradation >= 0.05 wherever the floor is beaten)
  CONFIRMED after A8 (23/23 cases).

## Engineering chain (all declared in the freeze)

Pre-run: A1 stride-8 accuracy subsample; A2 P4 scope n=16000/20000 iters=10;
A3 P5 EM fit cap 1500 blocks; A4 7200 s budget cap; A5 W2 generator corrected
to the freeze-declared depth-first law (oracle-generator deviation 0.0057);
A6 real-world OOV sentinel; A7 CANNOT_CHECK entry guards in verdict
assembly. Post-run: A8 UD null empty-window fix (this file, above). The
scored pipeline required four execution attempts (crashes: P8 short-history
index, W4 alphabet OOV, verdict guard — see REPO_STATE.json); none touched
scoring semantics; all fixes were declared and the freeze digests refreshed
before the first completed scored run.
