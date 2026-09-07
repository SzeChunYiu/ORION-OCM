"""One shared source-materialization continuation; original episode and semantic rows persist."""
from pathlib import Path
from hashlib import sha256
import json
import resource
import sys
import time


def host():
    import acquisition_contract as c
    import materialize_phase as phase
    here = Path(__file__).resolve().parent; prefix = Path(sys.base_prefix).resolve()
    python = c.record(Path(sys.executable).resolve()); git = c.record("/usr/bin/git")
    if python["sha256"] != c.PYTHON or git["sha256"] != phase.GIT: raise ValueError("HOST_TOOL_IDENTITY")
    origins = {}
    for name, module in list(sys.modules.items()):
        origin = getattr(module, "__file__", None)
        if not origin or origin.startswith("<"): continue
        path = Path(origin).resolve(strict=True)
        if not (path.is_relative_to(prefix) or path.is_relative_to(here)):
            raise ValueError("HOST_IMPORT_ORIGIN: " + name)
        origins[name] = c.record(path)
    return dict(python=python, git=git, imports=origins,
                scope="Trusted host source-only entry; no arbitrary Python sandbox claim.")


def dispatch(source, command, bounds, root, owned):
    import acquisition_contract as c
    frozen_boot = c.load_source(source / "resource_boot.py", "materialize_resource_boot")
    modules = frozen_boot.load()
    frozen_boot.loaded_sources(modules["build_profile"].__dict__)
    return modules["resource_runner"].run(command, {}, bounds, root, owned)


def run(registrar, episode, corpus_bare, destination):
    import acquisition_contract as c
    import materialize_boot as boot
    import materialize_phase as phase
    import materialize_custody as custody
    began = time.monotonic(); cpu = resource.getrusage(resource.RUSAGE_SELF)
    out = c.new_output(destination, [registrar, episode, corpus_bare, Path(__file__).parent])
    expected = []; frozen = {}; request = None; receipt = {}; result = None
    ready = False; error = None; reached = "INPUT_VALIDATION"; left = None
    def persist(name, value):
        raw = c.canonical(value); path = out / name
        binding = dict(path=str(path), sha256=sha256(raw).hexdigest(), bytes=len(raw))
        expected.append(binding); c.write(path, value); return binding
    try:
        host_record = host(); boot.recheck()
        authority = phase.authorize(registrar, episode, corpus_bare)
        persist("EPISODE-REFERENCE.json", dict(original=authority["start"],
                acquisition_phase_sha256=authority["acquisition_phase_sha256"],
                invocation_monotonic=began, claim="Continuation; original clock is never reset."))
        rows = dict(denominator=4, continuation_cursor=4,
                    keys=[r["key"] for r in authority["assignments"]["rows"]],
                    shared_preparation="MATERIALIZATION_PENDING", semantic_checks_reached=0)
        persist("ROWS-DECLARED.json", rows)
        source = out / "sources"; source.mkdir()
        for name, original in boot.recheck().items():
            raw = Path(original["path"]).read_bytes()
            if boot.binding(Path(original["path"]), raw) != original: raise ValueError("COPY_SOURCE_DRIFT")
            path = source / (name + ".py")
            with path.open("xb") as stream: stream.write(raw)
            frozen[name] = dict(original=original, frozen=boot.binding(path, raw))
        persist("SOURCE-FREEZE.json", dict(sources=frozen, host=host_record))
        request = dict(**authority, sources={n: pair["frozen"] for n, pair in frozen.items()},
                       reference=dict(registration_seal_sha256=c.SEAL,
                                      acquisition_phase_sha256=authority["acquisition_phase_sha256"],
                                      started_sha256=phase.PINS["STARTED.json"]))
        request_binding = persist("REQUEST.json", request)
        phase.recheck(authority["inputs"]); phase.recheck(expected); boot.recheck()
        for pair in frozen.values(): phase.recheck(list(pair.values()))
        bounds = c.limits(authority["policy"], phase.clock(authority["start"]))
        persist("LIMITS.json", bounds)
        command = [host_record["python"]["path"], "-I", "-S", str(source / "materialize_worker.py"),
                   str(out / "REQUEST.json"), request_binding["sha256"], str(out / "materials")]
        reached = "RESOURCE_SETUP"
        receipt = dispatch(source, command, bounds, out / "resource", [Path(episode), out])
        if receipt.get("dispatch", {}).get("attempted"): reached = "MATERIALIZATION"
        result_path = out / "materials/RESULT.json"
        if result_path.is_file():
            result, binding = phase.read(result_path); expected.append(binding)
        phase.process_ok(receipt)
        raw_receipt, binding = phase.read(out / "resource/resource-receipt.json"); expected.append(binding)
        if not custody.same(raw_receipt, receipt): raise ValueError("RESOURCE_RECEIPT_DRIFT")
        if (receipt.get("argv") != command or receipt.get("environment") != {}
            or not custody.same(receipt.get("limits"), bounds)):
            raise ValueError("RESOURCE_DISPATCH_BINDING")
        for name, item in receipt["raw"].items():
            if Path(item["path"]) != out / "resource" / name: raise ValueError("RESOURCE_RAW_PATH")
            expected.append(item)
        if set(receipt["raw"]) != {"stdout.bin", "stderr.bin", "samples.jsonl"}:
            raise ValueError("RESOURCE_RAW_INCOMPLETE")
        if receipt["raw"]["stderr.bin"]["bytes"] != 0: raise ValueError("WORKER_STDERR")
        if type(result) is not dict or type(result.get("pid")) is not int or result["pid"] != receipt["dispatch"]["pid"]:
            raise ValueError("WORKER_PID")
        if result.get("request") != request_binding: raise ValueError("WORKER_REQUEST")
        validation = custody.verify(result, request, out / "materials")
        persist("MATERIAL-REVALIDATION.json", validation)
        phase.recheck(authority["inputs"]); phase.recheck(expected)
        for pair in frozen.values(): phase.recheck(list(pair.values()))
        boot.recheck(); phase.recheck([host_record["python"], host_record["git"], *host_record["imports"].values()])
        left = phase.clock(authority["start"])
        rows["shared_preparation"] = "MATERIALIZED"
        rows["claim"] = "Ten exact source trees; BUILD and all semantic stages remain unexecuted here."
        persist("ROWS-AFTER-MATERIALIZATION.json", rows)
        phase.recheck(expected); boot.recheck(); left = phase.clock(authority["start"])
        ready = True
    except BaseException as exc:
        error = dict(kind=type(exc).__name__, message=str(exc)); ready = False
    after = resource.getrusage(resource.RUSAGE_SELF)
    value = dict(schema="ocm.f1.materialization-phase.v1", terminal="MATERIALIZED_READY" if ready else "CANNOT_CHECK",
                 resource=receipt, worker=result, error=error, reached_phase=reached,
                 semantic_checks_reached=0, remaining_whole_seconds=left,
                 whole_deadline_monotonic=request["start"]["whole_deadline_monotonic"] if request else None,
                 wall_before_phase_receipt_s=time.monotonic()-began,
                 supervisor_user_seconds=after.ru_utime-cpu.ru_utime,
                 supervisor_system_seconds=after.ru_stime-cpu.ru_stime,
                 cost_scope="Shared cold preparation and custody; original V2 waiting consumes clock; nested timings overlap. Outer process must charge final receipt persistence.")
    c.write(out / "MATERIALIZATION.json", value)
    return value


def main():
    if len(sys.argv) != 5 or not sys.flags.isolated or not sys.flags.no_site:
        raise SystemExit("use pinned Python -I -S materialize_run.py REGISTRATION V2_EPISODE CORPUS_BARE NEW_OUTPUT")
    import types
    path = Path(__file__).resolve().with_name("materialize_boot.py"); raw = path.read_bytes()
    module = types.ModuleType("materialize_boot"); module.__file__ = str(path)
    module.__source_record__ = dict(path=str(path), sha256=sha256(raw).hexdigest(), bytes=len(raw))
    sys.modules["materialize_boot"] = module
    exec(compile(raw, str(path), "exec"), module.__dict__)
    loaded = module.load(); value = loaded["materialize_run"].run(*sys.argv[1:])
    print(json.dumps(dict(terminal=value["terminal"], error=value["error"], semantic_checks_reached=0)))
    return 0 if value["terminal"] == "MATERIALIZED_READY" else 2


if __name__ == "__main__": raise SystemExit(main())
