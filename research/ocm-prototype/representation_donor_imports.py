"""Import the unchanged, content-pinned prior-study modules; no installed package needed."""
from pathlib import Path
import hashlib
import importlib.util
import json
import sys

DONORS = Path(__file__).resolve().parent / "results/representation-donor-absorption-20260906/donors"
PINS = {
    "router": ("orion/router.py", "f7f77e1e5b6993acb49f948e7e7c2e4f18513bb8045c842319ce3fb5bb86ca59"),
    "f2": ("v2/f2.py", "69c00fc1a0f291e2b252fbed22b49fa143846972396875a170aaf09bf7dfbe96"),
    "revision": ("v2/revision.py", "579527e288005bf48309442529ed9698831b1ea951b695516e8a3ba45c1357b2"),
}
CONTRACTS = {
    "orion/ROUTER_PROTOCOL.md": "5760a781464bcda06baa8baa90f73cb9711e7b374262883104770fd2013da5e3",
    "v2/F2_CONTRACT.md": "dcaef81ad0401ecb5db1f626902b632926eed4f044246ea622870a35ac4eaae1",
    "v2/REVISION_CONTRACT.md": "192bdc6d85d80006db795756b0bf7295c9ee08c509a5bb66cdf6335829b57cbc",
}


def load(root=DONORS):
    root = Path(root)
    manifest = json.loads((root / "MANIFEST.json").read_text())
    for row in manifest["records"]:
        raw = (root / row["path"]).read_bytes()
        if len(raw) != row["bytes"] or hashlib.sha256(raw).hexdigest() != row["sha256"]:
            raise ValueError("DONOR_SOURCE_DRIFT:" + row["path"])
    for path, digest in [*PINS.values(), *CONTRACTS.items()]:
        if hashlib.sha256((root / path).read_bytes()).hexdigest() != digest:
            raise ValueError("DONOR_SOURCE_DRIFT:" + path)
    result = {}
    for key, (path, digest) in PINS.items():
        name = "ocm_absorbed_" + key + "_" + digest[:12]
        spec = importlib.util.spec_from_file_location(name, root / path)
        obj = importlib.util.module_from_spec(spec)
        sys.modules[name] = obj
        spec.loader.exec_module(obj)
        result[key] = obj
    return result
