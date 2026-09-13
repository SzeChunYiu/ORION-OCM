"""Independent arithmetic and exact-polynomial finite differences."""
from fractions import Fraction
from itertools import product
from native_controls_v1 import dot_control
from source_loader_v1 import source_modules,require

def clip(v):return min(127,max(-128,v))
def qmul(a,b):return clip((a*b+8)//16)

def scalar_census():
    module=source_modules('corrected');values=(-128,-127,-64,-1,0,1,7,8,15,16,17,64,127)
    rows=[]
    for w,x,seed in product(values,repeat=3):
        out,grads=dot_control(module,[w],[x],seed)
        require(out==qmul(w,x) and grads.get('w0',0)==qmul(seed,x),'scalar reverse rule failed')
        rows.append([w,x,seed,out,grads.get('w0',0)])
    return rows

def exact_differences():
    module=source_modules('corrected');rows=[]
    for w,x,y in product((-16,0,16),(-16,-8,0,8,16),(-16,0,16)):
        out,_=dot_control(module,[w],[x],0);seed=out-y
        _,grads=dot_control(module,[w],[x],seed)
        plus,_=dot_control(module,[w+16],[x],0)
        minus,_=dot_control(module,[w-16],[x],0)
        lp=Fraction(plus-y,16)**2/2;lm=Fraction(minus-y,16)**2/2
        finite_difference=(lp-lm)/2
        analytic=Fraction(seed,16)*Fraction(x,16)
        require(finite_difference==analytic==Fraction(grads['w0'],16),'exact polynomial derivative mismatch')
        rows.append({'weight_fx':w,'input_fx':x,'target_fx':y,'gradient_fx':grads['w0'],
                     'finite_difference':[finite_difference.numerator,finite_difference.denominator]})
    return rows

def sharing_controls():
    module=source_modules('corrected');core,bases,_,vm=module
    tied=[]
    for x1,x2,seed in product((-16,0,16),repeat=3):
        out,grads=dot_control(module,[8,8],[x1,x2],seed,names=['tied','tied'])
        expected=clip(qmul(seed,x2)+qmul(seed,x1))
        require(grads.get('tied',0)==expected,'tied parameter contributions lost')
        tied.append([x1,x2,seed,out,grads.get('tied',0)])
    M=core.Machine(bases.B0);M.declare('w','fx',16)
    machine=vm.VM.__new__(vm.VM);machine.M=M
    one=machine._dot(['w'],[vm.Val(8)],True)
    root=vm.Val(M.op('ADD',one.v,one.v),[(one,16),(one,16)])
    shared=machine._backprop(root,16)
    require(shared=={'w':16},'shared downstream adjoint failed')
    M.declare('u','fx',8);M.cells['w']=8
    inner=machine._dot(['w'],[vm.Val(16)],True)
    outer=machine._dot(['u'],[inner],True)
    composed=machine._backprop(outer,outer.v)
    require(composed=={'w':2,'u':2},'composed multiplication adjoint failed')
    return {'tied':tied,'shared_value':root.v,'shared_adjoints':shared,
            'composed_value':outer.v,'composed_adjoints':composed}


def boundary_controls():
    module=source_modules('corrected')
    out,grads=dot_control(module,[64],[64],16)
    plus,_=dot_control(module,[80],[64],0);minus,_=dot_control(module,[48],[64],0)
    require(out==plus==minus==127 and grads['w0']==64,'saturation boundary control changed')
    bias=[]
    for x,seed in product((-16,0,16),repeat=2):
        _,g=dot_control(module,[8],[x],seed,bias=16)
        require(g['bias']==seed and g['w0']==qmul(seed,x),'bias identity path failed')
        bias.append([x,seed,g])
    _,ordered=dot_control(module,[8,8,8],[127,127,-128],16,names=['tied']*3)
    require(ordered['tied']==126,'ordered clamped accumulation changed')
    return {'saturation':{'three_forward_values':[minus,out,plus],
                         'central_output_difference':0,'registered_adjoint_fx':grads['w0'],
                         'literal_quantized_program_derivative_claimed':False},
            'bias_identity_cases':bias,'ordered_clamped_tied_adjoint':ordered}
