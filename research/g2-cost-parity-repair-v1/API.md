# Explicit successor caller boundary

Make the standalone [row_parity.py](row_parity.py) module importable in a separately
versioned caller, then use `g2_rows_equal(a_rows, b_rows)` or
`g3_rows_equal(a_rows, b_rows)` for the corresponding schema. No OCM/study import
is required. Neither historical module is monkey-patched or rebound.

Inputs are finite, stable, sized lists/tuples of row mappings. Empty populations,
including two empty lists, return False; unequal lengths return False. The
remaining comparisons preserve the historical behavior and list/tuple normalization:

| Schema | Compared fields |
|---|---|
| G2 | task, enumeration_attempts, unique_candidates_checked, program, token_word |
| G3 | the G2 fields plus ordered macros_used |

This is a parity guard, not a validity checker. It does not newly inspect `verified`
or G2's `macro_used`; the caller still owns verification and actual-use criteria.
Malformed/missing fields may raise as before. Unsized generators, arbitrary
iterables and concurrent mutation are outside this small API. No input is copied,
consumed as an iterator or mutated by the guard on the declared list/tuple domain.

Equal nonempty prefixes of two equally truncated populations cannot be detected
by pairwise equality. The caller must independently bind the expected ordered
population and cardinality, including its identity/duplication policy.

At pinned main7926c3, G3 imports G2 from its frozen path (lines25–29) and requires
blob4c8cb45c… at run375–379 and test13–16. G3 does not use G2.rows_equal: its own
rows_equal336–345 duplicates the unchecked zip and additionally compares macro
labels. Its parity/revocation call sites are466–470 and523–525. G2 call sites are
456–459. Both currently construct arms from a common nonempty task population;
this source defect does not overturn any retained parity result.

The additive patch creates only this successor directory. Any later caller
integration must name the chosen function and maintain its own source contract;
this artifact neither changes G3's G2 pin nor authorizes an experiment rerun.
