"""Independent products intersect domains; shared products retain supplied E."""
from itertools import product
from core_v17 import Context, checked, flags


def family(contexts):
    if type(contexts) is not tuple:
        raise ValueError("canonical tuple of contexts required")
    for context in contexts:
        checked(context)
    return contexts


def product_labels(contexts):
    family(contexts)
    return tuple(product(*(range(context.m) for context in contexts)))


def projection_index(contexts, product_code, component):
    labels = product_labels(contexts)
    if (type(product_code) is not int or not 0 <= product_code < len(labels)
            or type(component) is not int or not 0 <= component < len(contexts)):
        raise ValueError("projection outside declared product")
    return labels[product_code][component]


def common_admission(contexts, admitted):
    family(contexts)
    flags(admitted)
    if any(c.n != len(admitted) or c.admitted != admitted for c in contexts):
        raise ValueError("products require one common history/admission domain")


def build(contexts, admitted, defined):
    common_admission(contexts, admitted)
    flags(defined)
    if len(defined) != len(admitted):
        raise ValueError("definedness dimension mismatch")
    labels = product_labels(contexts)
    relation = tuple(tuple(all(c.order[a[i]][b[i]] for i, c in enumerate(contexts))
                           for b in labels) for a in labels)
    values = []
    for h, present in enumerate(defined):
        if not present:
            values.append(None)
            continue
        code = 0
        for context in contexts:
            if not context.defined[h]:
                raise ValueError("missing component cannot become a product value")
            code = code * context.m + context.values[h]
        values.append(code)
    return Context(len(admitted), len(labels), admitted, defined, tuple(values), relation)


def independent_product(contexts, admitted):
    common_admission(contexts, admitted)
    defined = tuple(all(c.defined[h] for c in contexts) for h in range(len(admitted)))
    return build(contexts, admitted, defined)


def shared_product(contexts, admitted, defined):
    common_admission(contexts, admitted)
    flags(defined)
    if any(c.defined != defined for c in contexts):
        raise ValueError("shared-domain product requires identical evaluator domains")
    return build(contexts, admitted, defined)
