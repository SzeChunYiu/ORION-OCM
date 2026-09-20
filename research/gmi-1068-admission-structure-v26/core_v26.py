"""Actual immutable category and guarded-tree interfaces."""
import importlib.util
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
PARENT = ROOT / "research/gmi-1068-guarded-foundations-v25"


def source_module(name):
    path = PARENT / (name + ".py")
    if name in sys.modules:
        module = sys.modules[name]
        if Path(module.__file__).resolve() != path:
            raise ValueError("same-name source collision")
        return module
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


old_core = source_module("core_v25")
syntax = source_module("syntax_v25")
trees = source_module("trees_v25")
Typed, Table = old_core.Typed, old_core.Table
old_categories, old_partial = old_core.old_categories, old_core.old_partial
need, index, nat = old_core.need, old_core.index, old_core.nat
checked_category = trees.checked_category


def checked_path(category, path):
    checked_category(category)
    need(type(path) is tuple and len(path) == 2, "path shape")
    start, word = path
    index(start, category.object_count)
    need(type(word) is tuple, "path word must be tuple")
    for arrow in word:
        index(arrow, len(category.table.rows))
    return start, word
