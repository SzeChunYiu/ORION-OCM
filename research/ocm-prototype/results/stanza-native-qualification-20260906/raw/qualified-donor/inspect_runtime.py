"""Pinned pipeline load/configuration inspection; never process text or execute a model."""
from pathlib import Path
from collections import Counter
import datetime, hashlib, importlib.metadata as metadata, json, resource, signal, socket, time
resource.setrlimit(resource.RLIMIT_AS, (8000000000, 8000000000))
resource.setrlimit(resource.RLIMIT_CPU, (120, 125))
signal.alarm(180)
start=time.monotonic(); cpu=time.process_time(); network_calls=[]; forwards=[]
def blocked_connect(*args, **kwargs):
    network_calls.append('BLOCKED'); raise RuntimeError('network forbidden during pinned inspection')
socket.socket.connect=blocked_connect; socket.create_connection=blocked_connect
import torch
import stanza
torch.set_num_threads(1); torch.set_num_interop_threads(1)
def blocked_forward(module, args):
    forwards.append(type(module).__name__); raise RuntimeError('model forward forbidden during qualification')
hook=torch.nn.modules.module.register_module_forward_pre_hook(blocked_forward)
def blocked_process(*args, **kwargs):
    raise RuntimeError('pipeline processing forbidden during qualification')
stanza.Pipeline.process=blocked_process
plan=json.loads(Path('/audit/plan.json').read_text()); packages=json.loads(Path('/audit/lock.json').read_text())
assert stanza.__version__=='1.14.0' and torch.__version__=='2.14.0+cpu'
assert torch.version.cuda is None
assert all(not any(x in p['name'].lower() for x in ('nvidia','cuda','triton','transformers','peft')) for p in packages['packages'])
for p in packages['packages']: assert metadata.version(p['name'])==p['version']
def sha(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''): h.update(b)
    return h.hexdigest()
expected={str(Path('/models') / Path(a['path']).relative_to('models')):a['sha256'] for a in plan['artifacts']}
assert {p:sha(p) for p in expected}==expected
assert sha('/models/resources.json')==plan['stanza']['resources_sha256']
loads=[]; original_load=torch.load
def bound_load(path,*args,**kwargs):
    name=str(Path(path).resolve()) if isinstance(path,(str,Path)) else None
    assert name in expected, 'unlisted model load: '+str(name)
    assert kwargs.get('weights_only') is True, 'restricted checkpoint loading required'
    loads.append(name); return original_load(path,*args,**kwargs)
torch.load=bound_load
options=dict(lang='en',dir='/models',package=None,
    processors={'tokenize':'combined_nocharlm','pos':'combined_nocharlm','lemma':'combined_nocharlm','depparse':'combined_nocharlm'},
    tokenize_pretokenized=True,download_method=None,resources_filepath='/models/resources.json',
    resources_version='1.14.0',use_gpu=False,device='cpu',verbose=False)
pipeline=stanza.Pipeline(**options)
assert set(pipeline.processors)=={'tokenize','pos','lemma','depparse'}
assert pipeline.processors['tokenize'].trainer is None
assert pipeline.processors['tokenize'].config['pretokenized'] is True
assert 'mwt' not in pipeline.processors
models=[]; processors={}; checkpoint_configs={}; modules=[]; parameters={}; storage={}; frozen_ids=set()
for name in ('pos','lemma','depparse'):
    processor=pipeline.processors[name]; trainer=processor.trainer; model=trainer.model
    args=trainer.args
    assert not args.get('bert_model') and not args.get('use_peft') and not args.get('charlm')
    assert getattr(model,'bert_model',None) is None
    assert getattr(model,'charmodel_forward',None) is None and getattr(model,'charmodel_backward',None) is None
    contextual=getattr(trainer,'contextual_lemmatizers',[])
    assert contextual==[], 'unexpected contextual lemma dependency'
    assert model is not None, 'identity/dictionary-only substitution is not this candidate'
    assert not processor.config.get('pretagged',False)
    config={k:v for k,v in args.items() if k in ('shorthand','bert_model','use_peft','charlm','charlm_forward_file','charlm_backward_file','pretrain','dict_only','word_emb_dim','tag_emb_dim','char_emb_dim','char_hidden_dim','hidden_dim','num_layers','transformed_dim','batch_size','max_steps','max_steps_before_stop','eval_interval','max_epoch','num_epoch')}
    # Training path strings are not an executable runtime dependency.
    config={k:(Path(v).name if isinstance(v,str) and ('/' in v or '\\' in v) else v) for k,v in config.items()}
    checkpoint_configs[name]=config
    local_count=0; local_frozen=0
    for key,p in model.named_parameters():
        assert p.device.type=='cpu'
        local_count+=p.numel(); local_frozen+=p.numel() if not p.requires_grad else 0
        sig=(p.untyped_storage().data_ptr(),p.storage_offset(),tuple(p.shape),tuple(p.stride()),str(p.dtype))
        parameters[sig]=p.numel()
        if not p.requires_grad:frozen_ids.add(sig)
        store=p.untyped_storage();storage[(store.data_ptr(),store.nbytes())]=store.nbytes()
    for module_name,module in model.named_modules():
        kind=type(module).__module__+'.'+type(module).__qualname__
        assert not any(x in kind.lower() for x in ('transformer','peft','multiheadattention','bert'))
        modules.append({'processor':name,'path':module_name,'class':kind})
    processors[name]={'class':type(processor).__module__+'.'+type(processor).__name__,
        'model_class':type(model).__module__+'.'+type(model).__name__,'parameters_nominal':local_count,
        'frozen_parameters_nominal':local_frozen,'contextual_lemma_classifiers':len(contextual),
        'configured_model':processor.config.get('model_path'),'pretrained_vectors':processor.config.get('pretrain_path'),
        'bert_model_attached':False,'charlm_attached':False,'peft_enabled':False}
    models.append(model)
assert not network_calls and not forwards
assert set(loads)==set(expected), 'runtime checkpoint closure differs from pinned four files'
assert {p:sha(p) for p in expected}==expected
assert sha('/models/resources.json')==plan['stanza']['resources_sha256']
result={'schema':'ocm.stanza-runtime-qualification.v1','status':'LOADED_RECURRENT_DEPENDENCY_CLOSURE_QUALIFIED_NO_INFERENCE',
    'completed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'versions':{'stanza':stanza.__version__,'torch':torch.__version__},
    'requested_options':options,'load_list':[[name,[spec._asdict() for spec in specs]] for name,specs in pipeline.load_list],
    'processors':processors,'loaded_checkpoints':loads,'checkpoint_configuration':checkpoint_configs,
    'unique_parameter_elements_by_identical_storage_view':sum(parameters.values()),
    'frozen_parameter_elements_deduplicated':sum(parameters[k] for k in frozen_ids),
    'unique_parameter_storage_bytes':sum(storage.values()),
    'module_class_counts':dict(Counter(x['class'] for x in modules)),
    'tokenizer_neural_model_loaded':False,'mwt_loaded':False,'contextual_lemma_classifiers':0,
    'network_connect_attempts':len(network_calls),'model_forward_calls':len(forwards),'processed_documents':0,
    'device':'cpu','cuda_runtime':torch.version.cuda,'cpu_threads':torch.get_num_threads(),
    'wall_seconds':time.monotonic()-start,'process_cpu_seconds':time.process_time()-cpu,
    'peak_rss_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
    'limits':'Architecture/load qualification only; no accuracy, useful-quality, heldout independence or efficiency result. Parameter storage excludes Python dictionaries, framework state and OS mappings; RSS is descriptive.'}
Path('/output/runtime-qualification.json').write_text(json.dumps(result,indent=2)+'\n')
Path('/output/loaded-modules.json').write_text(json.dumps(modules,indent=2)+'\n')
print(json.dumps({'status':result['status'],'unique_parameters':result['unique_parameter_elements_by_identical_storage_view'],'wall_seconds':result['wall_seconds'],'peak_rss_kib':result['peak_rss_kib']}))
