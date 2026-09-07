"""Tiny authored syntax fixtures; no public corpus or proof execution."""
import importlib


def api(name):
    try:
        return importlib.import_module(name)
    except ModuleNotFoundError as exc:
        raise AssertionError(f"inventory API not implemented: {name}") from exc


def wrapper(key="A", *, signature="(P : Prop) (h : P) : P", extra="",
            context="set_option autoImplicit false\n", body=None, tail=""):
    proof = body or f"by p2m_exact_reverting @_root_.P2MW.S_{key}.solution"
    return (f"import Mathlib\nimport P2M.Util\nimport P2M.Sol.S_{key}\n"
            + extra + "\n" + context + f"\ntheorem {key} {signature} := {proof}\n" + tail)


def solution(*dependencies):
    return "import Mathlib\n" + "".join(f"import Theorems.Thm_{d}\n" for d in dependencies)
