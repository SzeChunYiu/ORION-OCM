"""Position-preserving lexical inventory, adapted from pinned PR #129.

Recognizes nested comments and strings. This is not Lean parsing/elaboration.
"""
import re
from corpus_contract import CorpusError


def mask_comments_and_strings(text):
    out = list(text)
    i, nesting, string, escaped = 0, 0, False, False
    quoted_identifier = False
    while i < len(text):
        if quoted_identifier:
            if text[i] != "\n":
                out[i] = " "
            if text[i] == "»":
                quoted_identifier = False
            i += 1
            continue
        if nesting:
            if text.startswith("/-", i):
                out[i:i + 2] = "  "
                nesting += 1
                i += 2
                continue
            if text.startswith("-/", i):
                out[i:i + 2] = "  "
                nesting -= 1
                i += 2
                continue
            if text[i] != "\n":
                out[i] = " "
            i += 1
            continue
        if string:
            char = text[i]
            if char != "\n":
                out[i] = " "
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                string = False
            i += 1
            continue
        if text.startswith("/-", i):
            out[i:i + 2] = "  "
            nesting = 1
            i += 2
        elif text.startswith("--", i):
            end = text.find("\n", i)
            end = len(text) if end < 0 else end
            out[i:end] = " " * (end - i)
            i = end
        elif text[i] == "«":
            out[i] = "«"  # Nonidentifier occupancy marker; contents are masked.
            quoted_identifier = True
            i += 1
        elif text[i] == '"':
            out[i] = '"'  # Do not erase an extra literal argument as whitespace.
            string = True
            i += 1
        else:
            i += 1
    if nesting or string or quoted_identifier:
        raise CorpusError("LEXICAL_LAYOUT", "unterminated comment/string/escaped identifier")
    return "".join(out)


def active_imports(text):
    """Return lexical import commands, retaining order and duplicates."""
    masked = mask_comments_and_strings(text)
    imports = []
    for line in masked.splitlines():
        if not re.match(r"^\s*import\b", line):
            continue
        match = re.fullmatch(r"\s*import\s+(.+?)\s*", line)
        if match is None:
            raise CorpusError("IMPORT_LAYOUT", "empty/unsupported import")
        tokens = match[1].split()
        if not tokens:
            raise CorpusError("IMPORT_LAYOUT", "empty import")
        for token in tokens:
            if not re.fullmatch(r"[A-Za-z0-9_'.]+", token):
                raise CorpusError("IMPORT_LAYOUT", token)
            imports.append(token)
    return tuple(imports)
