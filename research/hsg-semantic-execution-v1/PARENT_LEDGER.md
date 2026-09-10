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
| P01 | Floyd-Hoare logic | T82 | Hoare, CACM 12(10) 1969, DOI 10.1145/363235.363259 | PENDING_PRIMARY_SOURCE |
| P02 | Dijkstra weakest preconditions / guarded commands | T82 | Dijkstra, CACM 18(8) 1975, DOI 10.1145/360933.360975 | PENDING_PRIMARY_SOURCE |
| P03 | Knuth generalized shortest path / AND-OR derivations | T70 | Knuth, IPL 8(1) 1977, DOI 10.1016/0020-0190(77)90002-3 | PENDING_PRIMARY_SOURCE |
| P04 | Goodman semiring parsing | T70 | Goodman, Computational Linguistics 25(4) 1999, J99-4004 | PENDING_PRIMARY_SOURCE |
| P05 | Algebraic dynamic programming | T70 | Giegerich-Meyer-Steffen, SCP 51(3) 2004, DOI 10.1016/j.scico.2003.12.005 | PENDING_PRIMARY_SOURCE |
| P06 | Abstract interpretation | T77 | Cousot-Cousot, POPL 1977, DOI 10.1145/512950.512973 | PENDING_PRIMARY_SOURCE |
| P07 | CEGAR | T79 | Clarke-Grumberg-Jha-Lu-Veith, CAV 2000, DOI 10.1007/10722167_15 | PENDING_PRIMARY_SOURCE |
| P08 | Lenses / round-trip laws | T66/T67 analogy only | Foster et al., TOPLAS 29(3) 2007, DOI 10.1145/1232420.1232424 | PENDING_PRIMARY_SOURCE |
| P09 | Provenance semirings | T72 | Green-Karvounarakis-Tannen, PODS 2007, DOI 10.1145/1265530.1265535 | PENDING_PRIMARY_SOURCE |
| P10 | Provenance with negation / FOL semiring semantics | T73 | Grädel-Tannen, arXiv 2412.07986 | PENDING_PRIMARY_SOURCE |
| P11 | Preservation theorems in semiring semantics | T94 | Brinke-Dawar-Grädel-Pago, ICALP 2026, DOI 10.4230/LIPIcs.ICALP.2026.172 | PENDING_PRIMARY_SOURCE |
| P12 | Institution theory | T84/T85 | Goguen-Burstall, JACM 39(1) 1992, DOI 10.1145/147508.147524 | PENDING_PRIMARY_SOURCE |
| P13 | Edinburgh LF | T84 | Harper-Honsell-Plotkin, LICS 1993 (info in registry row T84) | PENDING_PRIMARY_SOURCE |
| P14 | Proof-carrying code | T83 | Necula, POPL 1997, DOI 10.1145/263699.263712 | PENDING_PRIMARY_SOURCE |
| P15 | DPLL(T) | D24 context | Nieuwenhuis-Oliveras-Tinelli, JACM 53(6) 2006, DOI 10.1145/1217856.1217859 | PENDING_PRIMARY_SOURCE |
| P16 | Knuth-Bendix completion correctness | T86 | Huet, JCSS 23(1) 1981, DOI 10.1016/0022-0000(81)90002-7 | PENDING_PRIMARY_SOURCE |
| P17 | egg / equality saturation | T86 | Willsey et al., POPL 2021, DOI 10.1145/3434304; CACM 2026, DOI 10.1145/3815481 | PENDING_PRIMARY_SOURCE |
| P18 | STRIPS | D25 | Fikes-Nilsson, AI 2(3-4) 1971, DOI 10.1016/0004-3702(71)90010-5 | PENDING_PRIMARY_SOURCE |
| P19 | POMDP belief-state sufficiency | T89 | Kaelbling-Littman-Cassandra, AI 101(1-2) 1998, DOI 10.1016/S0004-3702(98)00023-X | PENDING_PRIMARY_SOURCE |
| P20 | Options / SMDP temporal abstraction | T90 | Sutton-Precup-Singh, AI 112(1-2) 1999, DOI 10.1016/S0004-3702(99)00052-1 | PENDING_PRIMARY_SOURCE |
| P21 | HTN complexity limits | T91 | Erol-Hendler-Nau, AMAI 18, 1996 | PENDING_PRIMARY_SOURCE |
| P22 | DRT / dynamic semantics | T92 | Kamp-Reyle (book); Groenendijk-Stokhof DPL (JPL 20(1) 1991) | PENDING_PRIMARY_SOURCE |
| P23 | Rate-distortion | T88 | Shannon 1959 / Cover-Thomas, Elements of Information Theory ch.10 | PENDING_PRIMARY_SOURCE |
| P24 | Confidence sequences | T93 | Howard-Ramdas-McAuliffe-Sekhon, Annals of Statistics 49(2) 2021, DOI 10.1214/20-AOS1991 | PENDING_PRIMARY_SOURCE |
| P25 | Blackwell comparison of experiments | T88 note | Blackwell 1951/1953 | PENDING_PRIMARY_SOURCE |

No HSG-v4 novelty claim may consist of renaming any row above. Novelty, if any
survives, lives in the joint object + cross-domain receipts + measured B_exec
developmental deltas (D27), never in a parent theorem restated.
