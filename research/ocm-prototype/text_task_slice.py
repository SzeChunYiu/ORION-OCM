"""Run: python text_task_slice.py --state STATE ask 'What is the largest of 8, 2 and 5?'"""
from __future__ import annotations

import argparse
from contextlib import contextmanager
import json
from pathlib import Path
import sys
import time

HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(HERE.parents[1] / "src"), str(HERE)]

from ocm.kso.ids import content_hash
from ocm.kso.warrant import WarrantProfile
from ocm.runtime.ocm_runtime import OCMRuntime
from ocm.runtime import solve as SV
from ocm.store.evidence import Channel
from clia_tasks import load_task
from g1_field import ROOT, SCOPE, payload, put
from text_task_contracts import (TASK_IDS, check_response, check_response_binding, contract,
                                 interpret, realize, response_plan, validate_semantic)
import text_task_programs as P


class TextTaskSession:
    """One persistent OCM field; explicit host seed and callable rebinding."""
    def __init__(self, root):
        start = time.perf_counter()
        self.root = Path(root)
        self.runtime = OCMRuntime(self.root, config=SV.SolveConfig(exact_extraction_max_atoms=0))
        self.compiled = {}
        self._setup()
        self.startup_wall_s = time.perf_counter() - start

    def _setup(self):
        r = self.runtime
        if ROOT not in r.state.ks.atom_view:
            _, prior = r.admit_evidence({"prior": "text-task host namespace v1"}, Channel.INSTRUCTION,
                                       "text-task-host", scope=SCOPE)
            put(r, ROOT, {"prior": prior}, WarrantProfile.of({prior}), ())
        for task_id in TASK_IDS:
            aid = "text:contract:" + task_id
            declared = contract(task_id)
            if aid in r.state.ks.atom_view:
                if payload(r.state.ks, aid)["contract"] != declared:
                    raise ValueError("persisted language/specification prior changed; qualify a successor explicitly")
                continue
            evidence = {}
            seeds = {"specification": load_task(task_id), "correspondence": declared,
                     "reuse_authority": {"permitted_task": task_id, "scope": "g1-pilot", "role": "executable reuse"}}
            for role, seed in seeds.items():
                _, eid = r.admit_evidence(seed, Channel.INSTRUCTION, "text-task-host:" + role, scope=SCOPE)
                evidence[role] = eid
                put(r, "text:" + role + ":" + task_id, {"seed": seed, "evidence": eid},
                    WarrantProfile.of({eid}))
            put(r, aid, {"contract": declared, "evidence": evidence},
                WarrantProfile.of({evidence["correspondence"]}), ("text:correspondence:" + task_id,))
        if not r.events or r.events[-1].event_type.value != "SNAPSHOT_WRITTEN":
            r.persist()

    def evidence(self, task_id):
        if task_id not in TASK_IDS:
            raise ValueError("unknown registered text task")
        return payload(self.runtime.state.ks, "text:contract:" + task_id)["evidence"]

    def ask(self, text):
        start, cpu = time.perf_counter(), time.process_time()
        counters = {name: 0 for name in ("synthesis_calls", "application_calls", "compile_calls",
                                        "universal_checker_calls", "pointwise_checker_calls", "ground_spec_checker_calls")}
        stages, traces = {}, []
        @contextmanager
        def stage(name):
            wall, process = time.perf_counter(), time.process_time()
            try:
                yield
            finally:
                stages[name] = {"wall_s": time.perf_counter() - wall, "host_cpu_s": time.process_time() - process}
        def finish(result):
            ks = self.runtime.state.ks
            return {**result, "counters": counters, "traces": traces,
                    "metrics": {"stages": stages, "query_wall_s": time.perf_counter() - start,
                                "query_host_cpu_s": time.process_time() - cpu,
                                "session_startup_wall_s": self.startup_wall_s,
                                "logical_objects": len(ks.atoms), "logical_relations": len(ks.hyperedges),
                                "unmeasured": ["process-tree total CPU/RSS", "physical resident/materialized bytes",
                                               "total cold/warm index work; runtime trace counters are not locality proof"]}}
        with stage("text_to_meaning"):
            parsed = interpret(text)
        if parsed["status"] != "INTERPRETED":
            return finish(parsed)
        semantic = parsed["semantic"]
        try:
            validate_semantic(semantic)
        except (ValueError, TypeError, KeyError) as exc:
            return finish({"status": "CANNOT_CHECK", "reason": str(exc)})
        evidence = self.evidence(semantic["task_id"])
        required = WarrantProfile.of(set(evidence.values()))
        if not required.is_live(self.runtime.state.revoked):
            return finish({"status": "CANNOT_CHECK", "reason": "language/specification/reuse support is not live",
                           "semantic": semantic})
        try:
            with stage("meaning_admission"):
                data = {"raw_text": text, "tokens": parsed["tokens"], "semantic": semantic}
                _, utterance = self.runtime.admit_evidence(data, Channel.INSTRUCTION, "text-task-user", scope=SCOPE)
                support = WarrantProfile.of({utterance, evidence["correspondence"]})
                qid = "text:request:" + content_hash(data)
                put(self.runtime, qid, data, support, ("text:contract:" + semantic["task_id"],), kind="query_seed")
            with stage("method_retrieval_or_acquisition"):
                desc, reused = P.obtain(self.runtime, semantic, qid, evidence, counters, traces)
            with stage("ocm_application"):
                value, answer_id, checks = P.apply(self.runtime, semantic, qid, desc, self.compiled, counters, traces)
            checked = checks[-1]["source_specification"]
            with stage("response_and_admission"):
                plan = response_plan(json.loads(json.dumps(semantic)), value, (qid, answer_id))
                binding = check_response_binding(plan, semantic, value, (qid, answer_id))
                if binding["status"] != "PASS":
                    raise ValueError("response plan does not match the independently checked task and support")
                english = realize(json.loads(json.dumps(plan)))
                response_checked = check_response(json.loads(json.dumps(plan)), english)
                binding = check_response_binding(plan, semantic, value, (qid, answer_id))
                if binding["status"] != "PASS":
                    raise ValueError("response plan changed after checked-task binding")
                if response_checked["status"] != "PASS":
                    raise ValueError("response meaning check failed")
                warrant = self.runtime.state.ks.atom_view[qid].warrant.meet(
                    self.runtime.state.ks.atom_view[answer_id].warrant)
                if not warrant.is_live(self.runtime.state.revoked):
                    raise ValueError("response support changed before admission")
                record = {"response_plan": plan, "english": english, "checks": {"specification": checked,
                          "response": response_checked, "binding": binding, "program_application": checks}}
                admitted = "text:utterance:" + content_hash(record)
                put(self.runtime, admitted, record, warrant, (qid, answer_id), "EXACT_CHECKER", "proof")
            with stage("persistence"):
                self.runtime.persist()
            return finish({"status": "ANSWERED", "value": value, "english": english, "semantic": semantic,
                           "response_plan": plan, "checks": record["checks"], "program_id": desc["id"],
                           "program_reused": reused, "admitted_id": admitted,
                           "scope": "seeded two-function development slice; no learned-English/general-solving claim"})
        except (ValueError, KeyError, TypeError, OSError) as exc:
            return finish({"status": "CANNOT_CHECK", "reason": str(exc), "semantic": semantic})


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--state", required=True, type=Path)
    parser.add_argument("--json", action="store_true", help="include semantic contracts, checks, traces and metrics")
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("ask").add_argument("text")
    commands.add_parser("evidence").add_argument("task", choices=TASK_IDS)
    for name in ("revoke", "reinstate"):
        sub = commands.add_parser(name)
        sub.add_argument("task", choices=TASK_IDS)
        sub.add_argument("role", choices=("correspondence", "specification", "reuse_authority"))
    args = parser.parse_args()
    try:
        session = TextTaskSession(args.state)
    except (ValueError, OSError, RuntimeError) as exc:
        result = {"status": "CANNOT_CHECK", "reason": str(exc)}
        print(json.dumps(result) if args.json else "CANNOT_CHECK: " + str(exc))
        return 2
    if args.command == "ask":
        result = session.ask(args.text)
        print(json.dumps(result, sort_keys=True) if args.json else result.get("english", result["status"] + ": " + result.get("reason", "")))
        return 0 if result["status"] == "ANSWERED" else 2
    evidence = session.evidence(args.task)
    if args.command in ("revoke", "reinstate"):
        getattr(session.runtime, args.command)([evidence[args.role]])
        session.runtime.persist()
    print(json.dumps({"status": "OK", "evidence": evidence}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
