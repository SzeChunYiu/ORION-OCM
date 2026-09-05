"""Exact checker for the public four-operation polynomial task; no OCM imports."""
import argparse
import json
from fractions import Fraction

p = argparse.ArgumentParser()
p.add_argument('--program', required=True, help='comma-separated inc,dec,double,square')
p.add_argument('--coefficients', required=True, help='constant coefficient first')
p.add_argument('--x')
a = p.parse_args()
program = a.program.split(',') if a.program else []
if len(program) > 8 or any(x not in ('inc', 'dec', 'double', 'square') for x in program):
    raise SystemExit('outside the declared grammar')
coefficients = [Fraction(0), Fraction(1)]
for op in program:
    if op == 'inc': coefficients[0] += 1
    elif op == 'dec': coefficients[0] -= 1
    elif op == 'double': coefficients = [2*x for x in coefficients]
    else:
        product = [Fraction(0)] * (2*len(coefficients)-1)
        for i, left in enumerate(coefficients):
            for j, right in enumerate(coefficients): product[i+j] += left*right
        coefficients = product
target = [Fraction(x) for x in a.coefficients.split(',')]
while len(coefficients)>1 and coefficients[-1]==0: coefficients.pop()
while len(target)>1 and target[-1]==0: target.pop()
result = {'identity_verified': coefficients==target,
          'program': program, 'coefficients': [str(x) for x in coefficients]}
if a.x is not None:
    value = Fraction(a.x)
    for op in program:
        if op=='inc': value+=1
        elif op=='dec': value-=1
        elif op=='double': value*=2
        else: value*=value
    result['input'] = a.x
    result['value'] = str(value)
print(json.dumps(result, sort_keys=True))
raise SystemExit(0 if result['identity_verified'] else 1)
