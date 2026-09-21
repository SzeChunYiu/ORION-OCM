"""Isolated standalone full replay of the Section-M re-audit RESULT.

Recomputes RESULT_V1.json with the same interpreter flags as the invoking
run and requires byte-identical output; writes the payload to stdout.  CI
runs ``python3 -I [-O] -B replay_v1.py`` from this package and compares to
the committed RESULT_V1.json, exactly as the hierarchy/causal legacy
packages replay their receipts.
"""
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent


def replay() -> bytes:
    committed = (HERE / "RESULT_V1.json").read_bytes()
    flags = ["-I", "-B"] + (["-O"] if sys.flags.optimize else [])
    p = subprocess.run(
        [sys.executable, *flags, str(HERE / "executor_v1.py")],
        cwd=str(HERE), capture_output=True, timeout=1800,
    )
    if p.returncode != 0:
        raise ValueError("replay executor failed: rc=%d stderr=%r"
                         % (p.returncode, p.stderr[:500]))
    if p.stderr:
        raise ValueError("replay executor stderr not empty: %r" % p.stderr[:500])
    recomputed = (HERE / "RESULT_V1.json").read_bytes()
    if recomputed != committed:
        raise ValueError("RESULT byte mismatch in replay")
    return recomputed


if __name__ == "__main__":
    sys.stdout.buffer.write(replay())
