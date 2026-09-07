import importlib.util,json
from pathlib import Path
import pytest

def subject():
    assert importlib.util.find_spec("build_profile_policy") is not None,"offline mount policy missing"
    return __import__("build_profile_policy")

def test_material_inventory_detects_added_file_and_symlink_escape(tmp_path):
    m=subject();root=tmp_path/"src";root.mkdir();(root/"a").write_text("allowed")
    inv=m.inventory(root);assert inv["a"]["bytes"]==7
    (root/"b").write_text("new")
    with pytest.raises(ValueError):m.verify_inventory(root,inv)
    (root/"b").unlink();(root/"bad").symlink_to("/etc/passwd")
    with pytest.raises(ValueError):m.inventory(root)

@pytest.mark.parametrize("path",["/../etc","/x//z",'/x" rw, /etc/**','/x\n/etc',"/"])
def test_profile_path_injection_refuses(path):
    with pytest.raises(ValueError):subject().guest_path(path)

def test_profile_grants_mapping_only_to_registered_libraries():
    text=subject().apparmor_policy("test-0123456789abcdef",[
      {"guest":"/tools/lean","access":"executable"},{"guest":"/lib/known.so","access":"library"}],
      ["/source"],["/work"])
    assert "/tools/lean rmix," in text and "/lib/known.so mr," in text
    assert "/work/** rwkl," in text and "/work/** m" not in text
    assert "deny network," in text
    assert "capability" not in text

def test_material_scan_permission_error_never_claims_complete(tmp_path,monkeypatch):
 m=subject()
 def denied(root,**kwargs):
  if kwargs.get("onerror"):kwargs["onerror"](PermissionError("unreadable material"))
  return iter(())
 monkeypatch.setattr(m.os,"walk",denied)
 with pytest.raises(PermissionError):m.inventory(tmp_path)
