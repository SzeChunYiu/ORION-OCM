# V24 — independent implementation and source-scope review

The reviewer authored the paper documents and independently inspected production,
old source calls, oracle algorithms and tests. This is an independent code/proof
review, not a second independent paper author. No frozen historical file was edited.

## Actual code and source contracts inspected

core_v24.py loads immutable V15/V20 definitions and old AF/morphology functions.
Its source-module path check rejects a same-name import from a different file.
AFGraph checks every row, absent/present slot, destination and provenance entry,
including unused mappings and unreachable edges. Strings/integers/containers are
checked before set membership; Boolean destination aliases are excluded.

profiles_v24.py preserves stable source/slot histories and explicitly projects to
old fields. selected_profiles calls the actual old gamma_profiles. Full histories
keep edge identity separately from dictionaries; shared action labels keep shared
provenance. Scores are the old exact strings; repeated tags give set membership
and presence integers. Selected/full code contexts retain their actual decoder,
identity indices, all-defined/all-admitted flags and equality order.

preferences_v24.py retains every candidate ID, including vector/score aliases.
Reverse-coordinate and reverse-scalar comparisons have the correct orientation.
Admission is viable and the supplied reachability mode; evaluation stays total.
Winners use actual V20 attained/maximal. Prices are validated even for empty input.
Concrete positive dimension/nonnegative Fraction rules remain narrower than the
abstract ordered-ring proof. Valid old behavior and stricter parsing are separate.

plans_v24.py uses one explicit plan universe, independent admission/definedness,
actual partial Context values and thresholded attained pairs. Intersection starts
at all declared IDs, so empty history families have the correct universe result.
Undefined ambient losses are still type-validated; no silent loss-only witness
substitution or separate per-history plan choice is made.

## Independent oracle and registered primary tests inspected

oracle_v24.py enumerates paths recursively and selects least length/slot words;
it does not duplicate the old BFS queue. Literal two-output policy comparison
constructs expected score strings, while set union independently computes resources.
Raw JSON certificates distinguish Boolean/integer aliases and extra fields.
Preference expectations use literal coordinate dominance and all scalar minima;
plans use literal shared-ID predicates. The test code compares actual old functions,
full Context fields/observations and independently computed output certificates.

The registered primary strata and their measured counts belong to the canonical
RESULT_V24.json. This review did not rerun or relabel them as independent samples.
Named controls inspected include parallel repeated labels, absent slots, reordered
adjacency, loops, too-short horizons, repeated presence, tied IDs, unattained
coordinatewise minima, unreachable candidates, pairwise/nonjoint plans, empty
universes and injective renaming within the mapped universe.

## Separately preregistered64-case AF review — executed

Both normal Python3.12 and -O passed with byte-identical result JSON.
The final replay includes the oracle's strict recursive decoder/context type checks.
The exact freeze RNG order was used: seed20260920, source then slot, destination
first, a tag draw only for present slots, then start and target. Horizon4 was fixed.
The independent path/field/context certifier ran against actual graphs and helpers.
Measured counts:64 cases;413 present edges;99 absent slots;1200 full histories;
179 selected histories;1379 actual Context observations. These are supplementary,
not additions to exhaustive primary counts.

Input corpus SHA256:
5fb468fb99aaf63d06d5c907e6311aeed5c14655810f2cec79246a2deda4f1df
Identical normal/-O receipt SHA256:
4cfbf6c59b99d254124168cedd793dd02867cffc8b418d44f544ae0573131c72
Reproducible script: /tmp/gmi-v24-independent-probe.py on billy-laptop.
Receipts: /tmp/gmi-v24-independent-{normal,optimized}.json.
The fixed RNG specification is retained in the committed freeze independently of
these temporary replay records; receipt source hashes bind the tested modules.

## Driver, custody and scientific boundary

The reviewed driver requires actual theory, source ledger, scope and review files;
it freshly checks formal registrations and a fixed independent-test inventory.
It preserves original requirement identity and binds local source/receipt bytes.
Custody verifies freeze ancestry and freeze-only original tree, all26 direct pins,
and dereferences V23 and both V16 receipt input inventories. It checks immutable
qualified-revision identities and ledger/science links, not stale totals as current.
Final exact inventory/coverage and integration results are recorded by the driver.

No semantic production defect was found in this bounded review. Formal review
requested the sharper active-domain injectivity premise, which the formal author
implemented. It also identified a construction-stage mismatch: the first rich AF
Lean Context compared only erased profiles, whereas Python compares full raw
history identities. The corrected constructor uses equality on rich values;
postcomposition explicitly supplies the projected order. Actual corrected source
was reread. This repairs refinement without claiming order reflection for erasure.
Only R3-009 can earn scope. BFS algorithm refinement remains paper plus finite
calibration; finite tests do not prove all source instances or all historical
Gamma/SEL statements. The mathematical mechanisms are parent-owned integration.
