"""Whole structural validation precedes semantic failure."""
from core_v25 import index, nat, need, permutation


def validate_tree(tree, arrow_size, empty_size):
    nat(arrow_size)
    nat(empty_size)

    def visit(node):
        need(type(node) is tuple and bool(node), "tree must be a nonempty tuple")
        need(type(node[0]) is str, "tree opcode")
        tag = node[0]
        if tag in ("arrow", "empty"):
            need(len(node) == 2, "leaf arity")
            index(node[1], arrow_size if tag == "arrow" else empty_size)
        elif tag == "seq":
            need(len(node) == 3, "sequence arity")
            visit(node[1])
            visit(node[2])
        else:
            raise ValueError("unknown tree opcode")
    visit(tree)


def _map(tree, object_map, arrow_map):
    tag = tree[0]
    if tag == "seq":
        return ("seq", _map(tree[1], object_map, arrow_map),
                _map(tree[2], object_map, arrow_map))
    return (tag, (arrow_map if tag == "arrow" else object_map)[tree[1]])


def map_tree(tree, object_map, arrow_map):
    need(type(object_map) is tuple and type(arrow_map) is tuple, "map tuples")
    permutation(object_map, len(object_map))
    permutation(arrow_map, len(arrow_map))
    validate_tree(tree, len(arrow_map), len(object_map))
    return _map(tree, object_map, arrow_map)


def leaves(tree):
    """Internal traversal: callers first validate the complete tree."""
    if tree[0] == "seq":
        return leaves(tree[1]) + leaves(tree[2])
    return (tree,)
