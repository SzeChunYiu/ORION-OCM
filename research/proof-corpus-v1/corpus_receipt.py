"""Source custody and measured costs for a global lexical inventory."""
from pathlib import Path
import resource
import sys
import time
from corpus_contract import CorpusError, sha256


def code_inventory():
    root = Path(__file__).resolve().parent
    files = {}
    for path in sorted(root.rglob("*")):
        relative = path.relative_to(root)
        if "__pycache__" in relative.parts or relative.parts[:2] == ("provenance", "runs"):
            continue
        if path.is_file() and (path.suffix in (".py", ".md", ".json") or path.name == ".gitignore"):
            if path.is_symlink():
                raise CorpusError("CODE_SOURCE_SYMLINK", str(relative))
            files[str(relative)] = sha256(path.read_bytes())
    return files


def require_same_source(before, after):
    if before != after:
        raise CorpusError("SOURCE_DRIFT")


class Costs:
    def __init__(self):
        self.wall = time.perf_counter()
        self.own = resource.getrusage(resource.RUSAGE_SELF)
        self.children = resource.getrusage(resource.RUSAGE_CHILDREN)

    def finish(self, metrics):
        own = resource.getrusage(resource.RUSAGE_SELF)
        children = resource.getrusage(resource.RUSAGE_CHILDREN)
        unit = 1 if sys.platform == "darwin" else 1024
        return dict(metrics, wall_seconds=time.perf_counter() - self.wall,
                    own_cpu_seconds=own.ru_utime + own.ru_stime - self.own.ru_utime - self.own.ru_stime,
                    child_cpu_seconds=children.ru_utime + children.ru_stime - self.children.ru_utime - self.children.ru_stime,
                    own_process_lifetime_peak_rss_bytes=own.ru_maxrss * unit,
                    finished_child_lifetime_max_rss_bytes=children.ru_maxrss * unit,
                    process_tree_peak_rss_bytes=None, physical_io_bytes=None,
                    cache_state="UNCONTROLLED", neural_inference_calls=0,
                    excluded_costs=["initial Python imports", "final report serialization/write",
                                    "external source acquisition", "Lean/library build"],
                    cost_scope="FULL_GLOBAL_INVENTORY_NOT_WARM_QUERY")
