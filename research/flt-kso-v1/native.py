"""Bounded explicit implicational/conjunctive proof proposals, never proof warrant.

No task-specific proof branch, imported proof text, learned ranking, API client,
model, external solver, file I/O or random policy exists in this mechanism.
The matched parent invokes this identical grammar and deterministic search.
"""
from __future__ import annotations
import re
from substrate import Refusal, digest_json


def atom(name): return ('atom', name)
def imp(left, right): return ('imp', left, right)
def conj(left, right): return ('and', left, right)


def validate_formula(value):
    count = [0]
    def visit(node, depth):
        count[0] += 1
        if depth > 24 or count[0] > 128 or type(node) not in (tuple,list) or not node:
            raise Refusal('CANNOT_CHECK_FORMULA_LANGUAGE')
        if node[0] == 'atom' and len(node) == 2 and type(node[1]) is str and re.fullmatch('[A-Z][A-Za-z0-9_]{0,15}',node[1]):
            return ('atom',node[1])
        if len(node)==3 and node[0] in ('imp','and'):
            return (node[0],visit(node[1],depth+1),visit(node[2],depth+1))
        raise Refusal('CANNOT_CHECK_FORMULA_LANGUAGE')
    return visit(value,0)


def render_formula(formula):
    if formula[0]=='atom': return formula[1]
    symbol = '→' if formula[0]=='imp' else '∧'
    return '(' + render_formula(formula[1]) + ' ' + symbol + ' ' + render_formula(formula[2]) + ')'


def emit_source(formula, term):
    formula=validate_formula(formula)
    variables=set()
    def collect(f):
        if f[0]=='atom': variables.add(f[1])
        else: collect(f[1]); collect(f[2])
    collect(formula)
    count=[0]
    def emit(t,scope,depth=0):
        count[0]+=1
        if depth>64 or count[0]>2048 or type(t) not in (list,tuple) or not t:
            raise Refusal('CANNOT_CHECK_PROOF_LANGUAGE')
        if len(t)==2 and t[0]=='var' and type(t[1]) is str and t[1] in scope:
            return t[1]
        if len(t)==3 and t[0]=='lam' and type(t[1]) is str and re.fullmatch(r'h\d+',t[1]) and t[1] not in scope:
            return '(fun '+t[1]+' => '+emit(t[2],scope|{t[1]},depth+1)+')'
        if len(t)==3 and t[0] in ('app','pair'):
            a,b=emit(t[1],scope,depth+1),emit(t[2],scope,depth+1)
            return '('+ ('And.intro '+a+' '+b if t[0]=='pair' else a+' '+b)+')'
        raise Refusal('CANNOT_CHECK_PROOF_LANGUAGE')
    body=emit(term,set())
    return ('import Init\nset_option autoImplicit false\nnamespace FLTMicro\n'
            'theorem goal ('+' '.join(sorted(variables))+' : Prop) : '+render_formula(formula)+
            ' :=\n  '+body+'\n#print axioms goal\nend FLTMicro\n')


class BudgetStop(Exception): pass


def synthesize(formula, *, max_expansions=256, max_depth=24):
    formula=validate_formula(formula)
    if type(max_expansions) is not int or type(max_depth) is not int or not 1<=max_expansions<=4096 or not 1<=max_depth<=24:
        raise Refusal('INVALID_SEARCH_BUDGET')
    events=[]; active=set(); seen=set()
    metrics={'proof_state_expansions':0,'unique_proof_states':0,
             'duplicate_states_avoided':0,'operator_candidates_considered':0,
             'local_hypotheses_examined':0,'Lean_checker_calls':0,'LLM_CALLS':0,'LLM_TOKENS':0}
    def state_id(goal,ctx):
        return digest_json({'goal':goal,'context_types':sorted({digest_json(t) for _,t in ctx})})
    def action(name,state,inputs=(),outputs=()):
        metrics['operator_candidates_considered']+=1
        event={'operator':name+'@1','input_state':state,'candidate_dependencies':list(inputs),
               'resulting_states':list(outputs),'resource_cost':{'operator_candidates':1},
               'checker_outcome':'NOT_RUN','failure_class':None}
        events.append(event)
        return event
    def search(goal,ctx,depth):
        sid=state_id(goal,ctx)
        if sid in active:
            metrics['duplicate_states_avoided']+=1
            return None
        if depth>max_depth: return None
        if metrics['proof_state_expansions']>=max_expansions: raise BudgetStop()
        metrics['proof_state_expansions']+=1; seen.add(sid); active.add(sid)
        try:
            for name,typ in ctx:
                metrics['local_hypotheses_examined']+=1
                ev=action('local_exact',sid,[name])
                if typ==goal: return ('var',name)
                ev['failure_class']='TYPE_MISMATCH'
            if goal[0]=='imp':
                name='h'+str(len(ctx)); nxt=ctx+((name,goal[1]),)
                ev=action('implication_intro',sid,(),[state_id(goal[2],nxt)])
                body=search(goal[2],nxt,depth+1)
                if body is not None: return ('lam',name,body)
                ev['failure_class']='SUBGOAL_NOT_CLOSED_UNDER_BUDGET'
            if goal[0]=='and':
                ev=action('conjunction_intro',sid,(),[state_id(goal[1],ctx),state_id(goal[2],ctx)])
                left=search(goal[1],ctx,depth+1)
                right=search(goal[2],ctx,depth+1) if left is not None else None
                if left is not None and right is not None: return ('pair',left,right)
                ev['failure_class']='SUBGOAL_NOT_CLOSED_UNDER_BUDGET'
            for name,typ in ctx:
                premises=[]; conclusion=typ
                while conclusion[0]=='imp':
                    premises.append(conclusion[1]); conclusion=conclusion[2]
                if not premises or conclusion!=goal: continue
                ev=action('implication_apply',sid,[name],[state_id(p,ctx) for p in premises])
                result=('var',name)
                for premise in premises:
                    arg=search(premise,ctx,depth+1)
                    if arg is None:
                        result=None; ev['failure_class']='SUBGOAL_NOT_CLOSED_UNDER_BUDGET'; break
                    result=('app',result,arg)
                if result is not None: return result
            return None
        finally: active.remove(sid)
    exhausted=False
    try: term=search(formula,(),0)
    except BudgetStop: term=None; exhausted=True
    metrics['unique_proof_states']=len(seen)
    return {'terminal':'NATIVE_CANDIDATE_CONSTRUCTED' if term is not None else 'FAILED_UNDER_BUDGET',
            'formula':formula,'term':term,'truth_warrant':'NONE','events':events,'metrics':metrics,
            'budget':{'max_expansions':max_expansions,'max_depth':max_depth},
            'expansion_budget_exhausted':exhausted,
            'negative_scope':'THIS_GRAMMAR_STATE_AND_BUDGET_NOT_MATHEMATICAL_REFUTATION'}
