"""Ordinary persistent records over the adopted bounded-language donor.

No OCM runtime, executive, dialogue workspace or admission machinery. These
records retain attributed reports, not mathematical or world-truth claims.
"""
import json
import hashlib
from pathlib import Path
from ocm.language.chat_frontend import add_lexical_lesson, seed_frontend
from ocm.language import lexicon as L
from ocm.language.meaning import canonical


class SemanticMemory:
    def __init__(self, manifest):
        self.manifest = Path(manifest)
        self.statements, self.lessons, self.revoked, self.asked = [], [], set(), []
        self.turn = 0
        self.unsupported_routes = {}
        self.revoked_observations = set()
        self.rebuild()

    def rebuild(self):
        self.lexicon, self.constructions = seed_frontend(self.manifest)
        for row in self.lessons:
            add_lexical_lesson(self.lexicon, row['word'], row['concept'], row['id'], L.Category(row['category']))

    def teach(self, word, concept, category):
        eid = f'parent:lesson:{len(self.lessons) + 1}'
        self.lessons.append(dict(id=eid, word=word, concept=concept, category=category.value))
        add_lexical_lesson(self.lexicon, word, concept, eid, category)
        return eid

    def record(self, meaning, speaker, negated, correction, utterance):
        digest = canonical(meaning)[1]
        same = [s for s in self.statements if s['active'] and s['speaker'] == speaker and s['digest'] == digest]
        # The bounded correction covers explicit same-proposition replacement.
        # Topic-only replacement is an unsupported route, not silently emulated.
        if correction and not same:
            return None
        old = same[-1] if correction else None
        # Match the OCM observation donor's content identity, independently of
        # logical report IDs. Repeated bytes share support; a paraphrase does not.
        payload = dict(speaker=speaker, utterance=utterance, digest=digest,
                       negated=negated, supersedes=old['observation'] if old else None)
        observation = hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()
        record = dict(id=f'parent:report:{len(self.statements) + 1}', speaker=speaker,
                      digest=digest, meaning=json.loads(json.dumps(meaning.as_dict())), negated=negated,
                      observation=observation, active=observation not in self.revoked_observations,
                      turn=self.turn, supersedes=old['id'] if old else None)
        if old:
            self.revoked_observations.add(old['observation'])
            for prior in self.statements:
                if prior['observation'] == old['observation']:
                    prior['active'] = False
            old['superseded_by'] = record['id']
        self.statements.append(record)
        return record

    def reports(self, meaning):
        digest = canonical(meaning)[1]
        rows = [s for s in self.statements if s['active'] and s['digest'] == digest]
        return [s for s in rows if not s['negated']], [s for s in rows if s['negated']]

    def save(self, path):
        payload = {k: getattr(self, k) for k in ('statements', 'lessons', 'asked', 'turn', 'unsupported_routes')}
        payload['revoked'] = sorted(self.revoked)
        payload['revoked_observations'] = sorted(self.revoked_observations)
        path = Path(path)
        tmp = path.with_suffix('.tmp')
        tmp.write_text(json.dumps(payload, sort_keys=True))
        tmp.replace(path)

    def load(self, path):
        d = json.loads(Path(path).read_text())
        for k in ('statements', 'lessons', 'asked', 'turn', 'unsupported_routes'):
            setattr(self, k, d[k])
        self.revoked = set(d['revoked'])
        self.revoked_observations = set(d['revoked_observations'])
        self.rebuild()
