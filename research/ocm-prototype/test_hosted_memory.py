"""Offline filesystem staging controls; fake model bytes are never loaded as a donor."""
from pathlib import Path

import pytest
import hosted_stage as S

ITEMS = [{"id": "synthetic", "request": {"kind": "syntax", "tokens": ["A"]}}]


@pytest.fixture
def model(tmp_path, monkeypatch):
    path = tmp_path / "UNIT_FIXTURE_NOT_A_DONOR.bin"
    path.write_bytes(b"UNIT_FIXTURE_NOT_A_DONOR")
    # Directory staging needs package identities, not native code execution.
    monkeypatch.setattr(S, "version", S.PINS.__getitem__)
    return path, S.sha(path)


def test_new_memory_directory_created_and_existing_memory_resumed(tmp_path, model):
    memory = tmp_path / "owner" / "memory"
    first = S.stage(ITEMS, *model, tmp_path / "stage-one", memory_dir=memory)
    assert memory.is_dir() and first["memory"] == str(memory)
    sentinel = memory / "saved.txt"
    sentinel.write_text("PUBLIC_RESUME_CONTROL")
    second = S.stage(ITEMS, *model, tmp_path / "stage-two", memory_dir=memory)
    assert second["memory"] == first["memory"]
    assert sentinel.read_text() == "PUBLIC_RESUME_CONTROL"


def test_relative_memory_directory_preserves_normal_resume(tmp_path, model, monkeypatch):
    memory = tmp_path / "memory"
    memory.mkdir()
    (memory / "saved.txt").write_text("PUBLIC_RELATIVE_CONTROL")
    monkeypatch.chdir(tmp_path)
    staged = S.stage(ITEMS, *model, tmp_path / "stage", memory_dir=Path("memory"))
    assert staged["memory"] == str(memory)
    assert (memory / "saved.txt").read_text() == "PUBLIC_RELATIVE_CONTROL"


@pytest.mark.parametrize("case", ["root", "ancestor", "dangling_root", "dangling_ancestor"])
def test_symlink_memory_paths_refused_without_stage_or_target_mutation(tmp_path, model, case):
    target = tmp_path / "target"
    if not case.startswith("dangling"):
        target.mkdir()
        (target / "saved.txt").write_text("PUBLIC_REFUSAL_CONTROL")
    alias = tmp_path / "alias"
    alias.symlink_to(target, target_is_directory=True)
    memory = alias / "child" if "ancestor" in case else alias
    output = tmp_path / "stage"
    before = sorted((p.relative_to(target).as_posix(), p.read_bytes()) for p in target.rglob("*") if p.is_file())
    with pytest.raises(ValueError, match="memory.*symlink"):
        S.stage(ITEMS, *model, output, memory_dir=memory)
    assert not output.exists()
    assert alias.is_symlink()
    assert target.exists() is (not case.startswith("dangling"))
    assert sorted((p.relative_to(target).as_posix(), p.read_bytes()) for p in target.rglob("*") if p.is_file()) == before
