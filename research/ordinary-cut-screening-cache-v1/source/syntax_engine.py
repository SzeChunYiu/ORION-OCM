"""Lark Earley adapter: syntax witnesses only, never native theorem acceptance."""
import time
from lark import Lark, Tree
from lark.exceptions import LarkError, UnexpectedInput
from contract_grammar import TYPES, compile_grammar
from proof_replay import replay


class SyntaxUnknown(RuntimeError):
    """Must never be swallowed as an ordinary negative ValueError type match."""


class SyntaxEngine:
    def __init__(self, contracts, parameters):
        started = time.perf_counter()
        try:
            self.compiled = compile_grammar(contracts, parameters)
            self.parser = Lark(self.compiled["text"], parser="earley", lexer="basic",
                               ambiguity="resolve", start=["n_" + k for k in self.compiled["productive"]])
        except (LarkError, ValueError, KeyError, TypeError, RecursionError, MemoryError) as error:
            raise SyntaxUnknown("grammar construction: " + str(error)) from error
        self.compile_wall_s = time.perf_counter() - started
        self.work = {"grammar_contracts_read": len(contracts),
                     "syntax_contracts": self.compiled["syntax_contracts"],
                     "compiled_syntax_contracts": self.compiled["compiled_syntax_contracts"],
                     "parse_calls": 0, "input_tokens": 0, "emitted_proof_labels": 0}

    def prove(self, wanted, tokens, checkpoint=None):
        started = time.perf_counter()
        result = {"native_acceptance": False,
                  "grammar_coverage_complete": not self.compiled["unsupported"],
                  "coverage_complete": False,
                  "unsupported_contracts": self.compiled["unsupported"], "proof": None}
        def tick():
            if checkpoint is not None:
                checkpoint()
        try:
            tick()
            if wanted not in TYPES or type(tokens) is not list or not tokens or len(tokens) > 512 or any(type(t) is not str for t in tokens):
                raise SyntaxUnknown("input outside registered type/token boundary")
            if wanted not in self.compiled["productive"] or any(t not in self.compiled["tokens"] for t in tokens):
                raise UnexpectedInput()
            self.work["parse_calls"] += 1
            self.work["input_tokens"] += len(tokens)
            text = " ".join(self.compiled["tokens"][t] for t in tokens)
            tree = self.parser.parse(text, start="n_" + wanted)
            tick()
            todo, active, proofs = [(tree, False)], set(), {}
            while todo:
                tick()
                node, finishing = todo.pop()
                key = id(node)
                if key in proofs:
                    continue
                if not isinstance(node, Tree):
                    raise SyntaxUnknown("unexpected retained parser terminal")
                if not finishing:
                    if key in active:
                        raise SyntaxUnknown("cyclic selected syntax derivation")
                    active.add(key)
                    todo.append((node, True))
                    todo.extend((child, False) for child in reversed(node.children))
                    continue
                name = str(node.data)
                if name.startswith("n_"):
                    if len(node.children) != 1:
                        raise SyntaxUnknown("type wrapper arity")
                    proof = proofs[id(node.children[0])]
                else:
                    rule = self.compiled["rules"][name]
                    if "float" in rule:
                        proof = [rule["float"]]
                    else:
                        proof = [label for i in rule["emit_order"]
                                 for label in proofs[id(node.children[i])]] + [rule["label"]]
                if len(proof) > 4096:
                    raise SyntaxUnknown("syntax proof label bound")
                proofs[key] = proof
                active.remove(key)
            proof = proofs[id(tree)]
            replay(proof, wanted, tokens, self.compiled)
            self.work["emitted_proof_labels"] += len(proof)
            result.update(status="SYNTAX_PROVED", proof=proof, structural_replay=True)
        except UnexpectedInput:
            result.update(status="NOT_DERIVABLE_REGISTERED_GRAMMAR" if result["grammar_coverage_complete"] else "UNKNOWN",
                          reason="No derivation in compiled grammar")
        except (SyntaxUnknown, LarkError, ValueError, KeyError, TypeError, IndexError, RecursionError, MemoryError) as error:
            result.update(status="UNKNOWN", reason=type(error).__name__ + ": " + str(error))
        result["coverage_complete"] = result["grammar_coverage_complete"] and result["status"] in {
            "SYNTAX_PROVED", "NOT_DERIVABLE_REGISTERED_GRAMMAR"}
        result["parse_emit_wall_s"] = time.perf_counter() - started
        return result

    def checker(self, wanted, tokens, checkpoint=None):
        result = self.prove(wanted, tokens, checkpoint)
        if result["status"] == "SYNTAX_PROVED":
            return True
        if result["status"] == "NOT_DERIVABLE_REGISTERED_GRAMMAR":
            raise ValueError("not a member of registered syntax grammar")
        raise SyntaxUnknown(result.get("reason", "incomplete syntax qualification"))
