# HSG-v4 Parent Ledger V1 (FROZEN)

Every PARENT/PARENT-LIMIT row of THEOREM_REGISTRY_V1.json must be primary-source
verified against this ledger before its status may leave OPEN. Verification =
publisher/primary page or full-text check of (a) authors+venue+year, (b) the exact
theorem/statement we instantiate, (c) its assumption list. Verdicts:
CONFIRMED_VERBATIM / CONFIRMED_SUBSTANTIVE / WORDING_IMPRECISE (cite fix, no
semantic change) / PARTIAL (statement drift — restate row) / NOT_FOUND / CANNOT_CHECK.

Status column starts PENDING_PRIMARY_SOURCE for all rows (verification lanes D16b).

| id | parent | consumed_by | primary source | status |
|---|---|---|---|---|
| P01 | Floyd-Hoare logic | T82 | Hoare, CACM 12(10) 1969, DOI 10.1145/363235.363259 | CONFIRMED_SUBSTANTIVE |
| P02 | Dijkstra weakest preconditions / guarded commands | T82 | Dijkstra, CACM 18(8) 1975, DOI 10.1145/360933.360975 | CONFIRMED_SUBSTANTIVE |
| P03 | Knuth generalized shortest path / AND-OR derivations | T70 | Knuth, IPL 6(1):1-5, Feb 1977, DOI 10.1016/0020-0190(77)90002-3 | WORDING_IMPRECISE |
| P04 | Goodman semiring parsing | T70 | Goodman, Computational Linguistics 25(4) 1999, J99-4004 | CONFIRMED_SUBSTANTIVE |
| P05 | Algebraic dynamic programming | T70 | Giegerich-Meyer-Steffen, "A discipline of dynamic programming over sequence data", SCP 51(3):215-263, 2004, DOI 10.1016/j.scico.2003.12.005 (LOPSTR'03 title "Algebraic Dynamic Programming") | PARTIAL |
| P06 | Abstract interpretation | T77 | Cousot-Cousot, POPL 1977, DOI 10.1145/512950.512973 | PARTIAL |
| P07 | CEGAR | T79 | Clarke-Grumberg-Jha-Lu-Veith, CAV 2000, DOI 10.1007/10722167_15 | CONFIRMED_VERBATIM |
| P08 | Lenses / round-trip laws | T66/T67 analogy only | Foster et al., TOPLAS 29(3) 2007, DOI 10.1145/1232420.1232424 | CONFIRMED_SUBSTANTIVE |
| P09 | Provenance semirings | T72 | Green-Karvounarakis-Tannen, PODS 2007, DOI 10.1145/1265530.1265535 | CONFIRMED_SUBSTANTIVE |
| P10 | Provenance with negation / FOL semiring semantics | T73 | Grädel-Tannen, arXiv 2412.07986 | CONFIRMED_SUBSTANTIVE |
| P11 | Preservation theorems in semiring semantics | T94 | Brinke-Dawar-Grädel-Pago, ICALP 2026, DOI 10.4230/LIPIcs.ICALP.2026.172 | CONFIRMED_VERBATIM |
| P12 | Institution theory | T84/T85 | Goguen-Burstall, JACM 39(1) 1992, DOI 10.1145/147508.147524 | CONFIRMED_SUBSTANTIVE |
| P13 | Edinburgh LF | T84 | Harper-Honsell-Plotkin, JACM 40(1):143-184, 1993, DOI 10.1145/138027.138060 (preliminary LICS 1987:194-204) | PARTIAL |
| P14 | Proof-carrying code | T83 | Necula, POPL 1997, DOI 10.1145/263699.263712 | CONFIRMED_VERBATIM |
| P15 | DPLL(T) | D24 context | Nieuwenhuis-Oliveras-Tinelli, JACM 53(6) 2006, DOI 10.1145/1217856.1217859 | CONFIRMED_SUBSTANTIVE |
| P16 | Knuth-Bendix completion correctness | T86 | Huet, JCSS 23(1) 1981, DOI 10.1016/0022-0000(81)90002-7 | CONFIRMED_SUBSTANTIVE |
| P17 | egg / equality saturation | T86 | Willsey et al., POPL 2021, DOI 10.1145/3434304; CACM 2026, DOI 10.1145/3815481 | CONFIRMED_SUBSTANTIVE |
| P18 | STRIPS | D25 | Fikes-Nilsson, AI 2(3-4) 1971, DOI 10.1016/0004-3702(71)90010-5 | CONFIRMED_VERBATIM |
| P19 | POMDP belief-state sufficiency | T89 | Kaelbling-Littman-Cassandra, AI 101(1-2) 1998, DOI 10.1016/S0004-3702(98)00023-X | CONFIRMED_VERBATIM |
| P20 | Options / SMDP temporal abstraction | T90 | Sutton-Precup-Singh, AI 112(1-2) 1999, DOI 10.1016/S0004-3702(99)00052-1 | CONFIRMED_VERBATIM |
| P21 | HTN complexity limits | T91 | Erol-Hendler-Nau, AMAI 18(1):69-93, 1996, DOI 10.1007/BF02136175 | CONFIRMED_SUBSTANTIVE |
| P22 | DRT / dynamic semantics | T92 | Kamp-Reyle, From Discourse to Logic, Springer 1993; Groenendijk-Stokhof, "Dynamic Predicate Logic", Linguistics and Philosophy 14(1):39-100, 1991 | PARTIAL |
| P23 | Rate-distortion | T88 | Shannon, IRE National Convention Record, Part 4:142-163, 1959 (IEEE doc 5311476); Cover-Thomas, Elements of Information Theory ch.10 | WORDING_IMPRECISE |
| P24 | Confidence sequences | T93 | Howard-Ramdas-McAuliffe-Sekhon, Annals of Statistics 49(2) 2021, DOI 10.1214/20-AOS1991 | CONFIRMED_SUBSTANTIVE |
| P25 | Blackwell comparison of experiments | T88 note | Blackwell, Proc. Second Berkeley Symp. Math. Stat. Prob. pp.93-102, 1951 (Euclid bsmsp/1200500222); Blackwell, Annals of Math. Statistics 24(2):265-272, 1953 | PARTIAL |

No HSG-v4 novelty claim may consist of renaming any row above. Novelty, if any
survives, lives in the joint object + cross-domain receipts + measured B_exec
developmental deltas (D27), never in a parent theorem restated.

---

## Verification appendix (D16b, 2026-09-10)

All 25 rows verified against primary sources by three parallel verification lanes
(batches A: P01-P09, B: P10-P18, C: P19-P25; raw verdict JSON retained at
parent_verification/BATCH_{A,B,C}.json in this directory). Verdict census:
- CONFIRMED_SUBSTANTIVE: 12
- CONFIRMED_VERBATIM: 6
- PARTIAL: 5
- WORDING_IMPRECISE: 2

Material findings (full detail in batch JSONs):
- P03/P13/P21/P22/P23/P25: venue/volume citation errors repaired in the source column above (no semantic change).
- P05: the SCP 2004 DOI carries the title 'A discipline of dynamic programming over sequence data'; 'Algebraic Dynamic Programming' is the LOPSTR'03 preliminary title; T70's instantiation is of the ADP discipline (semiring + yield grammar separation) which is present in both.
- P06: the POPL'77 paper proves semilattice/extreme-fixpoint abstract interpretation WITHOUT the word 'Galois' (the alpha/gamma Galois formulation debuts POPL'79); T77's assumption list already requires only 'order/fixpoint structure', so the row stands; any prose citing 'Galois connection, Cousot 1977' must read 'fixpoint approximation semantics, Cousot 1977; Galois formulation, Cousot-Cousot 1979'.
- P12: 'comorphism' is not the JACM'92 paper's own term (its device is institution morphisms); T85 uses the now-standard comorphism direction (Meseguer 1989, co-cited) - recorded as terminology provenance, not a claim drift.
- P24: 'e-process'/'e-value' appear 0 times in Howard et al. 2021 (successor terminology); T93's policy sentence using them is our framing, not a citation of that paper's vocabulary.
- P23: Cover-Thomas chapter could not be checked (Wiley 403) - recorded as CANNOT_CHECK component of an otherwise CONFIRMED primary (Shannon 1959 via Gray's author-hosted text).
- P01: notation is P{Q}R in the original (modern {P}S{Q} is later convention) - irrelevant to T82's use.
- P07: CEGAR termination quote verified WITH its ACTU* path/loop-fragment scope assumption - T79's instantiation keeps the scope condition explicit.

Gate consequence: every PARENT row is now primary-source verified; their THEOREM_REGISTRY
statuses may leave OPEN upon instantiation evidence (D17+ tranche), per the frozen rule.
