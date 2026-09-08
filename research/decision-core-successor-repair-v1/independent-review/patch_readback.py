"""Data-only exact unified-patch reader for this bounded capsule review."""
import hashlib
import json
import pathlib
import re
import sys


def apply_patch(text, originals):
    lines = text.splitlines(keepends=True)
    i, results = 0, {}
    while i < len(lines):
        assert lines[i].startswith("--- "), (i, lines[i])
        old = lines[i][4:].rstrip("\n")
        i += 1
        assert lines[i].startswith("+++ ")
        new = lines[i][4:].rstrip("\n")
        i += 1
        source = [] if old == "/dev/null" else originals[old.removeprefix("a/")].splitlines(keepends=True)
        pos, output = 0, []
        while i < len(lines) and not lines[i].startswith("--- "):
            match = re.match(r"^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@", lines[i])
            assert match, (i, lines[i])
            a, ac, b, bc = [int(x) if x is not None else 1 for x in match.groups()]
            start = a - 1 if ac else a
            assert start >= pos
            output.extend(source[pos:start])
            pos = start
            assert len(output) == (b - 1 if bc else b)
            used, made = 0, 0
            i += 1
            while i < len(lines) and not lines[i].startswith(("@@ ", "--- ")):
                mark, body = lines[i][0], lines[i][1:]
                assert mark in " +-", (i, lines[i])
                if mark in " -":
                    assert pos < len(source) and source[pos] == body, (old, pos, body)
                    pos += 1
                    used += 1
                if mark in " +":
                    output.append(body)
                    made += 1
                i += 1
            assert (used, made) == (ac, bc), (old, used, made, ac, bc)
        output.extend(source[pos:])
        name = new.removeprefix("b/")
        assert name not in results
        results[name] = "".join(output)
    return results


def controls():
    patch = "--- a/x\n+++ b/x\n@@ -1,2 +1,2 @@\n a\n-b\n+c\n"
    assert apply_patch(patch, {"x": "a\nb\n"}) == {"x": "a\nc\n"}
    try:
        apply_patch(patch, {"x": "a\nWRONG\n"})
    except AssertionError:
        pass
    else:
        raise AssertionError("bad context not rejected")
    assert apply_patch("--- /dev/null\n+++ b/y\n@@ -0,0 +1 @@\n+new\n", {}) == {"y": "new\n"}


def main(root):
    controls()
    binding = json.loads((root / "SOURCE-BINDINGS.json").read_text())
    base = pathlib.Path(binding["source_directory"])
    originals, base_checks = {}, []
    for row in binding["source_files"]:
        raw = (base / pathlib.Path(row["path"]).name).read_bytes()
        sha = hashlib.sha256(raw).hexdigest()
        blob = hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
        assert (len(raw), sha, blob) == (row["bytes"], row["sha256"], row["git_blob_sha1"])
        originals[row["path"]] = raw.decode()
        base_checks.append({"path": row["path"], "sha256": sha, "git_blob_sha1": blob})
    reconstructed = apply_patch((root / "integration.patch").read_text(), originals)
    expected_names = {"decision_core.py", "test_decision_core_exact_regressions.py", "FORMAL_DECISION_CORE_V2.md"}
    assert {pathlib.Path(p).name for p in reconstructed} == expected_names
    outputs = []
    for path, text in reconstructed.items():
        name = pathlib.Path(path).name
        raw = text.encode()
        sha = hashlib.sha256(raw).hexdigest()
        if name == "FORMAL_DECISION_CORE_V2.md":
            assert sha == binding["proposed_formal_sha256"]
        else:
            assert raw == (root / name).read_bytes()
        outputs.append({"path": path, "bytes": len(raw), "sha256": sha, "matches_capsule_or_formal_binding": True})
    for patch_name, target in [("decision-core.patch", "decision_core.py"), ("adaptive-information.patch", "FORMAL_DECISION_CORE_V2.md")]:
        subset = apply_patch((root / patch_name).read_text(), originals)
        assert len(subset) == 1
        path, text = next(iter(subset.items()))
        assert pathlib.Path(path).name == target and text == reconstructed[path]
    report = {"schema": "independent.decision-core.patch-readback.v1", "scope": "Data-only in-memory patch application; no target helper or study execution.", "reader_controls": {"valid_context": True, "bad_context_rejected": True, "new_file": True}, "base_checks": base_checks, "outputs": outputs, "derivative_patches_agree": True, "reader_sha256": hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest()}
    destination = root / "independent-review/PATCH-READBACK-02.json"
    with destination.open("x") as stream:
        stream.write(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"path": str(destination), "bytes": destination.stat().st_size, "sha256": hashlib.sha256(destination.read_bytes()).hexdigest()}))


if __name__ == "__main__":
    main(pathlib.Path(sys.argv[1]))
