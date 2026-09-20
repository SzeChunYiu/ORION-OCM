"""Fixed partial contexts over validated finite raw-history rosters."""
from core_v22 import Context, checked, need, permissions, spec_checked, subset, word_checked
from execution_v22 import support


def data(spec, context, histories, selected):
    spec_checked(spec)
    checked(context)
    need(type(histories) is tuple and len(histories) == context.n, "history dimension")
    for history in histories:
        need(type(history) is tuple and len(history) == 2, "raw history pair required")
        word_checked(spec.base, history[0], history[1])
    need(len(set(histories)) == len(histories), "duplicate raw history")
    subset(selected, context.n)
    return tuple(support(spec, *history) for history in histories)


def restricted_context(spec, enabled, context, histories, selected):
    allowed = permissions(spec, enabled)
    runs = data(spec, context, histories, selected)
    chosen = set(selected)
    admitted = tuple(context.admitted[i] and i in chosen and runs[i] is not None
                     and set(runs[i][1]) <= allowed for i in range(context.n))
    return Context(context.n, context.m, admitted, context.defined,
                   context.values, context.order)


def target_witnesses(spec, context, histories, selected, target):
    runs = data(spec, context, histories, selected)
    subset(target, context.m)
    return tuple(sorted((i, runs[i][1]) for i in selected
                        if runs[i] is not None and context.admitted[i]
                        and context.defined[i] and context.values[i] in target))


def attained(context):
    checked(context)
    return tuple(sorted({context.values[i] for i in range(context.n)
                         if context.admitted[i] and context.defined[i]}))
