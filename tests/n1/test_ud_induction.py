"""N1 step 1: UD reading, lexicon/morphology/skeleton induction, protected coverage, the frequency hostile."""
from __future__ import annotations

from pathlib import Path

from ocm.language import lexicon as L
from ocm.learning.language import ud as UD

CONLLU = """# sent_id = s1
# text = The girl held the cup .
1\tThe\tthe\tDET\tDT\tDefinite=Def|PronType=Art\t2\tdet\t_\t_
2\tgirl\tgirl\tNOUN\tNN\tNumber=Sing\t3\tnsubj\t_\t_
3\theld\thold\tVERB\tVBD\tMood=Ind|Tense=Past|VerbForm=Fin\t0\troot\t_\t_
4\tthe\tthe\tDET\tDT\tDefinite=Def|PronType=Art\t5\tdet\t_\t_
5\tcup\tcup\tNOUN\tNN\tNumber=Sing\t3\tobj\t_\t_
6\t.\t.\tPUNCT\t.\t_\t3\tpunct\t_\t_

# sent_id = s2
# text = The dog kicked the ball .
1\tThe\tthe\tDET\tDT\tDefinite=Def|PronType=Art\t2\tdet\t_\t_
2\tdog\tdog\tNOUN\tNN\tNumber=Sing\t3\tnsubj\t_\t_
3\tkicked\tkick\tVERB\tVBD\tMood=Ind|Tense=Past|VerbForm=Fin\t0\troot\t_\t_
4\tthe\tthe\tDET\tDT\tDefinite=Def|PronType=Art\t5\tdet\t_\t_
5\tball\tball\tNOUN\tNN\tNumber=Sing\t3\tobj\t_\t_
6\t.\t.\tPUNCT\t.\t_\t3\tpunct\t_\t_

# sent_id = s3
# text = She slept .
1\tShe\tshe\tPRON\tPRP\tCase=Nom|Gender=Fem|Number=Sing|Person=3|PronType=Prs\t2\tnsubj\t_\t_
2\tslept\tsleep\tVERB\tVBD\tMood=Ind|Tense=Past|VerbForm=Fin\t0\troot\t_\t_
3\t.\t.\tPUNCT\t.\t_\t2\tpunct\t_\t_
"""


def test_induction_lexicon_morphology_skeletons_and_coverage(tmp_path):
    p = tmp_path / "t.conllu"
    p.write_text(CONLLU)
    sents = list(UD.read_conllu(p))
    assert [s.sent_id for s in sents] == ["s1", "s2", "s3"] and sents[0].root().lemma == "hold"
    ind = UD.induce(sents)
    rec = ind.receipt()
    assert rec["lexemes"] == 9 and rec["by_category"] == {"D": 1, "N": 4, "PRO": 1, "V": 3} and rec["skipped_upos"] == {"PUNCT": 3}
    assert ind.attestations["the|D"] == 2 and ind.irregular_past == {"hold": "held", "sleep": "slept"} and rec["irregular_past_exceptions"] == 2   # kicked is regular
    assert ind.skeletons == {"VERB(nsubj<,obj)": 2, "VERB(nsubj<)": 1}
    lx = ind.lexicon
    assert "hold|V" in lx.lexemes and lx.lexemes["hold|V"].senses[0].warrant.evidence == frozenset({"ud:s1"})
    assert lx.lexemes["the|D"].senses[0].warrant.evidence == frozenset({"ud:s1", "ud:s2"})          # attestations accumulate as evidence ids, not as a stronger warrant
    # protected coverage on an unseen sentence with one unseen lemma and a seen skeleton
    q = tmp_path / "q.conllu"
    q.write_text(CONLLU.replace("s1", "q1").replace("cup", "key").split("\n\n")[0] + "\n\n")
    cov = UD.coverage(UD.read_conllu(q), ind)
    assert cov["token_coverage"] == "4/5" and cov["sentence_lexical_coverage"] == "0/1" and cov["skeleton_coverage"] == "1/1" and cov["unseen_lemmas_top"] == [("key", 1)]
    assert UD.mutant_frequency_promotes(ind, threshold=2) == 1 and rec["frequency_raises_warrant"] is False   # the hostile would promote "the"; nothing is promoted


def test_receipt_exists_when_data_was_run():
    rec = Path(__file__).resolve().parents[2] / "research/ocm-n1/N1_UD_INDUCTION_V1.json"
    if not rec.exists():
        return                                              # CANNOT_CHECK locally: the corpus lives on the compute host
    import json
    d = json.loads(rec.read_text())
    assert d["train_induction"]["frequency_raises_warrant"] is False and d["status"].startswith("DESCRIPTIVE")
