# Recorded work and timing

Admission tests: wall 0.224 s, user 0.195 s, system 0.014 s, max RSS 56,736 KiB. Native calls: 0.

Complete proposal replay ([replay-02](records/replay-02/PROCESS.json)):

| Measured window | Seconds |
|---|---:|
| Child wall | 366.067 |
| User CPU | 347.704 |
| System CPU | 2.757 |

Maximum RSS: 55,008 KiB. These are process records, not a speed comparison or lifetime-cost estimate. The windows include frozen RAW/P1 load and 76 sequential one-step screens. They are nested with test runtime and must not be summed into a lifetime cost.

The original audit's 60 s consumer deadline and 180 s outer containment are registered predecessor limits, not the work consumed here. Matching now actually runs; [replay-01](records/replay-01/PROCESS.json) shows that keeping the 180 s abort leaves 13 screens at `UNKNOWN_RESOURCE`. Completing all 76 exceeded those walls and stayed under the 2,000,000 token-state bound (`token_bound_reached=false`).

| Matcher / screen counter | Value |
|---|---:|
| P1 assertions visited | 328,548 |
| Token states | 1,773,758 |
| Type checks | 5,444,088 |
| Essential matches | 135,557 |
| DV checks | 48 |
| Syntax proof requests | 144 |

P1 assertions visited equals 76 × 4,323. The preceding native export and the frozen cut enumeration are separate runs and are not hidden inside these timings. No native verifier was invoked.
