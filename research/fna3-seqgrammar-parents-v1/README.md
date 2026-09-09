# FNA-3/D5 — non-neural sequence/grammar parent suite (START HERE)

Issue SzeChunYiu/ORION-OCM#214, lane FNA-3/D5: functional absorption of
bounded sequence/grammar parents (n-gram/PPM/CTW, weighted automata, PCFG,
BPE, case memory) into OCM, with the mandated report of where their
expressivity / data efficiency breaks.

## Reading order

1. `FNA3_RESULTS_V1.md` — the distilled findings (verdicts, break table,
   controls, lifecycle). Read this second; it cites everything below.
2. `FNA3_RESULTS_V1.json` — the scored artifact (single run, billy-laptop,
   wall 7028 s <= 7200 s cap; post-run correction A8 recorded inside).
3. `PROTOCOL.md` — execution mechanics: worlds, arms, implementation
   devices, metrics, controls, terminals.
4. `FREEZE_FNA3_V1.json` — design authority: frozen before any scored run,
   pre-run amendments A1-A7, post-run amendment A8 (UD null window fix) with
   before/after digests.
5. `fna3.py` / `test_fna3.py` — implementation + 23-test battery (green on
   billy-laptop, Python 3.8.10, stdlib only).
6. `nullfix_a8.py` / `NULLFIX_A8.json` — A8 correction driver + its output.
7. `REPO_STATE.json` — branch/base-commit/custody provenance, execution
   attempts.

## Headline (one line each)

- W1 (sparse PSA): CTW is PARENT_SUFFICIENT at n=1000; Witten-Bell n-gram
  never closes a 0.106-bit gap even at n=64000.
- W2 (nesting): REPRESENTATION_INSUFFICIENT for every finite-context parent
  (best CTW gap 0.068 bit); PCFG-EM ranks best (acc 0.917) yet loses 7.9
  bits/symbol to joint-likelihood/conditional-objective divergence.
- W3 (lexicon): REPRESENTATION_INSUFFICIENT (best gap 0.352 bit); BPE+PPM
  does NOT beat plain PPM (R3 refuted).
- W4/W5 (UD real corpus): no oracle -> CANNOT_CHECK; BPE+PPM strongest on
  characters (2.593 bpc), n-gram strongest on POS (0.602); P8 diagnostic
  loses to online parents everywhere (R4 confirmed).

Details, failure attributions and revival levers: `FNA3_RESULTS_V1.md`.
