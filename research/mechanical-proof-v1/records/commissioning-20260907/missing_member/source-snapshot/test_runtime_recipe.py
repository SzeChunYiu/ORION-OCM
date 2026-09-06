"""Runtime custody controls; no proof or search execution."""
import importlib.util
from pathlib import Path
import subprocess
from unittest.mock import patch

import pytest

HERE = Path(__file__).resolve().parent


@pytest.fixture
def recipe():
    path = HERE / "runtime_recipe.py"
    if not path.exists(): return None
    spec = importlib.util.spec_from_file_location("tested_runtime_recipe", path)
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    return module


def elf(path):
    path.write_bytes(b"\x7fELF" + bytes([2, 1, 1]) + bytes(9) + b"\x03\x00" + bytes(64))
    return path


def answer(text, code=0, stderr=""):
    return subprocess.CompletedProcess([], code, text, stderr)


def test_wrong_archive_refused_before_destination_or_tool_dispatch(recipe, tmp_path):
    assert recipe is not None, "runtime recipe is not implemented"
    archive = tmp_path / "wrong.tar.zst"; archive.write_bytes(b"wrong archive")
    destination = tmp_path / "destination"
    with patch.object(recipe.subprocess, "run") as run, pytest.raises(ValueError):
        recipe.prepare_runtime(archive, tmp_path / "python", destination)
    run.assert_not_called(); assert not destination.exists()


def test_archive_symlink_refuses_without_writes(recipe, tmp_path):
    source = tmp_path / "source"; source.write_bytes(b"wrong archive")
    link = tmp_path / "archive"; link.symlink_to(source)
    with pytest.raises(ValueError): recipe.prepare_runtime(link, tmp_path, tmp_path / "out")
    assert not (tmp_path / "out").exists()


def test_missing_library_is_not_silently_omitted(recipe, tmp_path):
    executable = elf(tmp_path / "tool"); destination = tmp_path / "deps"
    with patch.object(recipe.subprocess, "run", return_value=answer("libmissing.so => not found\n")):
        with pytest.raises(OSError): recipe.shared_libraries([executable], [], destination)
    assert not destination.exists()


@pytest.mark.parametrize("output", ["unrecognized dependency syntax\n", "/missing/loader (0x1)\n"])
def test_unknown_or_missing_dependency_fails_closed(recipe, tmp_path, output):
    executable = elf(tmp_path / "tool")
    with patch.object(recipe.subprocess, "run", return_value=answer(output)):
        with pytest.raises((ValueError, OSError)):
            recipe.shared_libraries([executable], [], tmp_path / "deps")
    assert not (tmp_path / "deps").exists()


def test_internal_library_skipped_and_external_guest_deduplicated(recipe, tmp_path):
    root = tmp_path / "runtime"; root.mkdir()
    tool = elf(root / "tool"); internal = elf(root / "internal.so")
    external = elf(tmp_path / "external.so")
    output = f"libinternal.so => {internal} (0x1)\nlibexternal.so => {external} (0x2)\n"
    with patch.object(recipe.subprocess, "run", return_value=answer(output)):
        record = recipe.shared_libraries([tool, internal], [root], tmp_path / "deps")
    assert len(record["mounts"]) == 1 and record["mounts"][0][1] == str(external)
    copied = Path(record["mounts"][0][0])
    assert copied.read_bytes() == external.read_bytes() and copied != external
    assert len(record["inspection"]) == 2


def test_conflicting_dependency_identity_is_refused_before_copy(recipe, tmp_path):
    tools = [elf(tmp_path / "one"), elf(tmp_path / "two")]
    library = elf(tmp_path / "external.so"); count = [0]
    def inspect(*args, **kwargs):
        count[0] += 1
        if count[0] == 2: library.write_bytes(library.read_bytes() + b"changed")
        return answer(f"{library} (0x1)\n")
    with patch.object(recipe.subprocess, "run", side_effect=inspect):
        with pytest.raises(ValueError, match="conflicting"):
            recipe.shared_libraries(tools, [], tmp_path / "deps")
    assert not (tmp_path / "deps").exists()


def test_real_trusted_binary_uses_only_individual_copied_dependencies(recipe, tmp_path):
    from isolation import run_isolated
    tool = Path("/usr/bin/true").resolve()
    record = recipe.shared_libraries([tool], [], tmp_path / "deps")
    assert record["mounts"]
    assert all(Path(host).is_file() and guest not in ("/", "/usr", "/lib", "/lib64")
               for host, guest in record["mounts"])
    result = run_isolated(["/bin/true"], read_only=[(tool, "/bin/true"), *record["mounts"]],
                          executable_sha256=recipe.file_hash(tool), timeout_s=3, max_output_bytes=4096)
    assert result["terminal"] == "COMPLETED" and result["returncode"] == 0, result
    assert result["cleanup"]["reaped"] and result["cleanup"]["group_absent"]


def test_elf_inventory_includes_extensions_but_not_objects_or_plain_data(recipe, tmp_path):
    runtime = tmp_path / "runtime"; runtime.mkdir()
    extension = elf(runtime / "extension.so")
    (runtime / "text").write_text("not an executable")
    obj = elf(runtime / "object.o")
    raw = bytearray(obj.read_bytes()); raw[16:18] = b"\x01\x00"; obj.write_bytes(raw)
    assert recipe.elf_files([runtime]) == [extension]


def test_internal_rpath_dot_segments_resolve_before_guest_mount_validation(recipe, tmp_path):
    root = tmp_path / "runtime"; (root / "bin").mkdir(parents=True); (root / "lib").mkdir()
    tool = elf(root / "bin/tool"); internal = elf(root / "lib/internal.so")
    reported = str(root) + "/bin/../lib/internal.so"
    with patch.object(recipe.subprocess, "run", return_value=answer(f"internal.so => {reported} (0x1)\n")):
        record = recipe.shared_libraries([tool], [root], tmp_path / "deps")
    assert record["mounts"] == [] and record["files"] == {}


def test_dependency_scope_excludes_dormant_lean_build_sysroot(recipe, tmp_path):
    lean = tmp_path / "lean"; (lean / "bin").mkdir(parents=True); (lean / "lib/glibc").mkdir(parents=True)
    entry = elf(lean / "bin/lean"); elf(lean / "lib/glibc/librt.so")
    python = tmp_path / "python"; (python / "bin").mkdir(parents=True); (python / "lib/lib-dynload").mkdir(parents=True)
    py = elf(python / "bin/python3.11"); extension = elf(python / "lib/lib-dynload/example.so")
    assert recipe.runtime_elfs(lean, python) == sorted([entry, py, extension])


def test_private_prefix_dependency_is_copied_to_explicit_loader_guest(recipe, tmp_path):
    private = tmp_path / "private"; private.mkdir()
    library = elf(private / "libexample.so.1"); tool = elf(tmp_path / "tool")
    with patch.object(recipe.subprocess, "run", return_value=answer(f"libexample.so.1 => {library} (0x1)\n")) as run:
        record = recipe.shared_libraries([tool], [], tmp_path / "deps", private_library_dirs=[private])
    assert record["mounts"][0][1] == "/lib/x86_64-linux-gnu/libexample.so.1"
    assert Path(record["mounts"][0][0]).read_bytes() == library.read_bytes()
    assert run.call_args.kwargs["env"]["LD_LIBRARY_PATH"] == str(private)
    assert record["files"][record["mounts"][0][1]]["original_source"] == str(library)
