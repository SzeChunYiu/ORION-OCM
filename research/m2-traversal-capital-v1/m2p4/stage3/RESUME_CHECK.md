# The resume precondition, and the instrument that checks it

Revival-ledger row 65 records a defect of mine: a `squeue` poller treated **empty ssh
output as "the array is fully settled"** and broke its loop the moment ssh began failing.
A could-not-check became a checked-and-fine — the eighth instance of row 64's pattern, and
the same defect the ingest tool had been hardened against (exit 7) earlier the same day.

Logging it was not enough, so it is fixed here.

## What must be true before the scorer runs

For each of the eight registered worlds: both primary arms present
(`arm_PARENT_GF_D4.json`, `arm_RESET.json`), each reporting `all_targets_verified: true`,
with row counts matching the registration's `protected_targets_per_world`.

This is not bookkeeping. `m2p4_score.py` guards with `os.path.exists` and silently
`continue`s past a world missing an arm — and a silently dropped world changes `m`, which
changes Holm, which changes the terminal. A run that half-finished would score cleanly and
answer a different question than the one registered.

## The design: transport failure cannot become a verdict

Two pieces, deliberately split so the confusion that caused row 65 is structurally
impossible:

- `m2p4_resume_check.py` runs **where the run tree is** and answers only the question above.
- `m2p4_resume.sh` does the ssh, and its **transport failures carry their own exit code**.

| exit | meaning |
|---|---|
| 0 | `COMPLETE` — every world ready; the scorer may run |
| 3 | `INCOMPLETE` — tree read fine, some world not ready |
| 4 | `CANNOT_CHECK` — the tree itself could not be read |
| 5 | `UNREACHABLE` — the query failed. **Not a verdict about the run.** |

The wrapper also refuses `rc=0` with an empty body: that exact combination *is* the row-65
defect, so silence is never read as success.

## Validated before use, on real fixtures

Run on laptop billy (Python 3.11.14), never the Mac. Checker sha256 `443460ca2c86b513…`,
shipped and sha-verified before execution.

| fixture | exit | verdict |
|---|---|---|
| A — 8 worlds, both arms, verified, NT matching | **0** | `COMPLETE`, 8/8 ok |
| B — one world missing `arm_PARENT_GF_D4.json` | **3** | `INCOMPLETE`, 7/8 |
| C — a world with `all_targets_verified: false` | **3** | `INCOMPLETE`, 7/8 |
| D — a world whose row count ≠ the registration | **3** | `INCOMPLETE`, 7/8 |
| E — missing runs root | **4** | `CANNOT_CHECK` |
| F — corrupt JSON in an arm file | **4** | `CANNOT_CHECK` |

Fixture A is the **no-alarm control**: a checker that fires on a healthy tree gets switched
off, so the clean case is asserted as deliberately as the dirty ones. Fixture B reproduces
the specific shape a mid-loop task death produces — `RESET` runs first in the arm loop, so a
dying task leaves `RESET` present and `PARENT_GF_D4` absent, precisely the world the scorer
would skip in silence. Fixture F matters on its own: an unreadable arm is `CANNOT_CHECK`,
never `INCOMPLETE`, because "I could not read it" is not "it is not ready".

Transport, tested twice:

| target | exit | stdout |
|---|---|---|
| a non-existent host | **5** | 0 bytes |
| `lunarc` in its current wedged state | **5** | 0 bytes |

The second is the real outage that produced row 65. The old poller called that state
"settled"; this one calls it `UNREACHABLE` and returns no verdict at all.

## Scope

This establishes only that the precondition can be checked honestly. It says nothing about
whether the run completed, and nothing about whether the OCM benefit replicates in this
grammar. Both remain unknown.
