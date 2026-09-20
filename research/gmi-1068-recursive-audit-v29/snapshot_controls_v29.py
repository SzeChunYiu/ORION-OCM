"""Real-data overlay for a formal-source plus receipt coupled rewrite."""
from contextlib import contextmanager
from copy import deepcopy
import hashlib
from pathlib import Path
import tempfile


@contextmanager
def formal_source_attack(root, receipt, contract):
    with tempfile.TemporaryDirectory(prefix="gmi-v29-formal-coupling-") as temporary:
        target = Path(temporary)
        (target / ".git").symlink_to(root / ".git")
        paths = set(receipt["source_bindings"])
        paths.update(contract.PACKAGE + "/" + name for name in receipt["inputs"])
        paths.add(contract.PACKAGE + "/RESULT_V29.json")
        for name in paths:
            destination = target / name
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes((root / name).read_bytes())
        source = contract.SOURCE_PATHS[-1]
        path = target / source
        path.write_bytes(path.read_bytes() + b"\n-- coupled replacement\n")
        changed = deepcopy(receipt)
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        changed["inputs"][path.name] = digest
        changed["kernel"]["sources"][source] = digest
        delta = len(b"\n-- coupled replacement\n")
        changed["source_costs"]["new_lean_bytes"] += delta
        changed["source_costs"]["deterministic_package_bytes"] += delta
        yield target, changed
