# Internal review, exposure and negative-result log

Date: 2026-09-07. Five user-requested AI roles worked alongside the coordinating session. These are computational research assistants, not human expert credentials, external reviewers or five independent scientific replications.

| Role | Background/task perspective | Contribution and disagreement |
|---|---|---|
| T1 | Algebra, operational semantics, finite reachability | Derived cyclic rank/word-cost examples; independently authored pair-composition/layer checker. Challenged T5's wrong residue vector. |
| T2 | Cognitive architecture and field representation | Read primary architecture donors; narrowed architectural correspondences; caught unbounded restoration identities in prospective tournament. |
| T3 | Synthesis, library learning, primitive admission | Reduced macro symbols to definitional extensions; audited resource model; caught V1/V2 primary-route inconsistency; restricted primitive-pressure inference. |
| T4 | Epistemology, support, verification | Derived support-state lower bound; distinguished alternate support from invalidation; reviewed primary support/diagnosis source and found graph/terminal wording gap. |
| T5 | Hostile theory referee | Attacked hidden controller/interpreter power and diagnosis leakage; reviewed exact specification; disclosed preliminary computation and arithmetic correction. |
| Coordinator | Scope, source custody, integration | Retrieved programme issues, isolated worktree, authored primary checker and comparison tool, reconciled findings into registry and checkpoint. |

Roles exchanged substantive findings. The final source reviews were text-only where stated. The independent checker did not import/read the primary checker while being authored, but both share the specification, host, team communications and research framing. This does not discharge #144 external or fresh-host replication gates.

## Access and chronology

1. Read latest GitHub #143/#144/#145 bodies and comments. Their pilot summaries and corrections became known. Comment timestamps were absent in connector output for some entries; preserve source URLs and bodies rather than inventing times.
2. Retrieved #93/#50/#62/#72 and ORION #507/#500/#501/#506/#508/#512, then V2 #304/#353/#358/#361. Archived issue payloads in sources/; these are source snapshots, not independent verification of the outcomes they mention.
3. Read the empirical branch's public STUDY_CARDS_V1.md via connector, blob SHA 9a9ecc4ae7390a8ce0a24326fa161aafc3fcd28c. Its bytes/revocation wording is superseded by the latest #143 correction. No empirical executable was run and no protected raw dataset/seed/split was opened.
4. Fetched OCM main and created a separate theory worktree at f9d2ff21e066328495638e8d3010107d8b91f018. Existing worktree files were not modified. Work stayed under research/cognitive-theory.
5. T1/T4 supplied analytical predictions. T5 made the disclosed preliminary computations below. These precede the model freeze and rule out retrospective E3 claims for the exact examples.
6. Committed EXACT_MODELS_V1 and issue snapshots at b404904. T5's text-only review found no blocking finite-model issue.
7. Two separately authored checkers executed; exact comparison and witness replay produced 315 agreements. These are comparison assertions, not 315 independent experiments.
8. T2/T3/T4 reviewed the resulting sources/designs. Corrections are in CORRIGENDA_V1; frozen model bytes and results are preserved. None changes a protected protocol.
9. During publication, the command-line push failed for missing credentials. A connected GitHub base-commit metadata request unexpectedly returned a broad diff for f9d2ff2, including sibling unary-study source/protocol material. This occurred after exact models, results and designs were written. No sibling study was executed and this material did not inform the recorded results, but blindness to returned contents cannot be certified for future sibling work. A future protected-study exposure audit must include this retrieval. The connected publication preserves file-tree identity; remote commit metadata/IDs can differ from local commits.

## Preliminary scratch computation retained verbatim

T5 executed this transient Python code before the specification freeze:

```python
from collections import deque
from itertools import combinations

def dist(n, gens):
    d = {0: 0}
    q = deque([0])
    while q:
        x = q.popleft()
        for g in gens:
            y = (x + g) % n
            if y not in d:
                d[y] = d[x] + 1
                q.append(y)
    return d

for a, b in [(1, 2), (2, 4), (1, 4)]:
    print('Z5', a, b, max(dist(5, [a])[b], dist(5, [b])[a]))
print('Z6 c2c3', dist(6, [2, 3]))
for k in range(1, 3):
    bases = []
    for gs in combinations(range(1, 6), k):
        d = dist(6, gs)
        if len(d) == 6 and max(d.values()) <= 3:
            bases.append(gs)
    print('Z6 cap3 feasible', k, bases)
for s in range(4):
    print('support', s, 'trace signature', tuple(bool(s & ~r) for r in range(4)))
```

Reported output:

```text
Z5 1 2 3
Z5 2 4 3
Z5 1 4 4
Z6 c2c3 {0: 0, 2: 1, 3: 1, 4: 2, 5: 2, 1: 3}
Z6 cap3 feasible 1 []
Z6 cap3 feasible 2 [(1, 2), (1, 3), (1, 4), (1, 5), (2, 3), (2, 5), (3, 4), (3, 5), (4, 5)]
support 0 trace signature (False, False, False, False)
support 1 trace signature (True, False, True, False)
support 2 trace signature (True, True, False, False)
support 3 trace signature (True, True, True, False)
```

T5 initially sent the incorrect Z6 vector [0,2,1,1,2,3]. T1 corrected it to [0,3,1,1,2,2]; T5's computation confirmed the correction. Maximum depth remained 3. This error is retained rather than erased from the account.

## Failures and unresolved requirements

- A convenience attempt to import `jsonschema` failed because it is not installed. No environment was modified. Standard-library checks verified required fields, routes, unique IDs and artifact existence; this is not a claim of full Draft 2020-12 validator conformance.
- One primary provenance PDF retrieval and the detailed BB1 report retrieval were unavailable; atlas labels those limitations.
- No computational mismatch between the final checkers occurred. Common-mode specification/modeling error remains possible.
- Full prior-art saturation, full V2 theorem-ledger reconciliation, production parity, learned operator recovery, lifetime measurements, protected transfer, independent task authorship, fresh-host execution and human scholarly sign-off remain open.
- The strongest currently justified disposition is parent-owned apparatus / no new cognitive primitive established. The field tournament and primitive-pressure rows remain unexecuted designs.
