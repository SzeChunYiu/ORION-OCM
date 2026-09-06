"""M12 exposed A correction: adopted interpretation, conventional memory.

Unsupported surrounding chat routes remain explicit; this is not a whole-chat
or whole-lifetime parity certification. The historical regex parent is intact.
"""
import re
from ocm.chat.spelling import propose
from ocm.dialogue import clarify as CL
from ocm.language.chat_frontend import world_query, _describe, _strip, _is_question, _is_negated, parse_lexical_lesson, correction_body
from ocm.language.interpret import interpret, Verdict
from ocm.language.meaning import canonical
from .matched_parent import MatchedParent
from .semantic_memory import SemanticMemory


class SemanticParent(MatchedParent):
    def __init__(self, manifest):
        super().__init__(manifest)
        self.memory = SemanticMemory(manifest)
        self.pending = None
        self.last_frontend = {}
        self.last_lesson = None

    def save(self, path):
        self.memory.save(path)

    def load(self, path):
        self.memory.load(path)
        self.last_lesson = self.memory.lessons[-1]['id'] if self.memory.lessons else None
        self._counts()

    def _counts(self):
        self.info.update(lessons=len(self.memory.lessons), statements=len(self.memory.statements),
                         interaction_turns=self.memory.turn)

    def unsupported(self, route):
        self.last_frontend.update(parity='CANNOT_CHECK', reason=route)
        return f'I cannot interpret this route under the matched contract ({route}).'

    def say(self, text, speaker='user'):
        if not isinstance(text, str):
            raise TypeError('chat input must be text')
        self.memory.turn += 1
        self.last_frontend = dict(parity='SUPPORTED_DONOR_ROUTE', mechanism='chat_frontend+interpret',
                                  speaker=speaker, utterance=text)
        result = self._say(text, speaker)
        if self.last_frontend['parity'] == 'CANNOT_CHECK':
            reason = self.last_frontend['reason']
            m = self.memory.unsupported_routes
            m[reason] = m.get(reason, 0) + 1
        self._counts()
        return result

    def _say(self, text, speaker):
        m = self.memory
        low = text.strip().lower()
        if low.startswith('teach:'):
            match = re.fullmatch(r'teach:\s*([a-z][a-z_-]*)\s*=\s*([a-z][a-z _-]*?)(?: as (noun|verb))?', low)
            if not match:
                return self.unsupported('CANNOT_CHECK_ALIGNED_OR_CONSTRUCTION_LESSON_PARITY')
            try:
                word, concept, category = parse_lexical_lesson(text.strip()[6:])
            except ValueError:
                return self.unsupported('CANNOT_CHECK_INVALID_LESSON_PARITY')
            self.last_lesson = m.teach(word, concept, category)
            return f"Noted: '{word}' means {concept} ({self.last_lesson}). I will use it."
        if low.startswith(('revoke ', 'reinstate ')):
            action, target = text.strip().split(None, 1)
            action, target = action.lower(), target.strip()
            if target not in {r['id'] for r in m.lessons}:
                return self.unsupported('CANNOT_CHECK_NONLEXICAL_REVOCATION_PARITY')
            m.revoked.add(target) if action == 'revoke' else m.revoked.discard(target)
            return 'Revoked.' if action == 'revoke' else 'Reinstated.'
        if (low.startswith(('explain ', 'compare ', 'be ', 'summar', 'forget ', 'remember:',
                           'learn method ', 'find method:', 'run ', 'tell me about ',
                           'can you explain ', 'please explain ', 'what is ', "what's ", 'what’s '))
                or low.rstrip('.!?') in ('hello', 'hi', 'hey', 'thanks', 'thank you', 'help',
                                        'good morning', 'list skills', 'can you learn',
                                        'what can you do', 'what can you learn',
                                        'what skills have you learned', 'what methods do you know')
                or any(low in (f'please be {reg}', f'{reg} please', f'answer {reg}ly')
                       for reg in ('brief', 'detailed', 'formal', 'casual'))):
            return self.unsupported('CANNOT_CHECK_PLANNER_STYLE_OR_MEMORY_COMMAND_PARITY')
        spelling = propose(text, m.lexicon, m.revoked)
        if spelling.status != 'UNCHANGED':
            return self.unsupported('CANNOT_CHECK_SPELLING_INTERACTION_PARITY')
        query = world_query(low)
        if query is not None:
            self.last_frontend['world_query'] = list(query)
            return self._fact(*query)
        if self.pending is not None:
            self.pending = None
            return self.unsupported('CANNOT_CHECK_CLARIFICATION_ANSWER_PARITY')
        body, correction = correction_body(text)
        result = interpret(body, m.lexicon, m.constructions, speaker=speaker, revoked=m.revoked)
        self.last_frontend.update(verdict=result.verdict.value,
            candidates=[canonical(c.meaning)[1] for c in result.candidates])
        if result.verdict is Verdict.NEEDS_CONTEXT:
            return self.unsupported('CANNOT_CHECK_REFERENCE_PARITY')
        if result.verdict is Verdict.AMBIGUOUS:
            self.last_frontend.update(parity='CANNOT_CHECK',
                reason='CANNOT_CHECK_CLARIFICATION_POLICY_PARITY')
            cs = list(range(len(result.candidates)))
            describe = lambda c: _describe(result.candidates[c].meaning) + ' [' + ', '.join(sorted({n.label for n in result.candidates[c].meaning.nodes if n.label})) + ']'
            decision = CL.decide(cs, {'asserted': lambda c: canonical(result.candidates[c].meaning)[1]},
                                 CL.binary_questions(cs, describe), asked_before=m.asked)
            if decision.ask:
                self.pending = result
                m.asked.append(decision.question.question_id)
                return decision.question.text
            return f'Noted ({len(cs)} readings retained; {decision.reason}).'
        if result.verdict is not Verdict.INTERPRETED:
            return f'I cannot interpret this yet ({result.verdict.value}). Show me what it means.'
        meaning = result.meaning
        if _is_question(meaning):
            meaning = _strip(meaning, 'ASKS', 'question_variable')
            pos, neg = m.reports(meaning)
            if pos and neg:
                return 'Contradictory statements are on record: ' + ', '.join(s['id'] for s in pos + neg)
            rows = pos or neg
            return (f"{rows[0]['speaker']} said {'so' if pos else 'it did not'}; I have no independent warrant."
                    if rows else 'Unknown — nothing on record supports or denies it.')
        negated = _is_negated(meaning)
        base = _strip(meaning, 'NEGATES') if negated else meaning
        record = m.record(base, speaker, negated, correction, text)
        if record is None:
            return self.unsupported('CANNOT_CHECK_TOPIC_CORRECTION_PARITY')
        pos, neg = m.reports(base)
        reply = f"Noted: {speaker} says {'not ' if negated else ''}{_describe(base)}."
        if record['supersedes']:
            reply += f" This supersedes {record['supersedes']}."
        if pos and neg:
            reply += ' It contradicts another report; both are retained as speaker commitments.'
        return reply
