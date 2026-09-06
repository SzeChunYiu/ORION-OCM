"""One frozen supplied-identity rewrite per process; no learning or synthesis."""
import argparse
import json
from pathlib import Path
import resource
import sys
import time
import traceback
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'source'))
sys.dont_write_bytecode=True
from supervision import write

def observe_verifier(directory):
    import clia_process
    native=clia_process.invoke
    calls={'verify_boundary_calls':0}
    def observed(action,payload,**kwargs):
        if action!='verify' or calls['verify_boundary_calls']>=4:
            raise ValueError('only four fixed verification obligations allowed')
        index=calls['verify_boundary_calls']; calls['verify_boundary_calls']+=1
        prefix=directory/('verify-%02d'%index)
        write(str(prefix)+'-request.json',{'action':action,'payload':payload,'kwargs':kwargs})
        try:
            result=native(action,payload,**kwargs)
        except BaseException as exc:
            write(str(prefix)+'-exception.json',{'type':type(exc).__name__,'message':str(exc)})
            raise
        write(str(prefix)+'-result.json',result)
        return result
    clia_process.invoke=observed
    return calls

def main(input_path,output):
    if sys.flags.optimize:
        raise ValueError('nonoptimized Python required')
    directory=Path(output); directory.mkdir()
    start=time.perf_counter(); cpu=time.process_time()
    state={'status':'CALLER_EXCEPTION','rewrite_dispatches':0}
    try:
        group=json.loads(Path(input_path).read_text())
        import qualification as Q
        import generation_stitch as G
        prepared=Q.prepare(group)
        expected={'manual':['orientation','bound_variables','existing_unary_binary','signed_nested'],
                  'train':['jmbl_fg_max3','jmbl_fg_mpg_guard2']}
        if [r['id'] for r in prepared]!=expected[group['group']]:
            raise ValueError('fixed group assignment mismatch')
        programs=[r['program'] for r in prepared]
        write(directory/'prepared.json',{'group':group['group'],'ids':[r['id'] for r in prepared],
                                        'programs':programs,'originals':[r['original'] for r in prepared]})
        state['calls']=observe_verifier(directory)
        donor=G.donor()
        abstraction=donor.Abstraction(**Q.RULE)
        write(directory/'rewrite-request.json',{'programs':programs,'abstractions':[vars(abstraction)],'kwargs':{}})
        state['rewrite_dispatches']=1
        try:
            returned=donor.rewrite(programs,[abstraction])
        except BaseException as exc:
            write(directory/'rewrite-exception.json',{'type':type(exc).__name__,'message':str(exc)})
            raise
        write(directory/'rewrite-return.json',returned.json) # before decode/check can refuse
        write(directory/'rewrite-programs.json',returned.rewritten)
        assessment=Q.assess(group,prepared,returned.rewritten)
        write(directory/'qualification.json',assessment)
        state.update(status='CALLER_RETURNED',qualification_status=assessment['status'])
    except BaseException as exc:
        state.update(qualification_status='CANNOT_CHECK_NORMALIZATION',
                     exception={'type':type(exc).__name__,'message':str(exc),'traceback':traceback.format_exc()})
        traceback.print_exc()
    state.update(caller_wall_s=time.perf_counter()-start,caller_self_cpu_s=time.process_time()-cpu,
        caller_self_peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        process_tree_cpu='UNKNOWN',process_tree_peak_rss='UNKNOWN',
        supplied_identity='IMPORTED_EXISTING_PRIMITIVE_NOT_LEARNED',compression='NOT_RUN',
        synthesis='NOT_RUN',persistence='NOT_RUN',useful_operator='NOT_ESTABLISHED',
        acquisition_cost='IMPORTED_PRIOR_NOT_EXECUTED_OR_CHARGED_HERE')
    write(directory/'caller-receipt.json',state)
    print(json.dumps(state),flush=True)
    return 0 if state['status']=='CALLER_RETURNED' else 2

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--input',required=True);p.add_argument('--output',required=True)
    a=p.parse_args();raise SystemExit(main(a.input,a.output))
