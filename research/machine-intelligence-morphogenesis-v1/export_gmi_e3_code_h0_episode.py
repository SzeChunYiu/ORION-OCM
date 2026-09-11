"""Official #208 H0 export path: validate source -> map -> validate episode.

The raw mapper remains useful for unit testing, but H0 runners should call this
wrapper so identity/verifier/resource custody cannot be bypassed accidentally.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from map_code_h0_trace_to_gmi_e3 import map_h0_trace
from validate_gmi_e3_code_h0_trace import validate_h0_trace
from validate_gmi_e3_episode import validate_episode


def export_episode(source: dict) -> dict:
    source_errors = validate_h0_trace(source)
    if source_errors:
        raise ValueError("source trace invalid: " + " | ".join(source_errors))

    episode = map_h0_trace(source)
    episode_errors = validate_episode(episode)
    if episode_errors:
        raise ValueError("mapped GMI episode invalid: " + " | ".join(episode_errors))
    return episode


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("trace", type=Path)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    if args.out.exists():
        print("ERROR: refusing to overwrite existing output")
        return 1

    try:
        source = json.loads(args.trace.read_text(encoding="utf-8"))
        episode = export_episode(source)
    except (OSError, ValueError, TypeError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}")
        return 1

    args.out.write_text(json.dumps(episode, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("GMI_E3_CODE_H0_EPISODE_EXPORT_GREEN")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
