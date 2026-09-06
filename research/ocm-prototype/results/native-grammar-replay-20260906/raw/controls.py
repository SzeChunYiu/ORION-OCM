"""Structural/metamorphic input controls only; never import a native solver."""
from copy import deepcopy
import json
from pathlib import Path
import sys
import build_inputs as B

ROOT=Path(__file__).resolve().parent


def main():
    task=json.loads(B.TASK.read_text()); request=json.loads((ROOT/'implicit_primitive.json').read_text())
    text=(ROOT/'native-implicit.stderr').read_text(); rows=[]
    result,grammar=B.build(request,task,text)
    assert result!=request and request==json.loads((ROOT/'implicit_primitive.json').read_text())
    assert result['payload']['sygus'].count('(synth-fun ')==1
    assert B.task_commands(result['payload']['sygus'])==B.G.forms(task['original_sygus'])
    assert [B.G.dump(x) for x in grammar[2]]==['(A_Int_489 Int)','(A_Bool_491 Bool)']
    assert 'fn_0' not in result['payload']['sygus'] and 'GEN_' not in result['payload']['sygus']
    rows.append({'case':'actual_printed_grammar_and_full_public_spec','status':'PASS'})
    same,g2=B.build(request,task,'\n  '+text+'\n')
    assert same==result and g2==grammar
    rows.append({'case':'whitespace_metamorphic_identity','status':'PASS'})
    variants=[
      ('missing_donor',request,''),
      ('duplicate_donor',request,text+B.G.dump(grammar)+'\n'),
      ('changed_function',request,text.replace('sygus-grammar mux_3','sygus-grammar other')),
      ('changed_sort',request,text.replace('A_Bool_491 Bool','A_Bool_491 Int')),
    ]
    changed=deepcopy(request);changed['payload']['sygus']=changed['payload']['sygus'].replace('(>= (mux_3 x y z) x)','(> (mux_3 x y z) x)')
    assert changed!=request;variants.append(('changed_public_constraint',changed,text))
    changed=deepcopy(request);changed['timeout_ms']=5001
    variants.append(('changed_native_deadline',changed,text))
    explicit=json.loads((ROOT/'explicit_primitive.json').read_text())
    assert B.task_commands(explicit['payload']['sygus'])==B.G.forms(task['original_sygus'])
    variants.append(('explicit_parent_cannot_be_silently_replaced',explicit,text))
    for name,req,stderr in variants:
        try:
            B.build(req,task,stderr)
        except (ValueError,IndexError,TypeError) as exc:
            rows.append({'case':name,'status':'EXPECTED_REFUSAL','type':type(exc).__name__,'reason':str(exc)})
        else:
            raise AssertionError(name+' incorrectly accepted')
    assert not any(n=='cvc5' or n.startswith('cvc5.') or n=='z3' or n.startswith('z3.') for n in sys.modules)
    result={'scope':'STRUCTURAL_INPUT_ONLY','rows':rows,'passed':len(rows),
            'synthesis_calls':0,'native_checker_calls':0,'runtime_grammar_parse':'NOT_RUN'}
    with (ROOT/'CONTROL.json').open('x') as out:json.dump(result,out,indent=2,sort_keys=True);out.write('\n')
    print(json.dumps({'passed':len(rows),'synthesis_calls':0,'native_checker_calls':0}))


if __name__=='__main__':
    main()
