"""Exactly three setup commands; no synthesis declaration/constraint/query input."""
import hashlib
import importlib.metadata as metadata
import json
from pathlib import Path
import sys
import cvc5

path = Path(sys.argv[1]); request = json.loads(path.read_text())
commands = request['commands']
assert commands[:2] == ['(set-logic LIA)', '(set-option :output sygus-sol-gterm)']
assert len(commands) == 3 and commands[2] in ['(set-option :out stderr)', '(set-option :out "stderr")']
assert metadata.version('cvc5') == '1.3.4'
solver = cvc5.Solver()
options = [('sygus','true'),('incremental','false'),('tlimit-per','5000'),('check-synth-sol','true')]
for key, value in options:
    solver.setOption(key, value)
parser = cvc5.InputParser(solver)
parser.setStringInput(cvc5.InputLanguage.SYGUS_2_1, '\n'.join(commands)+'\n', 'setup-only')
result = {'input_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
          'version':metadata.version('cvc5'),'host_options':options,
          'attempted_commands':[],'dispatched_commands':[],
          'synth_fun_dispatched':0,'constraint_dispatched':0,'check_synth_dispatched':0}
try:
    for text in commands:
        result['attempted_commands'].append(text)
        command = parser.nextCommand()
        if command.isNull():
            raise ValueError('unexpected end of setup input')
        command.invoke(solver, parser.getSymbolManager())
        result['dispatched_commands'].append(text)
    result['status'] = 'SETUP_COMPLETE'
except Exception as exc:
    result.update(status='SETUP_REFUSED', error_type=type(exc).__name__, error=str(exc))
print(json.dumps(result))
raise SystemExit(0 if result['status']=='SETUP_COMPLETE' else 2)
