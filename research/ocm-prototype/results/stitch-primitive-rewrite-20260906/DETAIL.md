# Three separately frozen public contracts

## Default rewrite: failure retained

[Original manifest](raw/manifest.json) fixes Abstraction('-', '(+ #0 (* (- 1) #1))', 2),
four manual cases and the same two imported TRAIN programs. Two fresh groups
each dispatch rewrite once. Both native calls panic before a rewrite return
or qualification. No native Z3 check executes; six semantic rows are unreached,
not six counterexamples. Raw Rust assertion text is preserved.

[Freeze](https://github.com/SzeChunYiu/ORION-OCM/issues/62#issuecomment-5560421657).
The reported followed body reverses the holes. Flipping the supplied body under
the existing minus name would change semantics and is not the repair used.

## Breadth-first option: finite qualification

[Successor source diff](raw/breadth-first-successor/successor-controls/source.diff)
only records and forwards hole_choice='breadth-first' to rewrite.
The rule body/orientation, six inputs, checkers, resources and group order
are unchanged. All four manual rows and both TRAIN rows qualify;
eight actual native Z3 obligations pass. The existing unary/binary-minus row
is an unchanged no-alarm control. This is finite supplied-rule qualification,
not evidence of general canonicalization or newly learned subtraction.

[Freeze](https://github.com/SzeChunYiu/ORION-OCM/issues/62#issuecomment-5560504193).
Actual BFS launch is root-launch-v2. The copied root-launch-v1 in that successor
is historical metadata for the earlier default panic, not a second BFS run.

## Normalized induction: one proposal

[Input lineage](raw/normalized-induction/input-lineage.json) joins the exact two
sealed BFS decoded candidates to their unchanged original TRAIN tasks and
fixed-spec receipts. Original induction caller, seven source modules and
settings remain unchanged: one compress, iterations=1, max_arity=2, threads=1.
Compression keeps its original default traversal; no BFS keyword is added.
There is no rewrite API call or supplied learned library in this induction.

[Freeze](https://github.com/SzeChunYiu/ORION-OCM/issues/62#issuecomment-5560587744).
Two native obligations check the normalized TRAIN programs against their
original specs; two check the decoded, expanded rewrites. Those expansions
equal the normalized inputs. These valid whole-program checks are not an
independent macro-alias proof or evidence that a novel semantic operator arose.
fn_0(h)=not(h>=1) is h<=0 for Int by source algebra. Raw alias assessment
stays NOT_RUN; useful operator and later-generation consumption stay unestablished.

## Controls, resources and custody

Default/BFS groups each retain CPU0, 4 GiB, 45 s + 2 s cleanup / 49 s watchdog.
Normalized induction retains CPU0, 4 GiB, 60 s + 2 s / 64 s watchdog.
Every native checker retains 5,000 ms / 10 s limits. Self CPU/RSS, process
wall, supervisor wall and child receipts are separate scopes. Full tree cost,
acquisition/installation, energy and lifetime economy remain UNKNOWN.
Donor weighted syntax costs are not measured execution savings.

Original harmless-control failures, forwarding refusal and missing-copy
diagnostic are retained alongside their corrections. No semantic negative is
silently promoted. Capture manifests preserve prospective status bytes.
Actual completion metadata establishes execution. All scratch source, fixtures,
raw/checker records and root-launch files are copied exactly; binaries/caches
are excluded with runtime bindings retained. Original absolute references are
historical metadata, without a new relocation or isolation guarantee.
Publication executed only static copy/hash checks, no actor, test or regrade.
