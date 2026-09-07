"""Portable derived-record audit. No Git, native runtime, raw input fetch or execution."""
import sys
from pathlib import Path
import types
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parent
# Compile owned helper bytes directly; imported bytecode caches are never authority.
for _name in ["registration_evidence_archive", "registration_evidence_order", "registration_evidence_bindings"]:
    _path = ROOT / (_name + ".py")
    _module = types.ModuleType(_name); _module.__file__ = str(_path)
    sys.modules[_name] = _module
    exec(compile(_path.read_bytes(), str(_path), "exec"), _module.__dict__)
from registration_evidence_archive import canonical, checked_file, decode, identity, read_archive, require
from registration_evidence_order import verify_order
from registration_evidence_bindings import digest_record, verify_omissions, verify_source_bindings

MANIFEST = {"sha256": "226ff793016e143cf7746d72030c8a585631aad530e84db39ed97166791590e4", "bytes": 1212}
SEAL_SHA = "9d02378c93369da33ccd8940509474422d898bee899c42ce28e7bc6958362a2e"
COMMIT = "aa2d8b34692b16c70f699536de0d8e75b9a3e9ef"
TREE = "8bb1c43c8f26f1c127591dddeffdead2b5094eb7"
TESTS = {"tests/" + n for n in ["registration_fixture.py", "test_registration_population.py", "test_registration_custody.py", "test_registration_run.py", "test_registration_cli.py"]}
CORE = {n + ".py" for n in ["coverage_boot", "coverage_git", "coverage_policy", "coverage_population", "coverage_register", "register"]}


def support_checks(files, package, derived):
    launch = decode(files["envelope/PRELAUNCH.json"])
    process = decode(files["envelope/PROCESS.json"])
    require(type(process["returncode"]) is int and process["returncode"] == 0, "registration outer process failed")
    require(launch["environment"] == {} and launch["argv"][1:3] == ["-I", "-S"], "outer launch contract differs")
    for stream in ["stdout", "stderr"]:
        require(identity(files["envelope/" + stream]) == digest_record(process[stream]), "outer stream identity differs")
    require(files["envelope/stderr"] == b"", "outer stderr is nonempty")
    for role, name in [("recorder", "registration_envelope.py"), ("entry", "register.py")]:
        checked_file(Path(package)/name, digest_record(launch[role]))
    require(identity(files["envelope/registration_envelope.py"]) == digest_record(launch["recorder"]), "recorder snapshot differs")
    q = decode(files["qualification/coverage-registration-qualification.json"])
    require(q["terminal"] == "AUTHORED_REGISTRATION_QUALIFICATION_PASS" and type(q["tests"]) is int and q["tests"] == 58, "qualification status differs")
    require(set(q["files"]) == CORE | TESTS, "qualification source keyset differs")
    for name, record in q["files"].items():
        wanted = digest_record(record)
        checked_file(Path(package)/name, wanted)
        require(identity(files["qualification/source/" + name]) == wanted, "qualification source snapshot differs")
    for name, sha in q["evidence"].items():
        require(identity(files["qualification/" + name])["sha256"] == sha, "qualification evidence differs")
    junit = ET.fromstring(files["qualification/coverage-registration-final-tests.xml"])
    suites = list(junit.iter("testsuite"))
    require(sum(int(s.attrib["tests"]) for s in suites) == 58 and all(int(s.attrib.get(k, 0)) == 0 for s in suites for k in ["errors", "failures", "skipped"]), "58-test result differs")
    review = decode(files["independent/AUDIT.json"])
    require(review["terminal"] == "INDEPENDENT_REGISTRATION_AUDIT_PASS" and review["seal"] == identity(derived["SEAL.json"]), "independent review binding differs")
    require(review["process"] == identity(files["envelope/PROCESS.json"]), "independent process binding differs")


def audit(package, records=None):
    package = Path(package)
    records = Path(records) if records is not None else package/"registration-records"
    manifest_raw = checked_file(records/"MANIFEST.json", MANIFEST)
    manifest = decode(manifest_raw)
    archives = {}
    for key in ["derived", "supporting"]:
        row = manifest[key]
        archive = records/row["archive"]["name"]
        checked_file(archive, digest_record(row["archive"]))
        members = decode(checked_file(records/row["members"]["name"], digest_record(row["members"])))
        archives[key] = read_archive(archive, members)
        require(len(members) == row["member_count"] and sum(v["bytes"] for v in members.values()) == row["raw_bytes"], "archive member accounting differs")
    omissions = decode(checked_file(records/manifest["omissions"]["name"], digest_record(manifest["omissions"])))
    files = archives["derived"]
    omitted_count = verify_omissions(files, omissions, SEAL_SHA)
    source_count = verify_source_bindings(files, package)
    counts = verify_order(decode(files["POPULATION.json"]), decode(files["ASSIGNMENTS.json"]), decode(files["REGISTRATION.json"]), 29511, COMMIT, TREE)
    support_checks(archives["supporting"], package, files)
    require(checked_file(records/"MANIFEST.json", MANIFEST) == manifest_raw, "manifest changed during audit")
    return dict(terminal="DERIVED_REGISTRATION_RECORDS_PASS", **counts,
                current_source_bindings=source_count + 6, omitted_inputs=omitted_count,
                raw_input_scope="OMITTED_RAW_METADATA_NOT_REVALIDATED")


def main():
    try:
        require(len(sys.argv) == 1 and sys.flags.isolated and sys.flags.no_site, "use Python -I -S with no arguments")
        result = audit(ROOT)
    except ValueError as error:
        print(canonical({"terminal": "RECORD_REJECTED", "reason": str(error)}).decode(), end=""); return 1
    except Exception as error:
        print(canonical({"terminal": "CANNOT_CHECK", "reason": type(error).__name__ + ": " + str(error)}).decode(), end=""); return 2
    print(canonical(result).decode(), end=""); return 0

if __name__ == "__main__":
    raise SystemExit(main())
