"""Small custody helpers shared by this one registered trial."""
from pathlib import Path
import hashlib
import base64
import csv
import json
import os
import sys

ROOT = Path(__file__).resolve().parent

def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()

def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def write(path, value):
    path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as f:
        f.write(canonical(value) + b"\n")

def read(path):
    return json.loads(Path(path).read_text())

def record_files(root, record):
    """Verify actual installed bytes against RECORD; return exact SHA256 closure."""
    found = {}
    with Path(record).open(newline="") as handle:
        for rel, encoded, size in csv.reader(handle):
            path = (Path(root)/rel).resolve()
            if not encoded:
                if path.is_file(): found[str(path)] = sha(path)
                continue
            algorithm, expected = encoded.split("=",1)
            data = path.read_bytes()
            actual = base64.urlsafe_b64encode(hashlib.new(algorithm,data).digest()).decode().rstrip("=")
            if actual != expected or (size and len(data) != int(size)):
                raise ValueError("DISTRIBUTION_CONTENT_DRIFT:" + str(path))
            found[str(path)] = hashlib.sha256(data).hexdigest()
    return found

def verify_freeze(manifest_path):
    manifest = read(manifest_path)
    for rel, expected in manifest["trial_files"].items():
        if sha(ROOT / rel) != expected: raise ValueError("TRIAL_SOURCE_DRIFT:" + rel)
    context = Path(manifest["context_root"])
    if sha(context / "SHA256SUMS") != manifest["context_inventory_sha256"]:
        raise ValueError("CONTEXT_INVENTORY_DRIFT")
    for line in (context / "SHA256SUMS").read_text().splitlines():
        expected, rel = line.split("  ", 1)
        if sha(context / rel) != expected: raise ValueError("CONTEXT_DRIFT:" + rel)
    for path, expected in manifest["runtime_files"].items():
        if sha(path) != expected: raise ValueError("RUNTIME_FILE_DRIFT:" + path)
    for name, expected in manifest["runtime_environment"].items():
        if os.environ.get(name) != expected: raise ValueError("RUNTIME_ENV_DRIFT:" + name)
    return manifest

def origins(manifest, arm):
    context = Path(manifest["context_root"])
    expected = {}
    baseline = read(context / "CONTEXT_MANIFEST.json")["source_files"]
    for rel in baseline:
        if rel.startswith("src/") and rel.endswith(".py"):
            name = rel[4:-3].replace("/", ".")
            if name.endswith(".__init__"): name = name[:-9]
            expected[name] = context / "source" / rel
        elif rel.startswith("research/ocm-prototype/") and rel.endswith(".py"):
            expected[rel[len("research/ocm-prototype/"):-3].replace("/", ".")] = context / "source" / rel
    for name in ("bound_context", "restore_context"):
        expected[name] = context / (name + ".py")
    for name in ("exact_sparse_donor", "exact_sparse_donor_check", "exact_sparse_donor_consumer", "representation_donor_grade"):
        expected[name] = ROOT / "source" / (name + ".py")
    actual = {}
    for name, target in expected.items():
        module = sys.modules.get(name)
        if module is None: continue
        path = Path(module.__file__).resolve()
        if path != target.resolve(): raise ValueError("MODULE_ORIGIN_DRIFT:" + name)
        actual[name] = {"path": str(path), "sha256": sha(path)}
    sympy = sorted(n for n in sys.modules if n == "sympy" or n.startswith("sympy."))
    if arm == "reference" and sympy: raise ValueError("UNUSED_SYMPY_IN_REFERENCE")
    external = {}
    for name, expected_record in manifest["runtime_modules"].items():
        module = sys.modules.get(name)
        if module is None: continue
        path = str(Path(module.__file__).resolve())
        record = {"path": path, "sha256": sha(path)}
        if record != expected_record: raise ValueError("RUNTIME_MODULE_DRIFT:" + name)
        external[name] = record
    return {"modules": actual, "external": external, "sympy_imported": bool(sympy), "sympy_module_count": len(sympy)}
