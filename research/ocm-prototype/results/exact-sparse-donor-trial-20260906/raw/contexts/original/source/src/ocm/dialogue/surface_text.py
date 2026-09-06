"""Read actual speech at the trusted boundary in registered bounded grammars.

Contextual 'said so' forms refer to the plan's question, source and evidence. Other
assertions are parsed as a world triple or by the registered clause interpreter.
This is not unrestricted English verification or a Python capability sandbox.
"""
from __future__ import annotations
import re
from typing import Iterable
from ocm.language.meaning import canonical

# The producer chooses a template. The checker below independently parses relations.
PHRASES = {'IS_A':'is a', 'LOCATED_IN':'is in', 'CAPITAL_OF':'is the capital of',
 'ORBITS':'orbits','PART_OF':'is part of','CONTAINS':'contains','BEFORE':'is before',
 'HAS_PROPERTY':'has property','HAS_COUNT':'has count','EQUALS':'equals',
 'BOILS_AT':'boils at','FREEZES_AT':'freezes at','HAPPENED_IN':'happened in',
 'HAPPENS_IN':'happens in','HAPPENS_AT':'happens at','USED_FOR':'is used for'}
RELATIONS = ((r'is the capital of','CAPITAL_OF'),(r'is part of','PART_OF'),
 (r'is used for','USED_FOR'),(r'is in','LOCATED_IN'),(r'is an?','IS_A'),
 (r'is before','BEFORE'),(r'orbits','ORBITS'),(r'contains','CONTAINS'),
 (r'has property','HAS_PROPERTY'),(r'has count','HAS_COUNT'),(r'equals','EQUALS'),
 (r'boils at','BOILS_AT'),(r'freezes at','FREEZES_AT'),(r'happened in','HAPPENED_IN'),
 (r'happens in','HAPPENS_IN'),(r'happens at','HAPPENS_AT'))
LABEL = re.compile(r'[a-zA-Z0-9][a-zA-Z0-9_ +/\-]*\Z')


def world_clause(meaning):
    if len(meaning.nodes)!=2 or len(meaning.edges)!=1:
        raise ValueError('CANNOT_CHECK: unregistered world-clause shape')
    e=meaning.edges[0]
    if len(e.tails)!=1 or len(e.heads)!=1 or e.relation not in PHRASES:
        raise ValueError('CANNOT_CHECK: unregistered world relation')
    a,b=meaning.node(e.tails[0]),meaning.node(e.heads[0])
    if any(n.node_type!='entity' or n.features or n.underspecified or not isinstance(n.label,str) or not LABEL.fullmatch(n.label) for n in (a,b)):
        raise ValueError('CANNOT_CHECK: world label/type requires another codec')
    value = ''
    if e.value is not None:
        if e.relation not in {'HAS_COUNT','BOILS_AT','FREEZES_AT'} or type(e.value) is not str or not re.fullmatch(r'-?[0-9]+(?:\.[0-9]+)?',e.value):
            raise ValueError('CANNOT_CHECK: unregistered quantity')
        value = e.value+' '
    subject = 'the '+a.label if a.label in {'moon','sun','earth'} else a.label
    s=f'{subject} {PHRASES[e.relation]} {value}{b.label}' 
    return s[0].upper()+s[1:]+'.'


def clause_matches(text, meaning, *, lexicon=None, constructions=None, revoked=()):
    if not isinstance(text,str) or not text or '\n' in text:
        return False
    core=text.strip().removesuffix('.').lower()
    # Never silently strip additional sentences, punctuation, negation or modalities.
    if len(meaning.nodes)==2 and len(meaning.edges)==1:
        from ocm.knowledge.world import triple
        readings=[]
        for pattern,relation in RELATIONS:
            # Enumerate every delimiter split, not only the first regex match.
            for match in re.finditer(r'(?= ('+pattern+r') )',core):
                a = core[:match.start()]
                b = core[match.start()+len(match[1])+2:]
                aliases = {'the moon':'moon','the sun':'sun','the earth':'earth'}
                a,b = aliases.get(a,a), aliases.get(b,b)
                value = None
                quantity = re.fullmatch(r'(-?[0-9]+(?:\.[0-9]+)?) (.+)',b)
                if quantity and relation in {'HAS_COUNT','BOILS_AT','FREEZES_AT'}:
                    value,b = quantity.groups()
                if a and b and all(LABEL.fullmatch(x) for x in (a,b)):
                    readings.append(triple(a,relation,b,value=value))
        return len(readings)==1 and canonical(readings[0])[1]==canonical(meaning)[1]
    from ocm.language.interpret import interpret, Verdict
    if lexicon is None:
        from ocm.language.bootstrap import microworld_lexicon
        lexicon=microworld_lexicon()
    if constructions is None:
        from ocm.language.constructions import seed_constructions
        constructions=seed_constructions()
    # Only this registered contraction is normalized; tokenize must not erase other content.
    if re.search(r'[^a-zA-Z0-9_\s\-\'?.]',text) or core.count('.') or '?' in core:
        return False
    reading=interpret(core.replace("didn't",'did not'),lexicon,constructions,revoked=frozenset(revoked))
    return reading.verdict is Verdict.INTERPRETED and canonical(reading.meaning)[1]==canonical(meaning)[1]


def check_text(plan,text,*,lexicon=None,constructions=None,revoked:Iterable=()):
    from .gate import Act, Marker, FeedbackEvent, FeedbackKind, REOPENS
    def fail(detail,kind=FeedbackKind.MEANING_DRIFT):
        return (FeedbackEvent(kind,detail,REOPENS[kind]),)
    if type(text) is not str:
        return fail('surface is not text')
    if plan.meaning is None:
        return () if not plan.assertions and plan.act not in (Act.ASSERT,Act.ANSWER) else fail('assertive act has no registered surface meaning')
    marker=plan.required_marker
    core=text
    evidence=tuple(dict.fromkeys(e for a in plan.assertions for e in a.evidence))
    if any(type(e) is not str or not re.fullmatch(r'[A-Za-z0-9_:/-]+',e) for e in evidence):
        return fail('evidence identifier cannot be represented in the registered citation grammar')
    if marker is Marker.NONE:
        return fail('semantic content needs an explicit epistemic marker',FeedbackKind.MARKER_MISMATCH)
    if marker is Marker.UNCERTAIN:
        if text in ('Unknown — nothing on record supports or denies it.',
                    'Contradictory statements are on record: '+', '.join(evidence)):
            return ()
        prefix='I am not sure whether '
        if not text.startswith(prefix):
            return fail('actual text lacks registered uncertainty marker',FeedbackKind.MARKER_MISMATCH)
        core=text[len(prefix):]
    elif marker is Marker.REPORTED:
        source=plan.source_name
        if type(source) is not str or not re.fullmatch(r'[A-Za-z0-9_:/ -]+',source):
            return fail('reported surface has no representable bound speaker/source')
        contextual=f'{source} said '+('it did not' if plan.reported_negative else 'so')
        if evidence and text==f'{contextual} ({evidence[0]}); I have no independent warrant.':
            return ()
        if plan.reported_negative:
            return fail('negative contextual report must preserve explicit polarity')
        prefix=f'A source ({source}) says so, but I have not verified it: '
        if text.startswith(prefix):
            core=text[len(prefix):]
        elif text.startswith(f'{source} said '):
            core=text[len(source)+6:]
        else:
            return fail('actual report source/marker differs from the bound plan',FeedbackKind.MARKER_MISMATCH)
    elif marker is Marker.ASSERTED:
        if text.startswith('Yes. '):
            core=text[5:]
            if evidence:
                suffix=f' That is a verified fact in my knowledge ({evidence[-1]}).'
                if not core.endswith(suffix):
                    return fail('actual citation/verification marker differs from plan')
                core=core[:-len(suffix)]
        elif text.startswith('Yes — '):
            suffix=f" ({', '.join(evidence)})."
            if not text.endswith(suffix):
                return fail('actual citation differs from plan')
            core=text[6:-len(suffix)]
    elif marker is Marker.DENIED:
        return fail('withdrawn support does not warrant denial of the proposition',FeedbackKind.UNSUPPORTED_ASSERTION)
    if not clause_matches(core,plan.meaning,lexicon=lexicon,constructions=constructions,revoked=revoked):
        return fail('actual surface does not parse uniquely to the planned meaning')
    return ()
