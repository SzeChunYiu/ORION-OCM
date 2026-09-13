"""Finite typed bytecode semantics; native internals stay separate obligations."""
import dis
import json
import operator
from dataclasses import dataclass
from typed_program_v1 import Refusal, require, value_ok

BINARY = {'+': operator.add, '-': operator.sub, '*': operator.mul,
          '^': operator.xor, '&': operator.and_, '|': operator.or_,
          '<<': operator.lshift, '>>': operator.rshift}
COMPARE = {'==': operator.eq, '!=': operator.ne, '<': operator.lt,
           '<=': operator.le, '>': operator.gt, '>=': operator.ge}
UNARY = {'UNARY_NEGATIVE': operator.neg, 'UNARY_POSITIVE': operator.pos,
         'UNARY_INVERT': operator.invert, 'UNARY_NOT': operator.not_}
NULL = object()

@dataclass(frozen=True)
class CallableRef:
    kind: str
    name: str

@dataclass(frozen=True)
class Result:
    value: object
    events: tuple

    @property
    def python_opcodes(self):
        return sum(e.startswith('py:') for e in self.events)

def obligation(kind, name, arg):
    return kind + ':' + name + ':' + json.dumps(arg, separators=(',', ':'))

def execute(program, entry, argument, chain=()):
    require(value_ok(argument), 'unresolved argument/implicit dispatch')
    require(entry in program.functions, 'entry must be a registered function')
    require(entry not in chain and len(chain) < 8, 'recursion/depth outside finite register')
    function = program.functions[entry]
    local, stack, events = {function.parameter: argument}, [], []
    for ins in dis.get_instructions(function.code, adaptive=False, show_caches=False):
        op = ins.opname
        if op in ('RESUME', 'CACHE'): continue
        events.append('py:' + op)
        if op in ('NOP', 'EXTENDED_ARG'): continue
        if op == 'LOAD_CONST':
            require(value_ok(ins.argval), 'untyped constant')
            stack.append(ins.argval)
        elif op in ('LOAD_FAST', 'LOAD_FAST_CHECK'):
            require(ins.argval in local, 'unbound local')
            stack.append(local[ins.argval])
        elif op == 'LOAD_GLOBAL':
            if ins.argrepr.startswith('NULL + '): stack.append(NULL)
            kind, value = program.binding(ins.argval)
            stack.append(value if kind == 'data' else CallableRef(kind, value))
        elif op == 'PUSH_NULL': stack.append(NULL)
        elif op == 'STORE_FAST':
            value = stack.pop()
            require(value_ok(value), 'callable aliases in locals are unsupported')
            local[ins.argval] = value
        elif op == 'UNPACK_SEQUENCE':
            value = stack.pop()
            require(type(value) is tuple and len(value) == ins.arg, 'exact tuple unpacking required')
            stack.extend(reversed(value))
        elif op == 'BUILD_TUPLE':
            values = tuple(stack[-ins.arg:]) if ins.arg else ()
            if ins.arg: del stack[-ins.arg:]
            require(value_ok(values), 'untyped tuple')
            stack.append(values)
        elif op in UNARY:
            value = stack.pop()
            require(type(value) in (int, bool), 'unresolved unary dispatch')
            stack.append(UNARY[op](value))
        elif op in ('BINARY_OP', 'COMPARE_OP', 'BINARY_SUBSCR'):
            right, left = stack.pop(), stack.pop()
            if op == 'BINARY_SUBSCR':
                require(type(left) is tuple and type(right) is int, 'unresolved subscription dispatch')
                require(-len(left) <= right < len(left), 'subscription outside tuple')
                stack.append(left[right])
            else:
                require(type(left) in (int, bool) and type(right) in (int, bool),
                        'unresolved numeric dispatch')
                table, key = (BINARY, ins.argrepr) if op == 'BINARY_OP' else (COMPARE, ins.argval)
                require(key in table, 'unmodeled numeric operation')
                require(key not in ('<<', '>>') or right >= 0, 'negative shift')
                stack.append(table[key](left, right))
        elif op == 'CALL':
            require(ins.arg == 1 and len(stack) >= 3, 'only unary static calls')
            arg, callee, null = stack.pop(), stack.pop(), stack.pop()
            require(null is NULL and type(callee) is CallableRef, 'unresolved call dispatch')
            require(value_ok(arg), 'untyped callee argument')
            if callee.kind == 'native':
                if callee.name == 'int':
                    require(type(arg) in (int, bool), 'int callback/type conversion forbidden')
                    value = int(arg)
                else:
                    require(callee.name == 'sum' and type(arg) is tuple
                            and all(type(x) in (int, bool) for x in arg), 'sum callback forbidden')
                    value = sum(arg)
                events.append(obligation('native', callee.name, arg))
            else:
                require(callee.kind in ('function', 'partial'), 'unresolved opaque work')
                if callee.kind == 'partial': events.append(obligation('adapter', callee.name, arg))
                inner = execute(program, callee.name, arg, chain + (entry,))
                events.extend(inner.events)
                value = inner.value
            stack.append(value)
        elif op == 'RETURN_VALUE':
            require(len(stack) == 1 and value_ok(stack[0]), 'invalid return stack/type')
            return Result(stack[0], tuple(events))
        elif op == 'RETURN_CONST':
            require(not stack and value_ok(ins.argval), 'invalid constant return')
            return Result(ins.argval, tuple(events))
        else:
            raise Refusal('unaccounted opcode: ' + op)
    raise Refusal('missing return')
