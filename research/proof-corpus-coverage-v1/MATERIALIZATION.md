# Exact source materialization

The apparatus is qualified on authored Git fixtures. The actual V2 continuation
remains a scheduling hold: all 60 observations lacked the registered initial
memory headroom, while disk headroom passed. Waiting lasted 300.022189 seconds.
There was no phase entry, controller dispatch or materialization output.
This is neither a materializer failure nor a build refusal.

Start with [the current successor records](materialization-handoff-records/CORE.md)
and [integrated qualification](INTEGRATION-MATERIALIZATION.md). The original
registration still contains four assigned rows; its continuation cursor is four.
No row has been replaced or given semantic success by this component.

## Mechanism and authority

`materialize_git.py` reconstructs a pinned commit/tree using offline Git plumbing.
It copies object storage independently, verifies Git object identities, preserves
exact file bytes/modes and safe relative symlinks, and verifies the detached HEAD
and index tree. It does not use checkout/archive, filters, hooks or network.
Git is the conventional parent; this implementation does not establish novelty.

The source-only `materialize_run.py` entry binds the original registration and
V2 acquisition/start records. Its worker has exactly ten materials: the registered
corpus and the nine ordered acquired dependencies. A single existing aggregate
resource controller supervises the worker, with the registered memory, CPU, PID,
file and sampled disk boundaries. All V2 and new output roots are charged.

The original V2 start SHA is
`735f3bca0600a55cd5ddc6c7678f79ea5399ef7b1fd0ce6ba007958e73b4f3af`;
its whole deadline remains monotonic `390867.56895429` on the recorded boot.
Validation, waiting, preparation and custody consume that clock. This component
does not create an episode or restart its clock.

Every successful material receipt must bind the exact request, source, commit,
tree, workspace bytes, six Git commands and all three raw streams. The parent
also checks the actual worker PID, resource receipt and completed cleanup, then
rechecks sources, input bytes, boot identity and deadline before readiness.
Partial results are retained on refusal. Trusted raw-source host execution and
the existing controller are the scope; no arbitrary-Python sandbox is claimed.

The entry accepts four paths under pinned Python with `-I -S`:
`REGISTRATION V2_EPISODE CORPUS_BARE NEW_OUTPUT`. It is not a generic invitation to
rerun the current episode. An authorized continuation must preserve its original
clock, exact inputs and qualified source identities.

## Qualification generations

| Retained generation | Observed outcome | Scope |
|---|---|---|
| Materializer boundary repair | Three RED failures plus one clean control; then 26 passes | Actual authored Git child cleanup after selector setup failure, and final-hash deadline refusal |
| Source-only entry | 47 passes | Fixed toy authority, exact ten tiny Git trees, request/source/output/cleanup faults; aggregate controller explicitly mocked |
| Test portability successor | Three initial RED controls; eight passes/one helper-composition failure; then nine passes | Explicit host skips, authored host-pin refusal and selected clean counterparts |
| Materializer-to-layout handoff successor | Five retained generations; final 14 passes | Deterministic tracked-directory modes, safe dangling links and final workspace-root custody |

The nine controls overlap earlier cases; these counts must not be added into an
independent-test total. All final counts above have zero skipped cases on the
qualified laptop. Hosted machines with incompatible Git or worker Python/Git
identities explicitly skip those real-host fixtures; skips are not passes.
The fully authored authority fixture uses its own host pins and still refuses a
wrong pin. Production constants are unchanged.

The portability successor also removes a redundant test discovery check that
failed after a legitimate raw-source load supplied a module without `__spec__`.
The 26/47 receipts retain their exact earlier test/helper sources and 18-file
production/helper population. Those receipts do not qualify changed source.
The [handoff successor](MATERIALIZE-HANDOFF.md) changes materializer/layout behavior
and adds targeted controls; integrated v4 separately qualifies 138 selected files.
Current tracked workspace directories are explicitly normalized to 0755, independent
of umask, and checked before readiness. Safe dangling links remain exact link text;
the unchanged execution-profile inventory still refuses them. Layout readiness
therefore does not authorize a build.

## Partial build-configuration review

Ten pinned Lake configurations were read as data in 30 successful bounded Git
calls. The read took 0.047407 seconds before receipt persistence and recorded
0.018039 seconds of child CPU. An additional successful tree-metadata query took
0.001476 seconds. These engineering reads have no aggregate-profile qualification.

The retained review preserves upstream options and supplied ProofWidgets assets.
It does not qualify the complete reachable theorem/tactic/initializer/native
closure, nor establish whether Lake accepts a particular supplied asset trace.
No package configuration, proof body, tactic, compiler or build was executed by
that reader. Its original 105-file seal plus the seal itself are archived.

## Retention and limits

The separate current envelope preserves 3,036 regular members: all five handoff
generations, independent review, and integrated-v4 source/log/receipt records.
Its 106 handoff symlinks are metadata only. Integrated-v4 temporary case bodies
are explicitly omitted without traversal or revalidation. Earlier packages remain
unchanged; their identities and all current bindings are retained in the successor.

The historical 28-file package is now stored in a lossless outer archive so raw
metadata does not overwhelm code review. Its original seal, six archives, maps
and source records remain byte-identical; the new compact index binds them.
The [independent repack review](materialization-review-records/materialization-package-repack-review-v1.json)
checked both package generations and unchanged current source.

Six deterministic archives preserve every observed regular byte in their assigned
roots: 9,428 files / 14,201,890 bytes, compressed to 1,787,348 bytes. Exact member
maps accompany them. Original directory/mode and 222 symlink records remain
metadata; archives contain only normalized regular-file data. Every archived byte
was compared with the original, and each original tree was rechecked afterward.

The scheduling audit separately checked output absence through `lstat` and scoped
parent-directory enumeration. It verified original start/boot, unchanged source
and qualification bindings, and the still-open clock. No absent phase CPU/RSS or
materialization performance is inferred. Nested timing scopes are not additive.

Earlier unretained temporary fixtures and external inputs are explicit in the
omissions record. Full runtimes and original bare stores remain external; this
archive is evidence custody, not a substitute for the live validation API.
No deleted fixture or missing output was recreated.

Materialization yields exact source trees only. Adding build/cache mount paths or
assembling a package layout requires a separately inventoried preparation stage.
BUILD, association, export, prepare and proof-check success remain unearned here,
as do OCM learning, F1 corpus success, scaling and novelty claims.
