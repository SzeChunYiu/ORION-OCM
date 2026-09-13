"""Consistency of the retained forward priming summaries, not raw-trace validation."""
from __future__ import annotations
from frozen_contract_v1 import IDS, require, same


def validate_priming(instrument, offsets):
    summaries = instrument["priming_witness_diagnostics"]
    require(type(summaries) is dict and set(summaries) == set(IDS),
            "priming summary universe differs")
    incomplete = []
    for cid in IDS:
        row = summaries[cid]
        n = len(offsets[cid])
        require(type(row) is dict, "priming diagnostic must be an object")
        # These are the two summary shapes retained in the three frozen packets.
        # This is not a general law of any interpreter version or tracing history.
        events = row["events_per_call"]
        require(events == [n] * 8 or events == [0] + [n] * 7,
                "outside retained forward-priming summary patterns")
        empty = int(events[0] == 0)
        expected = {"expected_events_per_call": n, "frames_observed": 8,
                    "events_per_call": [0] * empty + [n] * (8 - empty),
                    "total_events": n * (8 - empty), "complete_frames": 8 - empty,
                    "empty_frames": empty, "all_frames_returned": True}
        same(row, expected, "inconsistent retained priming summary")
        if empty:
            incomplete.append(cid)
    same(instrument["priming_was_required_on_this_interpreter"], bool(incomplete),
         "priming flag contradicts retained summary")
    return {"summary_consistency": "PASS", "reported_incomplete_candidates": incomplete,
            "forward_priming_raw_traces_available": False,
            "reverse_priming_summaries_available": False,
            "priming_necessity_or_causality_established": False}
