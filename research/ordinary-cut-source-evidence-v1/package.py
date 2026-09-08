from pathlib import Path
import hashlib, json, re, time, zipfile

SOURCE = Path("/home/billy/orion-director-work/20260908/ordinary-cut-opportunity-v1")
OUT = Path(__file__).resolve().parent
EXTERNAL = Path("/home/billy/orion-director-work/20260908/metamath-curriculum-feasibility-v1")
START = time.time()
def ident(data):
    return {"bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}
def write_json(name, data):
    p = OUT / name
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("x") as f:
        f.write(json.dumps(data, sort_keys=True, indent=2, allow_nan=False) + "\n")
def inventory():
    rows = {}
    for p in sorted(SOURCE.rglob("*")):
        if p.is_symlink():
            raise ValueError("Symlink requires an explicit archive contract: " + str(p))
        rel = p.relative_to(SOURCE).as_posix()
        rows[rel] = {"kind": "directory"} if p.is_dir() else {"kind": "file", **ident(p.read_bytes())}
    return rows
def omitted(rel):
    p = Path(rel)
    if p.name == "CUSTODIAN-PREFIX.mm":
        return "Full corpus prefix excluded from redistribution."
    if "__pycache__" in p.parts or p.suffix in {".pyc", ".pyo"}:
        return "Python cache excluded."
    return None
before = inventory()
write_json("SOURCE-INVENTORY.json", {"source_root": str(SOURCE), "entries": before})
selected = {k:v for k,v in before.items() if omitted(k) is None}
omissions = [{"relative_path": k, "source": str(SOURCE/k), "reason": omitted(k), **v}
             for k,v in before.items() if omitted(k) is not None]
members = {}
with zipfile.ZipFile(OUT/"HISTORICAL-RAW.zip", "x", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as z:
    for rel, row in selected.items():
        name = rel + "/" if row["kind"] == "directory" else rel
        data = b"" if row["kind"] == "directory" else (SOURCE/rel).read_bytes()
        if row["kind"] == "file":
            assert ident(data) == {k:row[k] for k in ["bytes","sha256"]}
        info = zipfile.ZipInfo(name, (2026, 9, 8, 0, 0, 0))
        info.compress_type = zipfile.ZIP_DEFLATED
        info.external_attr = (0o40755 if row["kind"] == "directory" else 0o100644) << 16
        z.writestr(info, data, compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)
        members[name] = {"source": str(SOURCE/rel), "kind": row["kind"], "zip_payload": ident(data)}
write_json("ARCHIVE-MEMBERS.json", {"schema":"ordinary.publication-archive-members.v1",
    "archive": ident((OUT/"HISTORICAL-RAW.zip").read_bytes()), "members": members})
write_json("OMISSIONS.json", {"schema":"ordinary.publication-omissions.v1", "omitted_entries": omissions,
    "policy":"Only full CUSTODIAN-PREFIX.mm and Python cache paths are omitted from the source-root archive."})
direct = {k for k,v in selected.items() if v["kind"]=="file" and
          (k.startswith("consumer-v3/") or k.startswith("allocation-audit/"))}
release_names = [
    "release_training.py","registry_scope.py","donor/trace_source.py","donor/trace_adapter.py",
    "REGISTRY-SCOPE.json","REGISTRY-SCOPE-REQUEST.json","RELEASE-REQUEST.json",
    "RELEASE-SOURCE-FREEZE-03.json","RELEASE-SOURCE-REVIEW-03.json",
    "ROOT-RELEASE-SOURCE-ACCEPTANCE-03.json","ROOT-RELEASE-GATE.json",
    "ROOT-RELEASE-OUTCOME-REVIEW.json","RELEASE-REPAIR-03.md","RELEASE-REPAIR-03.diff",
    "POPULATION-PROPOSAL.json","CONSUMER-BLOCKER-01.json","custody-release-01/RELEASE.json"]
direct.update("scoped-v2/"+n for n in release_names)
direct.update(k for k,v in selected.items() if v["kind"]=="file" and
    any(k.startswith("scoped-v2/"+s+"/") for s in ["custody-release-observer-01","startup-01","startup-02"]))
copies = {}
def copy_file(src, dest):
    p=OUT/dest
    p.parent.mkdir(parents=True,exist_ok=True)
    data=src.read_bytes()
    with p.open("xb") as f: f.write(data)
    copies[dest]={"source":str(src),**ident(data)}
for rel in sorted(direct):
    assert rel in selected and selected[rel]["kind"]=="file"
    copy_file(SOURCE/rel,rel)
copy_file(SOURCE/"DONORS.json","provenance/ORIGINAL-DONORS.json")
for n in ["ACQUISITION.json","set.mm.LICENSE"]:
    copy_file(EXTERNAL/n,"provenance/"+n)
acquisition=json.loads((OUT/"provenance/ACQUISITION.json").read_bytes())
corpus=next(x for x in acquisition["downloads"] if x["name"]=="set.mm")
request=json.loads((OUT/"scoped-v2/RELEASE-REQUEST.json").read_bytes())
assert all(corpus[k]==request["corpus"][k] for k in ["bytes","sha256"])
write_json("provenance/CORPUS.json",{"schema":"ordinary.publication-corpus-provenance.v1",
    "upstream_commit":acquisition["corpus_commit"], "url":corpus["url"],"original":request["corpus"],
    "custodian_prefix_omission":[x for x in omissions if Path(x["relative_path"]).name=="CUSTODIAN-PREFIX.mm"],
    "scope":"Original set.mm is outside the archived source root and is not copied or reopened by this packaging operation. Its identity is reconciled from retained acquisition and consumed release request records. Only the owned prefix omission is freshly byte-hashed."})
write_json("COPY-MANIFEST.json",{"schema":"ordinary.publication-exact-copies.v1","files":copies})
zip_checks=[]
with zipfile.ZipFile(OUT/"HISTORICAL-RAW.zip") as z:
    assert len(z.namelist())==len(set(z.namelist())) and set(z.namelist())==set(members)
    for name,row in members.items():
        data=z.read(name)
        source=Path(row["source"])
        assert ident(data)==row["zip_payload"]
        assert source.is_dir() if row["kind"]=="directory" else data==source.read_bytes()
        zip_checks.append(name)
for dest,row in copies.items():
    assert (OUT/dest).read_bytes()==Path(row["source"]).read_bytes()
assert inventory()==before
current="""# Ordinary cut opportunity: current record

The completed result in this capsule is a custody-only release of 128 training
positions (theorem ordinals 4096–4223). The current consumer v3 passed 18 authored
transport controls. These records establish neither a native opportunity census
nor a learned method, useful acquisition, held-out result or novelty claim.

Read [consumer v3](consumer-v3/CORE.md), its
[contract](consumer-v3/CONTRACT.md), and
[qualification](consumer-v3/QUALIFICATION.json).
The [release review](scoped-v2/ROOT-RELEASE-OUTCOME-REVIEW.json) records the separate
source release. [Corpus provenance](provenance/CORPUS.json) binds the source and
the omitted custodian prefix.

## Current source and qualification

[Consumer v3 freeze](consumer-v3/SOURCE-FREEZE.json) binds the hypothesis/context
and exact source-span repair. All released whole theorems remain in P1 when
their trace transport is unusable. Eighteen authored controls passed in a fresh
process; they made no native, exporter, extractor, alias or corpus calls.

The [raw process record](consumer-v3/qualification-01/PROCESS.json) and
[stdout](consumer-v3/qualification-01/stdout.txt) remain unchanged. These synthetic
controls do not qualify a real native packet. The
[request template](consumer-v3/OPPORTUNITY-REQUEST-TEMPLATE.json) retains unset
input bindings. Separate native authority and consumer-run qualification are
outside this capsule; see the frozen [gaps](consumer-v3/GAPS.md).

## Consumed source release

The [exact request](scoped-v2/RELEASE-REQUEST.json),
[four-source freeze](scoped-v2/RELEASE-SOURCE-FREEZE-03.json),
[source acceptance](scoped-v2/ROOT-RELEASE-SOURCE-ACCEPTANCE-03.json),
[once-only gate](scoped-v2/ROOT-RELEASE-GATE.json),
[outer receipt](scoped-v2/custody-release-observer-01/PROCESS.json), and
[release metadata](scoped-v2/custody-release-01/RELEASE.json) are direct exact copies.

The reviewed release retains all 128 positions without replacements. The prefix
inventory has 100 axiom declarations, compared with 96 in the earlier prefix;
these inventory entries are not a claim about independent mathematical
assumptions. Fresh native verification must establish the enlarged authority.
No prior native receipt establishes it.

The [registry declaration](scoped-v2/REGISTRY-SCOPE.json) covers 27 named
source/registration records and their recorded lineage. Its empty known protected
label set is a scoped programme governance decision, not universal clearance
across other hosts or private sessions. Future evaluations must reconcile this
newly exposed tranche with subsequently disclosed allocations.

## Preserved history

The [historical ZIP](HISTORICAL-RAW.zip) retains every source-root file except
the full custodian prefix and Python caches. It includes original candidate
sources/freezes, failed startup evidence, earlier synthetic fixtures and source
generations. Original and scoped-v2 consumers are historical: v2 could not
transport native hypothesis contracts. Current consumer v3 addresses that defect.
No older consumer is represented as a successful opportunity run.

Earlier reports and gates remain verbatim, including their then-current
pending/closed status. The later release outcome records the one consumed release.
Historical freezes bind their stated source generations, not every later mutable
path. Snapshot directories and original freeze bytes remain in the ZIP.
Absolute laptop paths are historical identities, not portable execution commands.

## Archive custody

[Exact copy map](COPY-MANIFEST.json), [archive members](ARCHIVE-MEMBERS.json),
[omissions](OMISSIONS.json), [verification](VERIFY.json) and [file inventory](FILES.json)
describe this byte-preserving package. All archive members were compared against
the source, and the complete source inventory was unchanged before and after.
Generated per-root fixtures stay inside the ZIP rather than becoming loose files.

The original full set.mm and the custodian prefix are not redistributed.
Packaging performed file reads, hashing and compression only. It imported no
research module and ran no native verifier, learner, corpus audit or tests.
"""
with (OUT/"CURRENT.md").open("x") as f:f.write(current)
links=[]
for p in sorted(OUT.rglob("*.md")):
    assert len(p.read_text().splitlines())<150, str(p)
    for dest in re.findall(r"\[[^\]]*\]\(([^)]+)\)",p.read_text()):
        if "://" not in dest and not dest.startswith(("#","/")):
            target=dest.split("#")[0]
            if target in {"VERIFY.json","FILES.json"} and p.name=="CURRENT.md":continue
            assert (p.parent/target).exists(),(str(p),dest)
            links.append({"file":str(p.relative_to(OUT)),"target":dest})
write_json("VERIFY.json",{"schema":"ordinary.publication-byte-verification.v1","terminal":"ALL_BYTES_MATCH",
    "archive_file_count":sum(r["kind"]=="file" for r in members.values()),
    "archive_directory_count":sum(r["kind"]=="directory" for r in members.values()),
    "archive_member_checks":len(zip_checks),"direct_copy_checks":len(copies),"relative_links":links,
    "source_inventory_unchanged":True,"research_imports":0,"native_calls":0,"tests_run":0,
    "scope":"Packaging byte comparison only; no semantic replay or new source qualification.",
    "elapsed_packaging_window_s":time.time()-START})
write_json("FILES.json",{"schema":"ordinary.publication-file-inventory.v1","files":{
    p.relative_to(OUT).as_posix():ident(p.read_bytes()) for p in sorted(OUT.rglob("*")) if p.is_file()}})
print(json.dumps({"terminal":"PACKAGE_READY","root":str(OUT),"archive":ident((OUT/"HISTORICAL-RAW.zip").read_bytes()),
    "file_manifest":ident((OUT/"FILES.json").read_bytes()),"copies":len(copies),"archive_members":len(members),
    "omissions":omissions},sort_keys=True))
