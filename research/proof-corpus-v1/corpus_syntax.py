"""Evaluator-only lexical records; context may contain helper proof text.

No record produced here is a sanitized solver view or an elaborated declaration.
"""
import re
import unicodedata
from corpus_contract import CorpusError, key_identity, sha256
from corpus_lex import active_imports, mask_comments_and_strings

DECLARATION = re.compile(
    r"(?m)^[ \t]*(?:(?:private|protected|noncomputable)\s+)*"
    r"(?:theorem|lemma)\s+(?P<name>[A-Za-z_][A-Za-z0-9_'.]*)\b")
BRIDGE = re.compile(r":=\s*by\s+p2m_exact_reverting\b")
COMMAND = re.compile(
    r"@\[|"
    r"(?:def|abbrev|opaque|instance|example|axiom|constant|structure|class|inductive|"
    r"mutual|syntax|macro|elab|namespace|section|end|open|variable|universe|"
    r"set_option|attribute|include|omit|export|theorem|lemma)")


def identifier_character(char):
    # Lexical boundary support only, not a complete Lean identifier parser.
    return char in "_.'’′″‴⁗" or char.isalnum() or unicodedata.category(char).startswith("M")


def has_intervening_command(text, start, end):
    for match in COMMAND.finditer(text, start, end):
        left = match.start() == 0 or not identifier_character(text[match.start() - 1])
        right = match.end() == len(text) or not identifier_character(text[match.end()])
        if left and right:
            return True
    return False



def extract_wrapper(text, key):
    key_identity(key)
    masked = mask_comments_and_strings(text)
    imports = active_imports(text)
    expected = "P2M.Sol.S_" + key
    if expected not in imports:
        raise CorpusError("PAIR_IMPORT", expected)
    markers = list(BRIDGE.finditer(masked))
    if len(markers) != 1:
        raise CorpusError("BRIDGE_COUNT", str(len(markers)))
    marker = markers[0]
    declarations = list(DECLARATION.finditer(masked, 0, marker.start()))
    if not declarations:
        raise CorpusError("DECLARATION_LAYOUT", "no preceding target declaration")
    declaration = declarations[-1]
    if has_intervening_command(masked, declaration.end(), marker.start()):
        raise CorpusError("DECLARATION_ASSOCIATION", "intervening command")
    reference = re.match(
        r"\s+@?(?:_root_\.)?P2MW\.S_" + re.escape(key) +
        r"\.solution(?![A-Za-z0-9_'.])", masked[marker.end():])
    if reference is None:
        raise CorpusError("BRIDGE_TARGET", "expected exactly " + expected + ".solution")
    end = marker.end() + reference.end()
    # The bridge is the entire tactic expression. Closing scopes and the known
    # unevaluated type-warning directive may follow; neither grants authority.
    tail = masked[end:]
    if tail.split("\n", 1)[0].strip():
        raise CorpusError("BRIDGE_TAIL", "extra proof arguments")
    directives = []
    name = r"[^\W\d][\w'.′″‴⁗]*"
    warning = r"\s*#p2m_type_eq_warn\s+" + name + r"\s+" + name + r"\s*"
    for line in tail.splitlines():
        if re.fullmatch(warning, line):
            directives.append("UNEVALUATED_P2M_TYPE_EQ_WARN")
        elif line.strip() and not re.fullmatch(r"\s*end(?:\s+[A-Za-z_][A-Za-z0-9_'.]*)?\s*", line):
            raise CorpusError("BRIDGE_TAIL", "unsupported trailing command/tactic")
    context = text[:declaration.start()]
    statement = text[declaration.start():marker.start()]
    bridge = text[marker.start():end]
    trailing = text[end:]
    return {
        "theorem_id": "Theorems.Thm_" + key,
        "theorem_name": declaration["name"],
        "expected_solution": expected,
        "imports": list(imports),
        "context_source": context,
        "declaration_source": statement,
        "bridge_source": bridge,
        "trailing_source": trailing,
        "trailing_directives": directives,
        "context_sha256": sha256(context.encode()),
        "declaration_sha256": sha256(statement.encode()),
        "bridge_sha256": sha256(bridge.encode()),
        "trailing_sha256": sha256(trailing.encode()),
        "wrapper_sha256": sha256(text.encode()),
        "wrapper_bytes": len(text.encode()),
        "lexical_only": True,
        "semantic_correspondence": "NOT_ELABORATED",
    }


def extract_solution(text, key):
    key_identity(key)
    return {"solution_id": "P2M.Sol.S_" + key,
            "imports": list(active_imports(text)),
            "solution_sha256": sha256(text.encode()),
            "solution_bytes": len(text.encode())}
