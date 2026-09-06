from __future__ import annotations
import argparse, json
from pathlib import Path
from .dependency_audit import DependencyAuditError, generate_audit
from .epistemics.authority import AuthorityViolation, verify_authority
from .historical import repository_root
from .provenance import ProvenanceError, verify_migration
RECEIPT_PATH="docs/provenance/M0_RECEIPT_V1.json"
def live_status(root:Path):
 m=verify_migration(root); d=generate_audit(root); a=verify_authority(root)
 return {"terminal":"M0_LIVE_CHECKS_GREEN","migrated_file_count":m["migrated_file_count"],"byte_identity_pass":m["byte_identity_pass"],"byte_identity_total":m["byte_identity_total"],"runnable_reference_entrypoints":d["runnable_reference_entrypoints"],"reference_entrypoints_total":d["reference_entrypoints_total"],"external_hidden_dependencies":d["required_hidden_orion_v2_filesystem_dependencies"],"manifest_drift":m["manifest_drift"],"authority":a}
def build_status(root:Path):
 live=live_status(root); p=root/RECEIPT_PATH
 if not p.exists(): return {**live,"terminal":"M0_CANNOT_CHECK_FINAL_RECEIPT_NOT_RECORDED","receipt":None}
 r=json.loads(p.read_text(encoding="utf-8")); return {**live,"terminal":r.get("terminal","M0_CANNOT_CHECK_RECEIPT_TERMINAL_MISSING"),"receipt":r}
def main(argv=None):
 p=argparse.ArgumentParser(); p.add_argument("--live",action="store_true"); p.add_argument("--strict",action="store_true"); a=p.parse_args(argv)
 try: root=repository_root(); s=live_status(root) if a.live else build_status(root)
 except (ProvenanceError,DependencyAuditError,AuthorityViolation,OSError,ValueError) as exc: print(json.dumps({"terminal":"M0_STATUS_FAIL","reason":f"{type(exc).__name__}: {exc}"},sort_keys=True)); return 1
 print(json.dumps(s,indent=2,sort_keys=True))
 if a.live or s["terminal"]=="M0_CANONICAL_REPO_GREEN": return 0
 if a.strict: return 2 if str(s["terminal"]).startswith("M0_CANNOT_CHECK") else 1
 return 0
if __name__=="__main__": raise SystemExit(main())
