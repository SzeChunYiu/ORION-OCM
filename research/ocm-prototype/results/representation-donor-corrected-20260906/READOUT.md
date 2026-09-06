# Exact result and operation

| Measure | Corrected once-only capture |
|---|---:|
| Assigned / recorded / completed scenarios | 19 / 19 / 19 |
| Assigned / recorded / completed arm records | 57 / 57 / 57 |
| Exact full-versus-parent/OCM comparisons | 38 |
| Consumer ERROR / CANNOT comparisons / observed mismatches | 0 / 0 / 0 |
| Navigation calls per arm record | 4 |
| Total compact / full selected calls | 72 / 156 |

Each record now contains query and global-uniform navigation in both WARRANTED
and EXPLORATORY modes. The adapter automatically handles the fourth background_x
channel introduced by the repaired consumer; no adapter source change was needed.
Fine per-atom rational values and complete consumer outputs match across all arms.

The original failures withdraw_both and withdraw_rule now complete with LEARN /
ACQUIRE_WARRANT, no answer and no commitment. withdraw_partial completes with
the supported answer 42 and commitment. Completion is not synonymous with answering.

The base fixture still has 14 fine atoms and an eligible 6-dimensional quotient,
with 8 prospectively fixed added background atoms. Four solves reconstruct 56 fine
values. Preparation materializes 3,136 matrix cells and serializes 24,395 matrix
bytes; the field is 5,496 bytes and partition 174 bytes. These serialized counts
are not resident-memory measures. Full output materialization and global
certificate/matrix construction remain charged; the mechanism is not yet a
sparse or lazy scalable runtime. Incoming-edge/mixed-warrant/missing-state/
changed-binding cases retain their required full fallback.

The capture ran once on 2026-09-06 from 10:20:21.456636 to 10:20:22.879925 UTC.
Recorded whole-capture wall 1.423288 s, self user 1.413080 s, self system 0.008593 s,
process high-water RSS 36,768 KiB. Outer launch+capture+grade wall 1.567790 s and
reaped-child user/system 1.534054/0.031895 s are separate scopes, not additive.
Other host activity was not experimentally controlled. Performance remains
NOT_TESTED. PID 216905 exited 0 and was reaped; there was no retry.

controls/ preserves the initial stale current-test assertions (3 fail / 5 pass)
and the corrected 34-pass scope, including 11 existing SV controls. Current tests
require repaired live completion and all four navigation call types. Negative
grader controls read and hash-check original failed rows; they do not reproduce
the old bug. Equal historical failures remain CANNOT; altered vectors/requests
remain mismatches; the immutable old 19/57 partial capture still yields CLI 2.
Current live subset yields CLI 0 and altered arm identity still refuses.

Custody:
- Executed source commit 422d6dfe1088ea1e31237cc4ccd5007809ab00f3.
- Capture SOURCE.json binds 184 source/dependency/license files.
- Raw seal 4306bbe84c7e5647b7805460668d7455a87dc4e146be99cef97693a7e42eab5f.
- Grade 69e29c4eaa40f35ea25dab26be319fa2396df0579f71e464bbe389ddbe12099e.
- Source files copied under source/ retain their exact executed bytes.
- Original e82 packet's 135-file inventory was rechecked and remains unchanged.

From an isolated checkout of the executed commit on the laptop, the exact entry
point is recorded in raw/functional-v2-launch.json. Use the supported Python 3.13.12
environment and pytest 8.3.5, with PYTHONPATH pointing explicitly at checkout/src.
A new actor capture is a new experiment, not reconstruction of these receipts.

To check the published raw without any actor call, load the copied pure
source/representation_donor_grade.py using importlib, call grade_archive with
raw/functional-v2, and compare the result to raw/functional-v2-grade.json.
That module uses only the standard library; no actor, router or checker is
imported by the external grader. Verify SHA256SUMS first. Historical absolute
paths inside raw records remain custody metadata; never rewrite their seals.

The informed parent shares the exact consumer and mechanism donors. The result
therefore supports correct selection/reconstruction transfer and parent
sufficiency here, not machine-level superiority, independent lifetime efficiency,
learning improvement, or protected generalization. Revision scenarios are
independent finite snapshots, not physical restarts or a persistent update study.
