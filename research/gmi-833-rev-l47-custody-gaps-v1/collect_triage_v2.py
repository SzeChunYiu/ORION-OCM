#!/usr/bin/env python3
"""REV-L47 triage collector v2 — cross-package custody evidence.

For each of the 18 packages: upstream producers (repo paths referenced by the
package's freeze/checker files) and downstream consumers (repo files that
reference this package's artifacts), each with first-add commit time relative
to the package freeze. This is the metadata the per-package L47 screen could
not see: ordering demonstrable across packages.
"""
from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
PKG_DIR = Path(__file__).resolve().parent

PACKAGES = json.loads((PKG_DIR / "triage_timeline_v1.json").read_text())["packages"]


def git(*args: str) -> str:
    return subprocess.run(["/usr/bin/git", "-C", str(REPO), *args],
                          capture_output=True, text=True, check=True).stdout


# first-add time for every path under research/ (one pass)
_first_add: dict[str, tuple[int, str]] = {}
_cur = None
for line in git("log", "--diff-filter=A", "--format=__CT__%ct %H", "--name-only",
                "--", "research/").splitlines():
    if line.startswith("__CT__"):
        _, rest = line.split("__CT__", 1)
        ct_s, sha = rest.split()
        _cur = (int(ct_s), sha)
    elif line.strip() and _cur is not None:
        _first_add.setdefault(line.strip(), _cur)


def first_add(path: str):
    return _first_add.get(path)


def refs_in_file(text: str) -> set[str]:
    """repo research/ paths mentioned in a file's text."""
    out = set()
    for m in re.finditer(r"research/([A-Za-z0-9._\-]+/)+[A-Za-z0-9._\-]+\.(?:py|json|md)", text):
        out.add(m.group(0))
    return out


def main() -> None:
    result = {}
    for pkg, rec in PACKAGES.items():
        base = f"research/{pkg}"
        fz_t = min(e["ct"] for e in rec["events"] if e["kind"] == "freeze")
        # upstream: paths referenced by freeze/checker/readme files of this package
        upstream = {}
        for f in (REPO / base).glob("*"):
            if f.suffix in {".md", ".py", ".json"} and f.is_file():
                try:
                    text = f.read_text(errors="replace")
                except OSError:
                    continue
                for ref in refs_in_file(text):
                    if ref.startswith(base + "/"):
                        continue
                    fa = first_add(ref)
                    if fa:
                        upstream[ref] = {"ct": fa[0], "dt_before_freeze_s": fz_t - fa[0]}
        # downstream: other packages whose files reference this package's dir
        art_names = [e["file"] for e in rec["events"]]
        downstream = {}
        hits = subprocess.run(
            ["grep", "-rl", "--include=*.py", "--include=*.json", "--include=*.md",
             base, str(REPO / "research")],
            capture_output=True, text=True).stdout.splitlines()
        for hit in hits:
            hit_p = Path(hit).relative_to(REPO).as_posix()
            if hit_p.startswith(base + "/"):
                continue
            fa = first_add(hit_p)
            if fa:
                downstream.setdefault(
                    str(Path(hit_p).parent), {"ct": fa[0], "dt_after_freeze_s": fa[0] - fz_t,
                                              "files": []})["files"].append(Path(hit_p).name)
        result[pkg] = {
            "freeze_ct": fz_t,
            "upstream_refs": {k: v for k, v in sorted(upstream.items(),
                                                      key=lambda kv: -kv[1]["dt_before_freeze_s"])[:12]},
            "downstream_consumers": {k: v for k, v in sorted(downstream.items(),
                                                             key=lambda kv: kv[1]["ct"])[:12]},
        }
        up = [f"{v['dt_before_freeze_s']}s:{Path(k).parent.name}" for k, v in result[pkg]["upstream_refs"].items()]
        dn = [f"+{v['dt_after_freeze_s']}s:{Path(k).name}" for k, v in result[pkg]["downstream_consumers"].items()]
        print(f"{pkg}\n  upstream(dt before freeze): {up[:6]}\n  downstream(dt after freeze): {dn[:6]}")
    (PKG_DIR / "triage_crosspkg_v1.json").write_text(json.dumps(result, indent=2) + "\n")
    print("wrote triage_crosspkg_v1.json")


if __name__ == "__main__":
    main()
