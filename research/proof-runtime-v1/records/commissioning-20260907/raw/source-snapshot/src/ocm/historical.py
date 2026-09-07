from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import ModuleType


class RepositoryNotFound(RuntimeError):
    pass


def repository_root(start: Path | None = None) -> Path:
    candidates = []
    if start is not None:
        candidates.append(start.resolve())
    candidates.extend([Path.cwd().resolve(), Path(__file__).resolve()])
    seen: set[Path] = set()
    for candidate in candidates:
        for path in (candidate, *candidate.parents):
            if path in seen:
                continue
            seen.add(path)
            if (path / "research" / "orion-machine" / "reference").is_dir():
                return path
    raise RepositoryNotFound("canonical repository root with research/orion-machine/reference not found")


def reference_path(name: str, root: Path | None = None) -> Path:
    base = root or repository_root()
    return base / "research" / "orion-machine" / "reference" / f"{name}.py"


def load_reference(name: str, root: Path | None = None) -> ModuleType:
    path = reference_path(name, root)
    if not path.exists():
        raise FileNotFoundError(path)
    module_name = f"ocm_historical_{name}"
    existing = sys.modules.get(module_name)
    if existing is not None:
        return existing
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load historical reference {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module
