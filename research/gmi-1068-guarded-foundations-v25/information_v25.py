"""Finite attained-fiber checks; the general equivalences are kernel theorems."""
from core_v25 import nat, need
from presentations_v25 import checked, core_signature, padded


def _inputs(models, codes, check):
    need(type(models) is tuple and type(codes) is tuple, "model/code tuples")
    need(len(models) == len(codes), "one code per model")
    for model in models:
        check(model)
    for code in codes:
        nat(code)


def _fibers(models, codes, signature):
    seen = {}
    for model, code in zip(models, codes):
        value = signature(model)
        if code in seen and seen[code] != value:
            return False
        seen[code] = value
    return True


def _presented_inputs(models, codes):
    _inputs(models, codes, checked)
    need(not models or all(model.ambient_size == models[0].ambient_size for model in models),
         "common ambient interface required")


def core_recoverable(models, codes):
    _presented_inputs(models, codes)
    return _fibers(models, codes, core_signature)


def table_recoverable(models, codes):
    _presented_inputs(models, codes)
    return _fibers(models, codes, lambda model: padded(model).rows)
