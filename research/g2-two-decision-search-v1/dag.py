"""Non-neural REFACTOR consumer: match a 2-step DAG as a proof subtree.

ADOPT: Zhou et al. ICLR 2024, App. A.3 RefactorSubroutine — compare proof
steps of an extracted theorem against a subtree, then replace. REJECT their
neural extractor (no-neural contract).

A 1-step identity of the later conclusion with the lemma is recorded, then
excluded from consumption. Consumption is a *proper* subtree hit.
"""


class Node:
    def __init__(self, label, children, kind, n_floating=0):
        self.label = label
        self.children = list(children)
        self.kind = kind
        self.n_floating = n_floating
        self._steps = None
        self._spine = None

    def steps(self):
        if self._steps is None:
            out = []
            for child in self.children:
                out.extend(child.steps())
            if self.kind in ("$a", "$p"):
                out.append(self.label)
            self._steps = out
        return self._steps

    def semantic_spine(self):
        if self._spine is None:
            out = []
            for child in self.children:
                out.extend(child.semantic_spine())
            if self.kind == "$p":
                out.append(self.label)
            self._spine = out
        return self._spine

    def essential_children(self):
        return self.children[self.n_floating:]

    def walk(self, seen=None):
        if seen is None:
            seen = set()
        ident = id(self)
        if ident in seen:
            return
        seen.add(ident)
        yield self
        for child in self.children:
            yield from child.walk(seen)


def lemma_steps(proof, skip_prefixes=("cut-f", "cut-h")):
    return [lab for lab in proof if not any(lab.startswith(p) for p in skip_prefixes)]


def match_getsteps(root, wanted_steps):
    hits = []
    for node in root.walk():
        if node.kind != "$p":
            continue
        if node.steps() == wanted_steps:
            hits.append({
                "label": node.label,
                "kind": "getsteps",
                "proper_subtree": node is not root,
            })
    return hits


def match_semantic_spine(root, wanted_spine):
    """Parent-child 2-step DAG: last label's essential child is the first label."""
    if len(wanted_spine) != 2:
        raise ValueError("2-step DAG")
    first, last = wanted_spine
    hits = []
    for node in root.walk():
        if node.label != last or node.kind != "$p":
            continue
        for child in node.essential_children():
            if child.label == first and child.kind == "$p":
                hits.append({
                    "label": node.label,
                    "kind": "semantic_spine",
                    "proper_subtree": node is not root,
                    "child": first,
                })
                break
    return hits


def save_value(n_heldout_proper, semantic_size=2):
    """Wernhard DAG save-value on the held-out forest: (n-1)*(s-1)."""
    n = int(n_heldout_proper)
    s = int(semantic_size)
    value = max(0, n - 1) * max(0, s - 1)
    if n <= 0:
        terminal = "NO_RECURRENCE"
    elif n == 1:
        terminal = "SINGLE_HELD_OUT_USE"
    else:
        terminal = "RECURRENCE"
    return {
        "n_heldout_proper": n,
        "semantic_size": s,
        "save_value": value,
        "terminal": terminal,
    }


def tree_from_rpn(rpn, arities, kinds, floating_counts=None, saved=None):
    floating_counts = floating_counts or {}
    stack = []
    saved = [] if saved is None else saved
    for lab in rpn:
        if lab == "Z":
            saved.append(stack[-1])
            continue
        if isinstance(lab, int):
            stack.append(saved[lab])
            continue
        n = arities.get(lab, 0)
        if n > len(stack):
            raise ValueError("stack underflow: " + lab)
        children = stack[len(stack) - n:] if n else []
        if n:
            del stack[len(stack) - n:]
        stack.append(Node(lab, children, kinds.get(lab, "$p"),
                          n_floating=floating_counts.get(lab, 0)))
    if not stack:
        raise ValueError("empty proof tree")
    return stack[-1]


def expand_compressed(proof, f_labels, e_labels, arities, kinds, floating_counts):
    """mmverify compressed integers → RPN of labels, with Z as DAG sharing."""
    idx_bloc = proof.index(")")
    plabels = list(f_labels) + list(e_labels) + list(proof[1:idx_bloc])
    compressed = "".join(proof[idx_bloc + 1:])
    proof_ints = []
    cur = 0
    for ch in compressed:
        if ch == "Z":
            proof_ints.append(-1)
        elif "A" <= ch <= "T":
            proof_ints.append(20 * cur + ord(ch) - 65)
            cur = 0
        else:
            cur = 5 * cur + ord(ch) - 84
    rpn = []
    n_saved = 0
    label_end = len(plabels)
    for n in proof_ints:
        if n == -1:
            rpn.append("Z")
            n_saved += 1
        elif n < label_end:
            rpn.append(plabels[n] or "")
        else:
            rpn.append(n - label_end)
    return tree_from_rpn(rpn, arities, kinds, floating_counts)
