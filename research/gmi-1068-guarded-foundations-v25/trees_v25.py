"""Actual typed construction and a separate weakened-law raw interpreter."""
from core_v25 import Table, Typed, need, old_categories, old_partial
from syntax_v25 import leaves, validate_tree


def checked_category(cat):
    need(type(cat) is Typed, "expected actual V19 Typed")
    old_categories.validate_category(cat)
    return cat


def typed_eval(cat, tree):
    checked_category(cat)
    validate_tree(tree, len(cat.table.rows), cat.object_count)

    def visit(node):
        if node[0] != "seq":
            arrow = node[1] if node[0] == "arrow" else cat.identities[node[1]]
            return (cat.source[arrow], cat.target[arrow], arrow)
        left, right = visit(node[1]), visit(node[2])
        if left is None or right is None:
            return None
        return old_categories.bundled_product(cat, left, right)
    return visit(tree)


def encode_typed(cat, tree):
    checked_category(cat)
    validate_tree(tree, len(cat.table.rows), cat.object_count)
    return tuple(leaf[1] if leaf[0] == "arrow" else cat.identities[leaf[1]]
                 for leaf in leaves(tree))


def typed_word(cat, tree):
    encoded = encode_typed(cat, tree)
    value = old_partial.word(old_categories.flatten(cat), encoded)
    return None if value is None else (cat.source[value], cat.target[value], value)


def _raw_checked(table, tree):
    need(type(table) is Table, "expected actual V19 Table")
    validate_tree(tree, len(table.rows), len(table.rows))


def raw_table_eval(table, tree):
    _raw_checked(table, tree)
    units = set(old_partial.units(table))

    def visit(node):
        if node[0] == "arrow":
            return node[1]
        if node[0] == "empty":
            return node[1] if node[1] in units else None
        left, right = visit(node[1]), visit(node[2])
        return None if left is None or right is None else table.rows[left][right]
    return visit(tree)


def raw_table_encoding(table, tree):
    _raw_checked(table, tree)
    units = set(old_partial.units(table))
    ls = leaves(tree)
    return tuple(leaf[1] for leaf in ls), all(
        leaf[0] == "arrow" or leaf[1] in units for leaf in ls)


def raw_table_word(table, tree):
    word, guard = raw_table_encoding(table, tree)
    return old_partial.word(table, word) if guard else None
