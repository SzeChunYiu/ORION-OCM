# gmi-833-real-transition-receipts-v1

Real-system evidence package for the #833 Section-J row `Validate at least 5 transitions on real systems` (#903). Executes the fail-closed protocol from `gmi-833-real-transition-protocol-v1` against real trained systems.

## Outcome (terminal `REAL_SYSTEM_TRANSITION_VALIDATED_AT_REGISTERED_SCOPE`, qualifying count 5)

Twelve real systems trained (torch, CPU, registered seeds; sha256-bound real data sources; protected 80/20 splits; opaque-ID selection; family-blind binomial-banded classification):

- 9 licensed systems (text-like sources: two ebooks, dictionary words, kernel headers, two stdlib source concats, programme corpus, Noise.wav) — every one shows the pre-registered `PERSISTENT_STATE -> STATELESS` transition under `lambda_low = lambda*/2 -> lambda_high = 3 lambda*/2` of the #901 law `lambda* = eta*p/(2B)`;
- 3 unlicensed systems (two ELF binaries, Front_Center.wav; measured `E0 < 1/8`) — correctly predicted NOT to transition at either endpoint: the licensed-band boundary `1/8 < E0 < 3/8` is demonstrated on both sides by real data.

Receipts (first five licensed in registered order): R01 gutenberg, R04 Noise.wav, R05 stdlib-json, R07 Frankenstein, R08 dictionary words. Shifted-law control (`2 lambda*`) falsified on every system; boundary ties recorded as controls; all 50 machine checks GREEN.

## Chain of custody

1. `FREEZE_V1.md` @ `cd6196aa5` — complete pre-outcome predictions, pushed before any training.
2. Machinery smoke exposed the uniform-bit premise failure (real-source stateless floor is data-derived, not `1/2`).
3. `FREEZE_V2_AMENDMENT.md` @ `c3fbf5b11` — registered revival: empirical stateless floor, amended blind classification, exact licensed band; V1 predictions unchanged.
4. V2 outcomes: 3 licensed / 3 unlicensed — every prediction correct; qualifying count 3 < 5.
5. `FREEZE_V3_ADDENDUM.md` @ `c03eb646e` — registered revival (attribution: system availability, lever: second text-weighted tranche), identical law/grid/rule.
6. V3 outcomes: six further licensed systems; terminal reached with 5 qualifying receipts.

Reproduce (no torch needed):

```bash
python -I -B research/gmi-833-real-transition-receipts-v1/test_real_transition_receipts_v1.py -v
python -I -O -B research/gmi-833-real-transition-receipts-v1/test_real_transition_receipts_v1.py -v
python -I -B research/gmi-833-real-transition-receipts-v1/real_transition_receipts_v1.py
```

CI re-runs the deterministic stage from committed `REAL_RUNS/` artifacts, byte-compares `RESULT_V1.json`, re-hashes every receipt-bound eval artifact, and applies the earned #833 row via the foundation reconciler.
