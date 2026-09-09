"""Provenance observer around an unchanged, hash-pinned mmverify.MM."""
import copy

def native_value(row):
    if row["kind"] in {"$f", "$e"}: return row["statement"]
    return (set(map(tuple, row["dv"])),
            [tuple(h["statement"]) for h in row["floating"]],
            [h["statement"] for h in row["essential"]], row["statement"])

def operations(row):
    proof = row["proof"]
    if proof[0] != "(":
        return [{"label": label} for label in proof]
    close = proof.index(")")
    labels = [h["label"] for h in row["floating"] + row["essential"]] + proof[1:close]
    out, value = [], 0
    for ch in "".join(proof[close + 1:]):
        if ch == "Z":
            if value: raise ValueError("unfinished compressed number")
            out.append({"save": True})
        elif "U" <= ch <= "Y": value = 5 * value + ord(ch) - 84
        elif "A" <= ch <= "T":
            number = 20 * value + ord(ch) - 65
            value = 0
            out.append({"label": labels[number]} if number < len(labels)
                       else {"reuse": number - len(labels)})
        else: raise ValueError("unsupported compressed character")
    if value: raise ValueError("unfinished compressed number")
    return out

def traced_class(native, source):
    class Labels(dict):
        def __setitem__(self, label, step):
            row = source[label]
            if step != (row["kind"], native_value(row)):
                raise ValueError("native/source contract mismatch: " + label)
            super().__setitem__(label, step)

    class TracedMM(native.MM):
        def __init__(self, selected, stop):
            super().__init__(None, stop)
            self.labels, self.selected = Labels(), set(selected)
            self.verified, self.traces, self.active = [], {}, None

        def read_p_stmt(self, toks):
            self.pending = toks.recent[-2]
            result = super().read_p_stmt(toks)
            row = source[self.pending]
            if result != (row["statement"], row["proof"]):
                raise ValueError("native/source statement/proof mismatch")
            return result

        def verify(self, f_hyps, e_hyps, conclusion, proof):
            label = self.pending
            row = source[label]
            if label in self.selected:
                variables = sorted(set().union(*(fr.v for fr in self.fs)))
                dvs = sorted([list(p) for p in set().union(*(fr.d for fr in self.fs))])
                if variables != row["active_variables"] or dvs != row["active_dv"]:
                    raise ValueError("native/source active scope mismatch")
                self.active = {"ops": operations(row), "position": 0, "stack": [],
                               "saved": [], "nodes": [], "events": []}
            try:
                super().verify(f_hyps, e_hyps, conclusion, proof)
                if self.active is not None:
                    self.saves()
                    a = self.active
                    if a["position"] != len(a["ops"]) or len(a["stack"]) != 1:
                        raise ValueError("trace schedule/final stack mismatch")
                    self.traces[label] = {"label": label, "terminal": "NATIVE_VERIFIED",
                        "source": copy.deepcopy(row), "nodes": a["nodes"],
                        "events": a["events"], "root": a["stack"][0],
                        "external_logical_hypotheses": copy.deepcopy(row["essential"])}
                self.verified.append(label)
            finally:
                self.active = None

        def saves(self):
            a = self.active
            while a["position"] < len(a["ops"]) and "save" in a["ops"][a["position"]]:
                node = a["stack"][-1]
                a["events"].append({"kind": "save", "slot": len(a["saved"]), "node": node})
                a["saved"].append(node)
                a["position"] += 1

        def treat_step(self, step, stack):
            if self.active is None: return super().treat_step(step, stack)
            a = self.active
            self.saves()
            op = a["ops"][a["position"]]
            a["position"] += 1
            if [a["nodes"][i]["output"] for i in a["stack"]] != stack:
                raise ValueError("native/provenance input stack mismatch")
            before = copy.deepcopy(stack)
            if "label" in op:
                label = op["label"]
                if step is not self.labels[label]: raise ValueError("native label mismatch")
                row = source[label]
                n = 0 if row["kind"] in {"$f", "$e"} else len(row["floating"] + row["essential"])
            else:
                label, n = None, 0
                saved = a["saved"][op["reuse"]]
                if step != ("$a", (set(), [], [], a["nodes"][saved]["output"])):
                    raise ValueError("native saved-reference mismatch")
            super().treat_step(step, stack)  # validity remains the native verifier's decision
            inputs = a["stack"][-n:] if n else []
            node = {"id": len(a["nodes"]), "output": copy.deepcopy(stack[-1]), "inputs": inputs}
            if label is None:
                node.update(kind="saved_reference", slot=op["reuse"], saved_node=saved)
            elif row["kind"] in {"$f", "$e"}:
                node.update(kind="floating_hypothesis" if row["kind"] == "$f" else "essential_hypothesis",
                            label=label)
            else:
                nf = len(row["floating"])
                subst = {h["statement"][1]: before[len(before)-n+i][1:]
                         for i, h in enumerate(row["floating"])}
                obligations = []
                for i, hyp in enumerate(row["floating"] + row["essential"]):
                    expected = ([hyp["statement"][0]] + subst[hyp["statement"][1]]
                                if i < nf else native.apply_subst(hyp["statement"], subst))
                    obligations.append({"kind": "floating" if i < nf else "essential",
                        "hypothesis": hyp["label"], "from": inputs[i], "expected": expected})
                dv = []
                for x, y in row["dv"]:
                    pairs = sorted([list(sorted((u, v))) for u in self.fs.find_vars(subst[x])
                                    for v in self.fs.find_vars(subst[y])])
                    dv.append({"variables": [x, y], "required_active_pairs": pairs})
                node.update(kind="semantic_application" if row["statement"][0] == "|-" else "syntax_application",
                            label=label, assertion_kind=row["kind"], substitution=subst,
                            obligations=obligations, distinct_variable_obligations=dv)
            if n: del a["stack"][-n:]
            a["stack"].append(node["id"])
            a["nodes"].append(node)
            a["events"].append({"kind": "step", "node": node["id"]})
            if [a["nodes"][i]["output"] for i in a["stack"]] != stack:
                raise ValueError("native/provenance output stack mismatch")
    return TracedMM
