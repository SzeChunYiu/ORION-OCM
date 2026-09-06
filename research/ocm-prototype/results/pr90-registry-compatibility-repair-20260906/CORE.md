# PR90 mutable-registry and cache-accounting repair

This successor preserves the earlier digest repair at 57392b3f5d564de11743ac8b11dc27295b7c3aa2.
Only space.py and test_space_hotpath_efficiency.py change outside this evidence packet.
Owner: #72/#70 and PR90. Classification: INFRASTRUCTURE.

The registry is a public mutable object. Removing or replacing an existing type/relation
can invalidate retained objects. The local shortcut validated only additions and could
return a space whose own validate() immediately rejected; empty additions also bypassed
the original validation behavior.

with_atoms/with_edges now use their original dataclasses.replace implementations.
Both validate the entire resulting space against the current registry, including no-add calls.
The unused local-construction shortcut is removed. No new registry fingerprint or API is added.
Read-only lookup views, evidence caching, direct endpoint lookup and fresh digest remain.

Six regression cases cover removal of an old atom/relation type, both empty-add paths,
and replacement of each registry collection. Three positive cases cover ordinary valid
atom/edge additions and a valid registry extension.

index_resources now charges the two mapping-proxy containers and cached evidence frozenset.
Shared underlying dictionary entries are counted once; the evidence cache owns its entries.
The documentation explicitly covers shallow containers/entry counts, not recursive memory,
process RSS, total lifetime cost or asymptotic performance.

- Before this repair: 9 failures/14 passes (six registry cases and three accounting cases).
- Focused file after repair: 23 passed, including all eight earlier digest controls.
- M1 suite after repair: 80 passed; zero skips/errors.
- Original exact-source registry diagnostic and earlier repair history remain byte-preserved.

Original failure records are in original-review/. New red/green/M1 logs and JUnit, exact
source/test bindings and commands are recorded in verification.json and ARTIFACTS.json.
No main merge, full engineering recorder, scientific study or timing comparison ran here.
Current-source qualification remains due after integration with final main.
