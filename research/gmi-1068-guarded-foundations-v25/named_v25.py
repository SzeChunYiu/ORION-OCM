"""Fixed external object names require their actual identity encoder."""
from dataclasses import dataclass
from core_v25 import index, need, old_partial
from information_v25 import _fibers, _inputs
from presentations_v25 import Presented, checked, guarded_word, padded, raw_eval
from syntax_v25 import _map, validate_tree


@dataclass(frozen=True)
class NamedPresented:
    model: Presented
    identities: tuple

    def __post_init__(self):
        checked(self.model)
        need(type(self.identities) is tuple, "named identity tuple")
        for value in self.identities:
            index(value, self.model.ambient_size)
        expected = {self.model.labels[i] for i in old_partial.units(self.model.table)}
        need(len(set(self.identities)) == len(self.identities)
             and set(self.identities) == expected, "bijection onto all true units")


def checked_named(named):
    need(type(named) is NamedPresented, "expected NamedPresented")
    return named


def _raw_tree(named, tree):
    checked_named(named)
    n = named.model.ambient_size
    validate_tree(tree, n, len(named.identities))
    return _map(tree, named.identities, tuple(range(n)))


def named_eval(named, tree):
    translated = _raw_tree(named, tree)
    return raw_eval(named.model, translated)


def named_word(named, tree):
    translated = _raw_tree(named, tree)
    return guarded_word(named.model, translated)


def named_signature(named):
    checked_named(named)
    return padded(named.model).rows, named.identities


def named_recoverable(models, codes):
    _inputs(models, codes, checked_named)
    need(not models or all(
        (m.model.ambient_size, len(m.identities)) ==
        (models[0].model.ambient_size, len(models[0].identities)) for m in models),
        "common named query interface required")
    return _fibers(models, codes, named_signature)
