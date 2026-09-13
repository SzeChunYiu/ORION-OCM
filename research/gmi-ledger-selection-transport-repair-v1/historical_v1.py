"""Original static tests and model countercontrols from unchanged pinned bytes."""
import io
import re
import sys
import tempfile
import unittest
from collections import Counter
from fractions import Fraction as F
from itertools import product
from pathlib import Path
from sources_v1 import module_from_bytes

LLS="research/gmi-learning-law-selection-v1/"
TL="research/gmi-transport-ledger-v1/"
DC="research/gmi-developmental-capital-v1/"

def original_suite(sources):
    """The four original modules do only bounded static arithmetic/document checks."""
    paths=(LLS+"test_learning_law_selection_v1.py",LLS+"test_ecology_prediction_v1.py",
           TL+"test_transport_ledger_v1.py",DC+"test_developmental_capital_v1.py")
    names=("learning_law_selection_v1","transport_model_v1")
    saved={name:sys.modules.get(name) for name in names}
    with tempfile.TemporaryDirectory(prefix="lst-original-") as tmp:
        root=Path(tmp)
        for (kind,path),data in sources.items():
            if kind=="PR594":continue
            target=root/path;target.parent.mkdir(parents=True,exist_ok=True)
            target.write_bytes(data)
        try:
            for name,path in zip(names,(LLS+names[0]+".py",TL+names[1]+".py")):
                sys.modules[name]=module_from_bytes(sources[("PR590",path)],name,root/path)
            outcomes={}
            for n,path in enumerate(paths):
                module=module_from_bytes(sources[("PR590",path)],"lst_original_"+str(n),root/path)
                suite=unittest.defaultTestLoader.loadTestsFromModule(module)
                result=unittest.TextTestRunner(stream=io.StringIO()).run(suite)
                outcomes[path]=dict(tests=result.testsRun,failures=len(result.failures),
                                    errors=len(result.errors),skipped=len(result.skipped))
                if not result.wasSuccessful() or result.skipped:
                    raise ValueError("original no-alarm tests failed: "+path)
        finally:
            for name in names:
                if saved[name] is None:
                    sys.modules.pop(name,None)
                else:
                    sys.modules[name]=saved[name]
    return outcomes

def old_controls(sources):
    m=module_from_bytes(sources[("PR590",LLS+"learning_law_selection_v1.py")],"old_m",LLS)
    t=module_from_bytes(sources[("PR590",TL+"transport_model_v1.py")],"old_t",TL)
    counts=Counter();compared=0
    # Independent logical menu: no read of the old LAWS table.
    for bits in product((False,True),repeat=7):
        d,e,s,l,h,p,o=bits
        costs=[]
        if d and e:costs.append(2)
        if d and s:costs.append(2)
        if l and h and s:costs.append(2)
        if p:costs.append(1)
        if p and o:costs.append(1)
        expected=("INFEASIBLE_AT_CONTRACT" if not costs else
                  "SELECTED" if costs.count(min(costs))==1 else "UNDETERMINED_TIE")
        caps={c for c,b in zip(m.CAPABILITIES,bits) if b}
        actual=m.select(caps,m.uniform_prices())["terminal"]
        if actual!=expected:raise ValueError("independent census disagrees")
        counts[actual]+=1;compared+=1
    caps={"LIKELIHOOD_MODEL","FINITE_HYPOTHESES","SIMPLEX_GEOMETRY"}
    admitted=m.select(caps,m.uniform_prices())
    lower=[t.transport(alloc,F(2),F(2))["bound"] for alloc in ([F(2)],[F(1),F(2)])]
    return dict(census=dict(counts),independent_contracts=compared,
                zero_likelihood_tag_menu=admitted,
                original_transport_bounds=lower,
                added_target_machine_cost=F(1))

def parent_readout(sources):
    ladder=sources[("PARENT","research/m2-traversal-capital-v1/m2p1/CLAIM_LADDER.md")].decode()
    m=re.search(r"cost on\s+(\d+)\s*/\s*(\d+)\s+fresh.*?registered\s+(\d+)\s*/\s*(\d+)",ladder,re.S)
    if not m:raise ValueError("registered fraction missing")
    ties=re.search(r"ties controller_v5 on\s+hc01, hc02, hc03, hc06 and hc10, and beats it on hc05, hc08 and hc09",ladder)
    if not ties:raise ValueError("strongest-parent comparison changed")
    receipt=sources[("PARENT","research/m2-traversal-capital-v1/m2p1/BEHAVIOURAL_RECEIPT.md")].decode()
    def number(pattern):
        match=re.search(pattern,receipt)
        if not match:raise ValueError("behavioral field missing")
        return int(match.group(1).replace(",",""))
    targets=number(r"targets\s*:\s*([\d,]+)")
    earlier=number(r"rank_H earlier than rank_0\s*:\s*([\d,]+)")
    later=number(r"rank_H later\s*:\s*([\d,]+)")
    worlds=number(r"worlds\s*:\s*([\d,]+)")
    return dict(status="PINNED_DOCUMENT_READOUT_NOT_NEW_EXPERIMENT",
                targets=targets,earlier=earlier,later=later,tied=targets-earlier-later,
                worlds=worlds,recorded_k2_passes=int(m[1]),recorded_k2_trials=int(m[2]),
                registered_numerator=int(m[3]),registered_denominator=int(m[4]),
                guided_first_ties=("hc01","hc02","hc03","hc06","hc10"),
                guided_first_beats=("hc05","hc08","hc09"),
                scope="C2 history effect retained; no OCM-specific residual beyond guided-first")
