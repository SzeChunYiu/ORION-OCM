"""Independent native execution and opcode tracing; no timing/physical measure."""
import dis
import functools
import sys
from typed_program_v1 import require

def native_functions(program):
    functions, namespaces = {}, {}
    for name, spec in program.functions.items():
        namespace = {'__builtins__': {'int': int, 'sum': sum}}
        exec(compile(spec.source, '<independent-native>', 'exec'), namespace)
        functions[name] = next(v for k, v in namespace.items() if k != '__builtins__')
        namespaces[name] = namespace
    environment = dict(program.data)
    environment.update(functions)
    environment.update({name: functools.partial(functions[alias.target])
                        for name, alias in program.aliases.items()})
    for namespace in namespaces.values(): namespace.update(environment)
    return functions

def trace_native(program, entry, argument):
    """Register INSTRUCTION before a fresh function's first call; no priming."""
    functions = native_functions(program)
    maps = {fn.__code__: {i.offset: i.opname for i in dis.get_instructions(fn, show_caches=False)}
            for fn in functions.values()}
    events, unexpected = [], []
    def instruction(code, offset):
        name = maps[code][offset]
        if name not in ('RESUME', 'CACHE'): events.append('py:' + name)
    def start(code, offset):
        if code not in maps: unexpected.append(code.co_name)
    require(sys.implementation.name == 'cpython' and sys.version_info[:2] == (3, 12),
            'UNVERIFIABLE: native oracle requires the declared CPython3.12 layout')
    monitor = sys.monitoring
    free = [i for i in range(6) if monitor.get_tool(i) is None and monitor.get_events(i) == 0]
    require(bool(free), 'UNVERIFIABLE: no free monitoring tool identifier')
    tool = free[0]
    monitor.use_tool_id(tool, 'DCR finite native oracle')
    old_instruction = monitor.register_callback(tool, monitor.events.INSTRUCTION, instruction)
    old_start = monitor.register_callback(tool, monitor.events.PY_START, start)
    try:
        require(old_instruction is None and old_start is None, 'stale monitoring callbacks')
        for code in maps: monitor.set_local_events(tool, code, monitor.events.INSTRUCTION)
        monitor.set_events(tool, monitor.events.PY_START)
        result = functions[entry](argument)
        monitor.set_events(tool, 0)
    finally:
        monitor.set_events(tool, 0)
        for code in maps: monitor.set_local_events(tool, code, 0)
        monitor.register_callback(tool, monitor.events.INSTRUCTION, old_instruction)
        monitor.register_callback(tool, monitor.events.PY_START, old_start)
        monitor.free_tool_id(tool)
    require(events and not unexpected, 'empty trace or unmodeled native Python frame')
    return result, tuple(events)
