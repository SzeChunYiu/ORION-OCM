from __future__ import annotations

import argparse
from collections.abc import Sequence


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="ocm")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("demo")
    sub.add_parser("status")
    args, rest = parser.parse_known_args(argv)
    if args.command == "demo":
        from .demo import main as demo_main
        return demo_main(["--controlled", *rest])
    from .status import main as status_main
    return status_main(list(rest))
