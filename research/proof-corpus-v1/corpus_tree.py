"""Walk selected paths through independently hashed tree payloads."""
from corpus_contract import CorpusError, ROOTS


def binary_entries(raw):
    rows, offset, names = [], 0, set()
    while offset < len(raw):
        space, zero = raw.find(b" ", offset), raw.find(b"\0", offset)
        if space < offset or zero < space or zero + 21 > len(raw):
            raise CorpusError("SOURCE_TREE", "binary framing")
        try:
            mode = raw[offset:space].decode("ascii")
            name = raw[space + 1:zero].decode("utf-8")
        except UnicodeError as exc:
            raise CorpusError("SOURCE_TREE", "entry encoding") from exc
        if (not name or name in (".", "..") or "/" in name or "\\" in name or
                name in names or any(ord(c) < 32 for c in name)):
            raise CorpusError("SOURCE_PATH", name)
        names.add(name)
        rows.append({"name": name, "mode": mode, "oid": raw[zero + 1:zero + 21].hex()})
        offset = zero + 21
    return rows


def selected_entries(root_oid, read_verified_tree):
    rows = []

    def descend(row, path, ancestors):
        if row["mode"] in ("40000", "040000"):
            if row["oid"] in ancestors:
                raise CorpusError("SOURCE_TREE", "cyclic tree path")
            raw = read_verified_tree(row["oid"])
            for child in binary_entries(raw):
                descend(child, path + "/" + child["name"], ancestors | {row["oid"]})
        elif row["mode"] == "100644":
            rows.append({"path": path, "mode": row["mode"], "oid": row["oid"]})
        else:
            raise CorpusError("SOURCE_MODE", path)

    for row in binary_entries(read_verified_tree(root_oid)):
        if row["name"] in ROOTS:
            descend(row, row["name"], {root_oid})
    return sorted(rows, key=lambda row: row["path"])
