"""Load inventoried source bytes and replay registered finite witnesses."""

import hashlib
import importlib
import importlib.abc
import importlib.machinery
import io
import json
import sys
import unittest


class SourceMismatch(Exception):
    pass


class BoundModules(importlib.abc.MetaPathFinder, importlib.abc.Loader):
    def __init__(self, root, inventory):
        self.root = root
        self.inventory = inventory
        self.names = {name[:-3] for name in inventory if name.endswith(".py")}

    def find_spec(self, fullname, path=None, target=None):
        if fullname in self.names:
            return importlib.machinery.ModuleSpec(fullname, self, origin=str(self.root / (fullname + ".py")))
        return None

    def create_module(self, spec):
        return None

    def exec_module(self, module):
        name = module.__name__ + ".py"
        path = self.root / name
        raw = path.read_bytes()
        if hashlib.sha256(raw).hexdigest() != self.inventory[name]:
            raise SourceMismatch("source changed before import: " + name)
        module.__file__ = str(path)
        exec(compile(raw, str(path), "exec"), module.__dict__)


def test_ids(suite):
    for item in suite:
        if isinstance(item, unittest.TestSuite):
            yield from test_ids(item)
        else:
            yield item.id()


def registered_replays(root):
    from factor_probe import run as factor_run
    from neutral_runner import run_case, REGISTRATION_SHA256
    from neutral_search import enumerate_space
    from test_memory_derivation import registered_results as memory_run
    from test_orbit_derivation import registered_results as orbit_run
    from test_orbit_raw import registered_results as raw_run

    raw = (root / "neutral_registration.json").read_bytes()
    if hashlib.sha256(raw).hexdigest() != REGISTRATION_SHA256:
        raise SourceMismatch("neutral registration changed")
    registration = json.loads(raw)
    spaces, searches = {}, []
    for arity, bound in sorted({(c["arity"], c["nodes"]) for c in registration["cases"]}):
        levels, counters = enumerate_space(arity, bound)
        spaces[arity, bound] = levels
        searches.append({"arity": arity, "node_bound": bound, **counters})
    cases = [run_case(c, registration, spaces[c["arity"], c["nodes"]]) for c in registration["cases"]]
    if any(c["status"] != "CHECKED" for c in cases):
        raise ValueError("registered neutral prediction refuted")
    return {"neutral": {"cases": cases, "searches": searches},
            "factor": factor_run("all"), "orbit": orbit_run(),
            "raw_ecology": raw_run(), "memory": memory_run()}


def run(root, inventory):
    loader = BoundModules(root, inventory)
    sys.meta_path.insert(0, loader)
    try:
        suite = unittest.TestSuite()
        for name in sorted(n for n in inventory if n.startswith("test_") and n.endswith(".py")):
            module = importlib.import_module(name[:-3])
            suite.addTests(unittest.defaultTestLoader.loadTestsFromModule(module))
        ids = sorted(test_ids(suite))
        stream = io.StringIO()
        result = unittest.TextTestRunner(stream=stream, verbosity=2).run(suite)
        if not ids or not result.wasSuccessful() or result.skipped or result.expectedFailures:
            return {"status": "WITNESS_FAILED", "tests_run": result.testsRun}, stream.getvalue()
        replays = registered_replays(root)
        return {"status": "CHECKED", "tests_run": result.testsRun, "tests": ids,
                "replays": replays}, stream.getvalue()
    finally:
        sys.meta_path.remove(loader)
