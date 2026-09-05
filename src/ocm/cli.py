from __future__ import annotations

import argparse
import json
from collections.abc import Sequence


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="ocm", description="Bounded conversational runtime; historical audit commands require a repository checkout.")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("chat", help="persistent bounded-world chat (installed package)", add_help=False)
    sub.add_parser("methods", help="checked method-learning demonstration (installed package)", add_help=False)
    sub.add_parser("demo", help="historical M0 controlled demo (repository custody required)")
    sub.add_parser("status", help="historical M0 audit status (repository custody required)")
    args, rest = parser.parse_known_args(argv)
    if args.command == "chat":
        from .chat.__main__ import main as chat_main
        return chat_main(list(rest))
    if args.command == "methods":
        from .evaluation.method_learning_eval import main as methods_main
        return methods_main(list(rest))
    from .historical import RepositoryNotFound
    try:
        if args.command == "demo":
            from .demo import main as demo_main
            return demo_main(["--controlled", *rest])
        from .status import main as status_main
        return status_main(list(rest))
    except RepositoryNotFound as exc:
        print(json.dumps({"terminal": "CANNOT_CHECK_REPOSITORY_CUSTODY", "command": args.command, "reason": str(exc), "runtime_entrypoint": "ocm chat"}, sort_keys=True))
        return 2
