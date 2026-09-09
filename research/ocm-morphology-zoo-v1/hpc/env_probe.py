#!/usr/bin/env python3
"""GS environment probe (#221 sec 2a reuse-first): runs ON THE TARGET HOST
(LUNARC login), records which mature search packages are importable, and
writes GS_ENV_PROBE.json.  freeze_gs.py REFUSES to freeze without it, and
pins the archive/surrogate implementations from it — a frozen campaign
must never depend on the ambient environment.

Usage: python3 hpc/env_probe.py <CAPSULE_ROOT>
"""
from __future__ import annotations

import json
import os
import platform
import sys
import time

ROOT = os.path.abspath(sys.argv[1])

_PACKAGES = {
    "ribs": ("pyribs (ProximityArchive novelty admission)", "0.8"),
    "sklearn": ("scikit-learn (HistGradientBoosting surrogate heads)", "0.24"),
    "deap": ("DEAP (GA/speciation toolbox)", None),
    "optuna": ("Optuna (scalar BO — forbidden by GS no-scalar contract)", None),
    "nevergrad": ("nevergrad (scalar optimizers — forbidden likewise)", None),
    "qdax": ("QDax/JAX (GPU-vectorized QD — GPU lane asset)", None),
    "hpbandster": ("HpBandSter (BOHB daemon workers)", None),
}


def _import(name: str):
    try:
        m = __import__(name)
        return getattr(m, "__version__", "unknown"), None
    except Exception as e:  # ImportError and any ABI failure
        return None, repr(e)[:120]


def main() -> None:
    pkgs = {}
    errors = {}
    for name, (_desc, _min) in _PACKAGES.items():
        ver, err = _import(name)
        pkgs[name] = ver
        if err:
            errors[name] = err

    def _has(name: str) -> bool:
        return pkgs.get(name) is not None

    choices = {
        # ProximityArchive needs pyribs >= 0.8; probe confirms import +
        # the class itself (0.7.x lacks it).  Host audit 2026-09-09: pip
        # resolves pyribs only to a useless 0.0.2 on laptop/old — the
        # class-level probe is what keeps the campaign on builtin there.
        "novelty_archive_impl": "ribs" if _has("ribs") and _probe_proximity()
        else "builtin",
        # HistGradientBoosting must exist AND instantiate (an importable
        # sklearn without working estimers pins builtin, never ambient).
        "surrogate_impl": "sklearn" if _has("sklearn") and _probe_histgb()
        else "builtin",
    }
    out = {
        "schema": "GS_ENV_PROBE_V1",
        "created_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "created_utc_by": "hpc/env_probe.py on the scoring host, BEFORE the "
                          "freeze (freeze_gs.py refuses without this file)",
        "host": os.environ.get("ZOO_HOST", os.uname().nodename),
        "python": platform.python_version(),
        "packages": pkgs,
        "import_errors": errors,
        "choices": choices,
        "package_roles": {k: v[0] for k, v in _PACKAGES.items()},
    }
    path = os.path.join(ROOT, "GS_ENV_PROBE.json")
    with open(path, "w") as fh:
        json.dump(out, fh, indent=1, sort_keys=True)
    print("ENV PROBE %s python=%s choices=%s" % (
        out["host"], out["python"], json.dumps(choices, sort_keys=True)))
    print("packages: " + json.dumps(pkgs, sort_keys=True))


def _probe_proximity() -> bool:
    try:
        from ribs.archives import ProximityArchive  # noqa: F401
        return True
    except Exception:
        return False


def _probe_histgb() -> bool:
    try:
        from sklearn.ensemble import HistGradientBoostingClassifier
        HistGradientBoostingClassifier(random_state=0)
        return True
    except Exception:
        return False


if __name__ == "__main__":
    main()
