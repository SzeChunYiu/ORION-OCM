#!/usr/bin/env python3
"""Exact finite INDEX feedback and strategic-comparison boundary witnesses.

The analytic proofs in INTERACTIVE_CUT_SCOPE_CORRECTION_V1.md establish the
general one-way lower bound and computable-real undecidability. These bounded
checks exercise concrete encoders, decoders, transcripts and rational games.
"""

from fractions import Fraction
from itertools import combinations, product
import json


def conflict_edges(response_rows, contexts=None):
    """Characteristic graph of a total finite exact-function obligation."""
    contexts = tuple(range(len(response_rows[0]))) if contexts is None else tuple(contexts)
    return {
        (i, j)
        for i, j in combinations(range(len(response_rows)), 2)
        if any(response_rows[i][y] != response_rows[j][y] for y in contexts)
    }


def exact_decoder(response_rows, encoder):
    """Construct a common decoder table, or reject conflicting message cells."""
    cells = {}
    for i, row in enumerate(response_rows):
        for y, required in enumerate(row):
            key = (encoder[i], y)
            if key in cells and cells[key] != required:
                return None
            cells[key] = required
    return cells


def feedback_messages(word, index):
    """Bob sends a fixed-width index; Alice sends one selected response bit."""
    width = (len(word) - 1).bit_length()
    request = tuple((index >> shift) & 1 for shift in reversed(range(width)))
    decoded_index = 0
    for bit in request:
        decoded_index = 2 * decoded_index + bit
    return request, (word[decoded_index],)


def index_witness(n):
    if n < 1:
        raise ValueError("INDEX needs at least one input bit")
    words = list(product((0, 1), repeat=n))
    edges = conflict_edges(words)
    # Every pair conflicts; the complete graph forces one distinct message per
    # input word. Sending the whole word supplies a matching construction.
    assert len(edges) == len(words) * (len(words) - 1) // 2
    one_way_encoder = {i: word for i, word in enumerate(words)}
    decoder = exact_decoder(words, one_way_encoder)
    assert decoder is not None
    transcripts = set()
    checked = 0
    for word in words:
        for y in range(n):
            request, response = feedback_messages(word, y)
            assert response[0] == word[y]
            assert len(request) == (n - 1).bit_length()
            transcripts.add((request, response))
            checked += 1

    # At each fixed received index, the new obligation has just two response
    # classes. A binary coloring is proper, and a cross-class edge requires 2.
    conditioned_edges = 0
    for y in range(n):
        fixed = conflict_edges(words, (y,))
        colors = [word[y] for word in words]
        assert fixed
        assert all(colors[i] != colors[j] for i, j in fixed)
        assert len(set(colors)) == 2
        conditioned_edges += len(fixed)

    # For n>=2 at least one fixed word has different replies to different
    # requests: there cannot be a reply encoder depending on x alone.
    feedback_dependence = any(len(set(word)) > 1 for word in words)
    assert feedback_dependence == (n >= 2)
    return {
        "input_bits": n,
        "upstream_words": len(words),
        "one_way_conflict_edges": len(edges),
        "one_way_minimum_complete_message_symbols": len(words),
        "one_way_minimum_fixed_bits": n,
        "interactive_input_pairs": checked,
        "interactive_complete_transcripts": len(transcripts),
        "interactive_backward_fixed_bits": (n - 1).bit_length(),
        "interactive_forward_fixed_bits": 1,
        "interactive_total_fixed_bits": (n - 1).bit_length() + 1,
        "conditioned_indices": n,
        "conditioned_conflict_edges": conditioned_edges,
        "conditioned_minimum_reply_symbols": 2,
        "reply_depends_on_feedback_for_some_fixed_input": feedback_dependence,
    }


def exhaustive_small_one_way_encoders():
    rows = []
    for n in (1, 2):
        words = list(product((0, 1), repeat=n))
        for alphabet in range(1, len(words) + 1):
            tested = successful = 0
            for encoder in product(range(alphabet), repeat=len(words)):
                table = exact_decoder(words, encoder)
                # Independent pigeonhole characterization for total INDEX.
                assert (table is not None) == (len(set(encoder)) == len(words))
                if table is not None:
                    assert all(table[(encoder[i], y)] == words[i][y]
                               for i in range(len(words)) for y in range(n))
                    successful += 1
                tested += 1
            rows.append({"n": n, "alphabet": alphabet,
                         "encoders": tested, "successful": successful})
    return rows


def exact_single_player_status(losses):
    """Rational finite game: return zero-regret and nondominated action IDs."""
    losses = tuple(Fraction(value) for value in losses)
    regret = [tuple(value - alternative for alternative in losses) for value in losses]
    zero_regret = tuple(i for i, row in enumerate(regret) if all(x <= 0 for x in row))
    nondominated = tuple(
        i for i, row in enumerate(regret)
        if not any(all(a <= b for a, b in zip(other, row))
                   and any(a < b for a, b in zip(other, row))
                   for other in regret)
    )
    return zero_regret, nondominated


def rational_strategic_checks():
    grid = tuple(Fraction(i, 2) for i in range(-2, 3))
    checked = tied = 0
    for actions in (2, 3):
        for losses in product(grid, repeat=actions):
            zero, frontier = exact_single_player_status(losses)
            optimum = tuple(i for i, value in enumerate(losses) if value == min(losses))
            assert zero == frontier == optimum
            checked += 1
            tied += len(optimum) > 1
    # Positive exact rationals far below ordinary float range are not zero.
    for exponent in (1, 32, 2048):
        assert exact_single_player_status((0, Fraction(1, 2**exponent))) == ((0,), (0,))
    assert exact_single_player_status((0, 0)) == ((0, 1), (0, 1))
    return {"finite_rational_games": checked, "games_with_tied_optima": tied,
            "strict_positive_vs_zero_cases": 3, "exact_zero_tie_cases": 1,
            "decides_arbitrary_computable_real_equality": False}


def run():
    rows = [index_witness(n) for n in range(1, 9)]
    return {
        "terminal": "GRAND_GMI_INTERACTIVE_CUT_SCOPE_CORRECTION_V1_ALL_GREEN",
        "scope": "bounded exact classical INDEX, registered one-way information patterns, finite rational games",
        "index_sweep": rows,
        "index_four_bit_hostile_witness": rows[3],
        "one_way_encoder_census": exhaustive_small_one_way_encoders(),
        "rational_strategic_specialization": rational_strategic_checks(),
        "claims_general_interactive_optimality": False,
        "claims_global_or_empirical_closure": False,
    }


if __name__ == "__main__":
    print(json.dumps(run(), indent=2, sort_keys=True))
