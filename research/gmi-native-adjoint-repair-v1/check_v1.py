"""Source-bound finite adjoint repair; no historical record is regenerated."""
from pathlib import Path
import hashlib
import json
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from source_loader_v1 import ROOT,require,verify_corrected_sources
from native_controls_v1 import run_control
from adjoint_reference_v1 import scalar_census,exact_differences,sharing_controls,boundary_controls

def equal(a,b):return json.dumps(a,sort_keys=True)==json.dumps(b,sort_keys=True)

def historical_packet():
    root=ROOT/'raw/pr551-grad-audit-20260913'
    manifest=(root/'AUDIT_MANIFEST_V1.json').read_bytes()
    require(hashlib.sha256(manifest).hexdigest()=='6aa6a24361c43a8086fa303ab41a692cc230a57c441b94265d03f1f52b6c715b',
            'historical manifest drift')
    record=json.loads(manifest)
    names={p.relative_to(root).as_posix() for p in root.rglob('*') if p.is_file()}
    require(names==set(record['files'])|{'AUDIT_MANIFEST_V1.json'},'historical membership drift')
    for name,row in record['files'].items():
        path=root/name;require(not path.is_symlink(),'historical symlink')
        data=path.read_bytes()
        require(len(data)==row['bytes'] and hashlib.sha256(data).hexdigest()==row['sha256'],'historical content drift')
    return {name:json.loads((root/name).read_text()) for name in
            ('GRAD_SIDE_EFFECT_CONTROL_V1.json','ZERO_INPUT_ADJOINT_CONTROL_V1.json')}

def run_checks():
    sources=verify_corrected_sources();historical=historical_packet();rows={}
    for basis in ('B0','B1'):
        for version in ('old','corrected'):
            for name,x,y,affine in [('zero_input',0,16,False),('nonzero_input',1,0,False),('affine_bias',0,0,True)]:
                row=run_control(version,x,y,basis,affine);rows[basis+'/'+version+'/'+name]=row
                gradients=row['tape_observations'][0]['parameter_adjoints_fx'];last=row['stages'][-1]['cells']
                if name=='zero_input':
                    require(gradients['dense_w0']==(-16 if version=='old' else 0),'zero-input adjoint failed')
                    require(last['dense_w0']==(9 if version=='old' else 8),'zero-input update failed')
                elif name=='nonzero_input':
                    require(gradients['dense_w0']==8 and last['dense_w0']==7,'known nonzero no-alarm failed')
                else:
                    require(gradients['dense_w1']==16 and last['dense_w1']==15,'AFFINE bias path changed')
                    require(last['dense_w0']==(7 if version=='old' else 8),'AFFINE zero-weight path failed')
                require(not row['grad_outgoing_edges'],'GRAD side-effect control unexpectedly has output edge')
    positive=historical['GRAD_SIDE_EFFECT_CONTROL_V1.json'];zero=historical['ZERO_INPUT_ADJOINT_CONTROL_V1.json']
    old=rows['B0/old/nonzero_input'];oldzero=rows['B0/old/zero_input']
    require(equal(old['stages'],positive['stages']) and equal(old['outputs'],positive['observed']),
            'original full state/ledger no-alarm failed')
    require(equal(oldzero['stages'],zero['stages']) and equal(oldzero['outputs'],zero['observed_outputs'])
            and equal(oldzero['tape_observations'],zero['tape_observations']), 'original full zero tape differs')
    for basis in ('B0','B1'):
        require(equal(rows[basis+'/old/nonzero_input']['stages'],rows[basis+'/corrected/nonzero_input']['stages']),
                'nonzero control changed state/ledger')
    scalars=scalar_census();differences=exact_differences();sharing=sharing_controls();boundaries=boundary_controls()
    return {'schema':'GMI_NATIVE_PARAMETER_ADJOINT_REPAIR_RECEIPT_V1','status':'PASS',
            'scope':'parameter leaf attribution under the registered ordered clamped pullback; no capability inference',
            'source_bindings':sources,'complete_historical_controls':historical,
            'native_vm_controls':rows,'scalar_fixed_point_cases':scalars,
            'exact_polynomial_finite_differences':differences,'sharing_controls':sharing,
            'boundary_controls':boundaries,'counts':{'scalar_cases':len(scalars),'finite_differences':len(differences),
                'tied_cases':len(sharing['tied']),'native_vm_controls':len(rows),'shared_and_composed_cases':2,
                'bias_cases':9,'clamped_tied_case':1,'saturation_boundary_case':1},
            'historical_authority_preserved':True,
            'not_claimed':['derivative of discontinuous quantized execution','global learning/capability improvement',
                           'new ecology/campaign result','physical cost or complete metering guarantee']}

if __name__=='__main__':print(json.dumps(run_checks(),indent=2,sort_keys=True))
