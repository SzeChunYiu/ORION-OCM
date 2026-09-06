# Breadth-first supplied rewrite successor — prospective only

Owner #62. The original manual and TRAIN rewrite calls both raised a native body
assertion and returned no rewrite; zero Z3 calls followed. Preserve original
CANNOT_CHECK_NORMALIZATION and seal d26b19f5e96fd19dc163bc30140825efd656323f6d897da0e4a7d28d5d841dcb.

## Single change
Pass hole_choice="breadth-first" to the same supplied-identity rewrite. The complete
identity remains name "-", body "(+ #0 (* (- 1) #1))", arity2. No swapped holes,
replacement symbol, removed assertion or changed checker. Same manual4/TRAIN2
programs, order, original specifications, resources and maximum8 Z3 obligations.
Two fixed groups, one rewrite each. No compress, synthesis or persistence.

## Source-bound hypothesis, not a proven fix
Pinned core0ef5ec7 defaults to depth-first, choosing the last queued hole.
Application expansion appends function then argument. The right hole is therefore
encountered first for this supplied body. PatternArgs.find_variable numbers newly
encountered arguments by discovery order; the tracked body becomes
(+ #1 (* (- 1) #0)). The final followed-body assertion refuses that permutation.
BFS chooses the first queued hole and is predicted to encounter the left hole first
for this exact pattern. This is not a general argument-canonicalization repair.

- [Native option and traversal](https://github.com/mlb2251/stitch/blob/0ef5ec7f17091d22b8fa959fb5705e359d735a47/src/compression.rs#L106)
- [Argument renumbering](https://github.com/mlb2251/stitch/blob/0ef5ec7f17091d22b8fa959fb5705e359d735a47/src/pattern_args.rs#L160)
- [Expansion ordering](https://github.com/mlb2251/stitch/blob/0ef5ec7f17091d22b8fa959fb5705e359d735a47/src/expansion.rs#L77)

The Python rewrite implementation forwards kwargs to native Clap configuration;
its docstring only advertises cost options. Native acceptance and semantic safety
of this explicit existing option remain UNEXECUTED here until root freezes/runs.
No claim of a primitive-name collision being solved follows from the source diagnosis.

## Harmless qualification and custody
successor-controls/source.diff is the exact two-line caller change plus fake-donor
keyword-forwarding assertions. One expected red forwarding control is retained.
A copied fixture-manifest omission caused the first combined attempt to have7pass/
1error; byte-exact restoration is recorded, then8 harmless controls passed.
These use explicit fake donor/verifier functions, not native calls.
All original77 bindings and22 sealed capture members were reverified unchanged.
The seven Python donor/checker files and three fixture files are byte-identical.
Only caller.py and test_capture.py differ among copied Python files.
Use manifest.json and launch.json as the prospective successor, not predecessor copies.
All costs/denominators/refusals in CORE.md remain; total process-tree CPU/RSS UNKNOWN.
