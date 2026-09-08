"""Replay the 54 frozen UNKNOWN_INTERFACE roots. Successor only; #164 stays frozen."""
import json
import os
import platform
import resource
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
REVIVAL = HERE.parent
sys.path[:0] = [str(HERE)]

import boundary as cuts
import classify as C
import load_frozen as frozen


class Work(dict):
    def __init__(self):
        super().__init__()


def rss_kib(usage):
    raw = usage.ru_maxrss
    if platform.system() == "Darwin":
        return int(raw / 1024)
    return int(raw)


def compact_cut(row):
    out = {"status": row.get("status"), "head": row.get("head"),
           "essential_port": row.get("essential_port"), "child": row.get("child")}
    if row.get("status") == "CUT_PROPOSAL":
        body = row["body"]
        out.update(canonical_id=row.get("canonical_id"),
                   query=body.get("query"), premises=body.get("premises"),
                   n_parameters=len(body.get("parameters") or []),
                   logical_dag_nodes=row.get("logical_dag_nodes"),
                   native_acceptance=False)
    else:
        out["reason"] = row.get("reason") or row.get("error")
    return out


def main(output):
    start = time.perf_counter()
    usage0 = resource.getrusage(resource.RUSAGE_SELF)
    output = Path(output).resolve()
    if output.exists():
        raise ValueError("output already exists")
    output.mkdir(parents=True)
    original = frozen.load_result()
    packet = frozen.load_packet()
    p1 = frozen.load_p1()
    p1_by = frozen.p1_index(p1)
    packet_by = {row["label"]: row for row in packet["roots"]}
    root_counts = frozen.root_status_counts(original)
    unknown = frozen.unknown_interface_roots(original)
    if [root_counts.get("TRACE_UNUSABLE", 0), root_counts.get("UNKNOWN_INTERFACE", 0),
        root_counts.get("ENUMERATED", 0)] != [57, 54, 17]:
        raise ValueError("frozen root status counts")
    if original.get("native_calls") != 0:
        raise ValueError("frozen native calls")
    work = Work()
    records = []
    status_counts = {}
    cut_status_counts = {}
    subtype_status = {}
    new_proposal_roots = 0
    new_proposals = 0
    still_unknown = 0
    terminal = "RUNNING"
    error = None
    try:
        for row in unknown:
            label = row["label"]
            contract = p1_by[label]
            subtype = C.classify(contract)
            packet_row = packet_by[label]
            record = {
                "ordinal": row["ordinal"],
                "label": label,
                "frozen_error": row.get("error"),
                "subtype": subtype,
                "n_float": len(contract.get("floating") or []),
                "float_types": C.floating_types(contract),
                "n_essential": len(contract.get("essential") or []),
                "n_dv": len(contract.get("dv") or []),
                "native_acceptance": False,
            }
            try:
                if packet_row.get("trace_disposition") != "TRACE_READY" or packet_row.get("trace") is None:
                    raise ValueError("missing ready trace")
                mined = cuts.enumerate_two(packet_row["trace"], packet_row["contracts"], work)
                cut_rows = mined["rows"]
                n_proposal = sum(1 for cut in cut_rows if cut.get("status") == "CUT_PROPOSAL")
                record.update(status="ENUMERATED", n_cuts=len(cut_rows),
                              n_cut_proposal=n_proposal,
                              cuts=[compact_cut(cut) for cut in cut_rows])
                if n_proposal:
                    new_proposal_roots += 1
                    new_proposals += n_proposal
                for cut in cut_rows:
                    st = cut.get("status")
                    cut_status_counts[st] = cut_status_counts.get(st, 0) + 1
            except (ValueError, KeyError, TypeError, IndexError, RecursionError) as exc:
                record.update(status="UNKNOWN_INTERFACE",
                              error=type(exc).__name__ + ": " + str(exc),
                              n_cuts=0, n_cut_proposal=0, cuts=[])
                still_unknown += 1
            status_counts[record["status"]] = status_counts.get(record["status"], 0) + 1
            subtype_status.setdefault(subtype, {"roots": 0, "enumerated": 0,
                                                "still_unknown": 0, "cut_proposal_roots": 0,
                                                "cut_proposals": 0})
            bucket = subtype_status[subtype]
            bucket["roots"] += 1
            if record["status"] == "ENUMERATED":
                bucket["enumerated"] += 1
                bucket["cut_proposal_roots"] += 1 if record["n_cut_proposal"] else 0
                bucket["cut_proposals"] += record["n_cut_proposal"]
            else:
                bucket["still_unknown"] += 1
            records.append(record)
        if still_unknown == 54:
            terminal = "UNKNOWN"
        elif new_proposals:
            terminal = "INTERFACE_ADMISSION_REPAIRED"
        else:
            terminal = "INTERFACE_DIAGNOSED_NO_PROPOSAL"
    except BaseException as exc:
        terminal = "CANNOT_CHECK_" + type(exc).__name__
        error = {"type": type(exc).__name__, "message": str(exc)}
    usage = resource.getrusage(resource.RUSAGE_SELF)
    exclusive = C.subtype_counts(records)
    result = {
        "schema": "ordinary.cut-interface-revival.v1",
        "terminal": terminal,
        "pid": os.getpid(),
        "native_calls": 0,
        "new_native_admissions": 0,
        "prefix_used": None,
        "frozen_root_status_counts": root_counts,
        "frozen_unknown_interface": 54,
        "replayed": len(records),
        "exclusive_subtype_counts": exclusive,
        "subtype_outcomes": subtype_status,
        "root_status_counts": status_counts,
        "cut_status_counts": cut_status_counts,
        "roots_newly_with_cut_proposal": new_proposal_roots,
        "new_cut_proposals": new_proposals,
        "still_unknown_interface": still_unknown,
        "ordinary_contracts_retained": len(p1),
        "work": dict(work),
        "roots": records,
        "error": error,
        "inputs": {
            "RAW": frozen.identity(frozen.RAW),
            "RESULT_member": {"path": frozen.RESULT_MEMBER, "sha256": frozen.RESULT_SHA256},
            "P1_member": {"path": frozen.P1_MEMBER, "sha256": frozen.P1_SHA256},
            "EXPORT_RAW": frozen.identity(frozen.EXPORT_RAW),
            "PACKET_member": {"path": frozen.PACKET_MEMBER, "sha256": frozen.PACKET_SHA256},
        },
        "measured_windows": {
            "wall_s": time.perf_counter() - start,
            "user_cpu_s": usage.ru_utime - usage0.ru_utime,
            "system_cpu_s": usage.ru_stime - usage0.ru_stime,
            "max_rss_kib": rss_kib(usage),
            "platform": platform.platform(),
            "nested_not_additive": True,
            "not_lifetime_cost": True,
        },
        "interpretation": (
            "Successor 2-or-3 class / no-DV / no-extra-$e context plus 0-ary P1 syntax "
            "constructors. Frozen #164 refusals were not rewritten. Not native admission."
        ),
    }
    (output / "RESULT.json").write_text(json.dumps(result, sort_keys=True, indent=2, allow_nan=False) + "\n")
    (output / "PROCESS.json").write_text(json.dumps({
        "pid": os.getpid(),
        "terminal": terminal,
        "wall_s": result["measured_windows"]["wall_s"],
        "user_cpu_s": result["measured_windows"]["user_cpu_s"],
        "system_cpu_s": result["measured_windows"]["system_cpu_s"],
        "max_rss_kib": result["measured_windows"]["max_rss_kib"],
        "native_calls": 0,
        "argv": sys.argv,
        "cwd": os.getcwd(),
        "python": sys.version,
    }, sort_keys=True, indent=2) + "\n")
    return 0 if terminal in ("INTERFACE_ADMISSION_REPAIRED", "INTERFACE_DIAGNOSED_NO_PROPOSAL") else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1]))
