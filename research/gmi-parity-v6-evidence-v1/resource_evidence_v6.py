"""Independent static opcode and block reconstruction, adapted from the V4 auditor."""
from __future__ import annotations
import dis
from frozen_contract_v1 import EXPECTED, FAMILIES, IDS, KEYS, require, same


def opcode_contract(module):
    offsets = {}
    for cid in IDS:
        fn = module.CANDIDATES[cid]["fn"]
        instructions = list(dis.get_instructions(fn, adaptive=False, show_caches=False))
        require(not any(i.opcode in dis.hasjabs or i.opcode in dis.hasjrel
                        or i.opname in ("RETURN_GENERATOR", "YIELD_VALUE")
                        for i in instructions), "non-straight-line candidate")
        offsets[cid] = [i.offset for i in instructions if i.opname not in ("RESUME", "CACHE")]
        require(bool(offsets[cid]), "empty opcode contract")
    return offsets


def validate_instrument(packet, module):
    offsets = opcode_contract(module)
    counts = {cid: 8 * len(offsets[cid]) for cid in IDS}
    instrument = packet["instrumentation"]
    require(set(instrument) == {"status", "opcode_counts", "witness_diagnostics",
            "forward_witnesses", "reverse_witnesses"}, "instrument fields differ")
    same(instrument["status"], "COMPLETE_OPCODE_WITNESSES_AND_ORDER_INVARIANCE_GREEN",
         "instrument status differs")
    for order in ("forward_witnesses", "reverse_witnesses"):
        require(set(instrument[order]) == set(IDS), "incomplete trace universe")
        for cid in IDS:
            expected = {"count": counts[cid], "calls": [
                {"opcode_offsets": offsets[cid], "output": y, "returned": True}
                for y in EXPECTED]}
            same(instrument[order][cid], expected, "incomplete/altered trace: " + cid)
    diagnostics = {cid: {"expected_events_per_call": len(offsets[cid]),
        "frames_observed": 8, "events_per_call": [len(offsets[cid])] * 8,
        "total_events": counts[cid], "complete_frames": 8, "empty_frames": 0,
        "all_frames_returned": True} for cid in IDS}
    same(instrument["witness_diagnostics"], diagnostics, "trace diagnostics differ")
    same(instrument["opcode_counts"], counts, "instrument counts differ")
    same(packet["opcode_counts"], counts, "packet opcode counts differ")
    return counts


def reconstruct_boxes(measurements, counts):
    require(type(measurements) is dict and set(measurements) == set(IDS),
            "incomplete timing register")
    boxes = {}
    for cid in IDS:
        rows = measurements[cid]
        require(type(rows) is list and len(rows) == 32, "missing/extra timing blocks")
        for block, row in enumerate(rows):
            order = list(IDS) if (block // 4) % 2 == 0 else list(reversed(IDS))
            offset = block % 4
            order = order[offset:] + order[:offset]
            require(type(row) is dict and set(row) == {"block_index", "order_index",
                    "candidate_id", "checksum", "wall_block_ns", "process_block_ns"},
                    "timing row fields differ")
            same([row["block_index"], row["order_index"], row["candidate_id"], row["checksum"]],
                 [block, order.index(cid), cid, 80000], "schedule/checksum mismatch")
            for key in KEYS[1:]:
                require(type(row[key]) is int and row[key] > 0, "invalid measured duration")
        boxes[cid] = {KEYS[0]: [counts[cid], counts[cid]], **{
            k: [min(r[k] for r in rows), max(r[k] for r in rows)] for k in KEYS[1:]}}
    return boxes


def derive_frontier(boxes):
    def dominates(a, b):
        return (all(a[k][1] <= b[k][0] for k in KEYS)
                and any(a[k][1] < b[k][0] for k in KEYS))
    parents = {cid: [other for other in IDS if other != cid
                    and dominates(boxes[other], boxes[cid])] for cid in IDS}
    frontier = [cid for cid in IDS if not parents[cid]]
    require(bool(frontier), "empty finite frontier")
    families = sorted({FAMILIES[cid] for cid in frontier})
    terminal = {("NEURAL",): "DERIVED_NEURAL_AT_REGISTERED_SCOPE",
                ("NON_NEURAL",): "DERIVED_NON_NEURAL_AT_REGISTERED_SCOPE"}.get(
                    tuple(families), "UNDECIDED_FROM_CURRENT_EVIDENCE")
    return {"dominated_by": parents, "frontier_candidate_ids": frontier,
            "frontier_families": families, "terminal": terminal,
            "winner_candidate_id": frontier[0] if len(frontier) == 1 else "NONE"}


def validate_resources(packet, module):
    counts = validate_instrument(packet, module)
    boxes = reconstruct_boxes(packet["measurements"], counts)
    same(packet["resource_boxes"], boxes, "observed envelopes differ")
    verdict = derive_frontier(boxes)
    for key, expected in verdict.items():
        same(packet[key], expected, "derived result differs: " + key)
    return {**verdict, "resource_boxes": boxes, "opcode_counts": counts}
