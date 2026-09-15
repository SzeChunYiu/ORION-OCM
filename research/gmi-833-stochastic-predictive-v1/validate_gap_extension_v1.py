#!/usr/bin/env python3
from __future__ import annotations
import importlib.util, json
from pathlib import Path
import sys
HERE=Path(__file__).resolve().parent
REPO=HERE.parents[1]
FOUND=REPO/'research'/'gmi-theory-foundations-v1'
BASE=FOUND/'GMI_GAP_GRAPH.json'
EXT=HERE/'GMI_GAP_GRAPH_836_EXTENSION.json'
VAL=FOUND/'validate_foundations.py'
spec=importlib.util.spec_from_file_location('gmi_foundation_validator',VAL)
if spec is None or spec.loader is None: raise RuntimeError('cannot load foundation validator')
v=importlib.util.module_from_spec(spec); sys.modules[spec.name]=v; spec.loader.exec_module(v)
base=json.loads(BASE.read_text()); ext=json.loads(EXT.read_text())
if ext.get('schema')!='GMI_GAP_GRAPH_EXTENSION_V1' or ext.get('issue')!=836: raise SystemExit('bad extension header')
merged=json.loads(json.dumps(base)); merged['nodes'].extend(ext['nodes'])
v.validate_gap_graph(merged)
by={n['id']:n for n in merged['nodes']}
if by['ISSUE-833']['status']!='OPEN': raise SystemExit('#833 must remain OPEN')
if by['GAP-833-STOCHASTIC-QUOTIENT']['status']!='OPEN': raise SystemExit('broad stochastic gap must remain OPEN')
if by['CLAIM-836-FINITE-PREDICTIVE-BLOCK']['status']!='LOCALLY_CLOSED': raise SystemExit('finite claim must be LOCALLY_CLOSED')
opens=['GAP-836-INFINITE-MEASURABLE','GAP-836-APPROXIMATE-PREDICTIVE','GAP-836-FINITE-SAMPLE-ID','GAP-836-CAUSAL-LATENT-ID']
for i in opens:
    n=by[i]
    if n['status']!='OPEN' or n['severity']!='CRITICAL': raise SystemExit(f'{i} must remain OPEN/CRITICAL')
    if n['parent']!='GAP-833-STOCHASTIC-QUOTIENT': raise SystemExit(f'{i} wrong parent')
print(json.dumps({'schema':'GMI836GapExtensionCheckV1','central_validator':'GREEN','issue_833':'OPEN','broad_stochastic_gap':'OPEN','finite_claim':'LOCALLY_CLOSED','stronger_open_gaps':opens},indent=2,sort_keys=True))
