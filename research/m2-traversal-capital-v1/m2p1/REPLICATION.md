# Replication of the full scored terminal across fresh worlds

Ten independently seeded E5 worlds on LUNARC, each with its own hidden motif set, each
run through the complete six-arm pipeline on a fresh host.

## Six worlds reach the registered positive terminal

```text
TERMINAL: HISTORY_INDUCED_SEARCH_PRIOR      G4: PASS
```

| world | `CONTINUED` | `RESET` | `SHUFFLED` | best history-free surface | mean `B` CONT → RESET | reduction |
|---|---|---|---|---|---|---|
| e5_2002 | **73** | 36 | 23 | 42 | 6 068 → 52 896 | 88.5 % |
| e5_2004 | **64** | 28 | 20 | 37 | 5 558 → 61 161 | 90.9 % |
| e5_2006 | **88** | 43 | 34 | 55 | 6 782 → 61 980 | 89.1 % |
| e5_2007 | **64** | 38 | 22 | 49 | 6 030 → 46 148 | 86.9 % |
| e5_2008 | **84** | 37 | 28 | 47 | 5 666 → 64 782 | 91.3 % |
| e5_2009 | **69** | 27 | 21 | 35 | 5 307 → 68 521 | 92.3 % |

In every admitting world:

- `CONTINUED` beats `RESET` by **1.8×–2.6×** on ladder successes and by **87–92 %** on work;
- `SHUFFLED_HISTORY` lands **below `RESET`**, so the benefit is structure, not volume;
- `CONTINUED` beats the best **history-free surface ordering** by **+15 to +37** ladder points.

That last row matters. The billy-old E5 world gave only **+2** over the surface baseline,
which was recorded as a thin-margin limitation. Across six fresh worlds the margin is
large and consistent, so **the thin margin was a property of that one world, not of the
mechanism.** E6 closed it by construction; this closes it by replication.

## Four worlds refuse, and the instrument reports it correctly

```text
TERMINAL: PARENT_SUFFICIENT__LEARNER_REFUSED_DEPLOYMENT      G4: CANNOT_CHECK
```

e5_2001, e5_2003, e5_2005, e5_2010 — each with 5/6 motifs recovered. `CONTINUED` is
identical to `RESET` to the slot in all four, since no generator is served.

`G4` correctly returns `CANNOT_CHECK_NO_DEPLOYED_HISTORY_ARM` rather than `FAIL`. This is
the repaired checker doing its job: before the repair it would have reported
"surface ordering explains the advantage" for an arm that had no advantage to explain.
`CANNOT_CHECK` stays distinct from both PASS and FAIL in all four.

## Summary

| | worlds |
|---|---|
| full positive terminal, G4 PASS | **6 / 10** |
| refusal, correctly reported `CANNOT_CHECK` | 4 / 10 |
| admission predicted by the recovery law | **10 / 10** |

The split is entirely explained by [ADMISSION_LAW.md](ADMISSION_LAW.md): 6/6 recovery
admits, 5/6 refuses, no exceptions.
