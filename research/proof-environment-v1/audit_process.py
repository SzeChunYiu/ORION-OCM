"""Inspect recorded host/native envelopes; never execute their argv or open host paths."""
import base64
from pathlib import PurePosixPath
from audit_data import bound, load_json, record, require, same


def streams(process, native=False):
    result = {}
    for key in ("stdout", "stderr"):
        raw = base64.b64decode(process[key + "_base64"], validate=True)
        if native:
            bound(raw, {"bytes": process[key + "_bytes"], "sha256": process[key + "_sha256"]}, key)
            require(process[key] == raw.decode(), "decoded native stream differs")
        result[key] = raw
    require(result["stderr"] == b"", "nonempty process stderr")
    return result


def check_processes(data, prefix, receipt, matrix, runtime, origin, freeze):
    op = receipt["operation"]; full = origin + "/" + prefix
    host_prefix = prefix + "-process"
    host = load_json(data[host_prefix + "/process.json"])
    native = receipt["process"]
    require(type(host["pid"]) is int and host["pid"] > 0 and
            type(native["pid"]) is int and native["pid"] > 0, "actual process IDs required")
    require(host["error"] is None and host["interrupted"] is False and
            same(host["cleanup"], {"reaped": True, "group_absent": True}), "host cleanup incomplete")
    wanted_code = 0 if receipt["terminal"] in {"PREPARED", "KERNEL_PASS"} else 2
    require(type(host["returncode"]) is int and host["returncode"] == wanted_code, "host exit differs")
    host_raw = streams(host)
    for key, raw in host_raw.items():
        name = host_prefix + "/" + key + ".bin"
        require(host[key]["path"] == origin + "/" + name and data[name] == raw, "host raw stream differs")
        bound(raw, host[key], "host stream")
    require(host_raw["stdout"] == (receipt["terminal"] + "\n").encode(), "host terminal output differs")
    entry = str(PurePosixPath(matrix["recorder"]["path"]).parent / "environment.py")
    argv = [runtime["host_python"]["path"], "-I", "-S", entry, op,
            "--freeze", freeze["path"], "--freeze-sha256", freeze["sha256"],
            "--runtime", matrix["runtime"]["path"], "--runtime-sha256", matrix["runtime"]["sha256"],
            "--output", full, "--timeout-s", str(matrix["timeout_s"]),
            "--max-output-bytes", str(matrix["max_output_bytes"])]
    require(same(host["argv"], argv), "host launch binding differs")
    require(native["terminal"] == "COMPLETED" and type(native["returncode"]) is int and
            native["returncode"] == 0 and native["timed_out"] is False and
            native["output_truncated"] is False and native["reason"] == "" and
            native["cleanup"]["reaped"] is True and native["cleanup"]["group_absent"] is True,
            "native process incomplete")
    native_raw = streams(native, True)
    require(native_raw["stdout"] == data[prefix + "/execution/native/result.json"], "native raw result differs")
    require(same(load_json(native_raw["stdout"]), receipt["native"]), "native response differs")
    require(native["execution_timeout_s"] == matrix["timeout_s"] and
            type(native["max_output_bytes"]) is int and native["max_output_bytes"] == matrix["max_output_bytes"],
            "native resource envelope differs")
    require(same(native["executable"], {"source": runtime["executable"]["path"],
            "sha256": runtime["executable"]["sha256"]}), "native executable differs")
    require(same(native["bwrap"], {k: runtime["bwrap"][k] for k in ("path", "sha256")}), "launcher differs")
    mounts = [(runtime["executable"]["path"], "/bridge/ocm_environment")]
    mounts += [(item["file"]["path"], item["guest"]) for item in runtime["libraries"]]
    mounts.append((full + "/request.json", "/request/request.json"))
    for role in sorted(receipt["inputs"]):
        name = role + (".json" if role in {"policy", "registration"} else ".ndjson")
        mounts.append((full + "/inputs/" + name, "/inputs/" + name))
    require(same(native["mounts"], [{"source": src, "destination": dst, "mode": "read-only"}
                                    for src, dst in mounts]), "native role mounts differ")
    invocation = [runtime["bwrap"]["path"], "--unshare-all", "--unshare-user", "--unshare-pid",
                  "--unshare-net", "--die-with-parent", "--new-session", "--cap-drop", "ALL",
                  "--proc", "/proc", "--dev", "/dev", "--tmpfs", "/tmp"]
    for src, dst in mounts: invocation += ["--ro-bind", src, dst]
    invocation += ["--bind", full + "/execution", "/work", "--remount-ro", "/", "--chdir", "/work",
                   "--", "/bridge/ocm_environment", "/request/request.json", "/work/native"]
    require(same(native["invocation"], invocation) and native["work_dir"] == full + "/execution",
            "native invocation differs")
    require(same(native["environment"], {"HOME": "/tmp", "LANG": "C.UTF-8", "LC_ALL": "C.UTF-8", "TMPDIR": "/tmp"}),
            "native environment differs")
    return host["pid"], native["pid"]
