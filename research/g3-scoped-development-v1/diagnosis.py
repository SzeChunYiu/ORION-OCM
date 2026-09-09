"""Witness-checking finite diagnosis, not planted cause labels or a general oracle."""
from __future__ import annotations
from dataclasses import replace
from itertools import product
from typing import Any
import mechanisms as X


def diagnose(packet:dict[str,Any]) -> dict:
    X.require(type(packet) is dict and 'kind' in packet,'DIAGNOSIS_PACKET')
    kind=packet['kind']
    if kind=='representation':
        X.require(set(packet)=={'kind','left','right','representation','observer','bound'},'ALIAS_FIELDS')
        a,b=tuple(packet['left']),tuple(packet['right']);bound=packet['bound']
        X.require(type(bound) is int and 0<=bound<=7 and len(a)<=bound and len(b)<=bound,'ALIAS_BOUND')
        pa,pb=X.M.normal_form(a),X.M.normal_form(b)
        same=X.representation_key(a,pa,packet['representation'])==X.representation_key(b,pb,packet['representation'])
        oa,ob=X.observation(a,pa,packet['observer']),X.observation(b,pb,packet['observer'])
        X.require(same and oa!=ob,'NO_CHECKED_REPRESENTATION_ALIAS')
        return {'terminal':'REPRESENTATION_INSUFFICIENT','witness':packet,
                'computed_observations':[oa,ob],'scope':'Registered finite representation and observation inventory only.'}
    if kind=='attempt':
        X.require(set(packet)=={'kind','attempt'},'ATTEMPT_DIAGNOSIS_FIELDS')
        X.validate_attempt(packet['attempt']);status=packet['attempt']['terminal']
        return {'terminal':'RESOURCE_BOUND' if status=='RESOURCE_BOUND' else 'CANNOT_CHECK',
                'observed_attempt_terminal':status,
                'scope':'Bounded method failure does not distinguish missing knowledge, representation, channel or operator.'}
    if kind=='checkpoint':
        X.require(set(packet)=={'kind','scope','target','visited'},'CHECKPOINT_FIELDS')
        s=X.MethodScope.parse(packet['scope']);target=X.coefficients(packet['target'])
        visited=packet['visited'];X.require(type(visited) is list and 0<len(visited)<s.attempts,'CHECKPOINT_BUDGET')
        programs=list(X.candidate_programs(s));X.require(len(visited)<len(programs),'NO_REMAINING_FRONTIER')
        expected=[{'program':list(p),'coefficients':X.wire(X.M.normal_form(p))} for p in programs[:len(visited)]]
        X.require(visited==expected and all(X.coefficients(row['coefficients'])!=target for row in visited),
                  'CHECKPOINT_NOT_ACTUAL_UNSOLVED_PREFIX')
        return {'terminal':'SEARCH_MORE','next_program':list(programs[len(visited)]),
                'remaining_budget':s.attempts-len(visited),'scope':'Checked finite frontier and unused registered budget.'}
    if kind=='missing-operator':
        X.require(set(packet)=={'kind','old_grammar','bound','target','repair_program'},'OPERATOR_WITNESS_FIELDS')
        grammar=packet['old_grammar'];bound=packet['bound'];repair=tuple(packet['repair_program'])
        X.require(type(grammar) is list and 0<len(grammar)<=4 and len(set(grammar))==len(grammar)
                  and all(t in X.M.PRIMITIVES for t in grammar),'OLD_GRAMMAR')
        X.require(type(bound) is int and 0<=bound<=5 and len(repair)<=bound,'OPERATOR_BOUND')
        target=X.coefficients(packet['target']);checks=0
        for n in range(bound+1):
            for p in product(grammar,repeat=n):
                checks+=1;X.require(X.M.normal_form(p)!=target,'OLD_GRAMMAR_ALREADY_SOLVES')
        X.require(X.M.normal_form(repair)==target and any(t not in grammar for t in repair),'UNVERIFIED_OPERATOR_REPAIR')
        return {'terminal':'MISSING_OPERATOR_AT_DECLARED_BOUND','old_programs_checked':checks,
                'repair_program':list(repair),'scope':'Fixed finite horizon; longer old-language solutions are not excluded.'}
    if kind=='channel':
        X.require(set(packet)=={'kind','worlds','probes','goal'},'CHANNEL_FIELDS')
        worlds=packet['worlds'];probes=packet['probes']
        X.require(type(worlds) is list and len(worlds)==2 and all(type(x) is int for x in worlds),'FINITE_WORLDS')
        X.require(type(probes) is list and bool(probes) and len(set(probes))==len(probes)
                  and all(p in ('parity','sign') for p in probes),'FINITE_PROBE_INVENTORY')
        X.require(packet['goal']=='greater-than-two','FINITE_GOAL')
        rows=[[x%2 if p=='parity' else int(x>=0) for p in probes] for x in worlds]
        required=[x>2 for x in worlds]
        X.require(rows[0]==rows[1] and required[0]!=required[1],'CHANNEL_DISTINCTION_NOT_ESTABLISHED')
        return {'terminal':'OBSERVATION_CHANNEL_INSUFFICIENT','observations':rows,'required_actions':required,
                'scope':'Authored pure deterministic finite world/probe model, not a diagnosis of unmodeled reality.'}
    if kind=='local-repair':
        X.require(set(packet)=={'kind','program','target'},'LOCAL_REPAIR_FIELDS')
        p=tuple(packet['program']);X.require('sqr' in p and all(t in (*X.M.PRIMITIVES,'sqr') for t in p),'LOCAL_ALIAS')
        repaired=tuple('square' if t=='sqr' else t for t in p)
        X.require(X.M.normal_form(repaired)==X.coefficients(packet['target']),'LOCAL_REPAIR_DOES_NOT_SOLVE')
        return {'terminal':'LOCAL_REPAIR','program':list(repaired),
                'scope':'Predeclared syntactic alias only; no new operator or representation.'}
    if kind=='unknown':
        X.require(set(packet)=={'kind'},'UNKNOWN_FIELDS');return {'terminal':'CANNOT_CHECK'}
    raise ValueError('UNREGISTERED_DIAGNOSIS')


def diagnose_support(rt,object_id:str) -> dict:
    """Use actual KSO and evidence/nogood liveness, never a supplied boolean flag."""
    atom=rt.state.ks.atom_view.get(object_id)
    if atom is None:return {'terminal':'MISSING_EVIDENCE','object':object_id,'liveness':'ABSENT'}
    w=rt.state.evidence.nogoods.filter_interval(rt.state.nogoods.filter_interval(atom.warrant))
    status=w.liveness(rt.state.revoked|rt.state.evidence.revoked).value
    return {'terminal':'CANNOT_CHECK' if status=='LIVE' else 'MISSING_EVIDENCE',
            'object':object_id,'liveness':status,'scope':'Current support only; absent evidence is not negative truth.'}
