"""Fixed typed output qualification; existing checker powers remain unchanged."""
import generation_clia as G
from clia_grammar import forms, validate
from clia_tasks import signatures, validate_task
from clia_checker import check

RULE={'name':'-','body':'(+ #0 (* (- 1) #1))','arity':2}

def prepare(group):
    rows=[]
    if group['group'] not in ('manual','train'):
        raise ValueError('unknown fixed group')
    for row in group['records']:
        if group['group']=='train':
            validate_task(row['task'])
            sigs=signatures(row['task']); name=next(iter(sigs)); ident=row['task']['task_id']
        else:
            name=row['name']; ident=row['id']
            sigs={name:{'parameters':[[G.S(n),G.S('Int')] for n in row['parameters']]}}
        encoded=G.encode(row['candidate'],sigs)
        if len(encoded)!=1:
            raise ValueError('exactly one function per row')
        rows.append({'id':ident,'name':name,'original':row['candidate'],
                     'program':encoded[0]['program'],'sigs':sigs,'input':row})
    return rows

def binary_count(node):
    if not isinstance(node,list):
        return 0
    return int(len(node)==3 and str(node[0])=='-')+sum(binary_count(x) for x in node)

def assess(group,prepared,rewritten):
    result={'status':'CANNOT_CHECK_NORMALIZATION','assigned':len(prepared),'rows':[]}
    if not isinstance(rewritten,list) or len(rewritten)!=len(prepared) or not all(isinstance(x,str) for x in rewritten):
        result['reason']='changed/malformed output inventory'
        return result
    for row,program in zip(prepared,rewritten):
        out={'id':row['id'],'status':'CANNOT_CHECK_NORMALIZATION','rewritten':program}
        result['rows'].append(out)
        try:
            decoded=G.decode(program,row['name'],row['sigs']) # no macro expansion/library
            out.update(decoded=decoded,grammar='PASS')
            before=binary_count(G.one(row['program'])); after=binary_count(G.one(program))
            out.update(binary_minus_before=before,binary_minus_after=after,
                       changed=G.one(program)!=G.one(row['program']))
            out['effective_binary_normalization']=out['changed'] and after>before
            # The left side is the exact independent original, never output expansion.
            out['equivalence']=G.equivalent(row['original'],decoded['candidate'],row['sigs'])
            if group['group']=='manual':
                expected=row['input']['expected']
                expected_program=G.encode(expected,row['sigs'])[0]['program']
                expected_canonical=G.decode(expected_program,row['name'],row['sigs'])['candidate']
                out['expected_primitive_tree']=forms(decoded['candidate'])==forms(expected_canonical)
                admissible=out['expected_primitive_tree']
            else:
                task=row['input']['task']
                out['fixed_spec']=check(task,{'status':'SOLUTION','candidate':decoded['candidate'],
                  'task_sha256':task['task_sha256'],'grammar_id':task['grammar']['id']})
                admissible=out['fixed_spec']['status']=='PASS'
            if out['equivalence']['status']=='PASS' and admissible:
                out['status']='PASS'
        except (ValueError,TypeError,KeyError,IndexError,RecursionError) as exc:
            out['reason']=type(exc).__name__+': '+str(exc)
    result['passed']=sum(x['status']=='PASS' for x in result['rows'])
    result['effective_rows']=sum(x.get('effective_binary_normalization',False) for x in result['rows'])
    if result['passed']==len(prepared):
        if group['group']=='manual':
            result['status']='MANUAL_BOUNDARY_QUALIFIED'
        elif result['effective_rows']:
            result['status']='TRAIN_NORMALIZATION_QUALIFIED'
        else:
            result['status']='TRAIN_EQUIVALENT_NO_EFFECTIVE_NORMALIZATION'
    return result
