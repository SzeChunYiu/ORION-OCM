from pathlib import Path
_here = Path(__file__).resolve().parent
for _name in ('grammar_bias_core_v1.py','grammar_remint_v1.py','grammar_receipt_v1.py'):
    _path = _here / _name
    exec(compile(_path.read_text(), str(_path), 'exec'), globals())

def canonical_json(obj: object) -> str:
    return json.dumps(obj, indent=2, sort_keys=True, separators=(',', ': ')) + '\n'

def main() -> None:
    print(canonical_json(build_receipt()), end='')

if __name__ == '__main__':
    main()
