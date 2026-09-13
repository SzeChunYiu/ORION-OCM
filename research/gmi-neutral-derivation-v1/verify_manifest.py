"""Check complete delivered payload, including raw evidence and replay files."""

import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent


def inventory():
    return {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(ROOT.rglob("*")) if p.is_file() and
            p != ROOT / "MANIFEST_V1.json" and "__pycache__" not in p.parts and p.suffix != ".pyc"}


def main():
    manifest = json.loads((ROOT / "MANIFEST_V1.json").read_text())
    if not isinstance(manifest, dict) or manifest.get("schema") != "GMI_NEUTRAL_COMPLETE_PAYLOAD_V1":
        raise ValueError("invalid complete payload schema")
    actual = inventory()
    if manifest.get("sha256") != actual or manifest.get("files") != len(actual):
        raise ValueError("delivered payload inventory differs")
    print(json.dumps({"status": "CHECKED", "payload_files": len(actual)}, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        code = main()
    except (OSError, ValueError, TypeError) as error:
        print(json.dumps({"status": "NOT_CHECKED", "problem": str(error)}))
        code = 2
    raise SystemExit(code)
