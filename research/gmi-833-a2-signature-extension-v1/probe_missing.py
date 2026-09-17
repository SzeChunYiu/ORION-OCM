import re

import a2_extension_v1 as x

pkg = 'gmi-section-d-uncertainty-extrap-v5'
pdir = x.RESEARCH / pkg
pat = re.compile(r"\s*[-*]\s*`[a-z_]")
for p in sorted(pdir.rglob('*')):
    if not p.is_file() or p.suffix not in ('.md', '.txt', '.py', '.json'):
        continue
    t = p.read_text(errors='replace')
    if not x.VOCAB_RE.search(t):
        continue
    hits = [line for line in t.splitlines() if pat.match(line)]
    if hits:
        print(p.name)
        for h in hits[:12]:
            print('   ', h[:110])
        other = [b for b in ('ops_assign', 'basis_phrase', 'def_op') ]
        print('   mdrow:', bool(re.search(r"\|\s*`[^`]{1,40}`\s*\|", t)))
