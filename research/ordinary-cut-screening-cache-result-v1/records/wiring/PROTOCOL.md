# One prospective cached screening attempt
## Fixed experiment
Use all 76 saved CUT_PROPOSAL occurrences in original root/cut order, including
duplicate canonical IDs, and the entire unchanged 4,323-contract P1. No roots,
proposals, contracts, syntax grammar or matcher semantics change.
The old two-node extractor and native exporter are not invoked.

Keep 2,000,000 matcher states, 60 seconds soft driver time, 512 syntax input tokens,
4,096 syntax proof labels and 180 seconds outer containment. Deadline checks
remain on cache hits. Inner Earley calls may overrun the soft deadline; the exact
existing outer cleanup is retained. Unsupported/resource outcomes remain UNKNOWN.

## Method and cost
The request/result discriminator is
functools.cache.completed-syntax-results.v1.
The 10 repaired modules are byte-identical to the independently accepted repair.
Cold library snapshot, per-context construction, cache lookups/misses/hits,
parse/emission on misses, stored key/proof sizes and returned proof labels stay
in the existing Work/context reports. No historical parse time is charged again
on hits. Returned proof labels count only successful returns; discarded copy-out
work remains charged in wall time.

The driver still starts its 60-second interval before request/source/input reads.
New history reads and copied-cache setup are charged within that interval.
previous_costs preserves the original opportunity driver/work/outer/caller.
prior_screen_costs separately preserves the first screen driver/work/contexts
and exact outer/caller records. All six raw source records are bound in inputs.
Within each attempt, caller/outer/driver windows are nested and must not be summed.
Across attempts the retained measured windows are disjoint. Authoring, review,
interpreter startup outside the declared windows, and uninstrumented I/O are not
silently treated as zero or a complete lifetime cost.

## Input/output and imports
Seven exact input descriptors are frozen: the full P1 plus both prior triples.
Only the original opportunity result supplies the proposed body/order; the
first screen is history only, never a result-based selector.
The output keeps 76 ordered SCREEN records and RESULT, with partial prefixes
and errors preserved. Output inspection checks identities, history, cache report
presence and current source imports; it does not independently prove aliases.
All 11 production files, fixed Python and Lark runtime retain exact byte pins.
The new syntax_memo import must be present at its declared absolute path.

## Once-only gate
The prospective request and observer contract are concrete. Their gate is absent.
The observer embeds the request identity; the request references the observer
path, avoiding a circular hash. Root's gate must bind that exact request, observer,
observer contract, argv/cwd/Python, seven inputs, output/observation paths and the
single integrated review as accepted_reviews.observer_source. The inherited
screen source and cache closure occupy screening_source and cache_repair.
Additional exact source/qualification/caller pins can be in review_bindings.
No execution follows from this source qualification.

## Affected controls only
Five authored JSON output controls cover the clean complete case; each new prior
cost component/hash; method identity; cache module path; and cache report presence.
One exact isolated observer startup refuses at its absent gate before real input
reads or research imports. One isolated driver startup refuses an authored wrong
method before gate/input access. All exercised control module paths and pinned
runtime files are recorded before/after.
Inherited process cleanup has exact block equality and its prior receipt; no new
cleanup experiment or old syntax/cache/integration suite was run.
