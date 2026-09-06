"""Faithful ordinary persistent program library: same program/check/cache/support powers."""
import json
from pathlib import Path
import time
import clia_reuse_descriptor as D
from clia_reuse_apply import CompiledProgram, check_value


class NativeLibrary:
    def __init__(self, root):
        self.root = Path(root); self.root.mkdir(parents=True, exist_ok=True)
        self._bound = {}; self.stats = dict(rebinds=0, applications=0, pointwise_checks=0, synthesis_calls_in_library=0, counter_scope="LIBRARY_ONLY; external acquisition requires runner metering", universal_check_receipts=[])
        self.revocations = self.root / 'revoked.json'
        self.revoked = set(json.loads(self.revocations.read_text())) if self.revocations.exists() else set()

    def path(self, key):
        if not isinstance(key, str) or len(key) != 64 or any(c not in '0123456789abcdef' for c in key):
            raise ValueError('invalid descriptor identity')
        return self.root / (key + '.json')

    def load(self, key):
        desc = D.validate(json.loads(self.path(key).read_text()))
        if desc['id'] != key: raise ValueError('library identity mismatch')
        return desc

    def _persist(self, desc):
        path = self.path(desc['id'])
        if path.exists():
            if self.load(desc['id']) != desc: raise ValueError('immutable program collision')
        else:
            with path.open('x') as f: json.dump(desc, f, sort_keys=True)
        return desc['id']

    def acquire(self, task, candidate, support, *, history=()):
        """One shared universal check; same entry cost as vessel adoption."""
        desc = D.create(task, candidate, support, history=history)
        self.stats['universal_check_receipts'].append(desc['universal_check'])
        return self._persist(desc)

    def install(self, descriptor):
        """Import an externally supplied descriptor: verify it, do not trust its PASS field."""
        return self._persist(D.verify_import(descriptor, self.stats['universal_check_receipts']))

    def bind(self, key):
        start = time.perf_counter(); desc = self.load(key)
        if D.liveness(desc['support'], self.revoked) != 'LIVE': raise ValueError('program support is not live')
        self._bound[key] = CompiledProgram(desc); self.stats['rebinds'] += 1
        return {'program_id': key, 'bind_wall_s': time.perf_counter() - start}

    def apply(self, request):
        start = time.perf_counter()
        try:
            desc = self.load(request['program_id'])
            live = D.liveness(desc['support'], self.revoked)
            if live != 'LIVE': return {'status': 'REFUSED_' + live + '_SUPPORT', 'answer': None}
            if desc['id'] not in self._bound: return {'status': 'CANNOT_CHECK_UNBOUND', 'answer': None}
            self.stats['applications'] += 1
            output = self._bound[desc['id']].apply(request)
            self.stats['pointwise_checks'] += 1
            receipt = check_value(desc, request, output)
            if receipt['status'] != 'PASS': return {'status': 'WRONG_APPLICATION', 'answer': None, 'check': receipt}
            record = {'request': request, 'answer': output, 'check': receipt, 'support': desc['support']}
            identity = D.digest(record)
            path = self.root / ('answer-' + identity + '.json')
            if not path.exists():
                with path.open('x') as f: json.dump(record, f, sort_keys=True)
            return {'status': 'ACCEPTED_PARENT', 'answer': output, 'check': receipt, 'record_id': identity,
                    'support': desc['support'], 'stats': dict(self.stats), 'apply_wall_s': time.perf_counter() - start}
        except (OSError, ValueError, KeyError, TypeError) as exc:
            return {'status': 'CANNOT_CHECK_APPLICATION', 'answer': None, 'reason': str(exc)}

    def answer_liveness(self, record_id):
        self.path(record_id)  # Validate spelling before using it in an answer filename.
        record = json.loads((self.root / ('answer-' + record_id + '.json')).read_text())
        if D.digest(record) != record_id: raise ValueError('answer record changed')
        return D.liveness(record['support'], self.revoked)

    def audit(self):
        programs, answers = {}, {}
        for path in sorted(self.root.glob('*.json')):
            if path.name == 'revoked.json': continue
            if path.name.startswith('answer-'):
                key = path.stem[7:]
                answers[key] = {'liveness': self.answer_liveness(key)}
            else:
                desc = self.load(path.stem)
                programs[desc['id']] = {'liveness': D.liveness(desc['support'], self.revoked),
                    'support': desc['support'], 'history_only': desc['history_only'],
                    'program_sha256': desc['program_sha256'], 'host_bound': desc['id'] in self._bound}
        return {'programs': programs, 'answers': answers, 'revoked': sorted(self.revoked), 'stats': dict(self.stats)}

    def _revise(self, evidence, withdraw):
        if not isinstance(evidence, list) or any(not isinstance(e, str) for e in evidence): raise ValueError('evidence list required')
        self.revoked = self.revoked.union(evidence) if withdraw else self.revoked.difference(evidence)
        temporary = self.revocations.with_suffix('.tmp')
        temporary.write_text(json.dumps(sorted(self.revoked)))
        temporary.replace(self.revocations)

    def revoke(self, evidence): self._revise(evidence, True)
    def reinstate(self, evidence): self._revise(evidence, False)
