# Recorded costs

These windows describe one authored invocation. They nest and must not be added.

| Window | Wall seconds | Scope |
|---|---:|---|
| GNU time | 2.46 | Entire Python process, including startup and final serialization; rounded display |
| Main | 2.425751573 | Entry through post-custody; excludes imports and final RESULT serialization |
| Flow | 2.375692799 | Nested caller flow |
| Source wrapper | 0.818630084 | Nested native wrapper through post-custody; excludes final receipt write |
| Replacement wrapper | 0.826709790 | Same nested scope |

The [outer GNU-time record](records/observation-01/gnu-time.txt) reports 2.37 user seconds, 0.05 system seconds and 113,292 KiB peak RSS. Per-wrapper RSS is the process's cumulative highwater; its difference is not an allocation measurement.

Each wrapper records 3,514,880 prefix bytes read, 80,152 source bytes read, two source-index calls and three dynamic source modules. Source/replacement database materialization and reread are respectively 1,757,694 / 1,757,685 bytes. These are recorded counters, not complete lifetime costs.

Adapter counters retain 60 target-node replays across two replay calls, two pattern replay calls, 22 pattern-target pairs, 14 validated body nodes, nine argument/source visits, 22 expanded-node visits and 21 emitted normal labels. Repeated visits are work counts, not distinct logical objects. See [full counts and nested timing scopes](review/outcome/OUTCOME-COUNTS-01.json).

The earlier six authored controls are separate: child wall 0.081663438 seconds; qualifier window 0.377644732 seconds. Their [process](records/qualification-01/PROCESS.json) and [control evidence](records/qualification-01/CONTROLS.json) are preserved. They were not rerun or counted as native execution. Source preparation, review and publication are outside the native invocation's measured windows.

The 30-to-21-label change is descriptive. No matched-parent latency, search, acquisition or lifetime advantage was measured.
