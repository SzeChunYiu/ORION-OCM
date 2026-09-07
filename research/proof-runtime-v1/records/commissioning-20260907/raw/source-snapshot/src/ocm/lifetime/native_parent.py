"""M12 conventional parent; constructs no OCM runtime or ChatSession.

Only exposed A/E parity is corrected. Historical science/revision/repair
procedures retain their declared limitations; no strongest-whole-system claim.
"""
import hashlib
import json
from pathlib import Path
from ocm.comparators.semantic_parent import SemanticParent
from ocm.comparators.matched_parent import MatchedParent
from ocm.data import default_manifest_path
from ocm.evaluation.m9_transfer_eval import SkillLibraryArm


class WholeSystemParent:
    name = 'whole_system_parent'

    def __init__(self, root: Path, *, frontend='semantic'):
        if frontend not in ('semantic', 'legacy_regex_ablation'):
            raise ValueError('unregistered frontend')
        self.root = Path(root) / 'parent'
        self.root.mkdir(parents=True, exist_ok=True)
        self.frontend = frontend
        self.parent_class = SemanticParent if frontend == 'semantic' else MatchedParent
        self.p = self.parent_class(default_manifest_path())
        self.state = self.root / 'parent.json'
        self.last_lesson = None
        self.last_frontend = {}
        self.work = SkillLibraryArm()
        self.phase_log, self.revoked_domains = [], set()

    def say(self, utt, speaker='user'):
        if utt == '__restart__':
            self.p.save(self.state)
            self.p = self.parent_class(default_manifest_path())
            self.p.load(self.state)
            self.last_frontend = dict(parity='SUPPORTED_DONOR_ROUTE' if self.frontend == 'semantic' else 'CANNOT_CHECK', route='restart')
            return 'restarted'
        if utt == '__revoke_last_lesson__':
            utt = f'revoke {self.last_lesson}'
        if self.frontend == 'semantic':
            reply = self.p.say(utt, speaker)
            self.last_frontend = dict(self.p.last_frontend)
            if utt.strip().lower().startswith('teach:'):
                self.last_lesson = self.p.last_lesson
        else:
            reply = self.p.say(utt)
            self.last_frontend = dict(parity='CANNOT_CHECK', reason='LEGACY_REGEX_AND_SPEAKER_ABLATION')
            if utt.strip().lower().startswith('teach:'):
                self.last_lesson = utt[len('teach:'):].split('=')[0].strip()
        self.p.save(self.state)
        return reply

    def identity(self):
        return dict(state_file=str(self.state), skills=sorted(self.work.skills), lessons=self.p.info.get('lessons'))

    def state_digest(self):
        self.p.save(self.state)
        payload = self.state.read_bytes() + json.dumps(self.identity(), sort_keys=True).encode()
        return hashlib.sha256(payload).hexdigest()[:16]

    def acquire(self, domain, ops, tasks, withheld):
        return self.work.acquire(domain, ops, tasks, withheld)

    def solve(self, domain, ops, task):
        return None if domain in self.revoked_domains else self.work.solve(domain, ops, task)

    def revoke_domain_demo(self, domain):
        self.revoked_domains.add(domain)
        return f'parent-flag:{domain}'

    def info(self):
        return {**self.p.info, 'work_skills': len(self.work.skills), 'protected_exposure': 0,
                'channels': ['manifest', 'lessons', 'corrections', 'demonstrations', 'oracle_observations', 'revocation_notices'],
                'undeclared_channels': 'NONE_DECLARED',
                'assumption_ids': ['manifest:curated:v1', 'manifest:almanac:v1', 'manifest:rumour:v1'],
                'identification_verdict_type': 'GUARANTEED_IDENTIFICATION_NOT_CLAIMED',
                'frontend': self.frontend,
                'unsupported_routes': dict(self.p.memory.unsupported_routes) if self.frontend == 'semantic' else {},
                'restart_scope': 'LANGUAGE_SESSION_ONLY',
                'whole_system_parity': 'CANNOT_CHECK', 'comparison_scope': 'EXPOSED_A_E_ONLY_WITH_UNSUPPORTED_ROUTES'}

    def resources(self):
        self.p.save(self.state)
        return dict(persistent_bytes=self.state.stat().st_size, ledger_events=0, kso_atoms=None, external_io=0)
