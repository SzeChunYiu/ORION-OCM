"""Public CLI deliberately has no target, selection, staging or solver options."""
import argparse
import json
from corpus_audit import run_audit


def main():
    parser = argparse.ArgumentParser(description="Pinned local lexical corpus inventory only.")
    parser.add_argument("--repo", required=True, help="Existing local repository; never fetched.")
    parser.add_argument("--out", required=True, help="Fresh evaluator-only receipt directory.")
    args = parser.parse_args()
    report = run_audit(args.repo, args.out)
    print(json.dumps({"terminal": report["terminal"],
                      "source_inventory_sha256": report["source_inventory_sha256"]}))
    return 0 if report["terminal"] == "LEXICAL_INVENTORY_VALIDATED" else 3


if __name__ == "__main__":
    raise SystemExit(main())
