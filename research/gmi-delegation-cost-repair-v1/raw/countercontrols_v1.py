"""Source-pinned synthetic countercontrols; no ecology/timing experiment."""
from pathlib import Path
from functools import partial
import dis, hashlib, importlib.util, json
ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "grand_gmi_delegation_invariant_cost_checks_v1.py"
if hashlib.sha256(SOURCE.read_bytes()).hexdigest() != "4160fe19a8bf04981af04ffa3f538b2649499100c01a861ada70e112e3420f4f":
    raise RuntimeError("pinned checker changed")
spec = importlib.util.spec_from_file_location("pinned_dic", SOURCE)
dic = importlib.util.module_from_spec(spec)
spec.loader.exec_module(dic)
parent_source = dic.REGISTERED["WRITTEN_SHARED_SUM_NET"]
parent = dic.vector(parent_source)
parent_fn = dic.account(parent_source)["fn"]
wrapper_source = "def f(x):\n    return delegate(x)\n"
opaque = partial(parent_fn)
opaque_row = dic.vector(wrapper_source, {"delegate": opaque})
direct_row = dic.vector(wrapper_source, {"delegate": parent_fn})
class PythonDispatch:
    def __getitem__(self, x):
        return parent_fn(x)
dispatch_source = "def f(x):\n    return table[x]\n"
dispatch_row = dic.vector(dispatch_source, {"table": PythonDispatch()})
rows = {"written_parent": parent, "explicit_python_wrapper": direct_row,
        "opaque_partial_wrapper": opaque_row, "implicit_python_subscript": dispatch_row}
if not all(row["exact_parity_on_all_eight_inputs"] for row in rows.values()):
    raise RuntimeError("incorrect candidate output")
if not (opaque.func is parent_fn and not hasattr(opaque, "__code__")):
    raise RuntimeError("not the exact original function behind the opaque wrapper")
if not dic.dominates(opaque_row, parent):
    raise RuntimeError("opaque-consolidation counterexample did not reproduce")
if not (dic.dominates(dispatch_row, parent) and dispatch_row["unaccounted_calls"] == 0):
    raise RuntimeError("implicit-dispatch counterexample did not reproduce")
if dic.relation(direct_row, parent) != "IS_DOMINATED_BY":
    raise RuntimeError("known explicit-recursion positive control failed")
fn = dic.account(dispatch_source, {"table": PythonDispatch()})["fn"]
print(json.dumps({
    "scope": "synthetic eight-input deterministic controls, no new empirical measurement",
    "source_commit": "d9e4a190b2d2fda9000483291262f6d658a0891f",
    "checker_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
    "rows": rows,
    "partial_wraps_exact_original_function": opaque.func is parent_fn,
    "partial_has_python_code_object": hasattr(opaque, "__code__"),
    "partial_dominates_exact_parent": dic.dominates(opaque_row, parent),
    "implicit_python_dispatch_has_code_object": hasattr(PythonDispatch.__getitem__, "__code__"),
    "implicit_dispatch_opnames": [i.opname for i in dis.get_instructions(fn)],
    "implicit_dispatch_dominates_parent": dic.dominates(dispatch_row, parent),
    "positive_explicit_recursion_relation": dic.relation(direct_row, parent),
    "all_eight_inputs": dic.INPUTS,
    "expected_outputs": dic.PARITY
}, sort_keys=True, indent=2))
