"""Manual AST preparation controls only; no native verification or actual capture read."""
import json
from pathlib import Path
import sys
root = Path(sys.argv[1]); sys.path.insert(0,str(root/'research/ocm-prototype'))
from clia_tasks import load_task
from generation_clia import admit_macros, decode
from postprocess import prepare
task = load_task('jmbl_fg_max3')
macro = {'role':'MANUAL_ENGINEERING_CONTROL_NOT_LEARNED','definitions':[{'name':'fn_0','body':'(ite (>= #0 #1) #0 #1)','arity':2}]}
manual = '(define-fun mux_3 ((x Int) (y Int) (z Int)) Int (+ (fn_0 x y) 7))'
prepared = prepare(manual,task,macro)
assert prepared['expanded_candidate'] == '(define-fun mux_3 ((x Int) (y Int) (z Int)) Int (+ (ite (>= x y) x y) 7))'
assert prepared['macro_calls']==['fn_0']
assert '(define-fun fn_0 ' in prepared['equivalence_smt2']
assert '(POST_ORIGINAL x y z)' in prepared['equivalence_smt2']
assert '(POST_EXPANDED x y z)' in prepared['equivalence_smt2']
bad = [manual.replace('(fn_0 x y)','(fn_0 x)'),manual.replace('(fn_0 x y)','(fn_0 true y)'),
       manual.replace('(+ (fn_0 x y) 7)','(let ((v x)) v)'),manual+' (check-sat)']
refusals=[]
for candidate in bad:
    try:prepare(candidate,task,macro)
    except ValueError as exc:refusals.append(str(exc))
    else:raise AssertionError('malformed manual candidate accepted')
print(json.dumps({'status':'PASS','scope':'Manual AST only; not a true solution/specification claim.',
                  'prepared':prepared,'refusals':refusals,'native_checks':0,'actual_capture_reads':0}))
