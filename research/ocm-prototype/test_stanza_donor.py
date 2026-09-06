"""Input/output custody controls without loading or invoking a learned model."""
import copy
import json
from pathlib import Path
from types import SimpleNamespace as NS
import pytest
import stanza_donor as D

FORMS = ["Birds", "fly"]
def document():
    words = [NS(id=1, text="Birds", head=2, deprel="nsubj", upos="NOUN"),
             NS(id=2, text="fly", head=0, deprel="root", upos="VERB")]
    return NS(sentences=[NS(words=words, tokens=[NS(text=w.text, words=[w]) for w in words])])

def test_clean_supplied_words_and_document():
    assert D.document_words(document(), FORMS)[0] == dict(id=1, form="Birds", head=2, deprel="nsubj", upos="NOUN")

@pytest.mark.parametrize("fault", ["form", "sentence", "word_count", "mwt", "head"])
def test_malformed_output_refused(fault):
    doc = document()
    if fault == "form": doc.sentences[0].words[0].text = "Bird"
    if fault == "sentence": doc.sentences.append(copy.deepcopy(doc.sentences[0]))
    if fault == "word_count": doc.sentences[0].words.pop()
    if fault == "mwt": doc.sentences[0].tokens[0].words.append(NS())
    if fault == "head": doc.sentences[0].words[0].head = 4
    with pytest.raises(ValueError): D.document_words(doc, FORMS)

def test_exact_file_binding_accepts_and_refuses(tmp_path):
    path = tmp_path / "artifact"; path.write_bytes(b"original")
    D.require_hash(path, D.sha(path))
    with pytest.raises(ValueError, match="binding"): D.require_hash(path, "0" * 64)

def test_real_public_inventory_accepts_and_refuses_annotated_input():
    public=json.loads((Path(__file__).parent / "results/g1-matched-plan-v1/public-items.json").read_text())
    assert len(D.syntax_items(public)) == 100
    with pytest.raises(ValueError): D.syntax_items([])
    next(row for row in public if row["request"]["kind"] == "syntax")["request"]["gold"] = []
    with pytest.raises(ValueError, match="forms-only"): D.syntax_items(public)
