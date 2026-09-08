"""Replay the 76 frozen proposals against the same P1. Screening only."""
import json
import os
import platform
import resource
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
REVIVAL = HERE.parent
CONSUMER = REVIVAL.parent / "ordinary-cut-source-evidence-v1" / "consumer-v3"
sys.path[:0] = [str(HERE), str(CONSUMER), str(CONSUMER / "donor")]

import alias_screen as alias
import load_frozen as frozen


class Work(dict):
    def __init__(self, maximum):
        super().__init__()
        self.maximum = maximum
        self.exhausted = False

    def __setitem__(self, key, value):
        if key == "token_states" and value > self.maximum:
            self.exhausted = True
            raise ValueError("REGISTERED_TOKEN_STATE_BOUND")
        super().__setitem__(key, value)


def compact_alias(row):
    return {
        "kind": row.get("kind"),
        "label": row.get("label"),
        "premise_indices": row.get("premise_indices"),
        "substitution": row.get("substitution"),
        "proof": row.get("proof"),
    }


def rss_kib(usage):
    raw = usage.ru_maxrss
    if platform.system() == "Darwin":
        return int(raw / 1024)
    return int(raw)


def main(output):
    start = time.perf_counter()
    usage0 = resource.getrusage(resource.RUSAGE_SELF)
    output = Path(output).resolve()
    if output.exists():
        raise ValueError("output already exists")
    output.mkdir(parents=True)
    log_path = output / "screens.jsonl"
    log = log_path.open("x")
    original = frozen.load_result()
    p1 = frozen.load_p1()
    root_counts = frozen.root_status_counts(original)
    proposals = frozen.proposals_in_order(original)
    work = Work(2000000)
    screens = []
    status_counts = {}
    alias_labels = {}
    admitted = 0
    still_unknown = 0
    aliases_found = 0
    primitive = 0
    negative = 0
    used_premises = 0
    terminal = "RUNNING"
    error = None
    try:
        if [root_counts.get("TRACE_UNUSABLE", 0), root_counts.get("UNKNOWN_INTERFACE", 0),
            root_counts.get("ENUMERATED", 0)] != [57, 54, 17]:
            raise ValueError("frozen root status counts")
        if len(proposals) != 76 or len(p1) != 4323:
            raise ValueError("frozen proposal/P1 population")
        if original.get("native_calls") != 0:
            raise ValueError("frozen native calls")
        for i, row in enumerate(proposals):
            if work.exhausted:
                screens.append({
                    "index": i, "ordinal": row["ordinal"], "label": row["label"],
                    "canonical_id": row["canonical_id"], "query": row["query"],
                    "premises": row["premises"], "status": "UNKNOWN_RESOURCE",
                    "coverage_complete": False, "ground_admitted": None,
                    "n_aliases": 0, "aliases": [], "native_acceptance": False,
                })
                log.write(json.dumps(screens[-1], sort_keys=True, separators=(",", ":")) + "\n")
                log.flush()
                still_unknown += 1
                continue
            body = {"query": row["query"], "premises": row["premises"],
                    "parameters": row["parameters"]}
            screen = alias.screen(body, p1, work)
            status = screen["status"]
            status_counts[status] = status_counts.get(status, 0) + 1
            record = {
                "index": i,
                "ordinal": row["ordinal"],
                "label": row["label"],
                "canonical_id": row["canonical_id"],
                "query": row["query"],
                "premises": row["premises"],
                "original_screen_status": (row["original_screen"] or {}).get("status"),
                "original_reasons": (row["original_screen"] or {}).get("reasons"),
                "status": status,
                "coverage_complete": screen.get("coverage_complete"),
                "n_aliases": len(screen.get("aliases") or []),
                "n_unknown_contract_reasons": len(screen.get("reasons") or []),
                "aliases": [compact_alias(a) for a in screen.get("aliases") or []],
                "native_acceptance": False,
            }
            if status == "UNKNOWN" and screen.get("reasons") and isinstance(screen["reasons"][0], str) and \
                    str(screen["reasons"][0]).startswith("UNSUPPORTED_GROUND_SYNTAX"):
                record["ground_admitted"] = False
                still_unknown += 1
            else:
                record["ground_admitted"] = True
                admitted += 1
                if status == "UNKNOWN":
                    still_unknown += 1
            if screen.get("aliases"):
                aliases_found += 1
                primitive += 1
                labels = []
                for a in screen["aliases"]:
                    lab = a.get("label")
                    if lab:
                        alias_labels[lab] = alias_labels.get(lab, 0) + 1
                        labels.append(lab)
                    if a.get("kind") == "one_logical_assertion" and a.get("premise_indices"):
                        used_premises += 1
                record["alias_labels"] = labels
            elif status == "SCREENED_NEGATIVE_IN_DOMAIN":
                negative += 1
            screens.append(record)
            log.write(json.dumps(record, sort_keys=True, separators=(",", ":")) + "\n")
            log.flush()
        if work.exhausted:
            terminal = "UNKNOWN"
        elif admitted == 76 and still_unknown == 0 and primitive == 76:
            terminal = "PRIMITIVE_ALIAS"
        elif admitted == 76 and still_unknown == 0:
            terminal = "SYNTAX_ADMISSION_REPAIRED_MATCHING_REACHED"
        elif admitted:
            terminal = "SYNTAX_ADMISSION_REPAIRED_MATCHING_REACHED"
        else:
            terminal = "UNKNOWN"
    except BaseException as exc:
        terminal = "CANNOT_CHECK_" + type(exc).__name__
        error = {"type": type(exc).__name__, "message": str(exc)}
    usage = resource.getrusage(resource.RUSAGE_SELF)
    result = {
        "schema": "ordinary.cut-syntax-revival.v1",
        "terminal": terminal,
        "pid": os.getpid(),
        "native_calls": 0,
        "new_native_admissions": 0,
        "frozen_root_status_counts": root_counts,
        "frozen_trace_unusable": 57,
        "frozen_unknown_interface": 54,
        "proposal_occurrences": len(proposals),
        "ordinary_contracts_retained": len(p1),
        "admitted": admitted,
        "still_unknown": still_unknown,
        "aliases_found": aliases_found,
        "primitive_alias_proposals": primitive,
        "screened_negative": negative,
        "aliases_using_cut_premises": used_premises,
        "screen_status_counts": status_counts,
        "alias_label_counts": dict(sorted(alias_labels.items(), key=lambda kv: (-kv[1], kv[0]))),
        "matcher_counter_reported": True,
        "work": dict(work),
        "token_bound_reached": work.exhausted,
        "registered_token_state_bound": 2000000,
        "original_consumer_deadline_s": 60,
        "original_outer_containment_s": 180,
        "g2_3_primitive_alias_box": (
            "ALL_ADMITTED_ARE_P1_ALIASES" if admitted == 76 and still_unknown == 0 and primitive == 76 else
            "MIXED_ALIAS_AND_NEGATIVE" if admitted == 76 and still_unknown == 0 else
            "NOT_YET"
        ),
        "g2_4_causal_use_box": "NOT_YET",
        "causal_method_reuse_supported": False,
        "screens": screens,
        "error": error,
        "inputs": {
            "RAW": frozen.identity(frozen.RAW),
            "RESULT_member": {"path": frozen.RESULT_MEMBER, "sha256": frozen.RESULT_SHA256},
            "P1_member": {"path": frozen.P1_MEMBER, "sha256": frozen.P1_SHA256},
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
        "interpretation": "Syntax-boundary repair and one-step P1 matching only. No restart, fresh-task, or removal ablation. Not a learned-method or novelty claim.",
    }
    try:
        log.close()
    except Exception:
        pass
    output.mkdir(parents=True, exist_ok=True)
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
    return 0 if terminal in ("PRIMITIVE_ALIAS", "SYNTAX_ADMISSION_REPAIRED_MATCHING_REACHED",
                             "NO_NEW_ABSTRACTION") else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1]))
