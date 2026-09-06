"""Adopt one exact native grammar; parse/dump only, no native solver/check calls."""
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'fixed-source/research/ocm-prototype'))
import clia_grammar as G
import clia_tasks as T
from sexpdata import Symbol as S

TASK = ROOT/'fixed-source/research/ocm-prototype/results/generation-feasibility-20260906/prospective/public-task.json'


def native_grammar(stderr, function):
    rows=[node for node in G.forms(stderr) if isinstance(node,list) and node
          and isinstance(node[0],S) and str(node[0])=='sygus-grammar']
    if len(rows)!=1 or len(rows[0])!=4 or rows[0][1]!=function:
        raise ValueError('exact single native grammar/function binding required')
    row=rows[0]; declarations, productions=row[2:]
    if len(declarations)!=2 or len(productions)!=2:
        raise ValueError('exact two-nonterminal donor required')
    if [str(x[1]) for x in declarations]!=['Int','Bool']:
        raise ValueError('original native nonterminal order/sorts required')
    for declaration,production in zip(declarations,productions):
        if len(declaration)!=2 or len(production)!=3 or production[:2]!=declaration:
            raise ValueError('native declaration/production mismatch')
    return deepcopy(row)


def task_commands(text):
    result=[]
    for node in G.forms(text):
        if str(node[0])=='set-option':
            if node not in [[S('set-option'),S(':output'),S('sygus-sol-gterm')],
                            [S('set-option'),S(':out'),'stderr']]:
                raise ValueError('unexpected diagnostic option')
            continue
        node=deepcopy(node)
        if str(node[0])=='synth-fun':
            node=node[:4]
        result.append(node)
    return result


def build(request,task,stderr):
    T.validate_task(task)
    if request['action']!='synthesize' or request['timeout_ms']!=5000:
        raise ValueError('original action/native deadline required')
    text=request['payload']['sygus']
    if task_commands(text)!=G.forms(task['original_sygus']):
        raise ValueError('original public specification changed')
    nodes=[n for n in G.forms(text) if str(n[0])=='synth-fun']
    if len(nodes)!=1 or len(nodes[0])!=4:
        raise ValueError('one implicit parent signature required')
    grammar=native_grammar(stderr,nodes[0][1])
    lines=text.splitlines(keepends=True)
    positions=[i for i,line in enumerate(lines) if line.lstrip().startswith('(synth-fun ')]
    if len(positions)!=1 or G.forms(lines[positions[0]])!=nodes:
        raise ValueError('exact single-line parent declaration required')
    index=positions[0]; original_line=lines[index]
    lines[index]=G.dump(nodes[0]+grammar[2:])+('\n' if original_line.endswith('\n') else '')
    replay=deepcopy(request);replay['payload']['sygus']=''.join(lines)
    assert task_commands(replay['payload']['sygus'])==task_commands(text)
    assert [n for n in G.forms(replay['payload']['sygus']) if str(n[0])=='synth-fun'][0][4:]==grammar[2:]
    return replay,grammar


def prepare():
    task=json.loads(TASK.read_text())
    request=json.loads((ROOT/'implicit_primitive.json').read_text())
    stderr=(ROOT/'native-implicit.stderr').read_text()
    result,grammar=build(request,task,stderr)
    with (ROOT/'native_grammar_replay.json').open('x') as out:
        json.dump(result,out,indent=2,sort_keys=True);out.write('\n')
    (ROOT/'native_grammar_replay.sl').write_text(result['payload']['sygus'])
    (ROOT/'printed-native-grammar.sl').write_text(G.dump(grammar)+'\n')
    assert not any(n=='cvc5' or n.startswith('cvc5.') or n=='z3' or n.startswith('z3.') for n in sys.modules)
    print(json.dumps({'status':'INPUT_PREPARED_NO_NATIVE_CALLS',
                      'input_sha256':hashlib.sha256((ROOT/'native_grammar_replay.json').read_bytes()).hexdigest(),
                      'grammar_sha256':hashlib.sha256((ROOT/'printed-native-grammar.sl').read_bytes()).hexdigest()}))


if __name__=='__main__':
    prepare()
