from pathlib import Path
import sys,json,time,signal,resource,collections,hashlib,platform
ROOT=Path('/home/billy/orion-director-work/20260906/language-g1-audit')
REPO=Path('/home/billy/orion-director-work/20260906/ocm-vessel')
sys.path.insert(0,str(REPO/'research/ocm-n1'))
from ud_induction import load_split,induce_lexicon,past_morphology
from ud_grammar import induce_grammar,parse_forms,is_projective,sentence_rules,gold_tree
resource.setrlimit(resource.RLIMIT_AS,(2*1024**3,2*1024**3))
class DevTimeout(Exception): pass
def timeout_handler(signum,frame): raise DevTimeout()
signal.signal(signal.SIGALRM,timeout_handler)
stages={}
t=time.perf_counter();train=load_split(ROOT/'data/en_ewt-ud-train.conllu','train');dev=load_split(ROOT/'data/en_ewt-ud-dev.conllu','dev');stages['custody_load_seconds']=time.perf_counter()-t
t=time.perf_counter();lex=induce_lexicon(train);stages['lexicon_induction_seconds']=time.perf_counter()-t
t=time.perf_counter();grammar=induce_grammar(train,min_attestations=1);stages['grammar_induction_seconds']=time.perf_counter()-t
t=time.perf_counter();morph=past_morphology(train);stages['morphology_inventory_seconds']=time.perf_counter()-t
known_rules={(r.lhs,r.pattern,r.family_id) for r in grammar.rules}
training={'sentences':len(train),'tokens_excluding_punct':lex.tokens,'lexeme_types':lex.lexeme_types,'form_types':lex.form_types,'attestations':len(lex.attestations),'rules':len(grammar.rules),'families':grammar.families,'order_hypotheses':grammar.order_hypotheses,'projective':grammar.projective_sentences,'nonprojective':grammar.nonprojective_sentences,'past_pairs':len(morph.past_pairs),'regular_ed_pairs':len(morph.regular_ed),'irregular_or_non_ed_pairs':len(morph.irregular_or_non_ed)}
(ROOT/'training-stages.json').write_text(json.dumps({'training':training,'stages':stages,'python':platform.python_version(),'train_source_sha256':hashlib.sha256((ROOT/'data/en_ewt-ud-train.conllu').read_bytes()).hexdigest()},indent=2)+'\n')
rows=[]
with (ROOT/'diagnostic-prefix50.jsonl').open('w') as stream:
 for index,sentence in enumerate(dev[:50]):
  tokens=[t for t in sentence.tokens if t.upos!='PUNCT'];forms=[t.form for t in tokens]
  row={'dev_index':index,'tokens':len(forms),'projective':is_projective(sentence),'lexical_gold_reading_covered':sum(any(lemma==tok.lower_lemma and upos==tok.upos for lemma,upos,_ in lex.form_readings.get(tok.lower_form,())) for tok in tokens),'surface_oov_tokens':sum(tok.lower_form not in lex.form_readings for tok in tokens)}
  if row['projective']:
   sr=sentence_rules(sentence);row['gold_rules']=len(sr);row['gold_rules_covered']=sum(r in known_rules for r in sr)
   t=time.perf_counter();signal.setitimer(signal.ITIMER_REAL,2.0)
   try:
    result=parse_forms(forms,lex,grammar,max_chart_nodes=10000)
    signal.setitimer(signal.ITIMER_REAL,0)
    gd=gold_tree(sentence).digest()
    row.update(status=result.status,chart_nodes=result.chart_nodes,derivations=result.derivations,structural_ambiguity=result.structural_ambiguity,root_count=len(result.roots),gold_in_candidate_set=any(r.tree.digest()==gd for r in result.roots),unique_correct=result.status=='PARSED' and len(result.roots)==1 and result.roots[0].tree.digest()==gd)
   except DevTimeout: row.update(status='EXTERNAL_PER_SENTENCE_TIME_BOUND')
   except MemoryError: row.update(status='EXTERNAL_ADDRESS_SPACE_BOUND')
   finally:signal.setitimer(signal.ITIMER_REAL,0)
   row['parse_wall_seconds']=time.perf_counter()-t
  else:row.update(status='CANNOT_CHECK_PROJECTIVITY')
  rows.append(row);stream.write(json.dumps(row)+'\n');stream.flush()
summary={'role':'DEVELOPMENT_DIAGNOSTIC_ONLY','selection':'same first50 official dev sentences; no length/OOV/gold-rule filter','existing_parser_unmodified':True,'max_chart_nodes':10000,'external_per_sentence_seconds':2.0,'address_space_bytes':2*1024**3,'training':training,'stages':stages,'sentences':len(rows),'statuses':dict(collections.Counter(r['status'] for r in rows)),'gold_in_candidate_set_count':sum(r.get('gold_in_candidate_set',False) for r in rows),'singleton_correct_count':sum(r.get('unique_correct',False) for r in rows),'sentence_lengths':[r['tokens'] for r in rows],'parse_seconds_total':sum(r.get('parse_wall_seconds',0) for r in rows),'maxrss_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,'protected_claim_authority':False,'selected_decoder':'NONE; singleton correctness only diagnostic'}
(ROOT/'diagnostic-summary.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary))
