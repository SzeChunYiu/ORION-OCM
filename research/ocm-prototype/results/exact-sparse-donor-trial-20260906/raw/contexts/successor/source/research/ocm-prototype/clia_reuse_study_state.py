"""Thin actor custody over existing OCM and ordinary NativeLibrary; no new learning."""
import json
from pathlib import Path
import shutil

import clia_reuse_descriptor as D
from clia_reuse_native import NativeLibrary
from clia_reuse_study_common import digest, sha, write


class Actor:
    def __init__(self, root, arm):
        self.root = Path(root); self.arm = arm; self.root.mkdir(parents=True, exist_ok=True)
        path = self.root / "study-bindings.json"
        self.bindings = json.loads(path.read_text()) if path.exists() else {"programs": {}}
        if arm == "native":
            self.library = NativeLibrary(self.root / "library")
        elif arm == "ocm":
            import g1_vessel as G
            import clia_reuse_vessel as V
            self.G, self.V = G, V
            self.runtime = G.OCMRuntime(self.root, config=G.CONFIG)
        else:
            raise ValueError("unknown arm")

    def evidence(self, payload, role):
        if self.arm == "ocm":
            from ocm.store.evidence import Channel
            from g1_field import SCOPE
            _, eid = self.runtime.admit_evidence(payload, Channel.OBSERVATION if role == "history" else Channel.INSTRUCTION,
                                                 "reuse-study-" + role, scope=SCOPE)
            record = self.runtime.state.evidence.records[eid].as_dict()
        else:
            eid = "native:" + digest({"role": role, "payload": payload})
            record = {"evidence_id": eid, "kind": "assumption", "role": role, "content_sha256": digest(payload)}
        path = self.root / "study-evidence" / (digest(eid) + ".json")
        if not path.exists(): write(path, {"record": record, "payload": payload})
        return {"id": eid, "record": record, "payload_sha256": digest(payload),
                "path": str(path.relative_to(self.root)), "file_sha256": sha(path)}

    def setup(self, model, training):
        self.bindings["model_sha256"] = sha(model)
        target = self.root / "archive" / (sha(model) + ".udpipe")
        if self.arm == "ocm":
            from g1_field import setup
            self.bindings["fixture"] = setup(self.runtime, Path(model), training)
        else:
            target.parent.mkdir(parents=True, exist_ok=True); shutil.copyfile(model, target)
            write(self.root / "training.json", training)
            self.bindings["prior"] = self.evidence({"prior": "public CLIA specifications and fixed grammar/checkers"}, "prior")
            self.bindings["model_support"] = self.evidence({"model_sha256": sha(model), "training": training}, "model")
        self.bindings["model_file"] = str(target.relative_to(self.root))

    def acquire(self, alias, task, events):
        start = len(events)
        request = {"kind": "clia", "task": task}
        if self.arm == "ocm":
            from g1_field import payload
            result = self.V.query(self.runtime, request)
            if result["status"] != "ADMITTED": raise ValueError("ACQUISITION_NOT_ADMITTED")
            proof = result["admitted_id"]; proposal = payload(self.runtime.state.ks, proof)["output"]
            qid = "g1:query:" + self.G.content_hash(request)
            registration = sorted(self.runtime.state.ks.atom_map()[qid].warrant.evidence)
        else:
            import clia_solver
            registered = self.evidence(request, "query-registration")
            registration = [registered["id"]]
            proposal = clia_solver.propose(task)
            result = {"proposal": proposal, "registration": registered}
            proof = "acquisitions/" + alias + ".json"
        invocations = [e for e in events[start:] if e["action"] == "synthesize"]
        if len(invocations) != 1 or not invocations[0].get("result", {}).get("native_invoked"):
            raise ValueError("EXACT_ONE_NATIVE_SYNTHESIS_NOT_OBSERVED")
        history = self.evidence({"kind": "ACTUAL_SEARCH_HISTORY", "task_sha256": task["task_sha256"],
                                 "invocations": invocations, "proposal_sha256": digest(proposal)}, "history")
        if self.arm == "ocm":
            desc = self.V.adopt(self.runtime, proof, history=[history["id"]])
        else:
            ids = sorted([self.bindings["prior"]["id"], *registration])
            key = self.library.acquire(task, proposal, {"lower": [ids], "upper": [ids]}, history=[history["id"]])
            desc = self.library.load(key)
            write(self.root / "acquisitions" / (alias + ".json"),
                  {"query": request, "result": result, "support": desc["support"], "descriptor_id": key})
        self.bindings["programs"][alias] = {
            "descriptor_id": desc["id"], "program_sha256": desc["program_sha256"], "task_id": task["task_id"],
            "task_sha256": task["task_sha256"], "checker_identity": digest(desc["checker_prior"]),
            "support": desc["support"], "registration": registration, "history_ids": [history["id"]],
            "history_records": [history], "proof_id": proof, "descriptor": desc}
        self.persist()
        return {"alias": alias, "result": result, "descriptor": desc, "history_record": history}

    def persist(self):
        if self.arm == "ocm": self.runtime.persist()

    def save_bindings(self):
        write(self.root / "study-bindings.json", self.bindings)
        self.persist()

    def model_path(self):
        model = self.root / self.bindings["model_file"]
        if sha(model) != self.bindings["model_sha256"]: raise ValueError("MODEL_ARCHIVE_CHANGED")
        return model

    def bind(self, key):
        return self.V.bind(self.runtime, key) if self.arm == "ocm" else self.library.bind(key)

    def revise(self, action, ids):
        if action not in ("revoke", "reinstate"): raise ValueError("unknown revision")
        getattr(self.runtime if self.arm == "ocm" else self.library, action)(ids)
        self.persist()

    def query(self, request):
        if self.arm == "ocm": return self.V.query(self.runtime, request)
        if request["kind"] == "clia_apply": result = self.library.apply(request)
        elif request["kind"] == "syntax":
            import udpipe_donor
            from syntax_contract import validate, validate_tokens
            validate_tokens(request["tokens"])
            output = udpipe_donor.predict(request["tokens"], self.model_path(), self.bindings["model_sha256"])
            reason = validate(output.get("words"), request["tokens"]) if output.get("status") == "PREDICTED" else "PREDICTOR_UNAVAILABLE"
            checked = {"status": "PASS" if reason is None else "CANNOT_CHECK", "reason": reason,
                       "scope": "STRUCTURE_ONLY_NO_GOLD_CORRECTNESS"}
            result = {"status": "ACCEPTED_PARENT" if reason is None else "NOT_ACCEPTED",
                      "answer": output if reason is None else None, "host_check": checked}
            registration = self.evidence(request, "syntax-registration")
            ids = sorted([self.bindings["model_support"]["id"], registration["id"]])
            record = {"request": request, "result": result, "support": {"lower": [ids], "upper": [ids]}}
            key = digest(record); path = self.root / "syntax" / (key + ".json")
            if not path.exists(): write(path, record)
        else:
            raise ValueError("no implicit reacquisition")
        return {**result, "catalogue": ["syntax:udpipe1", "procedure:cvc5"] +
                ["apply:" + b["descriptor_id"] for b in self.bindings["programs"].values()]}

    def audit(self):
        a = self.V.audit(self.runtime) if self.arm == "ocm" else self.library.audit()
        a["records"] = {}; a["history_records"] = {}
        for alias, b in self.bindings["programs"].items():
            for h in b.get("history_records", []):
                path = self.root / h["path"]
                if sha(path) != h["file_sha256"]: raise ValueError("HISTORY_RECORD_CHANGED")
                raw = json.loads(path.read_text())
                if digest(raw["payload"]) != h["payload_sha256"]: raise ValueError("HISTORY_PAYLOAD_CHANGED")
                a["history_records"][h["id"]] = {"sha256": sha(path), "payload_sha256": h["payload_sha256"]}
        if self.arm == "ocm":
            from g1_field import MODEL, payload
            from clia_reuse_support import assumptions, encode
            a["model_liveness"] = self.runtime.state.ks.atom_map()[MODEL].liveness(self.runtime.state.revoked).value
            for atom in self.runtime.state.ks.atoms:
                if atom.atom_id.startswith(("g1:answer:", "clia:application-answer:")) or atom.atom_id in {b.get("proof_id") for b in self.bindings["programs"].values()}:
                    data = payload(self.runtime.state.ks, atom.atom_id)
                    a["records"][atom.atom_id] = {"payload_sha256": digest(data),
                        "liveness": atom.liveness(self.runtime.state.revoked).value, "payload": data,
                        "support": encode(assumptions(self.runtime, atom.warrant))}
        else:
            model = self.bindings.get("model_support", {}).get("id")
            a["model_liveness"] = "DEAD" if model in self.library.revoked else "LIVE"
            for folder in ("library", "acquisitions", "syntax"):
                for path in sorted((self.root / folder).glob("*.json")):
                    if folder == "library" and not path.name.startswith("answer-"): continue
                    data = json.loads(path.read_text())
                    a["records"][str(path.relative_to(self.root))] = {
                        "payload_sha256": digest(data), "liveness": D.liveness(data["support"], self.library.revoked),
                        "payload": data, "support": data["support"]}
        return a

    def authority(self, key):
        if self.arm == "ocm":
            atom = self.runtime.state.ks.atom_map()[self.V.atom_id(key)]
            return {"liveness": atom.liveness(self.runtime.state.revoked).value,
                    "revoked": sorted(self.runtime.state.revoked)}
        desc = self.library.load(key)
        return {"liveness": D.liveness(desc["support"], self.library.revoked),
                "revoked": sorted(self.library.revoked)}
