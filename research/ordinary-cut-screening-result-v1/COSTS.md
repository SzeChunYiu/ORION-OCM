# Costs and measured-stage diagnosis

The four wall windows below are nested and must not be added. Unrounded values are in [SUMMARY.json](SUMMARY.json) and the exact process records.

| Recorded window | Seconds |
|---|---:|
| Caller around the observer | 60.198932 |
| Observer including its post-run checks | 60.175385 |
| Screening child process | 60.084585 |
| Driver | 60.004043 |

The caller window runs from observer `Popen` through `wait4` and log closure; caller setup, final custody and receipt serialization are excluded. The observer window runs from its entry through post-run input/output checks, excluding interpreter/import startup and final receipt serialization. The driver begins before input/source/gate reads and includes individual SCREEN writes; final custody, module inventory and RESULT serialization are outside it.

The child recorded 59.984411 user seconds, 0.063983 system seconds and 81,316 KiB peak RSS. The caller's nested resource record is retained separately. [Child/observer record](records/observation-01/PROCESS.json) · [caller record](records/caller-01/PROCESS.json)

One grammar construction read all 4,323 contracts and took 0.07732549798674881 seconds. The run recorded 110,178 parser calls, 114,898 syntax requests, 686,561 input tokens and 58.96280540712178 seconds of parse/emission time: 98.2647% of the driver interval. This is attribution from the existing timers, not an independent profiler. Internal Earley chart work and partially emitted labels on failure are uninstrumented.

Parent visits total 17,606 = 4 × 4,323 + 314. The matcher recorded 74,213 token states, 114,864 type checks, 1,714 essential matches and eight DV checks. The 60-second soft bound caused the refusal; the 2,000,000-state bound was not reached. One context was reused; no syntax-result memoization was present.

The original audit's cost objects are preserved verbatim in RESULT, including its separate 0.5324072589864954-second caller window. That earlier attempt is not erased, and its nested intervals are not added to this run's nested intervals. Source preparation, control qualifications, native export and other lifetime costs are outside this screening measurement. This is neither a speedup comparison nor lifetime economics.
