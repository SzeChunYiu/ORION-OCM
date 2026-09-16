from __future__ import annotations
from blind_search_core import semantic_dp,TARGET_DIFF,TARGET_ID,expr_semantics

def counts(e):
    out={'ADD':0,'POS':0,'NEG':0,'LEAF':0}
    def rec(x):
        t=x[0]
        if t in ('X0','X1','C'): out['LEAF']+=1; return
        if t=='A': out['ADD']+=1;rec(x[1]);rec(x[2]);return
        if t=='P': out['POS']+=1;rec(x[1]);return
        if t=='N': out['NEG']+=1;rec(x[1]);return
        raise ValueError(t)
    rec(e); return out

def depth(e):
    if e[0] in ('X0','X1','C'): return 1
    if e[0] in ('N','P'): return 1+depth(e[1])
    return 1+max(depth(e[1]),depth(e[2]))

def fingerprint_expression(e,parameter_lift=False,updateable=False):
    c=counts(e)
    # Registered posthoc structural tests. They are not used by search/evaluator.
    p1 = parameter_lift and c['LEAF']>=2
    p2 = c['ADD']>=1
    p3 = c['POS']>=1
    p4 = c['POS']>=2 and c['ADD']>=3 and depth(e)>=4
    p5 = parameter_lift and c['LEAF']>=4
    p6 = parameter_lift and updateable
    return {'P1':p1,'P2':p2,'P3':p3,'P4':p4,'P5':p5,'P6':p6,'counts':c,'depth':depth(e)}

def neural_like(fp,trainable=True):
    required=('P1','P2','P3','P4','P5') + (('P6',) if trainable else ())
    return all(fp[k] for k in required)

def classify(candidate,parameter_lift=False,updateable=False):
    art=candidate.get('artifact')
    if isinstance(art,tuple) and art and art[0] in ('X0','X1','C','N','P','A'):
        fp=fingerprint_expression(art,parameter_lift,updateable)
        return {'posthoc_family':'NEURAL_LIKE' if neural_like(fp) else 'UNCLASSIFIED_ARITHMETIC','fingerprint':fp}
    return {'posthoc_family':None,'fingerprint':None}

def certificate():
    xor=semantic_dp(TARGET_DIFF); ident=semantic_dp(TARGET_ID)
    assert xor and ident
    xfp=fingerprint_expression(xor['expr'],parameter_lift=True,updateable=True)
    ifp=fingerprint_expression(ident['expr'],parameter_lift=True,updateable=True)
    assert neural_like(xfp)
    assert not neural_like(ifp)
    negatives={
      'DIRECT_IDENTITY':ifp,
      'FINITE_TABLE':{'P1':False,'P2':False,'P3':False,'P4':False,'P5':False,'P6':False},
      'CONDITIONAL_RULE':{'P1':False,'P2':False,'P3':False,'P4':False,'P5':False,'P6':False},
      'PASSIVE_PARAMETER_STORE':{'P1':True,'P2':False,'P3':False,'P4':False,'P5':True,'P6':False},
      'SINGLE_NONLINEAR_TRANSFORM':{'P1':True,'P2':False,'P3':True,'P4':False,'P5':True,'P6':True}
    }
    assert all(not neural_like(v) for v in negatives.values())
    return {
      'xor_posthoc_family':'NEURAL_LIKE','xor_fingerprint':xfp,
      'identity_posthoc_family':'UNCLASSIFIED_ARITHMETIC','negative_controls':negatives,
      'classifier_causally_downstream_of_search':True,
      'fingerprint_audit':'The P1-P6 conjunction is intentionally a narrow post-hoc structural region, not an ontology primitive or reward. It resembles known neural conventions and therefore cannot itself establish leave-family-out historical ignorance; causal separation is provided by the frozen blind protocol.',
      'universal_programs_trivially_classified':False
    }
