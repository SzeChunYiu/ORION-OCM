import random

import a2_extension_v1 as x

core = x.load_audit_core()
pkgs = x.census_packages()
prim, unaud, cov, info = x.rederive_census(pkgs)
first_pass = sorted(p for p, v in pkgs.items() if v.get('L50', {}).get('surface') == 'UNAUDITED_OPERATOR_SURFACE')
screen_set = sorted(set(first_pass) | set(unaud))
package_blocks = {pkg: x.extract_blocks_all(pkg) for pkg in screen_set}
rng = random.Random(833215)
fam_tags = set(x.FAMILY_TAGS)
tagless = [(pkg, n, b) for pkg, blocks in package_blocks.items() for (n, b, k) in blocks
           if not (set(x.derive_signature(n, b)['tags_full']) & fam_tags)]
sample = tagless if len(tagless) <= 200 else rng.sample(tagless, 200)
f4, _ = x.match_families(core, [(n, x.derive_signature(n, b)) for _, n, b in sample], x.ALL_FAMILIES)
for fd in f4:
    for pkg, n, b in sample:
        if n == fd['primitive']:
            print("FLAG", fd['fingerprint'], pkg, n)
            print("SIG", x.derive_signature(n, b))
            print("BODY", b[:500].replace("\n", " | ")[:500])
