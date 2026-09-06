"""Gold-free output admission; ADOPT the official CoNLL18 structural loader."""
import io
import re
from vendor import conll18_ud_eval as official

UPOS = frozenset("ADJ ADP ADV AUX CCONJ DET INTJ NOUN NUM PART PRON PROPN PUNCT SCONJ SYM VERB X".split())


def validate_tokens(tokens):
    if not isinstance(tokens, list) or not tokens:
        raise ValueError("nonempty list of supplied integer-token forms required")
    if any(not isinstance(s, str) or not s or any(c in s for c in "\t\r\n") for s in tokens):
        raise ValueError("invalid supplied token form")


def validate(words, tokens):
    """Return a structural diagnostic, never a gold-correctness certificate."""
    try:
        validate_tokens(tokens)
        if not isinstance(words, list) or len(words) != len(tokens):
            return "WORD_COUNT_MISMATCH"
        lines = []
        for index, (word, form) in enumerate(zip(words, tokens), 1):
            if not isinstance(word, dict) or set(word) != {"id", "form", "head", "deprel", "upos"}:
                return "WORD_SCHEMA"
            if type(word["id"]) is not int or word["id"] != index or word["form"] != form:
                return "TOKEN_BINDING"
            if type(word["head"]) is not int or not 0 <= word["head"] <= len(tokens):
                return "HEAD_RANGE"
            if not isinstance(word["upos"], str) or word["upos"] not in UPOS:
                return "UPOS_TYPE"
            label = word["deprel"]
            if not isinstance(label, str) or re.fullmatch(r"[a-z]+(?::[a-z_]+)?", label) is None:
                return "LABEL_SHAPE"
            if (word["head"] == 0) != (label == "root"):
                return "ROOT_LABEL"
            lines.append("\t".join([str(index), form, "_", word["upos"], "_", "_",
                                    str(word["head"]), label, "_", "_"]))
        official.load_conllu(io.StringIO("\n".join(lines) + "\n\n"))
    except (ValueError, TypeError, official.UDError, RecursionError) as exc:
        return "INVALID_TREE:" + str(exc)
    return None
