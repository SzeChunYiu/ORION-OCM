"""A common raw query interface retains failures and anchored empty histories."""
from dataclasses import dataclass
from partial_v19 import empty, need, word


@dataclass(frozen=True)
class Query:
    kind: str
    payload: object

    def __post_init__(self):
        need(type(self.kind) is str and self.kind in ("word", "empty"), "query kind")
        if self.kind == "word":
            need(type(self.payload) is tuple and bool(self.payload), "nonempty word")
            need(all(type(x) is int and x >= 0 for x in self.payload), "word indices")
        else:
            need(type(self.payload) is int and self.payload >= 0, "empty anchor")


def observe(table, query):
    need(type(query) is Query, "expected Query")
    return word(table, query.payload) if query.kind == "word" else empty(table, query.payload)
