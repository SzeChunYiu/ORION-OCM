# FREEZE V3 ADDENDUM — second registered system tranche (revival iteration)

**Status:** registered BEFORE any V3 training outcome, under the operator revival doctrine. FREEZE_V1.md, FREEZE_V2_AMENDMENT.md, and all V2 outcomes are immutable history; nothing already measured is altered.

## B1. V2 outcome being revived

The V2 grid trained six registered real systems. Every per-system prediction was correct — three licensed systems (gutenberg text, Noise.wav, stdlib-json source) exhibited the predicted `PERSISTENT_STATE -> STATELESS` transition and three unlicensed systems (python3.8 binary `E0=0.0706`, git binary `E0=0.0642`, Front_Center.wav `E0=0.1244`) showed no transition at either endpoint, exactly as the licensed-band law requires. Qualifying count 3 < 5, terminal `INSUFFICIENT_REAL_SYSTEM_EVIDENCE`.

## B2. Attribution and lever (one stage)

Attribution: registered-system availability — the V2 grid under-sampled the licensed band `1/8 < E0 < 3/8`; binary-executable sources are strongly bit-biased (machine-code byte structure) and fall outside it. The law itself received zero falsifications.

Lever: register a SECOND tranche of six real systems weighted toward text-like real sources (the region the boundary evidence itself identifies as licensed), with identical frozen law, grid shape, classification rule, and controls. Each V3 system's predictions are registered here, before its outcomes exist:

- for every licensed V3 system: `PERSISTENT_STATE` at `lambda_low`, `STATELESS` at `lambda_high`;
- for every unlicensed V3 system: no transition predicted (fail-closed exclusion from receipts, recorded with measured `E0`).

No threshold, band, or rule changes. This is sampling within the law's registered scope, not outcome tuning; the conditional claim (`licensed-band real systems transition as the frozen law predicts`) is unchanged and the unlicensed boundary remains part of the evidence.

## B3. Registered V3 systems

| id | real data source (primary) | pre-registered fallback | T | W | H | p | seed |
|----|----------------------------|--------------------------|-----|-----|-----|-----|------|
| R07-frankenstein | Project Gutenberg ebook #84 (Frankenstein), downloaded at run time, sha256 recorded | `/usr/lib/python3.8/email/utils.py+/usr/lib/python3.8/http/client.py` concat | 350000 | 24 | 32 | 6.0 | 707 |
| R08-dict-words | `/etc/dictionaries-common/words` | `/usr/lib/python3.8/ast.py+/usr/lib/python3.8/token.py+/usr/lib/python3.8/tokenize.py` concat | 300000 | 32 | 16 | 4.0 | 808 |
| R09-kernel-headers | `/usr/src/linux-headers-5.15.0-139-generic/include/linux/sched.h+/usr/src/linux-headers-5.15.0-139-generic/include/linux/kernel.h+/usr/src/linux-headers-5.15.0-139-generic/include/linux/mm.h` concat | `/usr/share/sounds/alsa/Rear_Right.wav` | 300000 | 16 | 24 | 6.0 | 909 |
| R10-stdlib-ast | `/usr/lib/python3.8/ast.py+/usr/lib/python3.8/token.py+/usr/lib/python3.8/tokenize.py` concat | `/usr/share/sounds/alsa/Rear_Left.wav` | 250000 | 24 | 24 | 8.0 | 1010 |
| R11-programme-md | this package's `FREEZE_V1.md+FREEZE_V2_AMENDMENT.md+CORE.md` concat (real programme corpus text on the execution host) | `/usr/share/sounds/alsa/Rear_Right.wav` | 200000 | 16 | 16 | 2.0 | 1111 |
| R12-rearleft-wav | `/usr/share/sounds/alsa/Rear_Left.wav` | `/etc/dictionaries-common/words` | 250000 | 32 | 32 | 16.0 | 1212 |

Training hyperparameters, seeds `{s, s+1000}`, split, floor definition, licensed band `1/8 < E0 < 3/8`, classification rule, and controls are all inherited unchanged from FREEZE_V1.md + FREEZE_V2_AMENDMENT.md.

## B4. Receipt selection order (pre-registered)

Receipts are emitted for the first FIVE licensed systems in registered order `R01, R02, ..., R12` (V2 order then V3 order). Licensed systems beyond five and all unlicensed systems are recorded in `RESULT_V1.json` with measured quantities. If fewer than five systems are licensed across both tranches, the terminal stays `INSUFFICIENT_REAL_SYSTEM_EVIDENCE` and the row stays open — no further silent retrials; any V4 would itself be a registered revival with a named lever.

## B5. Custody

This addendum is committed and pushed before V3 training executes. V3 outcome artifacts are created only in descendant commits. CI additionally pins this addendum's commit and asserts V3 outcomes exist at neither the V1 freeze, the V2 amendment, nor this addendum.
