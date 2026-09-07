"""Isolated raw-source worker; the parent aggregate controller owns its descendants."""
from pathlib import Path
import sys
import types


def main():
    if len(sys.argv) != 3 or not sys.flags.isolated or not sys.flags.no_site:
        raise SystemExit('use pinned Python -I -S acquisition_worker.py LOCK NEW_OUTPUT')
    path = Path(__file__).resolve().with_name('acquisition_git.py')
    module = types.ModuleType('acquisition_git'); module.__file__ = str(path)
    sys.modules['acquisition_git'] = module
    exec(compile(path.read_bytes(), str(path), 'exec'), module.__dict__)
    result = module.acquire(Path(sys.argv[1]), Path(sys.argv[2]))
    return 0 if result['terminal'] == 'ACQUIRED' else 2


if __name__ == '__main__':
    raise SystemExit(main())
