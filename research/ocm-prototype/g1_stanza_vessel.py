"""A donor catalogue adapter into unchanged SV.solve and G1 checked admission."""
from dataclasses import replace
from pathlib import Path
import g1_vessel as G
from g1_field import MODEL, payload
import g1_stanza_donor as D
import g1_stanza_profile as P
from g1_stanza_field import setup


def catalogue(runtime, query_id, request, checks, fault=None):
    specs = list(G.catalogue(runtime, query_id, request, checks, fault,
                             syntax_operator_id=D.SYNTAX_OPERATOR))
    def backend(ks, name, context):
        if request["kind"] != "syntax":
            return {"status": "NOT_APPLICABLE"}
        profile = payload(ks, MODEL)["stanza_profile"]
        return D.predict(request["tokens"], P.archive_path(runtime.root, profile), profile)
    specs[0] = replace(specs[0], backend=backend)
    return tuple(specs)


def query(runtime, request, fault=None):
    return G.query(runtime, request, fault, catalogue_builder=catalogue,
                   syntax_operator_id=D.SYNTAX_OPERATOR)


def worker(root, command):
    runtime = G.OCMRuntime(Path(root), config=G.CONFIG)
    if command["action"] == "setup":
        return setup(runtime, Path(command["model"]), command["donor_profile"])
    if command["action"] == "query":
        return query(runtime, command["request"], command.get("fault"))
    return G.worker(root, command)
