from pathlib import Path
import pytest
from ocm.dependency_audit import generate_audit
from ocm.epistemics.authority import verify_authority
from ocm.historical import repository_root
from ocm.provenance import verify_migration

def _root_or_skip()->Path:
 try: root=repository_root()
 except Exception: pytest.skip("repository history not present")
 if not (root/".git").exists(): pytest.skip("git history required")
 return root

def test_frozen_migration_bytes_are_exact():
 m=verify_migration(_root_or_skip()); assert m["migrated_file_count"]>0 and m["byte_identity_pass"]==m["byte_identity_total"] and m["manifest_drift"]==0

def test_hidden_dependencies_are_closed():
 a=generate_audit(_root_or_skip()); assert a["required_hidden_orion_v2_filesystem_dependencies"]==0 and a["host_specific_path_dependencies"]==0 and a["runnable_reference_entrypoints"]==a["reference_entrypoints_total"]

def test_historical_authority_anchors_hold():
 r=verify_authority(_root_or_skip()); assert r["m2_parent_tie"]=="PARENT_SUFFICIENT" and r["m6a_parent_tie"]=="PARENT_SUFFICIENT" and r["general_novelty"]=="NOT_ESTABLISHED"
