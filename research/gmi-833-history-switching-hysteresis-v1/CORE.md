# gmi-833-history-switching-hysteresis-v1

Finite architecture-name-free history/switching extension of #893 / #833 Section J.

It defines history-conditioned morphology selection through explicit switching costs, proves the exact two-form hysteresis band, gives origin-additive and strict-margin sufficient conditions for erasing history dependence, and formalizes canonical reset semantics. Exact hostiles preserve boundary ties and reject negative switching costs.

Reproduce:

```bash
python -I -B research/gmi-833-history-switching-hysteresis-v1/test_history_switching_hysteresis_v1.py -v
python -I -O -B research/gmi-833-history-switching-hysteresis-v1/test_history_switching_hysteresis_v1.py -v
python -I -B research/gmi-833-history-switching-hysteresis-v1/history_switching_hysteresis_v1.py
```

Claim ceiling: `GMI_FINITE_HISTORY_SWITCHING_AND_HYSTERESIS_SELECTION_AT_REGISTERED_SCOPE`.
