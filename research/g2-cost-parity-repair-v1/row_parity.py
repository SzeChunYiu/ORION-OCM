"""Non-vacuous row parity for future versioned G2/G3 callers.

Inputs are finite, stable, sized lists/tuples of the existing row mappings.
Empty pairs and unequal lengths return False. Existing compared fields and
list/tuple normalization are preserved; this is not a correctness verifier.
Generators/unsized iterables, malformed rows and concurrent mutation are outside
this narrow API. Equal nonempty prefixes of two truncated populations cannot be
detected here: the caller must bind the expected population/cardinality.
No frozen study is imported or changed by this module.
"""

def g2_rows_equal(a_rows, b_rows):
    if not a_rows or len(a_rows) != len(b_rows):
        return False
    return all(
        a["task"] == b["task"]
        and a["enumeration_attempts"] == b["enumeration_attempts"]
        and a["unique_candidates_checked"] == b["unique_candidates_checked"]
        and tuple(a["program"]) == tuple(b["program"])
        and tuple(a["token_word"]) == tuple(b["token_word"])
        for a, b in zip(a_rows, b_rows)
    )

def g3_rows_equal(a_rows, b_rows):
    if not a_rows or len(a_rows) != len(b_rows):
        return False
    return all(
        a["task"] == b["task"]
        and a["enumeration_attempts"] == b["enumeration_attempts"]
        and a["unique_candidates_checked"] == b["unique_candidates_checked"]
        and tuple(a["token_word"]) == tuple(b["token_word"])
        and tuple(a["program"]) == tuple(b["program"])
        and tuple(a["macros_used"]) == tuple(b["macros_used"])
        for a, b in zip(a_rows, b_rows)
    )
