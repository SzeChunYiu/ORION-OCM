# -*- coding: utf-8 -*-
"""Independent verifier for the Section Z comment reconciliation.

Re-reads a live fetch of issue comment 5684819296 and re-checks every entry
without reusing the builder's data structures: byte-exactness, uniqueness in the
whole body, uniqueness under the declared ### anchor, that no `old` is already
checked, that every `new` preserves its row text verbatim, that no row appears in
two buckets, and that all 131 rows are accounted for exactly once.

Usage:
  gh api repos/SzeChunYiu/ORION-OCM/issues/comments/5684819296 --jq .body > body.md
  python3 -I -B research/gmi-833-z-map-v1/check_sec_z4_reconciliation_v1.py \
      body.md research/gmi-833-z-map-v1/ISSUE_833_COMMENT_RECONCILIATION_V1.json
"""
import hashlib, io, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
BODY = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, 'live_body.md')
RECON = (sys.argv[2] if len(sys.argv) > 2
         else os.path.join(HERE, 'ISSUE_833_COMMENT_RECONCILIATION_V1.json'))

body = io.open(BODY, encoding='utf-8').read()
raw = io.open(BODY, 'rb').read()
d = json.load(io.open(RECON, encoding='utf-8'))

fail = []
if d['comment_sha256_at_build'] != hashlib.sha256(raw).hexdigest():
    fail.append('sha256 drift since build')
if d['comment_bytes_at_build'] != len(raw):
    fail.append('byte length drift')

seen = set()
for r in d['replacements']:
    o = r['old']
    if body.count(o) != 1:
        fail.append('old not unique: %r (%d)' % (o[:60], body.count(o)))
    if not o.startswith(u'- [ ] '):
        fail.append('old not unchecked: %r' % o[:60])
    if not r['new'].startswith(u'- [x] ' + o[len(u'- [ ] '):]):
        fail.append('new does not preserve the row text: %r' % o[:60])
    if u' — ✅ ' not in r['new']:
        fail.append('new lacks the evidence marker: %r' % o[:60])
    if r['anchor'] not in body:
        fail.append('anchor missing: %r' % r['anchor'])
    # the old row must sit under its declared anchor
    seg = body.split(r['anchor'], 1)[1].split('\n### ', 1)[0]
    if seg.count(o) != 1:
        fail.append('old not under its anchor: %r' % o[:60])
    if o in seen:
        fail.append('duplicate entry: %r' % o[:60])
    seen.add(o)

for r in d['not_closed']:
    o = r['row']
    if body.count(o) != 1:
        fail.append('not_closed row not unique: %r' % o[:60])
    if not o.startswith(u'- [ ] '):
        fail.append('not_closed row already checked: %r' % o[:60])
    if o in seen:
        fail.append('row appears twice: %r' % o[:60])
    seen.add(o)
    if not r['reason'].strip():
        fail.append('empty reason: %r' % o[:60])

for r in d['already_applied']:
    o = r['line']
    if not o.startswith(u'- [x] '):
        fail.append('already_applied row is not checked: %r' % o[:60])
    if o in seen:
        fail.append('row appears twice: %r' % o[:60])
    seen.add(o)

total = len(d['replacements']) + len(d['not_closed']) + len(d['already_applied'])
if total != 131:
    fail.append('total %d != 131' % total)
if len(seen) != 131:
    fail.append('distinct rows %d != 131' % len(seen))

# every row of the live body must be accounted for exactly once
live_rows = [l for l in body.split('\n') if l.startswith('- [')]
for l in live_rows:
    if l not in seen:
        fail.append('live row unaccounted: %r' % l[:60])

print('VERIFY:', 'OK' if not fail else 'FAIL')
for f in fail:
    print('  -', f)
sys.exit(1 if fail else 0)
