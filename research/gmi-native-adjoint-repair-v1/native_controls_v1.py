"""Actual VM controls; no search/ecology and no mutated historical payload."""
from source_loader_v1 import source_modules

def genotype(morph, affine=False):
    nodes={'input':('INPUT',{'width':1}),'dense':('DENSE',{'width':2 if affine else 1}),
           'linear':('LINEAR',{}),'output':('OUTPUT',{}),'target':('TARGET',{}),'grad':('GRAD',{'lr':1})}
    edges=[('dense','linear',0),('input','linear',1),('linear','output',0),
           ('dense','grad',0),('linear','grad',1),('target','grad',2)]
    if affine:
        nodes.update({'affine':('AFFINE',{'width':1}),'last':('DENSE',{'width':1})})
        edges=[e for e in edges if e[1]!='linear']+[
            ('dense','affine',0),('input','affine',1),('last','linear',0),('affine','linear',1)]
    return morph.make(nodes,edges)

def snapshot(M,label):
    return {'stage':label,'cells':dict(M.cells),'stores':dict(M.stores),'ledger':dict(M.L.c),
            'native_ops':M.L.native_ops,'emulated_ops':M.L.emulated_ops,
            'ops_by_kind':dict(M.L.ops_by_kind),'writes_in_event':sorted(M.L.writes_in_event),
            'event_write_fracs':list(M.L.event_write_fracs)}

def serialize_tape(root):
    nodes,seen=[],{}
    def visit(v):
        if id(v) in seen:return seen[id(v)]
        index=len(nodes);seen[id(v)]=index;nodes.append(None);parents=[]
        for par in v.parents:
            parents.append({'parameter':par[1]} if par[0]=='param'
                           else {'node':visit(par[0]),'local_derivative_fx':par[1]})
        nodes[index]={'node':index,'value_fx':v.v,'adjoint_fx':v.grad,'parents':parents}
        return index
    return {'root':visit(root),'nodes':nodes}

def run_control(version,x,target,basis_name='B0',affine=False):
    core,bases,morph,vm=source_modules(version)
    graph=genotype(morph,affine);M=core.Machine(getattr(bases,basis_name),seed=0)
    machine=vm.VM(graph,M,seed=0);machine.init()
    if affine:
        M.cells.update({'dense_w0':8,'dense_w1':16,'last_w0':16})
    stages=[snapshot(M,'initialization')];observations=[];original=machine._backprop
    def observe(out,err):
        item={'error_fx':err,'before':serialize_tape(out),'machine_tape':list(M.tape or [])}
        result=original(out,err)
        item.update({'after':serialize_tape(out),'parameter_adjoints_fx':dict(result)})
        observations.append(item);return result
    machine._backprop=observe
    M.phase('exec');before=machine.query(x);stages.append(snapshot(M,'query_before'))
    M.phase('upd');machine.feedback(x,target);stages.append(snapshot(M,'feedback_before_end_event'))
    M.end_event();stages.append(snapshot(M,'feedback_after_end_event'))
    M.phase('exec');after=machine.query(x);stages.append(snapshot(M,'query_after'))
    return {'source_version':version,'input':x,'target_fx':target,'basis':M.basis.spec(),
            'genotype':graph,'grad_outgoing_edges':[e for e in graph['edges'] if e[0]=='grad'],
            'outputs':{'before':before,'after':after},'stages':stages,'tape_observations':observations,
            'initialization_override':{'dense_w0':8,'dense_w1':16,'last_w0':16} if affine else {}}

def dot_control(module,weights,xs,seed,bias=None,names=None):
    core,bases,_,vm=module;M=core.Machine(bases.B0,seed=0)
    if names is None:names=['w'+str(i) for i in range(len(weights))]
    for name,w in zip(names,weights):
        if name not in M.cells:M.declare(name,'fx',w)
        elif M.read(name)!=w:raise ValueError('tied cell has inconsistent values')
    if bias is not None:M.declare('bias','fx',bias);names=list(names)+['bias']
    machine=vm.VM.__new__(vm.VM);machine.M=M
    out=machine._dot(names,[vm.Val(x) for x in xs],True)
    result=machine._backprop(out,seed)
    return out.v,result
