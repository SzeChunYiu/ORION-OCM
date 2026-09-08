"""Fresh, source-pinned native checking of exact issued typed claims."""
import contextlib
import hashlib
import io
import json
import os
from pathlib import Path
import re
import resource
import time
import traceback
import types


def encoded(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=True, allow_nan=False).encode("ascii")


def identity(raw):
    return {"bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest()}


def require(condition, reason):
    if not condition:
        raise ValueError(reason)


def read_counted(path, work, key):
    raw = path.read_bytes()
    work[key] += len(raw)
    return raw


def store(path, raw):
    with path.open("xb") as stream:
        stream.write(raw)
        stream.flush()
        os.fsync(stream.fileno())


def tokens(value):
    require(type(value) is list and bool(value), "nonempty token list required")
    require(all(type(t) is str and t and t.isascii() and "$" not in t
                and not any(c.isspace() for c in t) for t in value), "unsafe token")


def validate_claims(claims):
    require(type(claims) is list and bool(claims), "nonempty issued claims required")
    names = []
    for claim in claims:
        require(set(claim) == {"label", "premises", "query", "holes", "proof", "parameters"}, "claim fields")
        require(type(claim["premises"]) is list and type(claim["holes"]) is list
                and len(claim["premises"]) == len(claim["holes"]), "ordered hole arity")
        names.extend([claim["label"], *claim["holes"]])
        for statement in [claim["query"], *claim["premises"]]:
            tokens(statement)
            require(statement[0] == "|-", "logical statement type")
        tokens(claim["proof"])
        require(len(claim["proof"]) <= 4096, "normal proof output bound")
        require(all(re.fullmatch(r"[A-Za-z0-9_.-]+", t) for t in claim["proof"]), "normal proof labels")
        ps = claim["parameters"]
        require(type(ps) is list and len(ps) == 3, "three typed parameters required")
        require(all(type(p) is dict and set(p) == {"type", "variable", "floating_label"}
                    and all(type(v) is str and v for v in p.values()) for p in ps), "parameter fields")
        require(len({p["type"] for p in ps}) == 1 and ps[0]["type"] in {"wff", "class"}, "homogeneous parameter type")
        require(len({p["variable"] for p in ps}) == len({p["floating_label"] for p in ps}) == 3, "distinct parameters")
    require(all(type(n) is str and re.fullmatch(r"[A-Za-z0-9_.-]+", n) for n in names), "local labels")
    require(len(set(names)) == len(names), "local label collision")
    return names


def serialize(claims):
    lines = []
    for claim in claims:
        lines.append("${")
        lines.extend(f"{label} $e {' '.join(stmt)} $." for label, stmt in zip(claim["holes"], claim["premises"]))
        lines.extend([f"{claim['label']} $p {' '.join(claim['query'])} $= {' '.join(claim['proof'])} $.", "$}"])
    return ("\n".join(lines) + "\n").encode("ascii")


def verify(prefix_path, claims, archive, source_bindings, expected_authority, suffix_bytes=None):
    """Retain every invocation; a previous receipt never supplies proof authority."""
    started, before = time.perf_counter(), resource.getrusage(resource.RUSAGE_SELF)
    archive, prefix_path = Path(archive), Path(prefix_path)
    archive.mkdir(exist_ok=False)
    directory = os.open(archive.parent, os.O_RDONLY)
    try: os.fsync(directory)
    finally: os.close(directory)
    result = {"terminal": "CANNOT_CHECK", "error": None, "native_calls": 0, "traces": {}, "contracts": {}}
    work = result["work"] = {"source_modules_loaded": 0, "source_bytes_read": 0, "prefix_bytes_read": 0,
                             "source_index_calls": 0, "database_bytes_materialized": 0, "database_bytes_reread": 0}
    stage, mm, native, checked_sources, database = "request", None, None, {}, None
    prefix_raw = None
    with (archive / "native.log").open("x", encoding="utf-8") as log:
        try:
            request_raw = encoded({"claims": claims, "sources": source_bindings, "authority": expected_authority})
            store(archive / "request.json", request_raw + b"\n")
            result["claims_sha256"] = identity(encoded(claims))["sha256"]
            names = validate_claims(claims)
            stage = "source_binding"
            require(set(source_bindings) == {"index", "adapter", "verifier"}, "native source set")
            modules = {}
            for key, binding in source_bindings.items():
                require(set(binding) == {"path", "bytes", "sha256"}, "source binding fields")
                path = Path(binding["path"])
                raw = read_counted(path, work, "source_bytes_read")
                require({"path": str(path), **identity(raw)} == binding, "native source identity: " + key)
                checked_sources[key] = binding.copy()
                module = types.ModuleType("_typed_native_" + key)
                module.__file__ = str(path)
                exec(compile(raw, str(path), "exec"), module.__dict__)
                work["source_modules_loaded"] += 1
                modules[key] = module
            source, adapter, native = (modules[k] for k in ("index", "adapter", "verifier"))
            native.verbosity, native.logfile = 2, log
            stage = "prefix_binding"
            prefix_raw = read_counted(prefix_path, work, "prefix_bytes_read")
            require(identity(prefix_raw) == expected_authority["prefix"], "closed prefix identity")
            work["source_index_calls"] += 1
            prefix_rows, _ = source.index(prefix_raw)
            require(not set(names).intersection(prefix_rows), "issued label already in library")
            suffix = serialize(claims) if suffix_bytes is None else suffix_bytes
            require(type(suffix) is bytes, "suffix bytes required")
            store(archive / "suffix.mm", suffix)
            result["suffix"] = identity(suffix)
            require(all(not t.startswith("$") or t in {"${", "$}", "$e", "$p", "$=", "$."}
                        for t, _, _ in source.lex(suffix)), "unissued suffix declaration")
            raw = prefix_raw + b"\n" + suffix
            database = archive / "database.mm"
            store(database, raw)
            work["database_bytes_materialized"] += len(raw)
            result.update(database={"path": str(database), **identity(raw)}, suffix=identity(suffix),
                          closed_prefix={"path": str(prefix_path), **identity(prefix_raw)}, sources=checked_sources)
            stage = "issued_claim_binding"
            work["source_index_calls"] += 1
            rows, _ = source.index(raw)
            require(set(rows).difference(prefix_rows) == set(names), "suffix label population")
            selected = [c["label"] for c in claims]
            trusted = [r["label"] for r in rows.values() if r["kind"] == "$a"]
            expected = [r["label"] for r in rows.values() if r["kind"] == "$p"]
            prefix_proofs = [r["label"] for r in prefix_rows.values() if r["kind"] == "$p"]
            result.update(selected=selected, trusted_assertions=trusted)
            require(len(trusted) == expected_authority["trusted_assertion_count"]
                    and identity(encoded(trusted))["sha256"] == expected_authority["trusted_assertions_sha256"], "trusted assertion identity")
            require(len(prefix_proofs) == expected_authority["prefix_proof_count"]
                    and expected == prefix_proofs + selected, "native theorem population/order")
            for claim in claims:
                row = rows[claim["label"]]
                essential = [{"label": h, "statement": p} for h, p in zip(claim["holes"], claim["premises"])]
                floating = [{"label": p["floating_label"], "statement": [p["type"], p["variable"]]} for p in claim["parameters"]]
                require(row["kind"] == "$p" and row["statement"] == claim["query"]
                        and row["essential"] == essential and row["proof"] == claim["proof"]
                        and row["floating"] == floating and row["dv"] == row["active_dv"] == [], "exact issued claim/context")
                require(not set(claim["proof"]).intersection(selected), "issued theorem shortcut")
                permitted = set(prefix_rows) | set(claim["holes"])
                require(set(claim["proof"]) <= permitted, "foreign proof label")
                require(all(rows[t].get("dv", []) == [] for t in claim["proof"]), "applied assertion DV outside scope")
                used_floats = {t for t in claim["proof"] if rows[t]["kind"] == "$f"}
                require(used_floats <= {p["floating_label"] for p in claim["parameters"]}, "extra used floating hypothesis")
            class Tokens(native.Toks):
                def __init__(self, stream):
                    super().__init__(stream)
                    self.recent = []
                def readc(self):
                    word = super().readc()
                    self.recent = (self.recent + [word])[-2:]
                    return word
            mm = adapter.traced_class(native, rows)(selected, None)
            stream = io.StringIO(raw.decode("ascii"))
            stream.name = str(database)
            stage = "native_check"
            result["native_calls"] = 1
            with stream, contextlib.redirect_stdout(log), contextlib.redirect_stderr(log):
                mm.read(Tokens(stream))
            stage = "native_trace_binding"
            require(mm.verified == expected and set(mm.traces) == set(selected), "native replay/trace population")
            used = {n["label"] for tr in mm.traces.values() for n in tr["nodes"] if "label" in n}
            contracts = {label: {**source.contract(rows[label]), "span": rows[label]["span"]} for label in sorted(used)}
            result.update(terminal="NATIVE_VERIFIED", traces=mm.traces, contracts=contracts)
        except Exception as exc:
            result["terminal"] = "NATIVE_REJECTED" if stage == "native_check" and native is not None and isinstance(exc, native.MMError) else "CANNOT_CHECK"
            result["error"] = {"type": type(exc).__name__, "message": str(exc), "stage": stage, "pending": getattr(mm, "pending", None)}
            traceback.print_exc(file=log)
        finally:
            result.update(verified_labels=getattr(mm, "verified", []), partial_traces=getattr(mm, "traces", {}))
            try:
                if prefix_raw is not None:
                    require(read_counted(prefix_path, work, "prefix_bytes_read") == prefix_raw, "prefix changed during invocation")
                for key, binding in checked_sources.items():
                    require(identity(read_counted(Path(binding["path"]), work, "source_bytes_read")) == {k: binding[k] for k in ("bytes", "sha256")}, "source changed during invocation: " + key)
                if database is not None:
                    require(read_counted(database, work, "database_bytes_reread") == raw, "archived database changed during invocation")
            except Exception as exc:
                result.update(terminal="CANNOT_CHECK", prior_error=result["error"], error={"type": type(exc).__name__, "message": str(exc), "stage": "post_custody"}, traces={}, contracts={})
            after = resource.getrusage(resource.RUSAGE_SELF)
            result["costs"] = {"wall_s": time.perf_counter() - started, "user_cpu_s": after.ru_utime - before.ru_utime,
                               "system_cpu_s": after.ru_stime - before.ru_stime, "process_highwater_rss_kib": after.ru_maxrss,
                               "scope": "wrapper through post-custody; RSS is process cumulative highwater on Linux; final receipt write excluded"}
    result["log"] = identity((archive / "native.log").read_bytes())
    store(archive / "result.json", encoded(result) + b"\n")
    return result
