"""Static retained-field consumer report; never an execution/campaign classifier."""
from pathlib import Path
import sys


def main(argv=None):
    native = Path(__file__).resolve().parent
    unit = native.parents[1] / "gmi-pr551-consumer-repair-v1"
    sys.path.insert(0, str(unit))
    from source_contract_v1 import bound_files
    from contract_v1 import require
    from scan_retained_v1 import main as scan_main
    _, sources = bound_files(unit)
    for name in ("vm.py", "morph.py"):
        path = native / name
        require(path.is_file() and not path.is_symlink(), "native source missing/linked")
        require(path.read_bytes() == sources["raw/native/" + name], "live native source drift")
    return scan_main(argv)


if __name__ == "__main__":
    raise SystemExit(main())
