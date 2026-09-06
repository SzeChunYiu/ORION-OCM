"""Actual loader path contract with fake package modules; no prediction."""
from pathlib import Path
from types import SimpleNamespace as NS
import sys
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import stanza_donor as S


def test_optional_model_root_preserves_fixed_loader(tmp_path, monkeypatch):
    root = tmp_path/"models"
    paths = ["models/en/"+name+".pt" for name in ("pos", "lemma", "parse", "vectors")]
    original_load = lambda *args, **kwargs: object()
    torch = NS(load=original_load, set_num_threads=lambda n:None,
               set_num_interop_threads=lambda n:None, manual_seed=lambda n:None)
    seen = []
    def pipeline(**kwargs):
        seen.append(kwargs)
        for path in paths:
            torch.load(root/path.removeprefix("models/"), weights_only=True)
        with pytest.raises(ValueError, match="unexpected checkpoint"):
            torch.load(root/"undeclared.pt", weights_only=True)
        with pytest.raises(ValueError, match="unexpected checkpoint"):
            torch.load(root/"en/pos.pt", weights_only=False)
        trainer = NS(args={}, model=NS(eval=lambda:None))
        return NS(processors={"tokenize":NS(trainer=None), **{
            name:NS(trainer=trainer, config={}) for name in ("pos","lemma","depparse")}})
    monkeypatch.setitem(sys.modules, "torch", torch)
    monkeypatch.setitem(sys.modules, "stanza", NS(Pipeline=pipeline))
    result, loads = S.load_pipeline({"packages":[], "models":paths}, model_root=root)
    assert set(result.processors) == {"tokenize","pos","lemma","depparse"}
    assert set(loads) == {str(root/p.removeprefix("models/")) for p in paths}
    assert torch.load is original_load
    assert seen[0]["dir"] == str(root) and seen[0]["resources_filepath"] == str(root/"resources.json")
    assert seen[0]["tokenize_pretokenized"] is True and seen[0]["download_method"] is None
    assert seen[0]["use_gpu"] is False and seen[0]["package"] is None
