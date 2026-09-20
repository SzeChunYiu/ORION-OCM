"""Independent test fixtures from the immutable contract and actual evidence."""
from copy import deepcopy
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SCIENCE = ROOT/'research/gmi-1068-corrected-targets-v16'


def load(name):
    spec = importlib.util.spec_from_file_location(name,HERE/(name+'.py'))
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


structure = load('ledger_structure_v16')
evidence = load('ledger_evidence_v16')
custody = load('custody_v16')


def digest(value):
    raw = json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()
    return hashlib.sha256(raw).hexdigest()


def contract():
    return custody.read_contract(ROOT)


def baseline(contract):
    return {'schema':'GMI_1068_AMENDMENT_LEDGER_V16','control_plane':1068,
            'protocol_freeze_commit':structure.FREEZE,'contract_sha256':structure.CONTRACT_SHA,
            'original_snapshot':{'path':structure.SNAPSHOT,'sha256':contract['source_bindings'][structure.SNAPSHOT]},
            'previous_ledger':None,'targets':deepcopy(contract['original_targets']),'events':[]}


def append(ledger,kind,identifier,payload):
    events = ledger['events']
    events.append({'seq':len(events),'previous_sha256':digest(events[-1]) if events else None,
                   'type':kind,'id':identifier,'payload':deepcopy(payload)})


def rebind(ledger):
    previous = None
    for event in ledger['events']:
        event['previous_sha256'] = previous
        previous = digest(event)
    return ledger


def successor(ledger):
    result = deepcopy(ledger)
    result['previous_ledger'] = {'sha256':digest(ledger),'event_count':len(ledger['events'])}
    return result


def revisions(contract):
    ledger = baseline(contract)
    for i,revision in enumerate(contract['permitted_revisions']):
        append(ledger,'REVISION','revision-'+str(i),revision)
    return ledger


def actual_evidence():
    receipt = json.loads((SCIENCE/'RESULT_V16.json').read_text())
    review = hashlib.sha256((SCIENCE/'REVIEW_V16.md').read_bytes()).hexdigest()
    return receipt,review


def attestation(revision,receipt,review,verdict='VERIFIED'):
    raw = json.dumps(receipt,indent=2,sort_keys=True)+'\n'
    return {'revision_id':revision['revision_id'],'kind':'REFUTATION_AND_REPLACEMENT',
            'statement_ids':deepcopy(revision['required_statements']),'verdict':verdict,
            'science_sha256':hashlib.sha256(raw.encode()).hexdigest(),'review_sha256':review}


def attested(contract,receipt,review):
    ledger = revisions(contract)
    for i,revision in enumerate(contract['permitted_revisions']):
        append(ledger,'ATTEST','attest-'+str(i),attestation(revision,receipt,review))
    return ledger


def retract(ledger,attestation_id,identifier='retract-one'):
    append(ledger,'RETRACT',identifier,{'attestation_id':attestation_id,
           'reason':'independent recheck withdrew current authority','evidence_sha256':'1'*64})
