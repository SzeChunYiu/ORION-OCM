"""Capture return values without replacing search or verifier decision rules."""
from copy import deepcopy
import json
from pathlib import Path
import time


def write_json(path, value):
    with Path(path).open("x") as handle:
        json.dump(value, handle, indent=2, sort_keys=True)
        handle.write("\n")


class TraceCapture(list):
    def __init__(self, path):
        super().__init__()
        self.handle = Path(path).open("x")
        self.io_seconds = 0.0

    def append(self, row):
        # Preserve exactly the object/list behavior expected by b1.search.
        super().append(row)
        started = time.perf_counter()
        self.handle.write(json.dumps(row, sort_keys=True)+"\n")
        self.handle.flush()
        self.io_seconds += time.perf_counter()-started

    def close(self):
        self.handle.close()


class VerifierCapture:
    def __init__(self, development, output):
        self.dev, self.output = development, Path(output)
        self.current = None
        self.scanned = self.charged = self.actual_calls = 0

    def __enter__(self):
        self.original_verify = self.dev.verify_candidate
        self.original_prune = self.dev.atrophy_ir.prune_all_interventions
        self.original_run = self.dev.ecology.run_genotype

        def observe_run(*args, **kwargs):
            self.actual_calls += 1
            row = {"spec": deepcopy(args[0]), "genotype": self.dev.morph.to_json(args[1]),
                   "intervention": args[3] if len(args) > 3 else kwargs.get("intervention", "standard")}
            try:
                result = self.original_run(*args, **kwargs)
            except Exception as exc:
                row["error"] = type(exc).__name__+": "+str(exc)
                if self.current is not None:
                    self.current["evaluation_outputs"].append(row)
                raise
            row["output"] = deepcopy(result)
            if self.current is not None:
                self.current["evaluation_outputs"].append(row)
            return result

        def observe_prune(*args, **kwargs):
            small, info = self.original_prune(*args, **kwargs)
            if self.current is not None:
                self.current["atrophy_outputs"].append({
                    "genotype": self.dev.morph.to_json(small), "info": deepcopy(info)})
            return small, info

        def observe_verify(g, spec, bc):
            self.current = {"raw_genotype": self.dev.morph.to_json(g),
                            "evaluation_outputs": [], "atrophy_outputs": []}
            before = self.actual_calls
            try:
                value, charged = self.original_verify(g, spec, bc)
                self.scanned += 1
                self.charged += charged
                summary = {"scan": self.scanned, "reported_charged": charged,
                           "actual_ecology_calls": self.actual_calls-before,
                           "pass": value["pass"], "fail": value.get("fail")}
                with (self.output/"verification_scan.jsonl").open("a") as handle:
                    handle.write(json.dumps(summary, sort_keys=True)+"\n")
                if value["pass"] and value.get("carrier_atrophied") == "DENSE":
                    self.current.update({"verifier": deepcopy(value), "reported_charged": charged,
                                         "actual_ecology_calls": self.actual_calls-before,
                                         "best_constant": bc, "theta": self.dev.THETA,
                                         "fx_unit": self.dev.FX_UNIT,
                                         "raw_fingerprint": self.dev.morph.fingerprint(g),
                                         "raw_margin_from_registered_caps": (value["min_over_six"]-bc)/self.dev.FX_UNIT,
                                         "atrophied_margin_from_registered_caps":
                                             (value["atrophied_min_over_six"]-bc)/self.dev.FX_UNIT})
                    write_json(self.output/"witness.json", self.current)
                return value, charged
            finally:
                self.current = None

        self.dev.ecology.run_genotype = observe_run
        self.dev.atrophy_ir.prune_all_interventions = observe_prune
        self.dev.verify_candidate = observe_verify
        return self

    def __exit__(self, *error):
        self.dev.verify_candidate = self.original_verify
        self.dev.atrophy_ir.prune_all_interventions = self.original_prune
        self.dev.ecology.run_genotype = self.original_run
