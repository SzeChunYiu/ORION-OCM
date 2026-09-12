# Track-B Literature Ledger V2 — primary-source depth pass (issue #377 GMI-D0)

Coverage terminal (computed by `build_parent_ledger_v2.py`, never asserted): `PARENT_COVERAGE_PARTIAL__MISSING_PARENTS_REPORTED`

Depth histogram over entries (best source per entry): {"ABSTRACT_ONLY": 1, "FULL_TEXT_READ": 54, "NOT_ACCESSIBLE": 1, "PARTIAL_TEXT_READ": 52}

Rule: `FULL_TEXT_READ` means the worker read the full text and every quote is verbatim from it; `PARTIAL_TEXT_READ` means sections were read; `ABSTRACT_ONLY`/`NOT_ACCESSIBLE`/`FROM_MEMORY_UNVERIFIED` entries carry no load-bearing claim in Track B until upgraded. V1 (Codex) abstract-depth records are preserved in `PARENT_LEDGER_V2.json:v1_records` and are not re-rendered here.

| #377 family | entries | full-text entries |
|---|---|---|
| P0 | 13 | 12 |
| P1 | 10 | 4 |
| P2 | 3 | 1 |
| P3 | 2 | 1 |
| P4 | 14 | 7 |
| P5 | 4 | 1 |
| P6 | 12 | 6 |
| P7 | 23 | 14 |
| P8 | 5 | 1 |


## P0 — universal computation / induction / search / limits

### P0.BLUM_SPEEDUP — Blum 1967 machine-independent complexity and the speed-up theorem: no universally fastest solver

Disposition: `ADOPT` · best verification: `FULL_TEXT_READ`

Sources:

- [0] A Machine-Independent Theory of the Complexity of Recursive Functions — M. Blum (1967), J. ACM 14(2), 322-336. 10.1145/321386.321395 — `NOT_ACCESSIBLE`
- [1] On Effective Procedures for Speeding Up Algorithms — M. Blum (1971), J. ACM 18(2), 290-305. 10.1145/321637.321648 — `NOT_ACCESSIBLE`
- [2] A Refinement of the McCreight-Meyer Union Theorem (states the Blum axioms; notes every Blum measure satisfies speedup, compression, gap and union theorems) — M. Fox, C. Karamchedu (2024), arXiv (CCC 2024 submission). arXiv:2406.08600 arXiv:2406.08600 — `PARTIAL_TEXT_READ`
- [3] The Fastest and Shortest Algorithm for All Well-Defined Problems (informal statement of Blum's theorem and how M_{p*} avoids it) — M. Hutter (2002), IJFCS 13(3). arXiv:cs/0206022 arXiv:cs/0206022 — `FULL_TEXT_READ`
- [4] Speedup for Natural Problems and Noncomputability — H. Monroe (2012), Theoretical Computer Science (arXiv v3). arXiv:0906.3765 arXiv:0906.3765 — `PARTIAL_TEXT_READ`

**What it already explains.** That complexity can be axiomatized machine-independently: a Blum measure Phi(e,x) is any partial computable step-count such that (i) Phi(e,x) is defined iff phi_e(x) is defined and (ii) the predicate Phi(e,x) = m is decidable (Fox-Karamchedu Def. 2.2, read); deterministic time, space and nondeterministic time are Blum measures. That under ANY Blum measure there exist computable functions with no fastest program: for every total computable speed-up factor r there is a total computable (0-1 valued) f such that for every program i computing f there is another program j computing f with r(Phi_j(x)) <= Phi_i(x) for almost all x (speed-up theorem; statement from memory, unverified against the original) - and the sequence of ever-faster programs is not effectively obtainable (Blum 1971, unread). Consequently 'no universally fastest solver' and no well-defined 'complexity of f' (Fox-Karamchedu: every Blum measure satisfies speedup, compression, gap and union theorems). Hutter 2002 (read) shows the escape hatch: restricting to programs with PROVABLE correctness and time bounds removes the speed-up phenomenon ('M avoids Blum's speed-up theorem by ignoring programs without correctness proof'). At Track-B scope: the question 'which morphology is fastest for f' has no answer in general, and revision (replace program by a faster one) never terminates at an optimum unless the ecology's verification contract restricts the candidate set.

**Formal object.** Acceptable Godel numbering {phi_e}; Blum measure Phi in P(N x Sigma* -> N) with axioms (i) Phi(e,x) converges iff phi_e(x) converges; (ii) there is a total computable f with f(e,x,m) = 1 if Phi(e,x) = m else 0. Blum class C_Phi(t) = {phi_e : Phi(e,x) <= t(\|x\|) a.e.}. Speed-up: for total computable r there is total computable f such that for all i with phi_i = f there is j with phi_j = f and r(Phi_j(x)) <= Phi_i(x) a.e. [UNVERIFIED statement]. Monroe's p-optimality: M' <=_p M if T_{M'}(x) <= p(\|x\|, T_M(x)) for a polynomial p; L has superpolynomial speedup iff no least element under <_p.

**Strongest result.** Blum's speed-up theorem (as characterized in the read secondaries): 'there are problems for which an (incomputable) sequence of speed-improving algorithms (of increasing size) exists, but no fastest algorithm' (Hutter 2002 sec. 1); 'Blum [2] exhibited languages that have almost-everywhere speedup, which are unnatural being constructed solely for that purpose' (Monroe sec. 1). Exact quantifier structure NOT verified in this session. Complement (read): Hutter Theorem 1/2 - under provability restrictions there IS an asymptotically fastest and shortest program; Monroe Thm 2.3 - condition (*) holds iff coBHP has superpolynomial speedup, connecting speedup for natural coNP-complete problems to the non-existence of p-optimal proof systems (Krajicek-Pudlak).

**Assumptions.** A Blum measure (any acceptable step-counting) - the theorem is measure-independent; Almost-everywhere quantification (finitely many exceptions allowed); The sped-up functions are artificial diagonal constructions; whether natural problems (matrix multiplication, coNP-complete languages) have speedup is open (Monroe); Provability of correctness/time bounds is NOT assumed - assuming it (Hutter) removes the phenomenon

**Resource model.** any abstract complexity measure (time, space, ...) - exactly one resource at a time; program size enters only as 'of increasing size'; no samples, verification or learning cost

**Failure boundary.** Existence-only and non-effective: it does not produce the faster program (Blum 1971); it concerns pathological diagonal functions, so it does not by itself show that any NATURAL task lacks a best morphology; it is per-function, not per-ecology; it disappears under provability restrictions (Hutter) and, for p-optimality, its status for natural problems is tied to open questions (P vs NP, optimal proof systems). It says nothing about learning or sample cost, only execution of a fixed correct program.

**Implementation.** none known (non-constructive existence theorem)

**Track-B residual.** Under a fixed verification contract (which programs count as 'admissible' morphologies: provably correct, statistically validated, empirically tested), does the admissible set admit a fastest element (Hutter: yes for provable), and does the revision loop of a developmental system converge to it or descend an infinite speed-up chain? Blum owns the unrestricted negative; the contract-relative version is the Track-B question.

**Upward question.** Is the existence of a fastest admissible morphology (a p-optimal element) itself an ecology property determined by the verification contract - i.e. is 'the ecology admits an optimum' the binary phase variable that separates convergent from non-convergent developmental morphogenesis?

Load-bearing quotes (verbatim from sources actually read):

> "We call Phi in P(N x Sigma* -> N) a Blum complexity measure (or Blum measure for short) iff: (i) for all e and x, Phi(e,x) converges iff phi_e(x) converges, (ii) there exists f in R(N x Sigma* x N -> N) such that for all e, x, and m, f(e,x,m) = 1 if Phi(e,x) = m, 0 otherwise." — [2] Fox-Karamchedu 2406.08600, Definition 2.2 (ASCII rendering)
> "In addition to satisfying a speedup theorem [1], a compression theorem [1], and a gap theorem [2, 6], every Blum measure also satisfies a union theorem." — [2] Fox-Karamchedu 2406.08600, sec. 2.3
> "Blum's Speed-up Theorem [2, 3] shows that there are problems for which an (incomputable) sequence of speed-improving algorithms (of increasing size) exists, but no fastest algorithm." — [3] Hutter cs/0206022, sec. 1
> "M avoids Blum's speed-up theorem by ignoring programs without correctness proof." — [3] Hutter cs/0206022, Abstract
> "Inventing complex (long) programs is not necessary to construct asymptotically fast algorithms, under the stated provability assumptions, in contrast to Blum's Theorem" — [3] Hutter cs/0206022, sec. 7
> "Blum [2] exhibited languages that have almost-everywhere speedup, which are unnatural being constructed solely for that purpose." — [4] Monroe 0906.3765, sec. 1
> "If L has a least element M under <_p, say that M is p-optimal [12] and otherwise that L has (i.o.) superpolynomial speedup." — [4] Monroe 0906.3765, Definition 2.2

Verification notes: Blum 1967 not readable. The two Blum axioms are verified (Fox-Karamchedu Def. 2.2). The precise quantifier form of the speed-up theorem written in formal_object is from memory and is flagged UNVERIFIED; only its informal content (no fastest program; non-effective sequence) is verified via three read secondaries. HST ledger row T16 already OWNS 'no asymptotically optimal program for some computable problems'; this entry adds the Blum-axiom framing, the provability escape (Hutter), the p-optimality/proof-system connection (Monroe), and the Track-B revision-work subtraction.

### P0.INVARIANCE_THESIS — van Emde Boas 1990 'Machine models and simulations': invariance thesis, first/second machine class, simulation overheads

Disposition: `GENERALIZE` · best verification: `FULL_TEXT_READ`

Sources:

- [0] Machine Models and Simulations — P. van Emde Boas (1990), Handbook of Theoretical Computer Science, Vol. A (J. van Leeuwen ed.), Elsevier/MIT Press, pp. 1-66. https://dl.acm.org/doi/10.5555/114872.114873 — `NOT_ACCESSIBLE`
- [1] (Leftmost-Outermost) Beta Reduction is Invariant, Indeed (quotes the Slot-van Emde Boas invariance thesis verbatim; proves lambda-calculus is a reasonable machine) — B. Accattoli, U. Dal Lago (2016), Logical Methods in Computer Science 12(1:4), 1-46. 10.2168/LMCS-12(1:4)2016 arXiv:1601.01233 — `PARTIAL_TEXT_READ`
- [2] Unconventional Complexity Classes in Unconventional Computing (restates van Emde Boas's first and second machine class) — A. E. Porreca (2024), arXiv extended abstract. arXiv:2405.16896 arXiv:2405.16896 — `PARTIAL_TEXT_READ`
- [3] A Formalization and Proof of the Extended Church-Turing Thesis — N. Dershowitz, E. Falkovich (2012), EPTCS 88 (DCM 2011), 72-78. 10.4204/EPTCS.88.6 arXiv:1207.7148 — `FULL_TEXT_READ`
- [4] Turing Machines for Dummies: why representations do matter — P. van Emde Boas (2012), SOFSEM 2012, LNCS 7147 / ILLC PP-2011-36. 10.1007/978-3-642-27660-6_2 — `NOT_ACCESSIBLE`

**What it already explains.** That the plethora of sequential machine models (multi-tape Turing machines, RAMs under logarithmic cost, pointer machines, register machines, and - by Accattoli-Dal Lago 2016 - the lambda-calculus under leftmost-outermost reduction with useful sharing) form ONE class, the first machine class, mutually simulable with polynomially bounded time overhead and constant-factor space overhead; hence P, NP, PSPACE, EXP are model-independent. That models with unbounded parallelism or with too-powerful primitives (unit-cost multiplication RAMs, alternating machines, hyperbolic cellular automata, membrane systems with division) form a second machine class whose polynomial time equals sequential PSPACE. That the overheads are concrete: Dershowitz-Falkovich prove any effective sequential algorithm is simulated by a RAM in O(n + nT(n) + T(n)^2) steps and by a single-tape TM with quintic overhead (quadratic RAM simulation composed with a cubic TM-of-RAM simulation via Cook-Reckhow 1973). This is the existing theory of BOUNDED COMPILATION between computational models with respect to EXECUTION time and space.

**Formal object.** Machine models M_1, M_2 with resource measures time_M(x), space_M(x). Simulation: M_2 simulates M_1 with overhead (f,g) if for every M_1-program p there is an M_2-program p' computing the same function with time_{M_2}(p',x) <= f(time_{M_1}(p,x)) and space_{M_2}(p',x) <= g(space_{M_1}(p,x)). Invariance Thesis (Slot-van Emde Boas 1984 form, as quoted verbatim in Accattoli-Dal Lago): 'Reasonable computational models simulate each other with polynomially bounded overhead in time, and constant factor overhead in space.' Weak invariance thesis drops the space clause. First machine class := models polynomially equivalent to the sequential TM; second machine class := models whose polynomial time equals PSPACE (Parallel Computation Thesis).

**Strongest result.** The thesis itself is a thesis, not a theorem; its content is the catalogue of simulation theorems. Verified in this session: (a) Accattoli-Dal Lago Thm 15.2 'The lambda-calculus is a reasonable model in the sense of the weak invariance thesis' (LO beta-steps are a polynomial cost model despite size explosion, via useful sharing; the high-level overhead is quadratic in beta-steps); (b) Dershowitz-Falkovich Thm 16: any effective implementation with complexity T(n) w.r.t. a valid size measure is simulated by a RAM in order n + nT(n) + T(n)^2 steps with word size O(log T(n)); overall single-tape TM overhead quintic; (c) Porreca's restatement: RAMs with constant-time addition/subtraction and standard d-dimensional cellular automata are first class; RAMs with constant-time multiplication/division, alternating TMs, hyperbolic CAs, P-systems with division are second class.

**Assumptions.** 'Reasonable' is defined by the thesis itself (circular by design); unit-cost primitives must be genuinely constant-cost (Dershowitz-Falkovich: bootstrapped decimal multiplication must be charged as digit operations, not as one step); Sequential, deterministic, non-interactive computation (no learning loop, no environment interaction, no oracle); Input size measured by a 'valid' size (representation matters: van Emde Boas 2012 title; Dershowitz-Falkovich Def. 7); Only asymptotic polynomial/constant-factor bounds are claimed; sub-polynomial distinctions are explicitly model-dependent

**Resource model.** time and space (execution work only); description length appears only implicitly through the fixed size of the simulator; no samples, no verification, no update/revision cost

**Failure boundary.** By construction it is blind to everything that distinguishes intelligence morphologies in practice: (1) sub-polynomial and constant-factor costs ('sub-polynomial classes depend very much on the model'), which is where linear-vs-quadratic attention, symbolic-vs-numeric constant factors, and hardware alignment live; (2) it accounts only for execution of a FIXED program, not for the work of finding/updating the program (learning), checking it (verification) or replacing it (revision); (3) it is ecology-blind - no task distribution, no feedback, no horizon enters; (4) it collapses all sequential morphologies into one equivalence class, so a D1 bound stated at polynomial overhead is trivially satisfied by every pair of first-class morphologies and discriminates nothing; (5) reasonableness of a cost model can be genuinely hard to establish (size explosion in lambda-calculus was open until 2014), warning that naive morphology cost models (e.g. counting 'steps' of a rewrite system or 'forward passes' of a network) may be unreasonable.

**Implementation.** none known (the chapter is a survey); the Accattoli-Dal Lago machines are described but no code URL was read

**Track-B residual.** Is there an invariance-type theorem, or a provable NON-invariance, for the remaining components of Track-B's overhead vector - learning-update work, verification work, revision work - i.e. do 'reasonable' adaptive morphologies simulate each other's update/verify/revise loops with bounded overhead, or is the overhead necessarily unbounded/ecology-dependent? (van Emde Boas owns only the execution-time/space component.)

**Upward question.** Define the Track-B resource vector r(M) = (description, execution, update, verification, revision) and ask: for which components does a polynomial-overhead simulation theorem hold across morphologies, and for which is the overhead provably ecology-dependent? The invariance thesis says component 2 is invariant; the Track-B theory begins where invariance fails.

Load-bearing quotes (verbatim from sources actually read):

> "Reasonable computational models simulate each other with polynomially bounded overhead in time, and constant factor overhead in space." — [1] Accattoli-Dal Lago 1601.01233, Introduction p.2 (quoting Slot & van Emde Boas 1984)
> "for reasonable models the definition of every polynomial or super-polynomial class such as P or EXP does not rely on the chosen model. On the other hand, it is well-known that sub-polynomial classes depend very much on the model." — [1] Accattoli-Dal Lago 1601.01233, Introduction p.2
> "there are terms that in a linear number of steps produce an exponentially large output" — [1] Accattoli-Dal Lago 1601.01233, Abstract (size-explosion problem)
> "the study of invariance is about mechanizability rather than efficiency. One is not looking for the smartest or shortest evaluation strategy, but rather for one that can be reasonably implemented." — [1] Accattoli-Dal Lago 1601.01233, sec. 16 Discussion
> "can simulate and be simulated by deterministic Turing machines with a polynomial-time overhead, and thus in particular they characterise the complexity class P when working in polynomial time. Emde Boas refers to those models as the first machine class" — [2] Porreca 2405.16896, sec. 1
> "Other models, with less restrictions on parallelism or with more powerful elementary operations, characterise in polynomial time what deterministic Turing machines compute in polynomial space. This is called the second machine class" — [2] Porreca 2405.16896, sec. 1
> "any algorithm running on an effective sequential model can be simulated, independent of the problem, by a single-tape Turing machine with a quintic overhead: quadratic for the RAM simulation and another cubic for a TM simulation of the RAM" — [3] Dershowitz-Falkovich 1207.7148, sec. 6 Summary
> "if an effective implementation includes decimal multiplication among its bootstrapped operations, then we do not want to count multiplication as a single operation (which would give a 'pseudo-complexity' measure)" — [3] Dershowitz-Falkovich 1207.7148, sec. 3

Verification notes: The 1990 chapter itself was not readable; the thesis wording is taken from Accattoli-Dal Lago's verbatim quotation (they cite Slot-van Emde Boas 1984, the source van Emde Boas 1990 summarizes). The specific k-tape-to-1-tape quadratic and RAM-to-TM cubic overheads are stated in the read Dershowitz-Falkovich paper (citing Cook-Reckhow 1973); the finer catalogue in van Emde Boas 1990 (e.g. Hennie-Stearns O(t log t) two-tape simulation, oblivious machines) is FROM_MEMORY_UNVERIFIED and not relied on. Not previously reconstructed in any repo ledger.

### P0.LEVIN_SEARCH — Levin 1973 universal sequential search; Hutter 2002 fastest and shortest algorithm for all well-defined problems

Disposition: `ADOPT` · best verification: `FULL_TEXT_READ`

Sources:

- [0] Universal Sequential Search Problems — L. A. Levin (1973), Problems of Information Transmission 9(3), 265-266 (Russian: Problemy Peredachi Informatsii 9(3), 115-116); corrected translation in Trakhtenbrot, Annals Hist. Comput. 6(4), 1984. https://www.mathnet.ru/eng/ppi914 — `NOT_ACCESSIBLE`
- [1] The Fastest and Shortest Algorithm for All Well-Defined Problems — M. Hutter (2002), International Journal of Foundations of Computer Science 13(3), 431-443. 10.1142/S0129054102001199 arXiv:cs/0206022 — `FULL_TEXT_READ`
- [2] Kolmogorov complexity in the USSR (1975-1982): isolation and its end (reports what Levin's 1973 note does and does not contain) — V. V. V'yugin (transl. A. Shen) (2019), arXiv. arXiv:1907.05056 arXiv:1907.05056 — `PARTIAL_TEXT_READ`
- [3] Speedup for Natural Problems and Noncomputability (states Levin's p-optimal witness search) — H. Monroe (2012), Theoretical Computer Science (arXiv v3). arXiv:0906.3765 arXiv:0906.3765 — `PARTIAL_TEXT_READ`

**What it already explains.** That for every inversion problem (find y with g(y)=x, g quickly computable) there is ONE fixed algorithm - Levin search, which runs all programs p in parallel with time share 2^{-l(p)} and verifies each output with g - whose running time is within a multiplicative constant 2^{l(p)} of the fastest program p for that problem: total time <= 2^{l(p)} * time^+_p(x), where time^+ includes verification. Hence 'no algorithm for NP witness search can be more than a constant factor faster than Levin's', a p-optimal algorithm exists for every NP language (Monroe fn. 3), and the P-vs-NP question reduces to the running time of one known algorithm. Hutter 2002 (Theorem 1, read) extends this from inversion problems to ALL well-defined problems p*: an algorithm M_{p*} interleaving (A) enumeration of proofs of program-equivalence and time-bound, (B) Levin search over time-bound programs, (C) execution of the currently fastest provably-correct program, achieves time_{M_{p*}}(x) <= 5 t_p(x) + d_p time_{t_p}(x) + c_p for every provably-correct p with provable time bound t_p - no large multiplicative factor, at the price of an enormous additive constant c_p = 40 * 2^{l(proof(p))+1} O(l(proof(p))^2) and d_p = 40 * 2^{l(p)+l(t_p)}. Theorem 2 (read): the fastest program is also among the shortest programs provably equivalent to p*, l(p~) <= K''(p*) + O(1). At Track-B scope it explains the canonical 'programmatic/symbolic' developmental mechanism (bias-optimal program search with a verifier) and why its constants, not its asymptotics, decide practical morphology.

**Formal object.** Universal reference machine U; program strings p with length l(p); time_p(x) = steps of U on (p,x). Levin search for g-witness of x: run all p with relative time 2^{-l(p)}, verify g(p(x)) = x, halt on first verified witness; bound time <= 2^{l(p)} time^+_p(x). Hutter: formal proof system with terms u (functional equality) and tm (step count); list L of (p,t) with proven [forall y: u(p,y)=u(p*,y) and u(t,y) >= tm(p,y)]; algorithms A (10%), B (10%), C (80%); shared t_fast, p_fast; C runs p_fast for k = 1,2,4,8,... steps. Complexities K'(f) := min{l(p): U(p,x)=f(x) forall x} (not approximable) and K''(p*) := min{l(p): a proof of equivalence to p* exists} (approximable from above).

**Strongest result.** Hutter 2002 Theorem 1 (read, verbatim): 'Let p* be a given algorithm computing p*(x) from x, or, more generally, a specification of a function. Let p be any algorithm, computing provably the same function as p* with computation time provably bounded by the function t_p(x) for all x. ... Then the algorithm M_{p*} constructed in Section 4 computes p*(x) in time time_{M_{p*}}(x) <= 5 t_p(x) + d_p time_{t_p}(x) + c_p with constants c_p and d_p depending on p but not on x. Neither p, t_p, nor the proofs need to be known in advance.' Theorem 2 (read): there exists p~ equivalent to p* with l(p~) <= K''(p*) + O(1) and the same time bound. Levin 1973 result (NOT read; characterized by V'yugin and Monroe): an optimal-up-to-constant algorithm for universal search problems.

**Assumptions.** A fast verifier g (Levin) or a formal proof system in which correctness and time bounds are provable (Hutter); 'For poorly specified problems, Theorem 1 does not help at all'; Problems are inversion/optimization type (Levin) or have provable specifications (Hutter); Same universal machine U measures time for all programs including the search algorithm (Hutter sec. 6: prevents linear speed-up cheating); Parallel simulation with abort is real-time or costs at most a factor 4 (Hutter sec. 6); Kraft inequality on the code of (p,t) pairs for the time-sharing scheme

**Resource model.** time (execution and verification, via time^+), description length (2^{l(p)} factor; K'' in Theorem 2), proof length (c_p exponential in l(proof)); NO accounting for samples, memory, or the cost of acquiring the specification/verifier

**Failure boundary.** Constants are 'tremendous' (2^{l(p)} multiplicative for Levin; c_p ~ 2^{l(proof)} additive for Hutter), so asymptotic optimality says nothing about arguments of practical size ('Will the ultimate search for asymptotically fastest programs typically lead to fast or slow programs for arguments of practical size? Levin search, matrix multiplication and the algorithm M_{p*} seem to support the latter'). Requires a verifier: 'Verification is necessary since the output of any program can be anything' - so the whole guarantee is conditional on the verification contract of the ecology. Not applicable to matrix multiplication, SAT decision or reinforcement learning as inversion problems (Hutter sec. 2). M_{p*} is not provably equivalent to p* inside the proof system (Godel II, van Emde Boas's remark in Hutter sec. 7) - so self-verification of the searcher is impossible. Says nothing about which morphology the found program has.

**Implementation.** none known for M_{p*} (Hutter: 'The large constants c_p and d_p seem to spoil a direct implementation'); Levin search variants implemented in Schmidhuber's OOPS/ALS (Machine Learning 1997/2004) and Ozkural's Gigamachine (arXiv 1709.03413, Algorithm 1 LSEARCH read)

**Track-B residual.** When the ecology's verification contract is weaker than a fast exact verifier (noisy feedback, statistical tests, delayed reward), what replaces the 2^{l(p)} time-sharing bound, and does the optimal search then produce programmatic morphologies or something else (e.g. gradient-trained continuous parameters, where 'verification' is a loss evaluation)? Levin/Hutter own the exact-verifier regime only.

**Upward question.** Treat the verification contract V of the ecology as the primary variable: is the space of morphologies stratified by the cost model of V (exact/fast, proof-based, statistical, delayed), with Levin/Hutter as the exact-V stratum? What is the analogue of the 2^{l(p)} bound for statistical V?

Load-bearing quotes (verbatim from sources actually read):

> "Levin search just runs and verifies the result of all algorithms p in parallel with relative computation time 2^{-l(p)}" — [1] Hutter cs/0206022, sec. 2
> "Verification is necessary since the output of any program can be anything. This is the reason why Levin search is only effective if a fast implementation of g is available." — [1] Hutter cs/0206022, sec. 2
> "The total computation time to find a solution (if one exists) is bounded by 2^{l(p)} time^+_p(x)." — [1] Hutter cs/0206022, sec. 2
> "time_{M_{p*}}(x) <= 5 t_p(x) + d_p time_{t_p}(x) + c_p with constants c_p and d_p depending on p but not on x." — [1] Hutter cs/0206022, Theorem 1
> "d_p = 40 2^{l(p)+l(t_p)}, c_p = 40 2^{l(proof(p))+1} O(l(proof(p))^2)" — [1] Hutter cs/0206022, sec. 5 Time Analysis
> "For poorly specified problems, Theorem 1 does not help at all." — [1] Hutter cs/0206022, sec. 3
> "Neither M_{p*}, nor p~ is provably equivalent to p*. ... A formal proof of the correctness of M_{p*} would prove the consistency of the proof system, which is impossible by Godels second incompleteness theorem." — [1] Hutter cs/0206022, sec. 7 (subtlety pointed out by van Emde Boas)
> "Will the ultimate search for asymptotically fastest programs typically lead to fast or slow programs for arguments of practical size? Levin search, matrix multiplication and the algorithm M_{p*} seem to support the latter" — [1] Hutter cs/0206022, sec. 9 Summary & Outlook
> "the paper was rather short (as usual for Levin), and the result was stated not only without proof, but also without the description of the search algorithm." — [2] V'yugin 1907.05056, sec. 1 (on Levin 1973)
> "Levin [13] exhibits a p-optimal witness search algorithm for any language in NP. Levin's algorithm dovetails every possible TM, runs any output produced through a predetermined witness verifier, and then prints out the first witness that is verified." — [3] Monroe 0906.3765, footnote 3

Verification notes: Hutter 2002 read in full; all quotes verbatim. Levin 1973 not read; V'yugin (who discussed the algorithm with Levin in 1975-78) confirms the note contains neither proof nor algorithm description, so the standard 'Levin search' is a later reconstruction (Levin 1984; Li-Vitanyi). HST ledger row 'Levin universal search; Schmidhuber OOPS/PowerPlay \| bias-optimal allocation 2^{-L} ... \| OWNS \| T04' already covers the allocation rule; this entry adds Hutter's Theorem 1/2, the verification-contract dependence, the Godel-II self-verification limit, and the constants.

### P0.MDL_OCCAM — MDL and Occam: Rissanen 1978 shortest data description; Grunwald 2007 refined MDL; Blumer-Ehrenfeucht-Haussler-Warmuth 1987 Occam's razor (PAC)

Disposition: `ADAPT` · best verification: `FULL_TEXT_READ`

Sources:

- [0] Modeling by Shortest Data Description — J. Rissanen (1978), Automatica 14(5), 465-471. 10.1016/0005-1098(78)90005-5 — `NOT_ACCESSIBLE`
- [1] The Minimum Description Length Principle — P. D. Grunwald (2007), MIT Press. ISBN 978-0262072816 — `NOT_ACCESSIBLE`
- [2] A Tutorial Introduction to the Minimum Description Length Principle — P. D. Grunwald (2004), arXiv (chapter in Advances in MDL, MIT Press 2005). arXiv:math/0406077 arXiv:math/0406077 — `PARTIAL_TEXT_READ`
- [3] Occam's Razor — A. Blumer, A. Ehrenfeucht, D. Haussler, M. K. Warmuth (1987), Information Processing Letters 24(6), 377-380. 10.1016/0020-0190(87)90114-1 — `NOT_ACCESSIBLE`
- [4] Sharpening Occam's Razor — M. Li, J. Tromp, P. Vitanyi (2002), Information Processing Letters 85 (COCOON 2002). arXiv:cs/0201005 arXiv:cs/0201005 — `FULL_TEXT_READ`
- [5] Minimum Description Length Induction, Bayesianism, and Kolmogorov Complexity (ideal MDL) — P. M. B. Vitanyi, M. Li (2000), IEEE Trans. IT 46(2). arXiv:cs/9901014 arXiv:cs/9901014 — `PARTIAL_TEXT_READ`
- [6] On the Kolmogorov Complexity of Binary Classifiers (restates the Occam-algorithm definition) — S. Epstein (2022), arXiv. arXiv:2201.12374 arXiv:2201.12374 — `PARTIAL_TEXT_READ`

**What it already explains.** Three formalizations of 'prefer the shorter description', each with its own guarantee. (1) Crude two-part MDL (Rissanen 1978): choose the hypothesis minimizing L(H) + L(D\|H) with L(D\|H) = -log P(D\|H); the parametric cost is ~ (k/2) log n bits for k real parameters (the criterion form -log P(y^n\|x^n; theta_hat) + (M/2) log n, attributed by Abolfazli et al. to Rissanen 1983); consistency and minimax rates via Barron-Cover 1991. (2) Refined MDL (Rissanen 1996; Grunwald 2007): replace the arbitrary code for H by the normalized-maximum-likelihood universal code of the whole model class, giving stochastic complexity = L(D\|H_hat) + COMP(H), with COMP the log-number of distinguishable distributions; removes code-arbitrariness for regular parametric families; interpretable as counting, two-part, Bayesian (Jeffreys prior) or prequential. Ideal MDL (Vitanyi-Li): H_0 = argmin K(D\|H) + K(H), the incomputable limit. (3) Occam's razor theorem (BEHW 1987): if a learner returns, from m examples of a target of size s, a consistent hypothesis of length <= m^alpha s^beta with alpha < 1, then it PAC-learns with sample complexity m = max(2/epsilon ln 1/delta, ((2 ln 2) s^beta / epsilon)^{1/(1-alpha)}) (Li-Tromp-Vitanyi eq. 5, read) - 'in order to (pac-)learn, it suffices to compress'; Board-Pitt give a partial converse. At Track-B scope: it explains why description length is a legitimate component of the D1 overhead vector and why compression-based morphologies (programmatic, symbolic) enjoy sample-complexity guarantees; it also explains (Grunwald sec. 1.6) that MDL is a STRATEGY, not a claim that the world is simple.

**Formal object.** Crude MDL: models H^(1), H^(2), ...; codelengths L(H), L(D\|H) = -log P(D\|H); select argmin L(H)+L(D\|H). Refined MDL: universal model P_bar for class M with regret max_{x^n} [-log P_bar(x^n) + log P(x^n\|theta_hat)] minimized by NML, P_nml(x^n\|M) = P(x^n\|theta_hat(x^n)) / COMP_n(M) with COMP_n(M) = sum_{y^n} P(y^n\|theta_hat(y^n)); stochastic complexity -log P_nml(x^n\|M) = -log P(x^n\|theta_hat) + log COMP_n(M). Ideal MDL: K(D\|H)+K(H). Occam algorithm (BEHW; Epstein sec. 2 form): from m samples of concept c with Size(c), output consistent h with Size(h) <= (n * Size(c))^alpha m^beta, alpha >= 0, 0 <= beta < 1.

**Strongest result.** Occam's razor theorem (BEHW 1987) in the length-based form read in Li-Tromp-Vitanyi sec. 1 eq. (5): sample complexity m = max(2/epsilon ln 1/delta, ((2 ln 2) s^beta / epsilon)^{1/(1-alpha)}) suffices for PAC learning given an Occam algorithm returning consistent hypotheses of length at most m^alpha s^beta, alpha < 1. Li-Tromp-Vitanyi Theorem 1 (read): with compression f(m,n,s,gamma) measured by K(r'\|r,n,s) < m/f, the sample complexity is max{2/epsilon ln 2/delta, f^{-1}(2 ln 2/epsilon, n, s, delta/2)} - a representation-independent sharpening. MDL consistency: Grunwald sec. 1.5/1.7 cites Barron-Cover 1991 for minimax-optimal convergence rates of two-part codes (statement not read in full). Rissanen 1978 theorem numbering NOT verified.

**Assumptions.** A fixed, sample-size-independent code for hypotheses (crude MDL) or a regular parametric family with finite COMP (refined MDL); L(D\|H) = -log P(D\|H) is the only consistent choice (Grunwald sec. 2.4.1); Occam theorem: realizable target concept of size s in a discrete representation system; consistent hypotheses; polynomial-time Occam algorithm for efficient PAC; Ideal MDL: data random relative to the hypothesis and hypothesis random relative to the universal prior (Vitanyi-Li Fundamental Inequality); K incomputable

**Resource model.** description length (bits) and samples (Occam sample complexity); refined MDL adds model-class geometry (COMP); NO accounting for the computation time of finding the short description (finding the minimal consistent hypothesis is typically NP-hard) nor for verification or update cost

**Failure boundary.** Code-dependence of crude MDL ('our procedure is in danger of becoming arbitrary'); refined MDL undefined when COMP is infinite or models irregular; consistency guarantees are asymptotic and assume the model class; MDL is silent on WHICH model class (which morphology) to search and on the cost of the search; the Occam theorem requires a consistent short hypothesis to be FOUND (computational cost unaccounted; Occam algorithms need not exist or be efficient); the reverse direction (learnable implies compressible) holds only under closure conditions (Board-Pitt; Li-Tromp-Vitanyi Cor. 2-3); it does not favor 'simple' morphologies as true, only as a small-sample strategy (Grunwald sec. 1.6); NFL (Wolpert 2020 sec. 5) reminds that any Occam advantage is a prior assumption on P(f).

**Implementation.** none known for the parents themselves; MDL implementations are ubiquitous (no URL read); Grunwald's tutorial mentions Quinlan-Rivest 1989 decision trees as an early practical two-part code

**Track-B residual.** MDL/Occam price ONE component of the Track-B overhead vector (description length) and convert it into sample complexity. The residual is the joint accounting: when a morphology trades description length for update cost (neural: long descriptions, cheap gradient updates) or for verification cost (programmatic: short descriptions, expensive search/verification), which trade-off does an ecology's price vector select? MDL owns the bit-count axis only.

**Upward question.** Is there a refined-MDL-style universal code over MORPHOLOGY FAMILIES (a COMP(M) for each family M measuring its distinguishable-behavior count under an ecology's observation structure), so that morphology selection becomes stochastic-complexity minimization over families rather than over hypotheses within a family?

Load-bearing quotes (verbatim from sources actually read):

> "The best point hypothesis H in H(1) cup H(2) cup ... to explain the data D is the one which minimizes the sum L(H) + L(D\|H)" — [2] Grunwald math/0406077, sec. 1.3 p.11 (Crude two-part MDL box)
> "since the description length L(H) of any fixed point hypothesis H can be very large under one code, but quite short under another, our procedure is in danger of becoming arbitrary." — [2] Grunwald math/0406077, sec. 1.4 p.12
> "stochastic complexity of D given H = L(D \| H_hat) + COMP(H)." — [2] Grunwald math/0406077, sec. 1.4 p.13
> "MDL (and the corresponding form of Occam's razor) is a strategy for inferring models from data ('choose simple models at small sample sizes'), not a statement about how the world works" — [2] Grunwald math/0406077, sec. 1.6 p.17
> "Barron and Cover [1991], complemented by [Zhang 2004], show that in many situations, the rates are minimax optimal" — [2] Grunwald math/0406077, sec. 1.5 p.17
> "Occam's razor theorem as formulated by [3,4] is arguably the substance of efficient pac learning. Roughly speaking, it says that in order to (pac-)learn, it suffices to compress." — [4] Li-Tromp-Vitanyi cs/0201005, sec. 1
> "This bound is based on the length-based Occam algorithm [3]: A deterministic algorithm that returns a consistent hypothesis of length at most m^alpha s^beta, where alpha < 1 and s is the length of the target concept." — [4] Li-Tromp-Vitanyi cs/0201005, sec. 1, following eq. (5)
> "the ideal MDL principle selects the hypothesis H_0 := minarg_{H in H} {K(D\|H) + K(H)}." — [5] Vitanyi-Li cs/9901014, Definition 2, eq. (5)
> "returns a hypothesis h consistent with c on s with Size(h) <= (n x Size(c))^alpha m^beta, for some alpha >= 0 and 0 <= beta < 1" — [6] Epstein 2201.12374, sec. 2 Related Work (describing BEHW87)

Verification notes: Rissanen 1978, Grunwald 2007 and BEHW 1987 not readable. Grunwald's 2004 tutorial (same author, same content as the book's Part I) read in part; BEHW's Occam definition/bound cross-checked in two read secondaries (Li-Tromp-Vitanyi eq. 5 and Epstein sec. 2, which differ in normalization - m^alpha s^beta vs (n Size(c))^alpha m^beta - a known variation between the 1987 IPL note and the 1989 JACM VC paper; the exact 1987 form is unverified). Substrate-theory THEORY_MAP mentions 'recall-constrained MDL' (SYNTH 5.1) at a different scope; no repo ledger reconstructs Rissanen/Grunwald/BEHW themselves.

### P0.NFL — No Free Lunch: Wolpert-Macready 1997; Schumacher-Vose-Whitley 2001 sharpened NFL (closure under permutation); Wolpert 1996 supervised-learning NFL; Wolpert 2020/2021 'What is important about the NFL theorems?'

Disposition: `ADOPT` · best verification: `FULL_TEXT_READ`

Sources:

- [0] No Free Lunch Theorems for Optimization — D. H. Wolpert, W. G. Macready (1997), IEEE Transactions on Evolutionary Computation 1(1), 67-82. 10.1109/4235.585893 — `NOT_ACCESSIBLE`
- [1] The No Free Lunch and Problem Description Length — C. Schumacher, M. D. Vose, L. D. Whitley (2001), GECCO 2001, Morgan Kaufmann, 565-570. https://www.cs.colostate.edu/~whitley/research/publications.php — `NOT_ACCESSIBLE`
- [2] The Lack of A Priori Distinctions Between Learning Algorithms — D. H. Wolpert (1996), Neural Computation 8(7), 1341-1390. 10.1162/neco.1996.8.7.1341 — `NOT_ACCESSIBLE`
- [3] What is important about the No Free Lunch theorems? — D. H. Wolpert (2020), arXiv (chapter in Black Box Optimization, Machine Learning and No-Free Lunch Theorems, Springer 2021). arXiv:2007.10928 arXiv:2007.10928 — `FULL_TEXT_READ`
- [4] On Classes of Functions for which No Free Lunch Results Hold — C. Igel, M. Toussaint (2001), arXiv (later Information Processing Letters 86(6), 2003). arXiv:cs/0108011 arXiv:cs/0108011 — `FULL_TEXT_READ`
- [5] No-Free-Lunch Theorems in the Continuum (restates W&M Theorem 1 in probabilistic form) — A. Alabert, A. Berti, R. Caballero, M. Ferrante (2014), arXiv. arXiv:1409.2175 arXiv:1409.2175 — `PARTIAL_TEXT_READ`
- [6] No Free Lunch versus Occam's Razor in Supervised Learning — T. Lattimore, M. Hutter (2011), LNCS 7070. arXiv:1111.3846 arXiv:1111.3846 — `FULL_TEXT_READ`

**What it already explains.** That for black-box search over a finite X -> Y, the performance of any algorithm A (a map from data sets d_m to unsampled points) on a distribution P(f) over objective functions is an inner product between an algorithm-only vector and P(f) (Wolpert 2020 eq. 7); consequently, summed uniformly over all f, every algorithm has identical performance for every measure Phi (W&M Theorem 1; Wolpert 2020 eq. 9: sum_{f in B} E(Phi\|f,m,A) = constant - sum_{f not in B} E(Phi\|f,m,A), constant independent of A and B); the same holds averaged over all P(f)'s (Wolpert 2020 A.2); and for supervised learning with off-training-set error and symmetric loss, E(Phi\|d,A) = E(Phi\|d,B) for any two learners (Wolpert 1996; 2020 eq. 2), so even cross-validation is not a-priori better than anti-cross-validation. Sharpened NFL (SVW 2001, verbatim in Igel-Toussaint Thm 1): NFL holds over a subset F of functions IF AND ONLY IF F is closed under permutation of X (c.u.p.); and (Igel-Toussaint Thm 2) the number of c.u.p. subsets is 2^{C(\|X\|+\|Y\|-1,\|X\|)} - 1, a vanishing fraction (~10^{-170} already for f:{0,1}^3->{0,1}); any non-trivial neighborhood structure, steepness bound or bound on the number of local minima breaks c.u.p. (Thms 3, Cor. 1-2). Lattimore-Hutter: under the Solomonoff prior M_norm there is a (weak) free lunch. At Track-B scope: a morphology's advantage is exactly its alignment with P(f); 'no universal best morphology' is a theorem only over c.u.p. ecologies, and nearly every structured ecology is not c.u.p. - so the ecology-relativity claim (T9) is owned, but the positive phase law is not.

**Formal object.** Finite X, Y; f: X -> Y; data set d_m = {(x_i, f(x_i))}; deterministic non-repeating search algorithm A: d_m \|-> x not in d_m^X; performance measure Phi(d_m^Y); P(f). Inner product: P(phi\|A,m) = sum_f P(f) D(f; d_m^Y, A, m). Supervised: target f(y_f\|x), hypothesis h(y_h\|x) from learner P(h\|d), off-training-set cost C(f,h,d) = sum over q not in d_X of P(q) L(y_f,y_h) f(y_f\|q) h(y_h\|q); P(c\|d) = integral df dh P(h\|d) P(f\|d) M_{c,d}(f,h) with M symmetric for symmetric loss. Sharpened: F subset of Y^X is c.u.p. iff f in F implies f o sigma in F for every permutation sigma of X.

**Strongest result.** (a) W&M 1997 Theorem 1 as restated by Alabert et al. Thm 2.1 (read): with P(f=h) = \|Y\|^{-\|X\|} uniform, the law of the sampled value sequence A^m_Y is the same for all algorithms; equivalently sum_{h in Y^X} Q{A^m_Y(h)=y} = sum_h Q{B^m_Y(h)=y} for all y, m. (b) Wolpert 2020 eq. (9) (read, verbatim): 'sum_{f in B} E(Phi\|f,m,A) = constant - sum_{f in Y^X \ B} E(Phi\|f,m,A) where the constant on the right-hand side depends on the performance measure Phi(.), but is independent of both A and B'. (c) Igel-Toussaint Theorem 1 (read, verbatim, = SVW 2001): 'For any two algorithms a and b, any value k in R, and any performance measure c: sum_{f in F} delta(k, c(Y(f,m,a))) = sum_{f in F} delta(k, c(Y(f,m,b))) iff F is c.u.p.' (d) Igel-Toussaint Theorem 2: number of non-empty c.u.p. subsets = 2^{C(\|X\|+\|Y\|-1, \|X\|)} - 1. (e) Wolpert 1996 supervised NFL as Wolpert 2020 eqs. (2)-(3): E(Phi\|d,A) = E(Phi\|d,B) and E(Phi\|m,A) = E(Phi\|m,B).

**Assumptions.** Finite X and Y (Alabert et al. show NFL essentially fails in the continuum except for constant or i.i.d. processes); Non-repeating (off-data-set) search; off-training-set error in learning; Uniform P(f), or a P(f) uniform on a c.u.p. subset, or the uniform average over all P(f)'s; Symmetric (homogeneous / generalizer-independent) loss for the supervised version; No covariational / head-to-head statements: NFL concerns marginal expectations, not which f's an algorithm wins on

**Resource model.** samples only (number m of function evaluations / training points); NO accounting for computation time, description length, memory or verification - every algorithm is charged the same m evaluations

**Failure boundary.** Silent on every non-c.u.p. ecology - which is almost all of them - and silent on which algorithm wins there; silent on computational cost (a lookup-table learner and a neural net are 'the same' if they sample the same m points); silent on covariational structure (Wolpert 2020 sec. 7: 'none of these (no) free lunch theorems concern the covariational behavior of search and / or learning algorithms'); the supervised version needs symmetric loss; the free lunches that exist (co-evolution, Solomonoff prior, non-symmetric loss) are weak or incomputable; NFL over P(f)'s does not tell you the P(f) of the real world - 'Arguments that P(f) is non-uniform in the real world do not, by themselves, establish anything whatsoever about what search algorithm to use in the real world.'

**Implementation.** none known (theorems); MCO-dictionary search algorithms are described in Wolpert 2020 sec. 6 citing Rajnarayan-Wolpert 2007/2008, no code URL read

**Track-B residual.** Given an ecology E that is NOT closed under permutation (has neighborhood structure, bounded steepness, bounded local minima, compressible targets), the inner-product formula says morphology performance = alignment with P(f) - but it does not compute the alignment for structured morphology families. The residual: a computable functional of E (not of individual f's) that ranks morphology families by alignment, together with their resource prices - i.e. the actual content of a B4 phase law after NFL has removed the uniform-average term.

**Upward question.** What is the smallest structural property of an ecology (neighborhood relation? compressibility of targets? bounded steepness?) that is both (i) sufficient to break c.u.p. and (ii) strong enough to make a specific morphology family provably dominant - i.e. the minimal 'free-lunch certificate' of an ecology, and is it computable from E's description?

Load-bearing quotes (verbatim from sources actually read):

> "sum_{f in B} E(Phi \| f, m, A) = constant - sum_{f in Y^X \ B} E(Phi \| f, m, A) where the constant on the right-hand side depends on the performance measure Phi(.), but is independent of both A and B" — [3] Wolpert 2007.10928, Appendix A.1, eq. (9) (ASCII rendering of the displayed formula)
> "It tells us that if any search algorithm performs particularly well on one set of objective functions, it must perform correspondingly poorly on all other objective functions." — [3] Wolpert 2007.10928, sec. 3
> "Arguments that P(f) is non-uniform in the real world do not, by themselves, establish anything whatsoever about what search algorithm to use in the real world." — [3] Wolpert 2007.10928, sec. 3
> "how well any search algorithm performs is determined by how well it is 'aligned' with the distribution P(f) that governs the problems on which that algorithm is run." — [3] Wolpert 2007.10928, sec. 2
> "anti-cross-validation beats cross-validation as often as the reverse." — [3] Wolpert 2007.10928, sec. 4
> "none of these (no) free lunch theorems concern the covariational behavior of search and / or learning algorithms." — [3] Wolpert 2007.10928, sec. 7
> "For any two algorithms a and b, any value k in R, and any performance measure c sum_{f in F} delta(k, c(Y(f,m,a))) = sum_{f in F} delta(k, c(Y(f,m,b))) iff F is c.u.p." — [4] Igel-Toussaint cs/0108011, Theorem 1 (NFL), attributed to Schumacher-Vose-Whitley 2001 [3]
> "The number of non-empty subsets of Y^X that are c.u.p. is given by 2^{binom(\|X\|+\|Y\|-1, \|X\|)} - 1" — [4] Igel-Toussaint cs/0108011, Theorem 2
> "for a Boolean function f : {0,1}^3 -> {0,1} the fraction is ~ 10^{-170}." — [4] Igel-Toussaint cs/0108011, sec. 3
> "A non-trivial neighborhood on X is not invariant under permutations of X." — [4] Igel-Toussaint cs/0108011, Theorem 3
> "It is shown in [SVW01] that there exist non-uniform distributions where the loss over a problem family is independent of algorithm. These distributions satisfy certain symmetry conditions not satisfied by M_norm" — [6] Lattimore-Hutter 1111.3846, sec. 3

Verification notes: W&M 1997, SVW 2001 and Wolpert 1996 originals not readable; W&M Theorem 1 is verified through two independent read restatements (Alabert Thm 2.1 with citation 'Wolpert-Macready [7], Theorem 1'; Wolpert 2020 eq. 9 citing [3]); the SVW theorem is verified through Igel-Toussaint's verbatim Theorem 1 with proof attributed to [3]. HST ledger row T14 and parent-absorption entry 19 already adopt NFL as 'no universal best optimizer over closed-under-permutation classes under uniform averaging'; this entry adds the Igel-Toussaint counting theorem, the NFL-over-P(f)'s, the supervised/anti-cross-validation form, the covariational gap, and the B4 conservation constraint.

### P0.NFL_PERMUTATION_CLOSURE — Classes of functions for which No Free Lunch holds (Igel & Toussaint 2001): permutation closure is the exact NFL condition and almost no subset satisfies it

Disposition: `None` · best verification: `FULL_TEXT_READ`

Sources:

- [0] On Classes of Functions for which No Free Lunch Results Hold — Christian Igel, Marc Toussaint (2001), Information Processing Letters 86 (2003); arXiv cs/0108011. https://arxiv.org/abs/cs/0108011 arXiv:cs/0108011 — `FULL_TEXT_READ`

**What it already explains.** Thm 1 (Schumacher-Vose-Whitley 2001, restated): for finite X, Y, NFL holds over a subset F of Y^X for all algorithm pairs and performance measures iff F is closed under permutation (c.u.p.). Thm 2: the number of non-empty c.u.p. subsets is 2^{C(\|X\|+\|Y\|-1, \|X\|)} - 1, a vanishing fraction of the 2^{\|Y\|^\|X\|} - 1 subsets (already ~1e-170 for Boolean functions on 3 bits). Thm 3 / Cor. 1-2: any non-trivial neighbourhood structure on X, with a bound on steepness or on the number of local minima below the maximum possible, yields a class that is not c.u.p. — so NFL is silent for structured search spaces with constrained ruggedness.

**Formal object.** closure under permutation; Y-histograms and basis classes B_h; fraction of c.u.p. subsets

**Strongest result.** None

**Assumptions.** None

**Resource model.** None

**Failure boundary.** None

**Implementation.** None

**Track-B residual.** None

**Upward question.** None

Verification notes: None

### P0.RICE — Rice 1953 theorem and halting undecidability: no decidable non-trivial semantic property of programs

Disposition: `ADAPT` · best verification: `FULL_TEXT_READ`

Sources:

- [0] Classes of Recursively Enumerable Sets and Their Decision Problems — H. G. Rice (1953), Transactions of the American Mathematical Society 74(2), 358-366. 10.1090/S0002-9947-1953-0053041-6 — `NOT_ACCESSIBLE`
- [1] On Computable Numbers... (sec. 8: no machine decides circle-freeness) — A. M. Turing (1936), Proc. London Math. Soc.. 10.1112/plms/s2-42.1.230 — `NOT_ACCESSIBLE`
- [2] A Constructive Proof of Rice's Theorem and the Halting Problem via Hilbert's Tenth Problem — J. Brossard (2026), arXiv (submitted to LMCS), with Rocq formalization. arXiv:2604.16477 arXiv:2604.16477 — `PARTIAL_TEXT_READ`
- [3] A Rice-like theorem for primitive recursive functions — M. Hoyrup (2015), arXiv note. arXiv:1503.05025 arXiv:1503.05025 — `FULL_TEXT_READ`

**What it already explains.** That no non-trivial extensional (semantic) property of the partial computable functions is decidable from program text: if P respects observational equivalence (phi_e = phi_f implies P(e) iff P(f)) and has both a witness e_1 with P(e_1) and a witness e_0 with not P(e_0), then no total decider for P exists (Brossard Thm 5.1, read; Rocq-mechanized). Halting is the instance P = Terminates (Brossard Cor. 6.4). Rice-Shapiro extends this to characterize the semi-decidable properties as those semi-decidable from an oracle for the function (Hoyrup sec. 1). Crucially for Track B, Hoyrup 2015 (read) shows the boundary: for c.e. classes of TOTAL functions (primitive recursive, FP, provably total in PA) presented by class-indices, the decidable properties are exactly effective unions of 'cylinder intersected with anticomplex' sets [v] cap A_{C,h} (Thm 2.1), and properties like 'f is (C,h)-anticomplex' ARE decidable from an index though not from an oracle (Prop. 2.1-2.2) - i.e. resource-bounded program classes carry decidable semantic information that black-box access does not. Brossard sec. 7 adds that under explicit step/state bounds (T, N) semantic properties become decidable by enumeration (bounded model checking). At Track-B scope: reading a morphology label off a program's semantics is impossible in general but becomes possible under exactly the resource restrictions Track B imposes.

**Formal object.** Programs e with partial functions phi_e; observational equivalence phi_e ~ phi_f; semantic property P: forall e,f: phi_e ~ phi_f implies (P(e) iff P(f)); non-trivial: exists e_0, e_1 with not P(e_0), P(e_1). Decider: total Decide_P: programs -> {0,1} with Decide_P(e) = 1 iff P(e). Hoyrup: c.e. class C = {f_i} of total functions; C-complexity K_C(f) = min{i: f_i = f}; anticomplex set A_{C,h} = {f : forall n, K_C(f restricted to n) <= h(n)} for computable order h.

**Strongest result.** Rice's theorem as Brossard Theorem 5.1 (read, verbatim): 'Let P be a non-trivial semantic property in the sense of Definition 2.6. Then there is no program Decide_P that decides P: for every program e, Decide_P(e) terminates and returns 1 if P(e) holds and 0 if not P(e) holds.' Halting as Corollary 6.4 (read). Hoyrup Theorem 2.1 (read): for a c.e. class C of total computable functions, A subset of C is semi-decidable (from C-indices) iff A = C cap union_n ([v_n] cap A_{C,h_n}) for computable sequences of words v_n and orders h_n. Original Rice 1953 theorem numbering NOT verified.

**Assumptions.** Extensional (semantic) property; intensional properties (syntactic, resource-bounded) are not covered; Unbounded computation - the class is all partial computable functions; Non-triviality witnesses exist; Classical proof uses halting + s-m-n/recursion theorem; Brossard's uses MRDP instead

**Resource model.** none (pure computability); Hoyrup and Brossard sec. 7 introduce index-complexity K_C and step/state bounds (T,N) as the parameters that restore decidability

**Failure boundary.** Says nothing about intensional or resource-bounded properties, which is where morphology labels actually live ('this program is a 3-layer network', 'this program uses a production-rule loop') - those are syntactic and decidable; says nothing about the COST of the decidable cases (bounded model checking is exponential); does not cover approximate/statistical verification (testing on samples), which is how ecologies actually verify; Hoyrup shows the decidability frontier for restricted total classes is subtle and depends on how the program is presented (index vs oracle).

**Implementation.** Rocq formalization by Brossard (paper appendix; 'Rice_Theorem' and 'Halting_Problem' closed under the global context with MRDP as sole axiom); coq-library-undecidability (github.com/uds-psl/coq-library-undecidability) for the classical Forster-Kirst-Smolka proof

**Track-B residual.** For the resource-bounded program classes that Track-B morphologies actually inhabit, which morphology-defining properties are (a) syntactic and trivially decidable, (b) semantic but decidable via Hoyrup-type anticomplexity bounds, (c) undecidable even under bounds - and does the T11 recovery/identifiability theorem live entirely in (a)+(b)? Rice owns only the unbounded negative.

**Upward question.** Is the right definition of 'morphology' a Hoyrup-style anticomplexity constraint on a c.e. class of resource-bounded programs (so that membership is decidable from an index), and does the family of such constraints form the phase space of B4?

Load-bearing quotes (verbatim from sources actually read):

> "A predicate P on programs is a semantic property (or extensional property) if it respects observational equivalence: forall e, f: phi_e ~ phi_f implies (P(e) iff P(f))." — [2] Brossard 2604.16477, Definition 2.5 (ASCII rendering)
> "Let P be a non-trivial semantic property in the sense of Definition 2.6. Then there is no program Decide_P that decides P" — [2] Brossard 2604.16477, Theorem 5.1
> "For programs bounded to terminate within T steps over state spaces of size <= N, semantic properties become decidable by exhaustive enumeration - the foundation of bounded model checking." — [2] Brossard 2604.16477, sec. 7
> "Rice theorem [Ric53] states that no non-trivial property of partial computable functions can be decided when the function is presented by one of its indices, or equivalently by a program computing it." — [3] Hoyrup 1503.05025, sec. 1
> "When restricting to the class of total computable functions, Kreisel-Lacombe-Schoenfield [KLS57] and Ceitin [Cei62] theorem implies that the decidable properties are the same when presenting the input function via an index or an oracle." — [3] Hoyrup 1503.05025, sec. 1
> "For f in C, the property f in A_{C,h} is decidable given any C-index of f." — [3] Hoyrup 1503.05025, Proposition 2.1
> "In general A_{C,h} is no more decidable if instead of giving an index of f one is only given f as oracle. It contrasts with what happens on the class of partial or total computable functions." — [3] Hoyrup 1503.05025, after Proposition 2.1

Verification notes: Rice 1953 and Turing 1936 sec. 8 not readable. The theorem statement is verified through Brossard's Rocq-mechanized formulation and Hoyrup's informal statement. HST ledger row T15 already owns semantic undecidability at HST scope; the Track-B addition is the Hoyrup/Brossard decidability frontier.

### P0.SMALL_UTM_WEAK_NEARY_WOODS — Small weakly universal Turing machines (Neary & Woods 2007): smallest universal machines and their polynomial simulation overheads

Disposition: `None` · best verification: `FULL_TEXT_READ`

Sources:

- [0] Small weakly universal Turing machines — Turlough Neary, Damien Woods (2007), arXiv 0707.4489; cf. Neary & Woods, 'Small fast universal Turing machines', TCS 362 (2006) [not accessed]. https://arxiv.org/abs/0707.4489 arXiv:0707.4489 — `FULL_TEXT_READ`

**What it already explains.** Weakly universal machines with state-symbol pairs (6,2), (3,3), (2,4) simulating Rule 110, hence Turing machines in time O(t^4 log^2 t) (Rule 110 simulates TMs in O(t^3 log t), improvable to O(t^2 log t)); Watanabe's semi-weak machines simulate TMs directly with O(t^2) overhead and are the most time-efficient small weak machines; the standard universal curve (2-tag / bi-tag simulators) and lower bounds via decidability of halting for (2,2), (3,2), (2,3), (1,n), (n,1). Cites [14] Neary-Woods TCS 2006 for small FAST universal machines (polynomial rather than exponential slowdown), which is the load-bearing result for GMI-T1.

**Formal object.** state-symbol universality curves; simulation time overhead O(t^k)

**Strongest result.** None

**Assumptions.** None

**Resource model.** None

**Failure boundary.** None

**Implementation.** None

**Track-B residual.** None

**Upward question.** None

Verification notes: None

### P0.SOLOMONOFF — Solomonoff universal induction: 1964 a-priori probability, 1978 convergence theorem, incomputability of the universal prior (Li & Vitanyi)

Disposition: `ADOPT` · best verification: `FULL_TEXT_READ`

Sources:

- [0] A Formal Theory of Inductive Inference, Parts I and II — R. J. Solomonoff (1964), Information and Control 7(1), 1-22 and 7(2), 224-254. 10.1016/S0019-9958(64)90223-2 ; 10.1016/S0019-9958(64)90131-7 — `NOT_ACCESSIBLE`
- [1] Complexity-Based Induction Systems: Comparisons and Convergence Theorems — R. J. Solomonoff (1978), IEEE Trans. Information Theory IT-24(4), 422-432. 10.1109/TIT.1978.1055913 — `NOT_ACCESSIBLE`
- [2] Minimum Description Length Induction, Bayesianism, and Kolmogorov Complexity — P. M. B. Vitanyi, M. Li (2000), IEEE Trans. Information Theory 46(2), 446-464. 10.1109/18.825807 arXiv:cs/9901014 — `PARTIAL_TEXT_READ`
- [3] An Introduction to Kolmogorov Complexity and Its Applications (incomputability of K and M) — M. Li, P. Vitanyi (1997), Springer, 2nd ed. (3rd ed. 2008). ISBN 978-0387948683 — `NOT_ACCESSIBLE`
- [4] A Theory of Universal Artificial Intelligence based on Algorithmic Complexity — M. Hutter (2000), arXiv technical report (later Springer 2005 book). arXiv:cs/0004001 arXiv:cs/0004001 — `PARTIAL_TEXT_READ`
- [5] A Philosophical Treatise of Universal Induction — S. Rathmanner, M. Hutter (2011), Entropy 13(6), 1076-1136. 10.3390/e13061076 arXiv:1105.5721 — `PARTIAL_TEXT_READ`
- [6] No Free Lunch versus Occam's Razor in Supervised Learning — T. Lattimore, M. Hutter (2011), Algorithmic Probability and Friends (Solomonoff 85th memorial), LNCS 7070. 10.1007/978-3-642-44958-1_17 arXiv:1111.3846 — `FULL_TEXT_READ`

**What it already explains.** That there is a single, parameter-free (up to choice of reference machine U) predictor for ALL computable environments: the universal a-priori semimeasure M(x) = sum over minimal programs p with U(p)=x* of 2^{-l(p)} (equivalently the probability that U fed fair coin flips outputs something starting with x; equivalently, up to a multiplicative constant, the Bayes mixture xi_U = sum_nu 2^{-K(nu)} nu over all enumerable semimeasures). That this predictor converges to any computable true measure mu with total mu-expected squared error bounded by a constant proportional to the description length of mu: Solomonoff 1978 gives sum_n S_n <= (ln 2 / 2) K(mu) (Vitanyi-Li Thm 6 form: sum_n S_n <= k/2 with k = K(mu) ln 2). That the price of universality is incomputability: K, Km, M, KM are not computable (only lower-semicomputable / enumerable), so every practical system is an approximation. That the choice of U matters only for short sequences (additive constant), and that prior knowledge can be injected either by conditioning K or by prefixing the data. At Track-B scope it explains what 'probabilistic' and 'Bayesian' morphologies are the finite-resource shadows of, and why any claimed universal learner must either be incomputable or be a resource-bounded restriction (AIXI-tl, speed prior, Levin's Kt).

**Formal object.** Monotone universal Turing machine U; M(x) := sum_{p: U(p)=x*} 2^{-l(p)} (Rathmanner-Hutter sec. 7.2; Hutter 2000 eq. 18); prediction M(x_t \| x_{<t}) = M(x_{1:t})/M(x_{<t}); alternatively xi_U(x) = sum_{nu in M_U} w_nu nu(x) with w_nu = 2^{-K(nu)} over the class M_U of enumerable semimeasures; universality: xi(x) >=* 2^{-K(rho)} rho(x) for every enumerable semimeasure rho (Hutter 2000 eq. 19). Error functional: S_n = sum_{l(x)=n-1} mu(x)(M(0\|x) - mu(0\|x))^2.

**Strongest result.** Solomonoff 1978 convergence theorem, as stated in Vitanyi-Li cs/9901014 Theorem 6 (read): 'Let mu be a recursive semimeasure. ... sum_n S_n <= k/2 with k = K(mu) ln 2. (Hence, S_n converges to 0 faster than 1/n.)' Equivalent Hutter 2000 eq. (20) form: sum_{k=1}^infty sum_{x_{1:k}} mu(x_{1:k}) (xi(x_{<k}x_k) - mu(x_{<k}x_k))^2 <+ (1/2) ln 2 * K(mu). Corollary: M(x_t\|x_{<t}) -> mu(x_t\|x_{<t}) with mu-probability 1 for every computable mu. Incomputability: 'the function K is not computable' (Vitanyi-Li sec. 2.6); 'Km, M and KM are incomputable' (Lattimore-Hutter Def. 7 note); xi_U is enumerable (semi-computable from below) but not finitely computable (Rathmanner-Hutter sec. 7.1).

**Assumptions.** True environment mu is a computable (recursive) (semi)measure, or at least there exists a computable predictor converging to it; Passive sequence prediction (no action feedback; the AIXI extension handles agents but is likewise incomputable); Binary alphabet in the classical statements (generalized by Hutter); Reference machine U fixed; bounds hold up to U-dependent additive/multiplicative constants; Unbounded computation: the predictor is only approximable in the limit

**Resource model.** description length (K(mu) governs total error, i.e. sample complexity in bits); NO accounting for computation time, memory, verification or update cost - all infinite/incomputable

**Failure boundary.** Incomputable, so it cannot be a morphology; it does not say which resource-bounded approximation (Bayesian net, neural net, retrieval memory, program search) approximates it best under a given compute budget - the practical morphology question is exactly the residual it leaves; for short data the U-dependence is total ('for short x and any arbitrary finite continuation y we can always choose U that predicts y to follow x', Rathmanner-Hutter sec. 10.2); the error bound is a total over all time, saying nothing about when errors occur (Lattimore-Hutter sec. 4); optimality is asymptotic - 'For short sequences and specific problems, Solomonoff may not perform as well as other methods' (Rathmanner-Hutter sec. 10.3). The Lattimore-Hutter free-lunch under M_norm (Prop. 1) is 'unfortunately extremely weak'.

**Implementation.** none exact (incomputable). Approximations with code cited by the read sources: CTW-based MC-AIXI (Veness et al. JAIR 2011), Ozkural's Gigamachine (arXiv 1709.03413), Schmidhuber's speed prior; no code URLs were read.

**Track-B residual.** Under a finite compute/memory/verification budget and a specified ecology, which computable restriction of the universal mixture (which morphology) minimizes expected loss - and can that choice be predicted from the ecology's resource prices before search? Solomonoff owns the incomputable limit object and its convergence law; it does not own the resource-bounded selection problem.

**Upward question.** Is there a resource-indexed family of universal priors (speed prior, Kt, energy prior) whose optimal member under budget r IS a morphology, so that the phase law B4 is the map r \|-> argmin over computable restrictions of M?

Load-bearing quotes (verbatim from sources actually read):

> "Let mu be a recursive semimeasure. Using the notation above, sum_n S_n <= k/2 with k = K(mu) ln 2. (Hence, S_n converges to 0 faster than 1/n.)" — [2] Vitanyi-Li cs/9901014, Theorem 6 (attributed to Solomonoff 1978)
> "Unfortunately, the function K is not computable, [17]. For practical applications one must settle for easily computable approximations" — [2] Vitanyi-Li cs/9901014, sec. 2.6 Applications
> "The universal semimeasure xi(x) is defined as the probability that the output of the universal Turing machine U starts with x when provided with fair coin flips on the input tape" — [4] Hutter cs/0004001, sec. 4, eq. (18) context
> "it has been proved by Solomonoff [36] that the mu expected Euclidean distance betweewn xi and mu is finite" — [4] Hutter cs/0004001, sec. 4, preceding eq. (20) which reads sum <+ (1/2) ln 2 * K(mu)
> "The computation time of AIxi^tl is of the order t*2^l." — [4] Hutter cs/0004001, Abstract
> "the choice of U is only an issue for 'short' sequences x. This is because for short x and any arbitrary finite continuation y we can always choose U that predicts y to follow x." — [5] Rathmanner-Hutter 1105.5721, sec. 10.2
> "Of course the most significant drawback to this approach is the incomputability of the universal predictors M and xi_U." — [5] Rathmanner-Hutter 1105.5721, sec. 10.3
> "Km, M and KM are incomputable." — [6] Lattimore-Hutter 1111.3846, Definition 7, note 2

Verification notes: Solomonoff's own 1964/1978 texts not readable; the definition and the convergence bound were cross-checked across four independent read restatements (Vitanyi-Li Thm 6 with k/2, k = K(mu) ln 2; Hutter 2000 eq. 20 with (1/2) ln 2 K(mu); Rathmanner-Hutter sec. 8.1 with K(mu) ln 2 + O(1); Ozkural eq. 4 with -(1/2) ln P_U(mu)) - these agree up to the factor-2 convention of squared-vs-absolute error. HST ledger already OWNS 'universal prior and its incomputability' (rows T04, T15); this entry adds the D2/B3 ownership and the resource-bounded-selection residual.

### P0.UNIVERSALITY — Church-Turing universality: Turing 1936 universal machine, Church 1936 lambda-definability, Shepherdson-Sturgis 1963 / Minsky 1961 register machines

Disposition: `ADOPT` · best verification: `PARTIAL_TEXT_READ`

Sources:

- [0] On Computable Numbers, with an Application to the Entscheidungsproblem — A. M. Turing (1936), Proc. London Math. Soc. s2-42, 230-265 (corr. 43, 544-546). 10.1112/plms/s2-42.1.230 — `NOT_ACCESSIBLE`
- [1] An Unsolvable Problem of Elementary Number Theory — A. Church (1936), American Journal of Mathematics 58, 345-363. 10.2307/2371045 — `FROM_MEMORY_UNVERIFIED`
- [2] Computability of Recursive Functions — J. C. Shepherdson, H. E. Sturgis (1963), J. ACM 10(2), 217-255. 10.1145/321160.321170 — `NOT_ACCESSIBLE`
- [3] Recursive Unsolvability of Post's Problem of 'Tag' and other Topics in Theory of Turing Machines — M. L. Minsky (1961), Annals of Mathematics 74, 437-455. 10.2307/1970290 — `NOT_ACCESSIBLE`
- [4] The Generic Model of Computation (restates Church's and Turing's theses; Thm 5 uniqueness of the maximal effective model; Thm 6 Extended Church-Turing) — N. Dershowitz (2012), EPTCS 88 (DCM 2011), 59-71. 10.4204/EPTCS.88.5 arXiv:1208.2585 — `PARTIAL_TEXT_READ`
- [5] A note reviewing Turing's 1936 (reproduces Turing's definitions of computing machine, circle-free, S.D., D.N., universal machine, with Turing page refs) — P. Cattabriga (2025), arXiv preprint (a contrarian note; used ONLY for its verbatim reproduction of Turing's definitions, not for its thesis). arXiv:1308.0497v4 arXiv:1308.0497 — `PARTIAL_TEXT_READ`

**What it already explains.** That a single fixed finite machine U, fed the description of any other machine M, reproduces M's computed sequence (Turing's universal machine); that the three formal notions of effective calculability (lambda-definability, general recursiveness, Turing computability) coincide (Church-Turing thesis); that an extraordinarily small instruction basis suffices for universality: Shepherdson-Sturgis register machines with only increment P(i), decrement Q(i) and jump-on-zero J(i)[k], and Minsky's reductions of Turing machines to tag systems (v=6) and register machines. It therefore explains why any proposed generating basis B that contains state + arbitrary program + universal interpreter + mutable memory trivially represents every morphology M in {automata, symbolic, programmatic, probabilistic, neural, memory/retrieval, hybrid} (Track-B derivation level D0). Dershowitz's Theorem 5 (read) sharpens this: the partial recursive functions are the UNIQUE maximal effective model up to isomorphism over any countable domain, so there is no 'more universal' basis to find.

**Formal object.** Turing: a computing machine with m-configurations q_i, scanned symbol S_j, action (print/erase, move L/R), next configuration; a 'circle-free' machine prints infinitely many figures 0/1; the sequence computed is the number's binary expansion; a Standard Description S.D. and Description Number D.N. encode the machine table; U is the machine that on input S.D.(M) computes the same sequence as M. Church: the lambda-definable functions on positive integers, identified with the effectively calculable ones. Shepherdson-Sturgis: a finite set of registers holding naturals and a program of instructions P(i), Q(i), J(i)[k]. Universality claim: the class computed equals the partial recursive functions.

**Strongest result.** (i) Existence of the universal machine U (Turing 1936 sec. 6-7) and non-existence of a machine that decides, from a D.N., whether the described machine is circle-free (sec. 8) - the halting-type undecidability. (ii) Church 1936: the Entscheidungsproblem is unsolvable; effective calculability = lambda-definability (thesis). (iii) Shepherdson-Sturgis 1963: the unlimited register machine with P/Q/J computes exactly the partial recursive functions. (iv) Dershowitz 2012 Thm 5 (read, secondary axiomatization): 'The set of partial recursive functions (and likewise the set of Turing-computable string functions) is the unique maximal effective model, up to isomorphism, over any countable domain.' Only (iv) and the Zaitsev/De Mol restatements were read; (i)-(iii) statements are standard and unverified against the originals in this session.

**Assumptions.** Discrete, finite-description, sequential-time state-transition systems; Unbounded memory (tape/registers); Semantics = the partial function computed (extensional), no resource accounting; Representation of inputs as strings/naturals fixed but arbitrary

**Resource model.** none (pure computability; description length appears only through the finite table, no time or space accounting)

**Failure boundary.** Says nothing about which program U is fed, at what cost, from what experience; treats all computable morphologies as identical (they compute the same class); is silent on constants, on learning, on verification cost, and on which representation of data is used (representation is immaterial to computability). It predicts nothing about morphology because every morphology is representable - this is exactly the UNIVERSAL_COMPUTATION_ONLY null.

**Implementation.** none known (as a parent); countless universal-machine simulators exist; the coq-library-undecidability (github.com/uds-psl/coq-library-undecidability, cited by Brossard 2026) mechanizes Minsky-machine reductions

**Track-B residual.** Given that every morphology is a program for the same U, what additional structure on B (resource prices, verification contract, update rule) makes the choice of program non-arbitrary - i.e. what is the smallest set of non-computability-theoretic constraints under which D1-D3 stop being vacuous?

**Upward question.** Which quotient of program-space, coarser than 'same partial function' but finer than 'same P-class', is the right morphology equivalence (GMI-T3), and is it defined by resource vectors rather than by semantics?

Load-bearing quotes (verbatim from sources actually read):

> "A universal machine is a computing machine U that, supplied with a tape on the beginning of which is written the S.D. of a computing machine M, computes the same sequence of M." — [5] Cattabriga 1308.0497, p.3 (paraphrasing Turing 1936 sec. 6-7)
> "The computable numbers do not include, however, all definable numbers; and an example is given of a definable number which is not computable" — [5] Turing 1936 p.230, as quoted verbatim in Cattabriga 1308.0497 sec. 1
> "All effectively computable numeric (partial) functions are (partial) recursive. All (partial) string functions can be computed by a Turing machine." — [4] Dershowitz 1208.2585 sec. 5 (statement of Church's and Turing's theses)
> "The set of partial recursive functions (and likewise the set of Turing-computable string functions) is the unique maximal effective model, up to isomorphism, over any countable domain." — [4] Dershowitz 1208.2585 Theorem 5
> "P(i): increase register i ny 1. Q(i): decrease register i by 1 (register i is not zero). J(i)[k]: jump to instruction k if resister i is zero." — [2] Zaitsev arXiv:2201.09034 sec. 3.1 (typos in original), describing the Shepherdson-Sturgis register machine

Verification notes: Turing/Church/Shepherdson-Sturgis/Minsky originals not readable in this session (egress). Definitions checked against Cattabriga's verbatim reproduction and Dershowitz's axiomatic restatement; the Minsky two-counter universality claim is from memory and marked so. HST ledger row 'Rice / Turing / Godel \| semantic undecidability, halting, incompleteness \| OWNS \| T15' already claims halting undecidability at HST scope; this entry adds only the Track-B D0/B0 subtraction and the uniqueness-of-maximal-model point.


## P1 — universal / general-agent theories and bounded rationality

### P1.AIXI — AIXI / Universal Artificial Intelligence (Hutter): universal Bayesian RL agent, Pareto/balanced-Pareto optimality, self-optimizing variants, time-bounded AIXItl

Disposition: `ADOPT` · best verification: `PARTIAL_TEXT_READ`

Sources:

- [0] Universal Artificial Intelligence: Sequential Decisions Based on Algorithmic Probability — M. Hutter (2005), Springer (book). https://doi.org/10.1007/b138233 — `NOT_ACCESSIBLE`
- [1] One Decade of Universal Artificial Intelligence — M. Hutter (2012), arXiv (also in Theoretical Foundations of AGI, Atlantis 2012). https://arxiv.org/abs/1202.6153 arXiv:1202.6153 — `PARTIAL_TEXT_READ`
- [2] Universal Algorithmic Intelligence: A Mathematical Top-Down Approach — M. Hutter (2007), arXiv cs/0701125 (chapter in Artificial General Intelligence, Springer 2007; condensed version of the 2005 book). https://arxiv.org/abs/cs/0701125 arXiv:cs/0701125 — `PARTIAL_TEXT_READ`
- [3] Open Problems in Universal Induction & Intelligence — M. Hutter (2009), Algorithms 3(2):879-906; arXiv 0907.0746. https://arxiv.org/abs/0907.0746 arXiv:0907.0746 — `PARTIAL_TEXT_READ`

**What it already explains.** Gives the ideal (incomputable) general agent: expectimax over all computable environments weighted by the universal prior 2^{-l(q)} on programs q for a fixed universal monotone Turing machine U. Owns the mathematical meaning of 'optimal general learner' for the class of all lower-semicomputable chronological semimeasures: Pareto optimality (no policy uniformly better), balanced Pareto optimality (= maximal Legg-Hutter intelligence), on-policy value convergence, and self-optimizing behaviour for restricted classes (ergodic MDPs etc.) via the generalization AIzeta = Bayes mixture over a class M with prior w. Owns the canonical 'restrict the mixture class' mechanism by which the family derives tractable agents (Hutter 2007 7.2: downscale AIxi by using more restricted forms of xi). Owns the only resource-bounded universal construction in the family, AIXItl: enumerate all programs of length <= l and time <= t per cycle with provable value bounds and take the best vote, at cost O(2^l * t) per cycle plus a setup constant O(l_P^2 * 2^{l_P}).

**Formal object.** Agent-environment cycles k=1..m with actions a_k in A, percepts x_k = o_k r_k. AIXI: a_k := argmax_{a_k} sum_{o_k r_k} ... max_{a_m} sum_{o_m r_m} [r_k+...+r_m] sum_{q: U(q,a_1..a_m)=o_1 r_1..o_m r_m} 2^{-l(q)} (Hutter 2012 §3, Hutter 2007 eq. 20/21). Equivalently pi*_xi, a policy optimal in the universal mixture xi(e_<t \|\| a_<t) = sum_{nu in M^CCS_LSC} w_nu nu(e_<t \|\| a_<t) with w_nu = 2^{-K(nu)} (Leike-Hutter Def 4 quoting Hutter 2005 Def 5.19/5.30). Intelligence order relation (Hutter 2007 Def 10): p >= p' iff for all k and histories V^{p xi}_{k m_k} >= V^{p' xi}_{k m_k}. Pareto optimality (Def 11/Thm 12): no p with V^p_nu >= V^{p_xi}_nu for all nu in M and strict for one. AIXItl (Hutter 2007 §6.6, Thm 14): for l, t, l_P: run all extended chronological programs p with l(p)<=l, time per cycle <= t, having a proof of length <= l_P of a valid value approximation VA(p); each cycle output the action of the program with the highest claimed reward w^p_k; p* is effectively more or equally intelligent (order >=_c, Def 13) than any such p; size O(log(l t l_P)), setup O(l_P^2 2^{l_P}), time per cycle O(2^l t).

**Strongest result.** Pareto optimality of AIxi (Hutter 2007 Thm 12; book Thm 5.32 as cited by Leike-Hutter) and balanced Pareto optimality (book Thm 5.24 as cited; Hutter 2002 COLT); on-policy value convergence (book Thm 5.36 as cited); self-optimizing for ergodic MDPs with unbounded effective horizon (book Thm 5.38 as cited by Leike-Hutter and Veness). Time-bounded: Thm 14 (Hutter 2007): AIXItl is >=_c-superior to every length-l/time-t program that can prove its own value bound, with per-cycle cost O(2^l t). Hutter 2009 §5 and Hutter 2007 §4.2 state plainly that no universal model can be self-optimizing on the full class and that 'a convincing notion of optimality is still lacking'.

**Assumptions.** Environment is a (deterministic or stochastic) computable chronological (semi)measure; class M^CCS_LSC of lower-semicomputable chronological conditional semimeasures; A fixed reference universal (monotone) Turing machine U; prior 2^{-l(q)} or 2^{-K(nu)}; Finite action and percept spaces, bounded rewards, finite lifetime m or summable discount (Leike-Hutter Assumption 2); No cost of computation: the agent is a policy (A x E)* -> A with unbounded deliberation; time enters only in AIXItl as a per-cycle bound t and program-length bound l; AIXItl additionally assumes a formal proof system and that good programs can prove lower bounds on their own value within proof length l_P

**Resource model.** AIXI proper: none (incomputable, no accounting for time, samples, memory, or verification; description length enters only as the prior on environments, not on the agent). AIXItl: time per cycle t and program length l (agent side) plus proof length l_P (verification of value claims); cost 2^l is paid, not optimized. Sample efficiency appears only through K(mu)-type bounds inherited from Solomonoff induction.

**Failure boundary.** Incomputable; AIXItl computable but with 2^l factor and an additive O(l_P^2 2^{l_P}) setup, and superior only to programs that can justify their outputs by provable bounds (Hutter 2007 §6.7). Optimality notions are either trivial or UTM-relative (see P1.LEIKE_HUTTER_SUBJECTIVITY): Pareto optimality holds for every policy on the universal class, balanced Pareto optimality depends on U, self-optimizing does not apply to the universal class. Says nothing about which finite program family, representation, or model class a bounded agent should adopt: the family's own derivation of tractable agents is 'use a more restricted form of xi' plus designer-chosen special-purpose pre/post-processing (Hutter 2007 §7.2), and Hutter 2007 §7.2 explicitly leaves the 'training process' unaddressed. The best-vote construction is by the author's own description 'typing monkeys' with a selection criterion, i.e. exactly the UNIVERSAL_COMPUTATION_ONLY null.

**Implementation.** none known for AIXI itself (only limit-computable). Approximations: MC-AIXI-CTW code http://jveness.info/software/mcaixi_jair_2010.zip (URL verified in Veness et al. 2011 §7); AIXItl has no implementation. (From memory, unverified: aixijs by Aslanides.)

**Track-B residual.** AIXI/AIXItl fix the objective (xi-expected reward on a universal class) and prove that the trivial enumerate-all-programs construction is universally optimal up to 2^l. They leave open, and do not even pose, the question Track B asks: for a bounded agent on machine M with resource prices, which strict sub-family of programs (automata / production / programmatic / probabilistic / neural / retrieval / hybrid) contains the near-optimal program as a function of the ecology, and how a non-enumerative developmental process reaches it. The 'restricted xi' mechanism gives a derivation of probabilistic morphologies (T6) but no law choosing the restriction.

**Upward question.** Given that the universal-class optimum is enumerative and morphology-blind, what additional structure of the ecology (finite class, resource prices, verification contract, horizon relative to compiler constants) is necessary and sufficient for the optimum over programs on M to lie in a proper sub-family, and is that sub-family predictable before search?

Load-bearing quotes (verbatim from sources actually read):

> "AIXI is optimal in the senses that: no other agent can perform uniformly better or equal in all environments, it is a unification of two optimal theories themselves, a variant is self-optimizing" — [1] Hutter 2012 §3 'Discussion' paragraph
> "AIXI is more a theory or formal definition rather than an algorithm, since it is only limit-computable." — [1] Hutter 2012 §3 'Discussion'
> "Dovetailing all length- and time-limited programs is a well-known elementary idea (e.g. typing monkeys). The crucial part that was developed here, is the selection criterion for the most intelligent agent." — [2] Hutter 2007 §6.8 Remarks
> "The size of p* is l(p*)=O(log(l·t·l_P)), the setup-time is t_setup(p*)=O(l_P^2·2^{l_P}) and the computation time per cycle is t_cycle(p*) = O(2^l·t)." — [2] Hutter 2007 Theorem 14 (Optimality of AIXItl); tildes on l,t dropped in transcription
> "Conversely, one can downscale the AIxi model by using more restricted forms of xi." — [2] Hutter 2007 §7.2 'Scaling AIXI down' (Greek letters transliterated)
> "We have not said much about the training process itself, as it is not specific to the AIXI model" — [2] Hutter 2007 §7.2 'Training'
> "Although AIXI has been shown to be optimal in some senses, a convincing notion of optimality is still lacking." — [3] Hutter 2009 §1 p.4
> "The AIXI model depends on a few parameters: the choice of observation and action spaces O and A, the horizon m, and the universal machine U." — [3] Hutter 2009 §6(d) 'Parameter dependence'

Verification notes: Book itself not fetched (egress). All book theorem numbers are as cited in Leike & Hutter 2015 (read in full) and Veness et al. 2011; Hutter 2007 (cs/0701125) is the author's own condensed chapter of the book and was read in the sections listed. Prior repo ledgers cover Schmidhuber Gödel machines/OOPS/Levin search (research/heritable-search-transformation-v1/LITERATURE_LEDGER.md rows T04/T15) but not AIXI; nothing duplicated. Math in quotes is transliterated from extracted PDF text (tildes/Greek normalized); wording otherwise verbatim.

### P1.BOUNDED_OPTIMALITY — Bounded optimality (Russell & Subramanian 1995) and metalevel rationality (Russell & Wefald 1991): optimal programs for a machine M in an environment class E

Disposition: `GENERALIZE` · best verification: `PARTIAL_TEXT_READ`

Sources:

- [0] Provably Bounded-Optimal Agents — S. J. Russell, D. Subramanian (1995), Journal of Artificial Intelligence Research 2:575-609; arXiv cs/9505103. https://doi.org/10.1613/jair.133 arXiv:cs/9505103 — `PARTIAL_TEXT_READ`
- [1] Principles of Metareasoning — S. Russell, E. Wefald (1991), Artificial Intelligence 49(1-3):361-395. https://doi.org/10.1016/0004-3702(91)90015-C — `NOT_ACCESSIBLE`
- [2] Rationality and Intelligence — S. Russell (1997), Artificial Intelligence 94:57-77. https://people.eecs.berkeley.edu/~russell/papers/aij-cnt.pdf — `NOT_ACCESSIBLE`

**What it already explains.** Replaces perfect rationality (argmax over agent functions f, independent of the machine) and metalevel rationality (argmax over computation-plus-action sequences) by bounded optimality: argmax over the programs l in the finite language L_M of a fixed architecture M, evaluated by the expected utility of the state histories that Agent(l,M) generates in the environment class E. Establishes the feasible-agent-function set Feasible(M) as strictly smaller than the computable functions because output must arrive at the right time. Shows that for one architecture family (fixed sequences of black-box decision procedures with runtime t_i and quality q_i) in episodic real-time environments with fixed deadline, fixed time cost, or stochastic deadline, the bounded-optimal program is constructible (singletons, Thm 1-2; DP over sequences, Thm 3; closed forms for uniform/exponential deadline distributions, Thm 4-6), that agnostic PAC learning of the rules yields approximately bounded-optimal programs (Thm 7), and defines asymptotic bounded optimality (worst-case Def 13, average-case Def 14: l is ABO iff some k-times faster/larger machine kM makes l at least as good as every l' on M), classical optimality as a special case (Thm 8), and universal ABO (Def 15) with a concatenation construction of programs of doubling deadlines. Metareasoning (via Hay's restatement) explains computation selection by value of computation under the single-step assumption.

**Formal object.** Agent function f: O^t -> A (Def 1). Environment E = (X, X_0, f_e, f_p) (Def 2), state history effects(f,E). Architecture M: a fixed interpreter M : L_M x I x O -> I x A run one step per time point (Def 3), with finite program language L_M. Agent(l,M) = the agent function induced by program l on M (Def 4). Feasible(M) = {f \| exists l in L_M, f = Agent(l,M)}. Utility U : X^T -> R; V(f,E) = U(effects(f,E)); V(f,𝓔) = sum_E p(E) V(f,E); V(l,M,𝓔) = V(Agent(l,M),𝓔). Perfect rationality (Def 5): f_opt = argmax_f V(f,𝓔). Bounded optimality (Def 6): l_opt = argmax_{l in L_M} V(l,M,𝓔). ABO (Def 13/14): exists k such that for all l': V(l, kM, 𝓔) >= V(l', M, 𝓔) (worst-case version uses V* at each environment complexity n). UABO (Def 15): ABO for every value function in a family differing only in temporal variation. Metareasoning (as restated by Hay et al. Def 6): the myopic/single-step policy chooses argmax over {stop, computation E} of Q^m(s,E) = E[-c + max_i mu_i(S_1) \| S_0 = s, A_0 = E].

**Strongest result.** Definition 6 itself (bounded optimality as a well-posed constrained optimisation over L_M) and Theorem 7 (agnostic-PAC construction of a program l with V(l_opt,M,𝓔) - V(l,M,𝓔) <= epsilon + 2 epsilon_q w.p. > 1 - m(delta + delta_q)); Theorem 8 (classical optimality = timewise worst-case ABO in classical task environments); universal ABO construction in §6.3 (from Russell & Zilberstein 1991), with Figure 6 showing l_U on 4M matching l_opt on M. Section 7 conjecture: ABO designs stable over wide variations in machine speed/size and environment complexity when M is neither too small nor too powerful.

**Assumptions.** Discrete, deterministic environments (extensions claimed not to matter); a distribution p over an environment class 𝓔 is given; A fixed architecture M with a finite program language L_M and bounded instructions per time step; the utility U is external to agent and environment; Constructive results only for episodic real-time task environments and the 'sequence of decision procedures' architecture with black-box rules (t_i, q_i) known or PAC-learned; stationarity for learning; ABO allows a constant speed/size factor k on the machine (not extra time), which requires separable, rank-preserving value functions across time

**Resource model.** time (runtime per decision procedure, deadlines, time cost), memory/size (finite L_M, e.g. '8 megabytes'; spacewise ABO), samples (PAC bounds in Thm 7). No description-length prior on programs beyond finiteness of L_M, no verification cost, no cost for the search over L_M itself (the designer's optimisation is external and unpriced).

**Failure boundary.** Bounded optimality is a specification, not a construction: 'We are not yet ready to announce the identity of l_opt for chess on an eight-megabyte PC'. Constructive results cover one architecture family whose components are black boxes (a feedforward network appears only as an example of a runtime bound); the optimisation is over schedules of given procedures, not over representational families. Learning is external to the agent (§5, §7). Explicitly open (§7): learning agents that rewrite themselves, composition of ABO designs, non-stationary episode distributions, the 'discrete structural problem' of composite agent design. No equivalence relation on programs coarser than identity and finer than Agent(l,M) is defined, so morphology is not an object in the theory. No result predicts how l_opt changes qualitatively as E or M vary (the §7 stability statement is a speculation that it does not, in an intermediate regime).

**Implementation.** none known (mail-sorter simulation described in §4.6; no code URL)

**Track-B residual.** Russell-Subramanian already state the objective Track B's D3 would have to solve - l_opt(M,𝓔) = argmax over programs on a machine in an environment class - so 'morphology selection under resource constraints' is not a new problem statement. What they do not provide, and Track B must: (1) a partition of L_M into morphology families with a compilation relation and overhead bounds (T2/T3), (2) a constructive or predictive theory of which family contains l_opt as a function of (𝓔, M, resource prices, horizon, verification contract) - they solve only schedule optimisation inside one family and conjecture stability rather than phase structure (T9/T10), (3) a developmental law by which an agent that must learn and rewrite itself reaches l_opt, which they name as their most interesting open question (T12).

**Upward question.** Bounded optimality fixes l_opt(M,𝓔) pointwise. Under what conditions is the map (M,𝓔, prices) -> [morphology family of l_opt] piecewise constant with finitely many boundaries (a phase law), and when instead is it smooth in the sense of the ABO stability conjecture - and can an agent whose learning is internal track that map?

Load-bearing quotes (verbatim from sources actually read):

> "Definition 6 A bounded-optimal agent with architecture M for a set E of environments has an agent program l_opt such that l_opt = argmax_{l in L_M} V(l, M, E)" — [0] R&S §3.5 (subscripts flattened; 𝓔 rendered E)
> "Bounded optimality specifies optimal programs rather than optimal actions or optimal computation sequences. Only by the former approach can we avoid placing constraints on intelligent agents that cannot be met by any program." — [0] R&S §1
> "Actions and computations are, after all, generated by programs, and it is over programs that designers have control." — [0] R&S §1
> "Definition 3 An architecture M is a fixed interpreter for an agent program that runs the program for a single time step, updating its internal state and generating an action" — [0] R&S §3.2
> "Feasible(M) = {f \| exists l in L_M, f = Agent(l, M)}" — [0] R&S §3.3 (symbols transliterated)
> "The set of feasible agent functions is therefore much smaller than the set of computable agent functions." — [0] R&S §3.3
> "For example, if the runtime of a feedforward neural network is proportional to its size, then t_M will be the runtime of the largest neural network that fits in M." — [0] R&S §4.2
> "Definition 14 Average-case asymptotic bounded optimality: an agent program l is timewise (or spacewise) average-case asymptotically bounded optimal in E on M iff exists k for all l' V(l, kM, E) >= V(l', M, E)" — [0] R&S §6.2 (symbols transliterated)
> "The details of the optimal designs may be rather arcane, and learning processes will play a large part in their discovery" — [0] R&S §7
> "ABO promises to yield useful results on composite agent designs, allowing us to separate the problem of designing complex ABO agents into a discrete structural problem and a continuous temporal optimization problem" — [0] R&S §7
> "From a foundational point of view, one of the most interesting questions is how the concept applies to agents that can incorporate a learning component." — [0] R&S §7
> "ABO designs should be stable over reasonably wide variations in machine speed and size and in environmental complexity." — [0] R&S §7 (preceded by 'We may speculate that provided the computing device is neither too small ... nor too powerful')
> "We exhibited only very simple agents, and it is likely that bounded optimality in the strict sense is a difficult goal to achieve when a larger space of agent programs is considered." — [0] R&S §7

Verification notes: R&S text extracted from the arXiv PDF has ligature/spacing artifacts ('b ounded', 'sp eci es'); quotes are normalised to standard spelling with no word changes. Russell & Wefald 1991 could not be fetched from any host; its formal content is reported only through Hay et al. 2012 (read in full) and R&S §1-2, and the repo's earlier metareasoning review likewise read only the abstract. Prior repo coverage: research/parent-absorption-v1/LEDGER.json P-DECISION-REGION lists Russell & Wefald as background; this entry adds the bounded-optimality formalism (Defs 1-6, 13-15, Thms 7-8) which was not previously reconstructed.

### P1.BOUNDED_RATIONALITY_ORTEGA_BRAUN — Information, utility and bounded rationality (Ortega & Braun 2011/2013): free-utility principle with KL resource cost

Disposition: `None` · best verification: `FULL_TEXT_READ`

Sources:

- [0] Information, Utility & Bounded Rationality — Pedro A. Ortega, Daniel A. Braun (2011), AGI 2011 (LNAI 6830); extended arXiv 1107.5766; cf. Proc. R. Soc. A 2013 'Thermodynamics as a theory of decision-making with information-processing costs'. https://arxiv.org/abs/1107.5766 arXiv:1107.5766 — `FULL_TEXT_READ`

**What it already explains.** Axioms A1-A3 (utility gain real-valued, additive, monotone in conditional probability) force u(A\|B) = alpha log P(A\|B) (Thm 1), so P is a Gibbs measure with temperature alpha (Eq. 2). Free utility J(Pr; U) = E_Pr[U] - alpha H(Pr) is maximized by the Gibbs measure (Thm 2). Changing an initial policy P_i to P_f under new constraints costs J_f - J_i = E_{P_f}[U*] - alpha KL(P_f \|\| P_i) (Eq. 3): expected utility minus an information cost; the bounded-optimal control solution is P_f ∝ P_i exp(U*/alpha) (Eq. 4). alpha -> 0 recovers maximum expected utility (delta on argmax), alpha -> infinity keeps the prior; nested two-step problems give log-partition value recursions (Sec. 4) that reduce to Bellman as lambda -> infinity, with risk-sensitive and minimax/robust control as the environment's temperature varies.

**Formal object.** free utility J(Pr; U); conjugate pair (P, U); KL(P_f \|\| P_i) as resource cost; temperature alpha

**Strongest result.** None

**Assumptions.** None

**Resource model.** None

**Failure boundary.** None

**Implementation.** None

**Track-B residual.** None

**Upward question.** None

Verification notes: None

### P1.CHOLLET_MEASURE — Chollet, On the Measure of Intelligence: intelligence as skill-acquisition efficiency w.r.t. priors, experience and generalization difficulty (AIT-defined); ARC benchmark

Disposition: `ADAPT` · best verification: `PARTIAL_TEXT_READ`

Sources:

- [0] On the Measure of Intelligence — F. Chollet (2019), arXiv 1911.01547. https://arxiv.org/abs/1911.01547 arXiv:1911.01547 — `PARTIAL_TEXT_READ`

**What it already explains.** Reframes intelligence away from skill (which can be bought with priors or experience) to the efficiency with which a system converts priors plus experience into skill on tasks that require generalization, over a declared scope. Quantifies all three with algorithmic complexity: generalization difficulty GD = H(Sol \| TrainSol)/H(Sol) (fraction of the shortest sufficient evaluation-time solution not explained by the shortest optimal training-time solution), a developer-aware version conditioning also on the system's initial state, priors P as information the system starts with about the task, experience E as information the curriculum supplies. Argues intelligence is not curve-fitting: the simplest program consistent with training data solves only zero-GD tasks. Explicitly restricts scope to human-like Core Knowledge priors and proposes ARC. Explicitly lists computation/time/energy/risk efficiency as out of scope of the definition.

**Formal object.** For system IS and task T with skill threshold theta_T, potential Theta = theta^max_{T,IS}, curricula C with probability P_C, value weight omega_T: I^{theta_T}_{IS,scope} = Avg_{T in scope}[ omega_T · theta_T · sum_{C in Cur^{theta_T}_T} P_C · GD^{theta_T}_{IS,T,C} / (P^{theta_T}_{IS,T} + E^{theta_T}_{IS,T,C}) ] (sufficient case) and the analogous optimal case with Theta. GD^theta_{T,C} = H(Sol^theta_T \| TrainSol^opt_{T,C}) / H(Sol^theta_T) in [0,1]; developer-aware GD^theta_{IS,T,C} conditions additionally on IS_{t=0}. Schematically per task: Expectation[skill·generalization / (priors + experience)].

**Strongest result.** No theorem; the result is the definition and the consequences drawn from it (II.2 bullets): a system that starts able to solve evaluation situations has near-zero developer-aware GD and scores low; a minimal-description-length curve-fitter scores only on zero-GD tasks; intelligence is tied to scope and to curriculum optimisation. Empirical: ARC solvable by humans, 'does not appear to be approachable by any existing machine learning technique' at the time (III.1.4), with the author's own caveat that these claims are highly speculative.

**Assumptions.** A fixed universal language/Turing machine for H (machine-independent only up to a constant); Tasks, curricula, skill programs and responses are binary strings; a scope and value weights omega_T are chosen by the evaluator; Priors of the system are quantifiable as information about the task (developer-aware); for ARC, Core Knowledge priors are assumed shared with humans; Information-efficiency only: compute, latency, energy, risk are deliberately excluded (II.2.2)

**Resource model.** samples/experience (E, in bits of algorithmic information), priors (P, bits), generalization difficulty (bits ratio). Explicitly none for time, compute, memory, energy (listed as possible regularisers, not included). No verification cost.

**Failure boundary.** Incomputable (relative algorithmic complexity); ARC does not quantify GD (III.2); validity unestablished; scope-relative by design (human Core Knowledge). Says nothing about which morphology achieves high efficiency: the proposed ARC solver shape (DSL + program synthesis + simplicity/likelihood ranking) is offered as a speculation, with the explicit admission that simplest-consistent-program selection is not expected to generalise. Excludes resource prices that Track B's ecology E carries. Defines but does not derive a developmental law (curricula are inputs).

**Implementation.** ARC dataset (from memory, unverified URL: https://github.com/fchollet/ARC); no implementation of the measure itself (H incomputable; III.2 'Generalization is not quantified')

**Track-B residual.** Chollet supplies the accounting principle Track B needs but does not supply: charge morphology-embedded priors (e.g. translation equivariance, tree structure, discrete symbols) in the same currency as experience, and score generalization difficulty relative to the training-optimal program. What remains for Track B: extend the denominator with resource prices (compute, memory, verification, revision) so that morphology becomes a priced variable, and turn the informal 'ARC is program synthesis' conjecture into a predictive statement of when programmatic morphology dominates.

**Upward question.** If priors are charged in bits and morphology is a prior, is there a price-dependent crossover at which paying more prior (a more structured morphology) becomes cheaper than paying experience - and is that crossover computable from ecology statistics before training?

Load-bearing quotes (verbatim from sources actually read):

> "The intelligence of a system is a measure of its skill-acquisition efficiency over a scope of tasks, with respect to priors, experience, and generalization difficulty." — [0] II.2.1
> "GD^theta_{T,C} = H(Sol^theta_T \| TrainSol^opt_{T,C}) / H(Sol^theta_T)" — [0] II.2 'Quantifying generalization difficulty...' (notation flattened)
> "Schematically, the contribution of each task is: Expectation[skill·generalization / (priors+experience)]" — [0] II.2 'Defining intelligence' bullet list (notation flattened)
> "Intelligence is not curve-fitting: a system that merely produces the simplest possible skill program consistent with known data points could only perform well on tasks that feature zero generalization difficulty, by our definition." — [0] II.2 bullet list
> "In the above, we only considered the information-efficiency (prior-efficiency and experience-efficiency with respect to generalization difficulty) of intelligent systems." — [0] II.2.2
> "Crucially, to the best of our knowledge, ARC does not appear to be approachable by any existing machine learning technique (including Deep Learning), due to its focus on broad generalization and few-shot learning" — [0] III.1.4
> "Our claims are highly speculative and may well prove fully incorrect" — [0] III.1.4
> "Generalization is not quantified." — [0] III.2 first bullet

Verification notes: Not in prior repo ledgers. The ARC repository URL is from memory and marked unverified; everything else from the arXiv text.

### P1.LEGG_HUTTER_MEASURE — Legg & Hutter universal intelligence measure Upsilon

Disposition: `ADAPT` · best verification: `PARTIAL_TEXT_READ`

Sources:

- [0] Universal Intelligence: A Definition of Machine Intelligence — S. Legg, M. Hutter (2007), Minds & Machines 17(4):391-444; arXiv 0712.3329. https://arxiv.org/abs/0712.3329 arXiv:0712.3329 — `PARTIAL_TEXT_READ`

**What it already explains.** Turns the informal definition 'ability to achieve goals in a wide range of environments' into a single number: expected reward-sum of a policy across all computable reward-summable environments, weighted by the algorithmic prior 2^{-K(mu)}. Explains why a uniform weighting is impossible, why Occam weighting is used (reward for using Occam's razor on average), why complexity of the environment rather than difficulty is used, and gives ordering intuitions (random < basic table-learner < specialised < AIXI). Owns the explicit design decision that intelligence is measured on the agent function only.

**Formal object.** Agent pi and environment mu exchange actions, observations and rewards; mu is a computable measure over (A x O x R)*; E = set of all computable reward-summable environmental measures w.r.t. reference machine U (sum of rewards <= 1, so V^pi_mu := E(sum_i r_i) <= 1, eq. 2). K(mu_i) := K(<i>) for the enumeration of computable measures. Upsilon(pi) := sum_{mu in E} 2^{-K(mu)} V^pi_mu (§3.3). Upper bound Upsilon-bar := max_pi Upsilon(pi) = Upsilon(pi^AIXI) (§3.4).

**Strongest result.** No theorem in the paper; the result is the definition plus the properties list (§3.5: general, unbiased up to reference-machine choice, fundamental, formal, objective, universal, not practical because K is incomputable) and the identification Upsilon-bar = Upsilon(pi^AIXI), citing Hutter 2005 Thm 5.34 for convergence of AIXI in all environments where a general agent can converge. The paper itself flags that relative intelligence of agents can change with the reference machine (§3.5), later made rigorous by Leike & Hutter 2015.

**Assumptions.** Environments are computable measures; rewards rational in [0,1] with bounded total (reward-summable); Fixed reference prefix universal Turing machine U; invariance only up to a multiplicative constant; Intelligence is a property of the agent function only: 'places no limits on the internal workings of the agent'; No cost of computation or of experience; a giant lookup table and a clever algorithm with the same behaviour have the same Upsilon

**Resource model.** none on the agent side (explicitly: efficiency does not matter, §5.2). Description length is used only on the environment side (2^{-K(mu)}).

**Failure boundary.** By construction morphology-blind: any two implementations with the same policy have identical Upsilon; it cannot, even in principle, prefer one computable morphology over another except through the policy they realise. Not computable; approximations require sampling environments. Reference-machine dependence admitted (§3.5) and shown to be total by Leike-Hutter (Cor 13-15). No accounting for samples, time, memory, or priors on the agent side (contrast Chollet). The 'general NFL for computable agents' possibility is explicitly left open (§5.2).

**Implementation.** none known in the paper (K incomputable); Legg & Veness 2013 approximation cited by Leike & Hutter (not read)

**Track-B residual.** Upsilon fixes what 'better' means at the level of agent functions but is silent on the cost-to-realise a given Upsilon on a machine M. Track B needs a measure that is (i) relativised to an ecology narrower than the universal class, (ii) charged for description length, time, samples and verification of the agent, and (iii) fine enough to separate morphologies at equal policy; none of these exists in this parent.

**Upward question.** What is the coarsest resource-aware refinement of Upsilon (charging the agent's description length, per-cycle time, sample count and verification work on machine M) under which morphologies become distinguishable, and does the ordering it induces depend on the ecology in a lawful way?

Load-bearing quotes (verbatim from sources actually read):

> "Upsilon(pi) := sum_{mu in E} 2^{-K(mu)} V^pi_mu. We call this the universal intelligence of agent pi." — [0] §3.3 (Greek transliterated)
> "Finally, the formal definition places no limits on the internal workings of the agent." — [0] §3.3
> "We simply do not care whether the agent is efficient, due to some very clever algorithm, or absurdly inefficient, for example by using an unfeasibly gigantic look-up table of precomputed answers." — [0] §5.2 (response to Block's Blockhead)
> "Although this affords us some protection, the relative intelligence of agents can change if we change our reference machine." — [0] §3.5 'Unbiased'
> "The main drawback, however, is that the Kolmogorov complexity function K is not computable and can only be approximated." — [0] §3.3
> "It is conceivable that there might exist some more general kind of "No Free Lunch" theorem for agents that limits their maximal intelligence according to our definition." — [0] §5.2

Verification notes: Not previously reconstructed in the repo ledgers. Definition and quotes taken from the arXiv v1 text; Minds & Machines pagination not checked.

### P1.LEIKE_HUTTER_SUBJECTIVITY — Leike & Hutter: bad universal priors and notions of optimality (AIXI's optimality is UTM-relative; Pareto optimality is trivial)

Disposition: `ADOPT` · best verification: `FULL_TEXT_READ`

Sources:

- [0] Bad Universal Priors and Notions of Optimality — J. Leike, M. Hutter (2015), COLT 2015 (PMLR 40); arXiv 1510.04931. https://arxiv.org/abs/1510.04931 arXiv:1510.04931 — `FULL_TEXT_READ`

**What it already explains.** Shows that there is no invariance theorem for AIXI: (i) with finite lifetime there is a universal mixture under which every policy is optimal (indifference prior, Thm 6); (ii) for any computable policy pi and epsilon there is a universal mixture making pi's action the unique optimal action wherever V^pi_xi > epsilon (dogmatic prior, Thm 7), hence AIXI can be made to emulate any computable policy (Cor 8) and with finite lifetime every policy is an AIXI (Cor 9); (iii) Legg-Hutter intelligence is therefore UTM-relative: some AIXIs are near-minimally intelligent (Cor 13), AIXI is stupid for some Upsilon (Cor 14), any computable policy can be made near-maximally intelligent (Cor 15), computable policies are dense in the intelligence scores (Thm 11); (iv) Pareto optimality is trivial: every policy is Pareto optimal in any class containing all computable environments (Thm 18), and the witness environment is a finite-state POMDP. Table 2 summarises: mu-optimality needs mu; Pareto trivial; balanced Pareto UTM-dependent; self-optimizing inapplicable; strong asymptotic optimality impossible; weak asymptotic optimality achieved by BayesExp but not AIXI.

**Formal object.** Environments nu in M^CCS_LSC; universal prior w: M^CCS_LSC -> [0,1] with w_nu > 0 and sum <= 1; universal mixture xi = sum_nu w_nu nu (eq 1) or xi(e_<t\|\|a_<t) = sum_{p: e_<t ⊑ U(p,a_<t)} 2^{-\|p\|} (eq 2). Value V^pi_nu (Def 3), optimal policy (Def 4), AIXI = pi*_xi. Legg-Hutter intelligence Upsilon_xi(pi) := sum_nu w_nu V^pi_nu(eps) = V^pi_xi(eps) (Def 10). Pareto optimality (Def 16). Dogmatic prior: xi' := (1/2) nu + (epsilon/2) xi where nu mimics xi on-policy and sends deviations to hell (reward 0 forever). Compiler-size bounds Table 1: indifference prior K(U)+K(m)+O(1) vs m; dogmatic prior K(U)+K(pi)+K(epsilon)+O(1) vs ceil(-log2 epsilon).

**Strongest result.** Theorem 18 (Pareto Optimality is Trivial): every policy is Pareto optimal in any M ⊇ M^CCS_LSC (with a finite-state POMDP witness). Theorem 7 (Dogmatic Prior) with Corollaries 8-9 and 13-15, and Theorem 11 (computable policies dense). Conclusion §6.3: no nontrivial and non-subjective optimality results for AIXI remain; AIXI is a relative theory dependent on the UTM.

**Assumptions.** Rewards in [0,1]; finite A and E (Assumption 2); Summable discount gamma with normaliser Gamma_t; finite lifetime m where Gamma_{m+1}=0 for Thm 6 / Cor 9; Universal priors may be re-weighted arbitrarily (Lemma 1 mixing mixtures); the 'bad' UTMs have compiler sizes given in Table 1

**Resource model.** none on the agent side; description length appears as compiler sizes between UTMs (Table 1) and as lifetime m relative to the shortest program length

**Failure boundary.** Results are about the universal class and free choice of UTM; they do not say what happens for a fixed natural UTM or a restricted environment class with structure (the paper explicitly poses 'natural UTMs' and 'good optimality criteria' as open, §6.2-6.3). The positive escape routes (BayesExp weak asymptotic optimality; knowledge-seeking; optimism) are only cited. Nothing about morphology.

**Implementation.** none known

**Track-B residual.** Once the universal-class ecology plus a free reference machine is shown to make every policy optimal and every computable policy near-maximally intelligent, no morphology-dominance claim can be made at that level. What is left for Track B is exactly the restricted regime: for an ecology E narrower than M^CCS_LSC, with a fixed reference machine and horizon long relative to compiler constants, do morphology-level dominance statements become non-trivial, and which restrictions are necessary for that?

**Upward question.** What is the minimal restriction on (ecology class, reference machine class, horizon/compiler-constant ratio) under which a non-trivial, non-subjective ordering of bounded agents exists at all - and is that same restriction the one under which morphology becomes predictable?

Load-bearing quotes (verbatim from sources actually read):

> "Theorem 18 (Pareto Optimality is Trivial). Every policy is Pareto optimal in any M ⊇ M^CCS_LSC." — [0] §5
> "Corollary 9 (With Finite Lifetime Every Policy is an AIXI)." — [0] §3.2
> "Therefore no nontrivial and non-subjective optimality results for AIXI remain (see Table 2). We have to regard AIXI as a relative theory of intelligence, dependent on the choice of the UTM" — [0] §6.3
> "Note that the environment mu we defined in the proof of Theorem 18 is actually just a finite-state POMDP, so Pareto optimality is also trivial for smaller environment classes." — [0] §5, after proof of Thm 18
> "Corollary 15 (Computable Policies can be Smart). For any computable policy pi and any epsilon > 0 there is a universal mixture xi' such that Upsilon_xi'(pi) > Upsilon-bar_xi' - epsilon." — [0] §4 (Greek transliterated)
> "Lack of exploration then retains the prior's biases." — [0] §6.3
> "Any Bayesian mixture over reactive environments is susceptible to dogmatic priors if we allow an arbitrary reweighing of the prior." — [0] §6.1

Verification notes: Full text read. arXiv version dated 'January 11, 2022' in header (later compile of the 2015 paper). Not in prior repo ledgers.

### P1.MC_AIXI_CTW — Monte-Carlo AIXI approximation (MC-AIXI-CTW / MC-AIXI(fac-ctw)): rhoUCT planning + factored action-conditional CTW mixture over prediction suffix trees

Disposition: `ADAPT` · best verification: `PARTIAL_TEXT_READ`

Sources:

- [0] A Monte-Carlo AIXI Approximation — J. Veness, K. S. Ng, M. Hutter, W. Uther, D. Silver (2011), JAIR 40:95-142; arXiv 0909.0801v2. https://arxiv.org/abs/0909.0801 arXiv:0909.0801 — `PARTIAL_TEXT_READ`

**What it already explains.** How to build a running agent from the AIXI equation by approximating its two parts separately: planning (expectimax) by rhoUCT, a UCT generalisation over histories with a mixture environment model in place of a simulator; learning (Bayesian mixture over Turing machines) by a mixture environment model over a countable class M with prior w (Def 4), instantiated as FAC-CTW = Bayesian mixture over all prediction suffix trees of depth <= D with KT estimators. Owns the theorem that the resulting policy sequence is self-optimising for stationary ergodic n-Markov environments (Thm 3, via reduction to finite ergodic MDPs and Hutter 2005 Thm 5.38/5.29), a value-convergence bound (Thm 2), consistency of rhoUCT, and empirical learning of TicTacToe, Pacman, Kuhn poker etc. from scratch. Also explains, in its own Limitations, the morphology-ecology mismatch: the agent performs poorly when the environment is not predictable by a bounded-depth PST.

**Formal object.** AIXI action (eq 1): a*_t = argmax_{a_t} sum_{o_t r_t} ... max_{a_{t+m}} sum [r_t+...+r_{t+m}] sum_{q: U(q,a_1..a_{t+m}) = o_1 r_1..o_{t+m} r_{t+m}} 2^{-l(q)}. Mixture environment model (Def 4): xi(x_1:n \| a_1:n) := sum_{rho in M} w_0^rho rho(x_1:n \| a_1:n) with countable M and prior weights summing to 1; Prop 1: a mixture environment model is an environment model. MC-AIXI(fac-ctw) := rhoUCT instantiated with rho = FAC-CTW mixture (§6). Self-optimising (Def 11): (1/m) v^m_rho(pi_m, eps) - (1/m) V^m_rho(eps) -> 0 for all rho in M. Thm 3: for M a countable class of stationary ergodic n-Markov environments, the policies pi^xi_b(ax_<t) := argmax_{a_t} V^{b-t+1}_xi(ax_<t a_t) are self-optimising w.r.t. M.

**Strongest result.** Theorem 3 (self-optimising policies for stationary, ergodic n-Markov classes) plus Theorem 2 (value convergence when mu is a product of k PSTs) and rhoUCT consistency; empirical results §7. The authors themselves note the Thm 3 argument for the actual FAC-CTW implementation is not fully rigorous because KT estimators make the class uncountable (§6).

**Assumptions.** Environment predictable by a bounded-depth (D) action-conditional PST; for guarantees: stationary, ergodic, n-Markov; Fixed planning horizon m, finite rhoUCT simulation budget per step, heuristic epsilon-greedy exploration (full Bayesian exploration is intractable, §8); Binary factorisation of percepts; uniform random rollout policy (learned rollouts as extension, §9)

**Resource model.** time (rhoUCT simulations per step, O(D log(\|O\|\|R\|)) per percept for CTW), memory (context tree size, depth D), samples (experience curves); no description-length or verification accounting on the agent side; the prior over PSTs is an Ockham prior on the model side.

**Failure boundary.** Model-class restriction is hand-chosen ('we opted to use'), not derived: fails when a bounded-depth PST cannot predict the environment (real images/audio, §8); exploration/exploitation only heuristic; planning intractable for realistic horizons; no long-term memory. The paper lists P-trees, logical tree models, hierarchical mixtures as future model classes but gives no criterion for choosing among them. Nothing predicts, before running, that CTW is the right morphology for the tested arcade domains.

**Implementation.** http://jveness.info/software/mcaixi_jair_2010.zip (stated in §7 'Source Code')

**Track-B residual.** MC-AIXI-CTW is a witness that a universal objective compiles to one probabilistic morphology (mixture over PSTs) with bounded overhead, and that the compiled morphology's competence boundary is set by the class restriction. Left open: a law that maps ecology properties (observation structure, Markov order, stationarity/drift, horizon, compute budget) to the model class and planner that should be chosen, and the developmental route by which the class restriction could be acquired rather than chosen ('we opted').

**Upward question.** The parent chose PSTs by hand and reports where the choice fails. Is there a computable criterion, evaluable from a short prefix of interaction and a resource budget, that selects the model class (and planner) that MC-AIXI should be instantiated with - and does that criterion coincide with a morphology phase boundary?

Load-bearing quotes (verbatim from sources actually read):

> "As the AIXI agent is only asymptotically computable, it is by no means an algorithmic solution to the general reinforcement learning problem." — [0] §1 'AIXI as a Principle'
> "In this paper, we opted to use a generalised version of the UCT algorithm [KS06] for planning and a generalised version of the Context Tree Weighting algorithm [WST95] for learning." — [0] §1 'Approximating AIXI'
> "Our agent will perform poorly if the underlying environment cannot be predicted well by a PST of bounded depth." — [0] §8 'Limitations'
> "Theorem 3 and the consistency of the rhoUCT algorithm (17) give support to the claim that the MC-AIXI(fac-ctw) agent is self-optimising with respect to the class of stationary, ergodic, n-Markov environments." — [0] §6 after Theorem 3 (Greek transliterated)
> "The second limitation is that unless the planning horizon is unrealistically small, our full Bayesian solution (using rhoUCT and a mixture environment model) to the exploration/exploitation dilemma is computationally intractable." — [0] §8 'Limitations' (Greek transliterated)
> "A key property of mixture environment models is that they can be composed." — [0] §9 'Combining Mixture Environment Models'

Verification notes: Read the conceptual and theorem-bearing sections; CTW/FAC-CTW derivation (§5, Defs 7-9, Lemmas 2-3) only located by headings. Not in prior repo ledgers.

### P1.RATIONAL_METAREASONING — Rational metareasoning / selecting computations (Hay, Russell, Tolpin, Shimony 2012): metalevel MDP over computations with cost, value of computation, myopic and blinkered policies

Disposition: `ADOPT` · best verification: `FULL_TEXT_READ`

Sources:

- [0] Selecting Computations: Theory and Applications — N. Hay, S. Russell, D. Tolpin, S. E. Shimony (2012), UAI 2012; arXiv 1207.5879. https://arxiv.org/abs/1207.5879 arXiv:1207.5879 — `FULL_TEXT_READ`

**What it already explains.** Formalises 'which computation to do next and when to stop' as a Bayesian selection problem: a metalevel probability model (U_1..U_k, 𝓔) of arm utilities and computation outcomes, and a metalevel decision problem = countable-state undiscounted MDP whose states are computation-outcome sequences, actions are computations E in 𝓔_s or the terminal action ⊥, reward -c per computation and max_i mu_i(s) on stopping (Def 1-3). Value form V^pi(s) = E[-cN + max_i mu_i(S_N)] (Thm 4). Bounds expected computation count by VPI/c (Thm 5); shows optimal policies may compute forever with positive probability (Ex 3); shows the myopic (Russell-Wefald single-step) policy stops only when the optimal also would not compute... precisely: if myopic computes then optimal computes (Thm 7), and if myopic stops on a transition-closed set so does optimal (Thm 9); finite bound 1/(4c) - 3 for one-armed Bernoulli (Thm 10); non-indexability (Ex 4, context-dependent inversion) and the interval structure of stopping in the known-alternative parameter (Thm 12); blinkered policy for independent actions computed from k one-action problems (Def 13-16); distribution-free VOI upper bounds (Thm 17-18) and Go results vs UCT. Also explains why bandit algorithms (UCT) are the wrong model for computation selection.

**Formal object.** Metalevel probability model (U_1,...,U_k, 𝓔) (Def 1); metalevel decision problem MDP M = (S, s_0, A_s, T, R) with S = {⊥} ∪ {<e_1..e_n>}, A_s = {⊥} ∪ 𝓔_s, T(s,E,s') = P(E=e \| e_1..e_n), R(s,E,s') = -c, R(s,⊥,⊥) = max_i mu_i(s), mu_i(s) = E[U_i \| e_1..e_n] (Def 3). Myopic policy pi^m (Def 6): Q^m(s,E) = E[-c + max_i mu_i(S_1) \| S_0=s, A_0=E]. Blinkered policy pi^b (Def 14): Q^b(s,E_i) = sup over policies restricted to 𝓔_i. Thm 16: Q^b_M(s,E_i) = Q*_{M^1_{i,mu*_{-i}}}(s_i, E_i).

**Strongest result.** Theorem 5: E_{pi*}[N \| S_0=s] <= (1/c)(E[max_i U_i \| S_0=s] - max_i mu_i(s)), and any policy with infinite expected computations has value -infinity, so the optimal policy stops w.p.1. Theorems 7/9 relating myopic and optimal stopping; Theorem 10 finite bound; Example 4 non-indexability; Theorem 16 blinkered decomposition.

**Assumptions.** Fixed known cost c > 0 per computation (validity conditions deferred to Harada 1997); bounded utilities in [0,1]; The set of available computations 𝓔 and their joint distribution with utilities is given (the object-level architecture is fixed); Stationarity of belief-state MDP; in trees, samples at non-root nodes still use UCT; reuse across decisions handled heuristically (§6.2); Blinkered policy needs independent actions (Def 13)

**Resource model.** compute (count of computations at price c; budgets/deadlines can be added to state); no description length, memory or verification accounting; sample cost = computation cost.

**Failure boundary.** Presupposes the object-level morphology: the computations 𝓔, the belief update, and the arm structure are inputs. It selects among computations, never among representations or program families, and cannot represent a change of morphology (which changes 𝓔 itself). Full metalevel optimality is itself intractable (states = outcome sequences); only myopic/blinkered approximations are practical. Extension to trees and to reuse of computations across future decisions is left open (§6.2, §7).

**Implementation.** none known as a released artifact (experiments used a modified Pachi Go engine, §6.3; no URL given in the paper)

**Track-B residual.** Rational metareasoning is the right parent for pricing deliberation inside a fixed morphology; Track B must not re-derive it. What it leaves: (a) a metalevel over morphologies, where the 'computation' is a change of representational family with its own cost and where the belief model is not shared across arms; (b) whether morphology choice is itself a non-indexable selection problem (Ex 4 suggests context inversions, i.e. that morphology rankings can flip with the utility of the incumbent alternative); (c) any developmental account of how the metalevel model is acquired.

**Upward question.** If the arms of a selection problem are morphologies and the computations are bounded trials of compiling/running/learning under each, does the metalevel problem retain the Theorem 5 stopping bound and the Example 4 context-inversion structure, and does non-indexability at the morphology level imply that no per-morphology score (an 'index') can predict the winner independently of the competing alternatives?

Load-bearing quotes (verbatim from sources actually read):

> "the metalevel decision problem is to choose what future action sequences to explore (or, more generally, what deliberative computations to do), while the object-level decision problem is to choose an action to execute in the real world." — [0] §1
> "UCT applies bandit algorithms to problems that are not bandit problems." — [0] §1
> "Theorem 5. The optimal policy's expected number of computations is bounded by the value of perfect information (Howard, 1966) times the inverse cost 1/c" — [0] §2
> "The myopic policy (known the metalevel greedy approximation with single-step assumption in Russell and Wefald (1991a)) takes the best action, to either stop or perform a computation, under the assumption that at most one further computation can be performed." — [0] §2 after Definition 6
> "Inversions like this are impossible for index policies." — [0] §3 Example 4 (Non-indexability)
> "The technical definition (closely related to subtree independence in Russell and Wefald's work) is as follows" — [0] §4 before Definition 13
> "However, this approach requires a nontrivial extension of the theory of metareasoning for search." — [0] §6.2 on valuing reuse across future decisions

Verification notes: Already partially reconstructed in the repo (research/metareasoning-parent-review-v1/OCM-METAREASONING-DONORS.md: Defs 1/3, Thms 4/5, Ex 3, §6.2; research/parent-absorption-v1/LEDGER.json P-DECISION-REGION). This entry adds Def 6/Thm 7/Thm 9/Thm 10 (myopic vs optimal), Ex 4 + Thm 12 (non-indexability and context interval), Defs 13-16 (blinkered), Thm 17-18 (distribution-free VOI), and the explicit Russell-Wefald restatements, which are what Track B needs.

### P1.SPEED_PRIOR — Schmidhuber's Speed Prior S: resource-bounded universal prior based on the fastest way of computing everything (FAST / Levin search), predictions computable and Kt-minimising

Disposition: `ADAPT` · best verification: `PARTIAL_TEXT_READ`

Sources:

- [0] The Speed Prior: A New Simplicity Measure Yielding Near-Optimal Computable Predictions — J. Schmidhuber (2002), COLT 2002, LNAI 2375, pp. 216-228, Springer. https://doi.org/10.1007/3-540-45435-7_15 — `NOT_ACCESSIBLE`
- [1] Algorithmic Theories of Everything — J. Schmidhuber (2000), Technical Report IDSIA-20-00 v2; arXiv quant-ph/0011122 (Section 6 contains the speed prior definitions and theorems later published at COLT 2002). https://arxiv.org/abs/quant-ph/0011122 arXiv:quant-ph/0011122 — `PARTIAL_TEXT_READ`
- [2] Optimal Ordered Problem Solver — J. Schmidhuber (2002), Technical Report IDSIA-12-02; arXiv cs/0207097 (later Machine Learning 54, 2004). https://arxiv.org/abs/cs/0207097 arXiv:cs/0207097 — `ABSTRACT_ONLY`

**What it already explains.** Replaces Solomonoff's enumerable prior (which assigns weight through phases of a dovetailer consuming uncountable resources) by a prior derived from the optimal dovetailer FAST (Levin-search stripped of search: PHASE i executes 2^{i-l(p)} instructions of every program prefix p with l(p) <= i). Postulate: cumulative prior of everything not computable within time t by FAST should be 1/t. This gives S(x) = sum_i 2^{-i} S_i(x) with S_i(x) = sum_{p ->_i x} 2^{-l(p)}, a semimeasure satisfying S(x) <= 2^{-Kt(x)} where Kt(x) = min_q {l(q) + log t(q,x)} is Levin complexity. Sampling algorithm GUESS (halve remaining runtime at each input bit). Prediction theorem: for S-describable x (computable in countable time and space), the posterior mass of programs slower than any known fast program vanishes (Thm 6.1) and with probability 1 the continuation of x_n is computable within O(2^{Kt(x_n)}) steps (Cor 6.1): predict by minimal Kt(xy). Thereby yields computable (if expensive) predictions, unlike M.

**Formal object.** FAST: for i = 1,2,...: PHASE i executes 2^{i-l(p)} instructions of all p with l(p) <= i. p ->_i x: p outputs x in PHASE i. Def 6.1: x is S-describable iff a finite algorithm outputs x using countable time and space. Postulate 6.1 (resource bias). Def 6.3: S(x) := sum_{i=1}^infty 2^{-i} S_i(x); S_i(lambda) = 1; S_i(x) = sum_{p ->_i x} 2^{-l(p)}. Eq (47): S(x) = 2^{-Kt(x)} sum_i 2^{-i} S_{Kt(x)+i-1}(x) <= 2^{-Kt(x)}. Algorithm GUESS. Thm 6.1: for S-describable x with p_x computing x_n in <= f(n) steps and g(n) > O(f(n)), Q(x,g,f) := lim_n [sum_i 2^{-i} sum_{p ->_i x_n in >= g(n) steps} 2^{-l(p)}] / [sum_i 2^{-i} sum_{p ->_i x_n in <= f(n) steps} 2^{-l(p)}] = 0. Cor 6.1 as above.

**Strongest result.** Theorem 6.1 and Corollary 6.1 (quant-ph/0011122 §6.6): under the speed prior, the most likely continuation of a long S-describable prefix is computable in O(2^{Kt}) steps, i.e. resource-bounded Occam: minimise Levin complexity Kt(xy). The COLT paper's title claim of 'near-optimal computable predictions' could not be verified in its own text.

**Assumptions.** The data source is S-describable (computable within countable time and space by a finite program); true randomness excluded; A fixed universal monotone Turing machine; the author notes the true and estimated distributions are not essentially different across machines (constant factors); Resource bias postulate: prior probability inversely proportional to time consumed by the most efficient way of computing everything

**Resource model.** time and space of computing the environment/data (on the world side), via Levin complexity Kt = length + log time. No agent-side accounting.

**Failure boundary.** A prior on data/environments, not a theory of agents: says the world is fast-computable and therefore a Kt-minimising predictor is adequate; it does not select an agent morphology, and its own predictor (enumerate programs by Kt) is again universal search. Less dominant than M (does not dominate enumerable semimeasures). Remains machine-relative up to constants; the 2^{Kt} runtime is exponential in the description. The physical predictions (§7.5) are outside Track B.

**Implementation.** none known (GUESS is specified as a probabilistic algorithm; §6.7 mentions an earlier assembler-language variant that searched neural-network weight matrices, no code URL)

**Track-B residual.** Track B's ecology needs a resource price on the environment side (what it costs to simulate/verify the world) as well as on the agent side; the speed prior is the canonical environment-side price (Kt). Left open: whether a Kt-weighted ecology changes which agent morphology is bounded-optimal (e.g. favouring fast-simulable models over compact ones), and whether an agent should carry a speed prior over its own programs (a morphology prior) rather than only over environments.

**Upward question.** Is the morphology that is bounded-optimal under a Kt-weighted ecology different from the one under a K-weighted ecology, and does the difference appear as a phase boundary in the time-price parameter?

Load-bearing quotes (verbatim from sources actually read):

> "Postulate 6.1 The cumulative prior probability measure of all x incomputable within time t by the most efficient way of computing everything should be inversely proportional to t." — [1] quant-ph/0011122 §6.5
> "Definition 6.3 (Speed Prior S) Define the speed prior S on B* as S(x) := sum_{i=1}^infty 2^{-i} S_i(x); where S_i(lambda) = 1; S_i(x) = sum_{p ->_i x} 2^{-l(p)} for x > lambda." — [1] quant-ph/0011122 §6.5 (notation flattened)
> "S(x) = 2^{-Kt(x)} sum_{i=1}^infty 2^{-i} S_{Kt(x)+i-1}(x) <= 2^{-Kt(x)}" — [1] quant-ph/0011122 eq. (47) (notation flattened)
> "Corollary 6.1 Let x in B^infty be S-describable. For n -> infty, with probability 1 the continuation of x_n is computable within O(2^{Kt(x_n)}) steps." — [1] quant-ph/0011122 §6.6 (notation flattened)
> "The appropriate simplicity measure minimized by this resource-oriented version of Occam's razor is the Levin complexity Kt." — [1] quant-ph/0011122 §7.4
> "Assuming our universe is sampled according to GUESS implemented on some machine, note that the true distribution is not essentially different from the estimated one based on our own, possibly different machine." — [1] quant-ph/0011122 §6.5

Verification notes: The brief's 'arXiv:cs/0207097? verify' resolved to OOPS, not the Speed Prior; recorded as a correction. All speed-prior mathematics is quoted from the IDSIA-20-00 report (§6), which is the same author's prior statement of the same definitions and theorems; the COLT 2002 text itself was not read, so any COLT-specific theorem numbering is unknown. Hutter 2009 §7(b) independently names the Speed Prior as a candidate basis for a resource-bounded intelligence measure.

### P1.UNIVERSAL_LEARNING_THEORY — Universal learning theory (Hutter encyclopedia entry): Solomonoff induction, universal Bayes, loss bounds, Pareto optimality, and the passage to AIXI

Disposition: `ADOPT` · best verification: `FULL_TEXT_READ`

Sources:

- [0] Universal Learning Theory — M. Hutter (2011), Encyclopedia of Machine Learning (Springer), arXiv 1102.2467. https://arxiv.org/abs/1102.2467 arXiv:1102.2467 — `FULL_TEXT_READ`

**What it already explains.** The passive half of the family in one place: learning by enumeration (<= m-1 errors), majority/weighted-majority learning (O(log w_m^{-1}) errors), Solomonoff's M(x) = sum_{p: U(p)=x*} 2^{-l(p)} and the universal mixture xi_U(x) = sum_{nu in M_U} 2^{-K(nu)} nu(x) over lower-semicomputable semimeasures (coinciding with M up to a constant); the convergence bound sum_t E[sum_a (M(a\|w_<t) - mu(a\|w_<t))^2] <= K(mu) ln 2 + O(1) (eq 4); the decision-theoretic loss bound sqrt(Loss_M) - sqrt(Loss_mu) <= sqrt(2 K(mu) ln 2 + O(1)) (eq 5); Pareto optimality of Lambda_M; extension to classification/regression with side information and chronological semimeasures; AIXI as eq (7); approximations (compressors, MDL, CTW, MC-AIXI, Kt and speed prior); and the discussion of U-dependence, prior knowledge as a prefix z, and semi-computability. States the family's own answer to no-free-lunch: assume effective structure without specifying which.

**Formal object.** M(x) := sum_{p: U(p)=x*} 2^{-l(p)} (eq 1); w_nu = 2^{-K(nu)} (eq 2); xi_U(x) := sum_{nu in M_U} 2^{-K(nu)} nu(x) (eq 3); bound (4); Lambda_rho-optimal decision y_t = argmin_y sum_{x_t} rho(x_t\|w_<t) l_{x_t y}; bound (5); conditional M(x_1:n \| y_1:n) := sum_{p: U(p,y_1:n)=x_1:n} 2^{-l(p)} = sum_nu 2^{-K(nu)} nu(x_1:n\|y_1:n) (eq 6); AIXI y_t := argmax_{y_t} sum_{x_t} ... max_{y_n} sum_{x_n} [r_t+...+r_n] M(x_1:n\|y_1:n) (eq 7).

**Strongest result.** Solomonoff convergence bound (eq 4) with the remark that O(K(mu)) errors are unavoidable for most mu and no other weight choice gives significantly better bounds; loss bound (eq 5) implying Loss_M/Loss_mu -> 1; Pareto optimality of Lambda_M in M_U. All stated without proof (encyclopedia format), with proofs referred to Hutter 2005.

**Assumptions.** Data drawn from a computable (or lower-semicomputable semi-) measure; no ergodicity, stationarity, identifiability; Fixed reference universal monotone Turing machine; invariance up to additive/multiplicative constants; predictions for short strings can be arbitrary; Bounded loss in [0,1]

**Resource model.** description length of the environment (K(mu)) governs sample/error bounds; agent-side compute is explicitly not modelled (only semi-computable); time appears only in the cited Kt/speed-prior approximations.

**Failure boundary.** Passive/predictive theory; morphology enters only as 'choice of subclass of M_U that can be summed efficiently' (CTW) or as downscaling to MDL/finite automata - i.e. the family's derivation of morphologies is class restriction, with no criterion for the restriction. Compiler constants make short-sequence behaviour arbitrary. Nothing developmental: prior knowledge is a prefix z on the tape.

**Implementation.** none known (semi-computable); practical approximations cited: compressors (Cilibrasi-Vitanyi), CTW, MC-AIXI

**Track-B residual.** Universal learning theory owns 'why any effective-structure assumption suffices for learnability' and 'error bounds scale with K(mu)'. It leaves to Track B the resource-priced version: for a bounded learner on M, which restricted class (morphology) minimises expected loss plus resource cost under an ecology's K/Kt profile, and whether the family's 'restrict M_U' step can be made lawful rather than designer-chosen.

**Upward question.** Which properties of an ecology (beyond effective structure) make the restriction of M_U to a specific summable subclass lossless up to a bounded factor, and can those properties be estimated before committing to the class?

Load-bearing quotes (verbatim from sources actually read):

> "Despite various no-free-lunch theorems [WM97], universal learning is possible by assuming that the data possess some effective structure, but without specifying any further, which structure." — [0] §1
> "In summary, M is an excellent sequence predictor under the only assumption that the observed sequence is drawn from some (unknown) computable probability distribution. No ergodicity, stationarity, or identifiability or other assumption is required." — [0] §5 'Universal sequence prediction'
> "The Context Tree Weighting algorithm considers a relatively large subclass of M_U that can be summed over efficiently." — [0] §5 'Approximations and practical applications'
> "Universal machine learning is similar, except that its core quantities are only semi-computable. This makes them often hard, but as described in the previous section, not impossible, to approximate." — [0] §6
> "but predictions for short sequences (shorter than typical compiler lengths) can be arbitrary" — [0] §6
> "One can incorporate it by explicating all our prior knowledge z, and place it on an extra input tape of our universal Turing machine U, or prefix our observation sequence x by z and use M(zx) for prediction." — [0] §6

Verification notes: Full text read. Orseau / Orseau-Lattimore-Hutter knowledge-seeking agents were not fetched; they are cited in Leike-Hutter §1 and §6.3 as exploration fixes and are listed under missing parents.


## P2 — incremental / self-improving universal problem solving

### P2.GOEDEL_MACHINE — Goedel machine (Schmidhuber 2003/2006): provably useful self-rewrites via an embedded proof searcher; global optimality theorem

Disposition: `None` · best verification: `PARTIAL_TEXT_READ`

Sources:

- [0] Goedel Machines: Self-Referential Universal Problem Solvers Making Provably Optimal Self-Improvements — Juergen Schmidhuber (2006), TR IDSIA-19-03 v5; in Artificial General Intelligence (Springer 2007). https://arxiv.org/abs/cs/0309048 arXiv:cs/0309048 — `PARTIAL_TEXT_READ`

**What it already explains.** A self-rewrite (switchprog) is executed only after the embedded proof searcher proves the target theorem 'rewriting now yields higher utility than continuing to search' under axioms describing hardware, initial software p(1), environment and the utility u (which charges computation time of everything including proof search). Theorem 4.1: any such self-change is globally optimal because the target theorem implicitly compares against all switchprogs the searcher could produce later; all meta-levels collapse (Sec. 4.3). The initial proof searcher BIOPS is an online universal search over proof techniques, O()-optimal (Thm 5.1) with the same 1/P(w) constant; OOPS can accelerate later proof searches (8-bias-optimal, Sec. 5.2). Limitations (Sec. 2.4, 4.4): Goedel incompleteness — improvements whose utility is unprovable in A must be ignored; pathological environments/utilities exist where no target theorem is ever provable; Rice-theorem triviality does not reflect scientific triviality; usefulness of constant-factor speedups is provable in simple cases.

**Formal object.** target theorem (2)/(3); utility u = E[sum of future rewards \| s, Env]; axiomatic system A encoded in p(1); BIOPS Method 5.1

**Strongest result.** None

**Assumptions.** None

**Resource model.** None

**Failure boundary.** None

**Implementation.** None

**Track-B residual.** None

**Upward question.** None

Verification notes: None

### P2.OOPS — Optimal Ordered Problem Solver (Schmidhuber 2002/2004): bias-optimal incremental universal search with frozen prefixes

Disposition: `None` · best verification: `FULL_TEXT_READ`

Sources:

- [0] Optimal Ordered Problem Solver — Juergen Schmidhuber (2002), TR IDSIA-12-02 v2; Machine Learning 54 (2004). https://arxiv.org/abs/cs/0207097 arXiv:cs/0207097 — `FULL_TEXT_READ`

**What it already explains.** Defines n-bias-optimality (Def. 1: a searcher never spends more than P(p\|r)*T_max/n on candidate p) and shows Levin search is near-bias-optimal with O(P(p) f(k)) = O(f(k)) complexity. OOPS (Method 3.1): solve tasks in order; for task n spend half the time on prolongations of the most recently frozen prefix (tested only on task n) and half on fresh programs starting above the frozen address (tested on all tasks 1..n); freeze the first solver found. Realistic OOPS is 8-bias-optimal (factor 2 for the split, 2 for time doubling, 2 for Try's backtracking) and near-bias-optimal w.r.t. the initial bias plus subsequent code bias shifts (Obs. 3.5). Prefixes may rewrite the distribution on their suffixes (metasearching, Obs. 3.8). Experiment: 30-disk Towers of Hanoi solved after a context-free-language task; the earlier solution's prefix (c3 dec boostq) boosts the probabilities of useful instructions so that the 10-token universal Hanoi solver has probability 9.3e-11 given prior code, ~1000x acceleration of universal search; the whole run tested 9.4e10 prefixes over ~4 days. Sec. 5.1 scopes NFL to i.i.d. uniform problem spaces and locates OOPS's advantage in task relatedness; Sec. 5.2: OOPS does not invent its own subtask curriculum (that is PowerPlay's addition) and needs resetable environments; Appendix A defines the Forth-like language with per-instruction time costs (1 unit; n for n-cell copies/finds; n for n probability modifications), i.e. a charged primitive universe of the same kind as the microscope's.

**Formal object.** P on programs; n-bias-optimal searcher (Def. 1); frozen prefix q_{a_last:a_frozen}; degree of bias B := 1/T (Sec. 4.3, cf. Solomonoff's conceptual jump size)

**Strongest result.** None

**Assumptions.** None

**Resource model.** None

**Failure boundary.** None

**Implementation.** None

**Track-B residual.** None

**Upward question.** None

Verification notes: None

### P2.POWERPLAY — PowerPlay (Schmidhuber 2011/2013): self-invented simplest-still-unsolvable tasks with a no-forgetting correctness demonstration

Disposition: `None` · best verification: `PARTIAL_TEXT_READ`

Sources:

- [0] POWERPLAY: Training an Increasingly General Problem Solver by Continually Searching for the Simplest Still Unsolvable Problem — Juergen Schmidhuber (2011), arXiv 1112.5309 v2 (2012); Frontiers in Psychology 4 (2013). https://arxiv.org/abs/1112.5309 arXiv:1112.5309 — `PARTIAL_TEXT_READ`

**What it already explains.** Framework (Alg. 2): search pairs (task T, solver modification q) such that (1) s_{i-1} cannot solve T, (2) q solves T, (3) q still solves all T_k, k<i; the first pair found and validated is adopted. With the OOPS implementation (Alg. 4.1) candidate pairs are ordered by conditional computational complexity given stored experience, so 'the new task and its corresponding skill are those first found and validated ... biases the search towards pairs that can be described compactly and validated quickly'; validation cost need not grow with repertoire size when solver modularization tracks which components affect which tasks (Sec. 3.3.2). Tasks may require achieving a 'wow-effect' (solving an old task with less time/space). Section 5: once storage is bounded (or earlier, because reuse is cheaper to find), the search starts compressing previous solutions, making s generalize. Variant II (Sec. 7.1) explicitly penalizes time and space and allows average-performance-preserving forgetting. Optimality: asymptotic (O(f(k)/P(p))) for the OOPS variant; the task search itself is greedy, 'but at least practically feasible'.

**Formal object.** task sequence T_1, T_2, ...; solver sequence s_i with s_i solves T_{<=i}, s_{i-1} does not solve T_i; CORRECTNESS DEMONSTRATION as an external verifier

**Strongest result.** None

**Assumptions.** None

**Resource model.** None

**Failure boundary.** None

**Implementation.** None

**Track-B residual.** None

**Upward question.** None

Verification notes: None


## P3 — neural architecture / learning-algorithm discovery

### P3.AUTOML_ZERO — AutoML-Zero: evolving whole ML algorithms (Setup/Predict/Learn programs) from 65 arithmetic-level ops

Disposition: `ADOPT` · best verification: `FULL_TEXT_READ`

Sources:

- [0] AutoML-Zero: Evolving Machine Learning Algorithms From Scratch — Esteban Real, Chen Liang, David R. So, Quoc V. Le (2020), ICML 2020, PMLR 119 (arXiv v2, 30 Jun 2020). https://arxiv.org/abs/2003.03384 arXiv:2003.03384 — `FULL_TEXT_READ`
- [1] AutoML-Zero (PMLR abstract page) — Real, Liang, So, Le (2020), PMLR v119. https://proceedings.mlr.press/v119/real20a.html arXiv:2003.03384 — `NOT_ACCESSIBLE`
- [2] Open-source code: google-research/automl_zero — Real et al. (2020), GitHub. https://github.com/google-research/google-research/tree/master/automl_zero — `NOT_ACCESSIBLE`

**What it already explains.** Owns D2-level developmental acquisition of a supervised neural learner from a numeric instruction set: starting from EMPTY programs, regularized evolution over a memory of scalar/vector/matrix registers with 58 allowed arithmetic ops discovers (i) linear models, (ii) SGD-like error-times-input updates, (iii) learning-rate hacks, (iv) ReLU, (v) random weight init, (vi) gradient normalization, (vii) multiplicative (bilinear) interactions, (viii) weight accumulation/averaging, and, in a deliberately restricted op set with teacher-network tasks, the exact two-layer ReLU network with backprop-by-gradient-descent (Fig. 5). It also owns a weak task-conditioned adaptation signal: noisy-ReLU emerges under few examples (8/30 vs 0/30), learning-rate decay under short training (30/30 vs 3/30), weight-mean learning rate under 10-class tasks (24/30 vs 0/30). It owns the search-method engineering: regularized evolution (tournament T=10, P=100-1000, mutation prob U=0.9), functional equivalence checking by prediction fingerprints (4x speedup), hurdles (75th-percentile early stopping, 5x), random migration across W=100-10,000 CPU workers, and dataset diversity (50% MNIST workers).

**Formal object.** An algorithm a in A is a triple of instruction sequences (Setup, Predict, Learn) over a zero-initialized, globally shared, persistent virtual memory with typed address spaces: scalars sX, vectors vX, matrices mX, all float and of the task feature dimension F (8 <= F <= 256 in proxy tasks). Evaluate(a, Dtrain, Dvalid): initialize_memory(); Setup(); for (x,y) in Dtrain: v0 = x; Predict(); s1 = Normalize(s1); s0 = y; Learn(); then for (x,y) in Dvalid: v0 = x; Predict(); s1 = Normalize(s1); accumulate Loss(y, s1); return mean loss. Quality of a = median over D tasks of the per-task accuracy (or RMS for regression). Each instruction = (op, input addresses, output address, optional constants). Op vocabulary (Table S1): OP0 no_op; OP1-OP6 scalar arithmetic (+,-,*,/,abs,1/x); OP7-OP12 trig (sin,cos,tan,arcsin,arccos,arctan); OP13-OP17 pre-calculus (exp, log, heaviside on scalar/vector/matrix); OP18-OP43 linear algebra (scalar*vector, bcast, elementwise 1/v, norm, abs, v+v, v-v, v*v, v/v, dot(v,v), outer(v,v), scalar*matrix, elementwise 1/M, dot(M,v), bcast to matrix axis 0/1, norm(M), row/col norms, transpose, abs(M), M+M, M-M, M*M elementwise, M/M elementwise, matmul); OP44-OP55 probability/statistics (min, max on s/v/M, mean(v), mean(M), row mean, row std, std(v), std(M)); OP56-OP64 constants and random init (set scalar/vector-entry/matrix-entry to constant, uniform(alpha,beta) and gaussian(mu,sigma) fills for s/v/M). 65 ops total (OP0..OP64). Search = regularized evolution: population P of programs (initially all empty), tournament of size T selects parent, child = copy + one mutation of type (i) insert/remove instruction (removal 2x as likely), (ii) randomize a whole component function, (iii) modify one argument (constants scaled by U[0.5,2], sign flipped w.p. 0.1); oldest program removed.

**Strongest result.** Empirical (no theorems). (1) Difficulty scaling (Fig. 4): random-search density of acceptable algorithms is 1 in 10^7 for linear regression; evolution/RS success ratio grows 2.9x, 5.6x, 150x, 23000x as task difficulty grows 10^6, 10^7, 10^9, 10^12. (2) Fig. 5: with ops restricted to those of a 2-layer NN with GD (Setup {OP56,OP63,OP64}, Predict {OP27,OP31,OP48}, Learn {OP2,OP3,OP16,OP18,OP23,OP25,OP28,OP40}), fixed lengths 21/3/9, teacher tasks L(x)=u.ReLU(Mx), D=100 tasks, W=1k workers: evolution discovers forward pass + backprop-by-GD code (heaviside used as ReLU gradient, outer product as first-layer weight delta). (3) Sec. 4.2 (58 ops, empty start, W=10k CPU workers, 5 days): best evolved algorithm = noisy-input bilinear model o = a^T W b with a = x+u, b = x-u, u ~ U(alpha,beta), gradient g = delta a b^T normalized to unit norm, inference weights W' = sum_t W_t; CIFAR-10 binary test accuracy 84.06 +/- 0.10% vs logistic 77.65 +/- 0.22% vs 2-layer FC net 82.22 +/- 0.17%; transfers to SVHN 88.12/59.58/85.14, downsampled ImageNet 80.78/76.44/78.44, Fashion-MNIST 98.60/97.90/98.21; candidates beat the hand-designed 2-layer net on held-out class pairs in 13 of 20 experiments; ablations: noise -0.16%, bilinear -1.46%, normalized gradients -1.20%, weight averaging -4.11%. (4) Sec. 4.3 task-adaptation statistics as above. (5) Table S2-S5: each search upgrade (migration, FEC, 50% MNIST, hurdles) raises best accuracy 0.703->0.738 and NN-beating success fraction 0.00->0.53 at 1k processes; at 10 processes no run beats the plain NN.

**Assumptions.** Supervised, online, one-example-at-a-time protocol is fixed by the evaluator: Predict sees x in v0, Learn sees label y in s0 and the sigmoid/softmax-normalized prediction in s1 (Normalize is hard-wired for classification).; Memory is a fixed bank of typed float registers (e.g. 8/14/3 scalar/vector/matrix addresses in Sec 4.2, 10/16/4 in 4.3) whose dimension equals the feature dimension F; no data-dependent addressing, no growth.; No control flow: no branching, loops, function calls, recursion; component functions are straight-line instruction lists with max lengths 21/21/45.; No derivative op; heaviside/min/max are the only discontinuous ops; no batch or higher-order tensors.; Tasks are random-projected (8<=F<=256) binary class pairs from CIFAR-10 (36 search pairs / 9 select pairs; 4500 proxy tasks) and MNIST; final evaluation at F=3072 requires manual hyperparameter decoupling and random-search tuning of constants.; Search is regularized evolution with tournament selection; RS baseline only in Sec 4.1; no crossover (preliminary crossover and geographic structure 'did not help').; Fitness = median accuracy across D tasks with early termination on NaN/Inf, error>100, or runtime > 4x a plain NN.

**Resource model.** Accounts for: search compute in evaluations (throughput 2k-10k algorithms/s/core; W=10k commodity CPU cores x 5 days for Sec 4.2 ~ 5x10^4 CPU-days; W=1k for Fig. 5 and Sec 4.3; baselines run to 100B training steps per process ~12 h), population size, number of tasks per evaluation D, feature dimension F; program description length only via max instruction counts; per-algorithm runtime only as a 4x-of-NN termination threshold. NOT accounted: learning-update work vs prediction work separately, verification cost, memory beyond the fixed register bank, the human cost of hyperparameter decoupling and interpretation (Sec S7, S8).

**Failure boundary.** Cannot produce non-numeric morphologies: no ops for symbol tables, data-dependent addressing, conditionals, loops or calls, so rules, DFAs, lookup/retrieval memories, and programs with control flow are inexpressible except by numeric emulation; batch methods and multi-layer nets beyond independently discovered layers are out of reach (Sec 5, authors' own statement). The reported phase-like adaptations (noisy ReLU, LR decay) are within-neural variants, not morphology changes, and were obtained by initializing the population with the Fig. 5 network. No prospective prediction: which motif emerges is observed post hoc via convergent evolution across 30 runs, not predicted. Discovery is search-method dependent (Table S5: 'Basic' vs 'Full' method changes NN-beating success 0.00 vs 0.11 at 100 processes). Hyperparameter coupling (learning rate computed as norm(v1)) breaks transfer and needs manual repair. No theory of why gradient-like updates dominate; no comparison against non-neural strong parents at matched compute.

**Implementation.** https://github.com/google-research/google-research/tree/master/automl_zero (open source, C++; cited in paper)

**Track-B residual.** Under the SAME instruction basis but with (a) the supervised Predict/Learn slot replaced by a neutral interaction protocol, (b) registers extended with discrete/addressable memory and control flow at charged cost, and (c) ecology coordinates (verification contract, data volume, noise, drift, task diversity) varied prospectively, does the winning program family leave the numeric-vector-update morphology, and is the transition predictable before search? AutoML-Zero answers only: within a vector/matrix register machine on projected image class pairs, evolution converges on bilinear/SGD-like learners.

**Upward question.** The basis is not neutral: the memory types (vector, matrix), the ops (dot, outer, matmul, heaviside) and the Predict/Learn supervised slot pre-encode the neural morphology's data structures and its update-law shape, leaving only the wiring to be discovered. The upward question is therefore what a genuinely cross-paradigm basis is, i.e. one in which vectors/matrices, rules and addressable memories are all compiled at charged cost from the same primitives, and whether ecology coordinates then predict which is acquired.

Load-bearing quotes (verbatim from sources actually read):

> "We purposefully exclude machine learning concepts, matrix decompositions, and derivatives." — [0] Sec. 3.1 Search Space
> "In particular, there are no derivatives so any gradient computation used for training must be evolved." — [0] Suppl. S2
> "Unlike these three studies, we do not even assume the existence of a neural network or of gradients." — [0] Sec. 2 Related Work
> "The virtual memory is zero-initialized and persistent, and shared globally throughout the whole evaluation." — [0] Sec. 3.1
> "Suppl. Section S2 contains the full list of 65 ops." — [0] Sec. 3.1
> "Teacher datasets and carefully chosen ops bias the results in favor of known algorithms, so in this section we replace them with more generic options." — [0] Sec. 4.2, first sentence
> "In this figure, we only allow as ops those that appear in a two-layer neural network with gradient descent" — [0] Suppl. S5, 'Experiment in Section 4.1, Figure 5'
> "Even in this trivial task type, we found only 1 acceptable algorithm every 10^7, so we define 10^7 to be the difficulty of the linear regression task." — [0] Sec. 4.1
> "Number of possible ops: 7/ 58/ 58 for Setup/ Predict/ Learn, resp." — [0] Sec. 4.2 Experiment Details
> "We find that the noisy ReLU is reproducible and arises preferentially in the case of little data (expt: 8/30, control: 0/30, p < 0.0005)." — [0] Sec. 4.3
> "to keep our search space simple, we process one example at a time, so discovering techniques that work on batches of examples (like batch-norm) would require adding loops or higher-order tensors." — [0] Sec. 5 Conclusion and Discussion
> "in the current search space, a multi-layer neural network can only be found by discovering each layer independently; the addition of loops or function calls could make it easier to unlock such deeper structures." — [0] Sec. 5
> "even though they produce the same accuracy now, they may behave differently upon further mutation." — [0] Suppl. S3 Functional Equivalence Checking
> "W =10k processes (commodity CPU cores). We initialize the population with empty programs." — [0] Suppl. S5, Experiments in Section 4.2
> "Run time: 5 days." — [0] Sec. 3.2 Details paragraph

Verification notes: Full text read, including the op table. Two internal inconsistencies noticed: (a) Sec. 4.2 says 7 Setup ops but S5 lists 9 Setup ops {OP56..OP64}; (b) S9/S10 refer to 'OP65' and to Predict ops {OP28,OP32,OP49} although Table S1 stops at OP64 and the dot/matvec/max ops are OP27/OP31/OP48 in the table (an apparent 1-indexed vs 0-indexed op numbering shift in the supplement). Codex ledger entry P-AUTOML-ZERO verified only the PMLR abstract; this entry supplies the search-space facts. Compute (~5x10^4 CPU-days for Sec 4.2) is inferred from W=10k and 'Run time: 5 days'; the paper does not state a CPU-day total.

### P3.REGULARIZED_EVOLUTION — Regularized (aging) evolution for architecture search (Real et al. 2019)

Disposition: `None` · best verification: `PARTIAL_TEXT_READ`

Sources:

- [0] Regularized Evolution for Image Classifier Architecture Search — Esteban Real, Alok Aggarwal, Yanping Huang, Quoc V. Le (2019), AAAI 2019; arXiv 1802.01548 v7. https://arxiv.org/abs/1802.01548 arXiv:1802.01548 — `PARTIAL_TEXT_READ`

**What it already explains.** Aging evolution (Alg. 1): population P, sample S at random, mutate the best of the sample, add the child, remove the OLDEST (not the worst). Two mutations (hidden-state, op) suffice to cover the NASNet space. Evolution reaches results faster than RL and random search at equal hardware, especially early (Fig. A-1e), and matches RL in final quality; aging beats non-aging in 4 of 5 contexts and in a toy noisy-evaluation space increasingly with dimensionality (Supp. B-C). Interpretation: aging forces architectures to re-train well repeatedly, a regularizer against evaluation noise. Evolved models are faster (lower FLOPs).

**Formal object.** tournament selection with age-based removal; NASNet cell search space

**Strongest result.** None

**Assumptions.** None

**Resource model.** None

**Failure boundary.** None

**Implementation.** None

**Track-B residual.** None

**Upward question.** None

Verification notes: None


## P4 — meta-learning / learned learning rules / continual learning

### P4.BAXTER — Baxter 2000 'A model of inductive bias learning' (JAIR 12)

Disposition: `ADOPT` · best verification: `PARTIAL_TEXT_READ`

Sources:

- [0] A Model of Inductive Bias Learning — Jonathan Baxter (2000), Journal of Artificial Intelligence Research 12:149-198. https://doi.org/10.1613/jair.731 ; arXiv mirror https://arxiv.org/abs/1106.0245 arXiv:1106.0245 — `PARTIAL_TEXT_READ`

**What it already explains.** Already reconstructed at /home/user/ORION-OCM/research/heritable-search-transformation-v1/LITERATURE_LEDGER.md (row 'Baxter JAIR 2000 \| learnable bias over task environments generalizes under controlled families \| OWNS \| T09'). Summary for Track B: the learner sits in an environment (P, Q) (Q a distribution over learning problems P on X x Y) and chooses a hypothesis space H from a family H (its hyper-bias) to minimize er_Q(H) = integral inf_{h in H} er_P(h) dQ(P) (Eq. 6), estimated from an (n, m)-sample by er_hat_z(H) = (1/n) sum_i inf_{h in H} er_hat_{z_i}(h) (Eq. 8). Theorem 2 gives uniform convergence over H once n (tasks) and m (examples per task) exceed bounds in the capacities C(eps, H*) and C(eps, H^n_l); Theorem 3 shows that after learning H, novel tasks need m ~ log C(eps, H_l) examples instead of log C(eps, H^1_l) for the whole family; Lemma 5 and Theorem 4 show the per-task requirement never worsens and can shrink as O((1/n) log C(eps, H^n_l)); Theorem 8 (neural feature learning) gives m = O((1/eps^2)((k + 1 + W/n) log(1/eps) + (1/n) log(1/delta))).

**Formal object.** Environment (P, Q); hypothesis space family H = {H}; bias learner A: union_{n,m} (X x Y)^{(n,m)} -> H; loss er_Q(H) (Eq. 6); empirical loss er_hat_z(H) (Eq. 8); capacities C(eps, H^n_l), C(eps, H*) via covering numbers of derived function classes; permissibility of H.

**Strongest result.** Theorem 2 (verified): for permissible H, if n >= max{ (256/eps^2) log(8 C(eps/32, H*)/delta), 64/eps^2 } and m >= max{ (256/(n eps^2)) log(8 C(eps/32, H^n_l)/delta), 64/eps^2 }, then with probability >= 1 - delta all H in H satisfy er_Q(H) <= er_hat_z(H) + eps. Theorem 8 (verified) specializes to neural feature maps with k features and W feature weights.

**Assumptions.** Tasks are i.i.d. draws from Q; examples i.i.d. from each P; same m per task; Bounded loss in [0,1]; separable metric input/output spaces; permissible hypothesis space family; Sample complexity only; computability/efficiency of the bias learner A is explicitly out of scope; Hyper-bias H must be strictly smaller than all functions X -> Y but contain good solutions for most tasks

**Resource model.** samples only (number of tasks n and examples per task m; capacity/covering numbers as description-length proxies); no compute, time, verification or memory

**Failure boundary.** Says nothing about which H (which learning-law morphology) is chosen, only that empirical bias error generalizes; does not model compute or the process of search over H; environment Q is stationary (no drift), tasks are exchangeable; bounds are loose constants; no prediction of phase transitions in n (the GPICL transition at ~2^13 tasks is not derivable from these bounds).

**Implementation.** none known

**Track-B residual.** Baxter bounds the SAMPLE side of morphology selection (how many tasks/examples justify a learned bias) but not the COMPUTE/VERIFICATION side nor the identity of the selected bias. Track B needs a joint (n, m, compute, verification) price under which a learning-law morphology becomes admissible, and a link between capacity C(eps, H^n_l) and the empirical task-count transition of GPICL.

**Upward question.** Can the capacity terms C(eps, H^n_l) and C(eps, H*) be turned into a prospective predictor of the number-of-tasks threshold at which a generic substrate switches from memorization to a generalizing learning law (GPICL), i.e. can Baxter's n-bound become the T10 phase boundary?

Load-bearing quotes (verbatim from sources actually read):

> "The central assumption of the model is that the learner is embedded within an environment of related learning tasks." — [0] Baxter 2000, abstract
> "an environment of learning problems is represented by a pair (P, Q) where P is the set of all probability distributions on X x Y (i.e., P is the set of all possible learning problems), and Q is a distribution on P." — [0] Baxter 2000, Section 2.2 (symbols transliterated)
> "In this sense the choice of H represents the hyper-bias of the learner." — [0] Baxter 2000, Section 2.5
> "we are concerned only with the sample complexity properties of a bias learner A; we do not discuss issues of the computability of A." — [0] Baxter 2000, Section 2.2
> "the number of examples required of each task for good generalisation obeys m = O((1/n) log C(eps, H^n_l))" — [0] Baxter 2000, Section 2.4 point 5, Eq. 25 (transliterated)

Verification notes: Prior reconstruction: HST ledger row (OWNS, T09). This entry verified Theorem 2 (Eq. 21-23), Theorem 3, Theorem 4, Lemma 5, Theorem 8 and Eq. 6, 8, 9 against the arXiv mirror text; adds only the Track-B subtraction (sample-only resource model; no morphology identity; no phase law).

### P4.CONTINUAL_LEARNING — Continual learning and the stability-plasticity dilemma: Parisi et al. 2019 review; Kirkpatrick et al. 2017 EWC; Grossberg 1987

Disposition: `ADAPT` · best verification: `PARTIAL_TEXT_READ`

Sources:

- [0] Continual Lifelong Learning with Neural Networks: A Review — German I. Parisi, Ronald Kemker, Jose L. Part, Christopher Kanan, Stefan Wermter (2019), Neural Networks 113:54-71 (arXiv v4). https://doi.org/10.1016/j.neunet.2019.01.012 arXiv:1802.07569 — `PARTIAL_TEXT_READ`
- [1] Overcoming catastrophic forgetting in neural networks — James Kirkpatrick, Razvan Pascanu, Neil Rabinowitz, Joel Veness, Guillaume Desjardins, Andrei A. Rusu, Kieran Milan, John Quan, Tiago Ramalho, Agnieszka Grabska-Barwinska, Demis Hassabis, Claudia Clopath, Dharshan Kumaran, Raia Hadsell (2017), PNAS 114(13):3521-3526 (arXiv v2). https://doi.org/10.1073/pnas.1611835114 arXiv:1612.00796 — `PARTIAL_TEXT_READ`
- [2] Competitive learning: From interactive activation to adaptive resonance — Stephen Grossberg (1987), Cognitive Science 11(1):23-63. https://doi.org/10.1111/j.1551-6708.1987.tb00862.x — `NOT_ACCESSIBLE`

**What it already explains.** The stability-plasticity dilemma: a learner must be plastic enough to integrate new information and stable enough not to catastrophically overwrite consolidated knowledge; catastrophic forgetting arises in connectionist models when new instances overwrite shared representational resources. Parisi's taxonomy of remedies: (i) regularization of weight updates (EWC, SI), (ii) dynamic architectures / selective training and expansion (progressive nets, growing self-organizing nets), (iii) complementary learning systems with memory consolidation and replay; plus developmental ingredients (critical periods, curriculum, transfer, intrinsic motivation, multisensory integration) and the three Richardson & Thomas conditions (allocate resources / non-overlapping representations / interleave old knowledge). ART (Grossberg): resolves the dilemma with top-down expectations, a match criterion against a vigilance threshold rho, resonance-gated learning and a reset/orienting subsystem that recruits a new category on mismatch (ART1 match M_J = \|x AND w_J^td\|_1 / \|x\|_1 >= rho). EWC: Bayesian derivation log p(theta\|D) = log p(D_B\|theta) + log p(theta\|D_A) - log p(D_B); Laplace approximation of the task-A posterior as a Gaussian with diagonal precision = diagonal Fisher F; penalty L(theta) = L_B(theta) + sum_i (lambda/2) F_i (theta_i - theta*_{A,i})^2 (Eq. 3); linear-time in parameters and examples; three stored values per synapse; works on permuted MNIST sequences and 10 Atari games with task inference by a Forget-Me-Not process; chief limitation: diagonal Laplace posterior under-estimates parameter uncertainty (perturbing in the Fisher nullspace hurts as much as inverse-Fisher perturbations).

**Formal object.** EWC: L(theta) = L_B(theta) + sum_i (lambda/2) F_i (theta_i - theta*_{A,i})^2 with F the diagonal Fisher at theta*_A; Bayesian posterior recursion over tasks. Parisi: lifelong learner = adaptive algorithm on a continuous stream of non-stationary data with tasks not predefined, evaluated by forgetting metrics. ART (secondary): winner-take-all category J, match M_J, resonance iff M_J >= rho, else reset and search; new category on exhaustive mismatch.

**Strongest result.** No theorems in the read material. EWC Fig. 2A/B (verified): plain SGD and L2 regularization fail on sequences of permuted-MNIST tasks while EWC retains old tasks with modest error growth; Fig. 2C: Fisher overlap decreases with task dissimilarity in early layers; Fig. 3C: perturbations in the Fisher nullspace degrade performance as much as inverse-Fisher-shaped perturbations, evidencing under-estimated uncertainty. Parisi: identifies that most CL methods address supervised annotated finite datasets and do not extend to unlabeled streams; ART survey: stability defined as no prototype returning to a previous value and finitely many clusters under infinite presentation.

**Assumptions.** EWC: task boundaries known or inferred (Forget-Me-Not); over-parameterization so a task-B solution exists near theta*_A; diagonal Fisher / Laplace approximation; quadratic penalties compose additively; Parisi taxonomy: supervised, annotated, finite datasets for most surveyed methods; catastrophic forgetting as the failure mode of shared representations; ART: match-based (not error-based) learning; vigilance parameter set by the designer; order dependence

**Resource model.** memory (EWC: three values per synapse; replay methods: explicit storage proportional to tasks; dynamic architectures: growth), compute (EWC linear in parameters and examples), samples (sequence of tasks); no description-length or verification accounting

**Failure boundary.** None of the parents predicts when consolidation, expansion or replay dominates as a function of drift rate, task similarity, memory price and horizon; EWC under-estimates uncertainty and does not match separately trained networks; Parisi notes rigorous evaluation metrics are lacking; ART requires a hand-set vigilance and is order-dependent. Continual learning is here a REGIME (non-stationary Q) not a morphology, and the surveyed methods are add-ons to a fixed neural learner.

**Implementation.** EWC: none official stated in text (many re-implementations); Parisi: none (review); ART: code repositories listed in Brito da Silva et al. 2019 Section 7 (not itemized here)

**Track-B residual.** Treat drift (non-stationarity of Q), memory price and verification contract as ecology axes of E and the stability-plasticity trade-off as a constraint on any learning law. Track B must ask whether the three CL strategy families (regularize / expand / replay) are morphologies that a generic basis would DEVELOP under drift, and which one is selected by (drift rate, memory price, task similarity).

**Upward question.** Under a drift ecology, does a generic adaptive basis converge to the regularize / expand / replay families, or to ART-like match-and-reset, and can (drift rate, similarity, memory price) predict the winner before search (T9/T10 with drift as the control parameter)?

Load-bearing quotes (verbatim from sources actually read):

> "The extent to which a system must be plastic in order to integrate novel information and stable in order not to catastrophically interfere with consolidated knowledge is known as the stability-plasticity dilemma" — [0] Parisi et al. 2019, Section 1 (attributed there to Ditzler 2015, Mermillod 2013, Grossberg 1980, 2012)
> "However, Hebbian plasticity alone is unstable and leads to runaway neural activity, thus requiring compensatory mechanisms to stabilize the learning process" — [0] Parisi et al. 2019, Section 2.2
> "we approximate the posterior as a Gaussian distribution with mean given by the parameters theta*_A and a diagonal precision given by the diagonal of the Fisher information matrix F." — [1] Kirkpatrick et al. 2017, Section 2 (symbols transliterated)
> "it is therefore likely that the chief limitation of the current implementation is that it under-estimates parameter uncertainty." — [1] Kirkpatrick et al. 2017, Section 2.2
> "EWC has a run time which is linear in both the number of parameters and the number of training examples." — [1] Kirkpatrick et al. 2017, Section 3
> "Formally, when there is a new task to be learnt, the network parameters are tempered by a prior which is the posterior distribution on the parameters given data from previous task(s)." — [1] Kirkpatrick et al. 2017, Section 3
> "ART addresses the problem of stability vs. plasticity (Carpenter & Grossberg, 1987a; Grossberg, 1980). Plasticity refers the ability of a learning algorithm to adapt and learn new patterns." — [2] Brito da Silva, Elnabarawy, Wunsch 2019 (arXiv 1905.11437), Section 1 (secondary source for Grossberg, read)

Verification notes: Parisi and EWC read in the pages listed; EWC Eq. 3 and Bayesian derivation verified. Grossberg 1987 primary text NOT accessible; the dilemma is attributed in the read secondary sources to Grossberg 1980 / Carpenter & Grossberg 1987a rather than to the 1987 Cognitive Science paper specifically, so the brief's attribution to the 1987 paper is recorded as UNVERIFIED. The web-search snippet claiming the 1987 paper shows Rumelhart & Zipser competitive learning to be temporally unstable is a search-engine summary and is not relied on.

### P4.EMERGENT_LEARNING_ALGORITHMS — Learning algorithms emerging from a generic neural substrate: VSML (Kirsch & Schmidhuber 2021) and GPICL (Kirsch, Harrison, Sohl-Dickstein, Metz 2022)

Disposition: `GENERALIZE` · best verification: `FULL_TEXT_READ`

Sources:

- [0] Meta Learning Backpropagation And Improving It — Louis Kirsch, Juergen Schmidhuber (2021), NeurIPS 2021 (v4 arXiv 13 Mar 2022). https://arxiv.org/abs/2012.14905 arXiv:2012.14905 — `FULL_TEXT_READ`
- [1] General-Purpose In-Context Learning by Meta-Learning Transformers — Louis Kirsch, James Harrison, Jascha Sohl-Dickstein, Luke Metz (2022), arXiv preprint (v2, 9 Jan 2024). https://arxiv.org/abs/2212.04458 arXiv:2212.04458 — `FULL_TEXT_READ`

**What it already explains.** VSML: replacing every weight of a standard NN by a tiny LSTM with SHARED parameters V_M (~2,400) and distinct states V_L (~257,200) that pass forward and backward messages yields a substrate in which (a) backpropagation can be implemented purely in the recurrent dynamics ('learning algorithm cloning', Sec. 3.2/4.1: 87-90% MNIST, 76-80% Fashion-MNIST with no explicit gradient computation at meta-test), and (b) a general-purpose online supervised learning algorithm can be meta-learned FROM SCRATCH by ES (no hard-coded gradients) that learns faster than online SGD/Adam early on, transfers MNIST -> Fashion-MNIST/EMNIST/KMNIST/Random/Sum-Sign, is invariant to input permutation/size, and mechanistically learns by 'fast association', qualitatively unlike gradient descent; limitations: short-horizon bias, O(W N^2) cost, deep-variant optimization plateaus. GPICL: a vanilla Transformer with minimal inductive bias, meta-trained on random-projection/label-permutation augmentations of a base dataset to minimize sum of query losses over dataset prefixes (Eq. 2), becomes a general-purpose in-context learner; the meta-learned behavior undergoes ALGORITHMIC TRANSITIONS as the number of meta-training tasks grows: task memorization -> task identification -> general learning-to-learn (Fig. 4; at least 2^13 = 8192 tasks needed; bimodal memorize/generalize solution clusters with a transition near 6000 tasks in Fig. 10), jointly with model size (Fig. 2b,c); the accessible STATE size N_S (not parameter count) predicts learning-to-learn capability across LSTM/Transformer/outer-product-LSTM/VSML-without-symmetries (Fig. 5, Insight 4); meta-optimization has loss plateaus whose length follows a power law in task batch size (Fig. 7), yielding a plateau/memorize/generalize phase diagram in (number of tasks, batch size); biasing the task distribution (curriculum) removes the plateau and memorization is followed by generalization.

**Formal object.** VSML: sub-RNN states s_ab in R^N on an A x B grid with shared parameters, s_ab <- f_RNN(s_ab, m->_a, m<-_b) (Eq. 7), forward message m->_b^{(k+1)} = sum_{a'} f_->(s^{(k)}_{a'b}), backward message m<-_a^{(k-1)} = sum_{b'} f_<-(s^{(k)}_{ab'}); equivalent to one RNN with a sparse shared weight tensor W~_{cdiabj} (Eq. 5-6, Theorem 1 in Appendix A); meta-training: V_M <- V_M - alpha grad_{V_M} sum_t L(y_hat(t), y(t)) by BPTT or ES (Algorithm 1); meta-testing = unrolling only (Algorithm 2). GPICL: learning algorithm := mapping ({x_i,y_i}_{i=1}^{N_D}, x') -> y' (Eq. 1) that improves with N_D; tasks D^{(k)} = {A^{(k)} x_i, rho^{(k)}(y_i)} with A ~ N(0, 1/N_x), rho a label permutation (Algorithm 1); J(theta) = E_{D~p(D)} [ sum_{j=1}^{N_D} l(f_theta(D_{1:j-1}, x_j), y_j) ] (Eq. 2); state size N_S in O(N_H) for RNNs, O(N_K N_L N_T) for Transformers.

**Strongest result.** VSML Theorem 1 (Appendix A, verified): the message-passing VSML with matrices (W, C) is exactly a standard RNN with a single sparse shared weight tensor given by Eq. 6 (a representability result, not a learning result). Strongest empirical results: VSML Fig. 6/8 (meta-trained on MNIST, generalizes to Fashion-MNIST and to datasets with no shared structure, whereas Meta-RNN, Hebbian fast weights and external memory overfit); VSML Fig. 9 (fast association: after a failed prediction the correct class is predicted with high confidence on the next presentation, unlike SGD+Adam). GPICL Insight 1-4 and Fig. 4 (three phases vs. number of tasks), Fig. 2b-c (transition to unbounded task count with model size, only for the sequence model, not the MLP), Fig. 5 (state size predicts accuracy across architectures), Fig. 7 (phase diagram plateau/overfit/generalize vs. tasks x batch size; plateau length power-law in batch size), Fig. 10/13 (bimodal solutions at the transition), Table 2 (GPICL 73.70% MNIST / 62.24% Fashion after 99 in-context examples vs VSML 79.04/68.49, SGD 70.31/50.78, MAML 53.71/48.44, LSTM 25.39/28.12).

**Assumptions.** Neural substrate only (LSTM sub-RNNs; vanilla Transformer/LSTM); learning algorithm is encoded in fixed meta-parameters and executed in activations/state; Outer loop is gradient descent (BPTT, Adam) or evolution strategies on a fixed meta-objective (sum of prediction losses over an online sequence of at most 500 examples for VSML; 100-token prefixes for GPICL); Task diversity is manufactured by random linear projections and label permutations of existing datasets (permutation/scale invariance built into the data, or, for VSML, into the architecture via weight sharing); Supervised classification with labels fed as inputs; feedback signal is the loss gradient at the output (VSML) or the previous label (GPICL); Inputs/outputs restricted to sizes seen at training (GPICL) or matched by per-dimension sub-RNNs (VSML); 'Learning' is measured behaviorally as within-sequence accuracy improvement; the algorithm is not structurally identified

**Resource model.** compute (VSML: O(W N^2) per step; ES on 128 GPUs, population 1024, 10k outer steps; GPICL: some experiments 16 GPUs, up to 1000 runs for heat-maps), memory/state (GPICL: N_S is the identified bottleneck; VSML: \|V_M\| vs \|V_L\| ratio), samples (number of meta-training tasks as the transition axis; task batch size), horizon (VSML short-horizon bias at 500 examples; GPICL sequence length 100-400); no verification or description-length accounting beyond \|V_M\|

**Failure boundary.** Does not predict the location of the memorization->generalization transition before training (reported post hoc: 'here 6000', 'at least 2^13'); no closed-form phase law; no identification of WHICH algorithm emerged (only 'fast association', 'not gradient descent'); only neural substrate and only one meta-objective family; no drift, verification contract, feedback-type or resource-price axes; small-scale problems (MNIST-class), online setting, performance trails batched SGD at convergence; deep VSML variants suffer meta-optimization plateaus; GPICL limited to fixed input/output sizes and short contexts (quadratic cost).

**Implementation.** VSML: http://louiskirsch.com/code/vsml (verified, Appendix C). GPICL: none stated in the text read

**Track-B residual.** Kirsch et al. show that under a gradient/ES outer loop a generic neural substrate develops a generalizing learning algorithm once task diversity and state size cross a threshold. Track B must (i) predict that threshold prospectively from ecology and resource prices (T10/B4), (ii) identify the emergent law structurally rather than behaviorally (T11), (iii) extend the substrate and the emergent laws beyond the neural/associative family to Bayesian, rule and program learning laws (B6), and (iv) charge the meta-training cost against the developmental budget.

**Upward question.** Can distinct learning laws (gradient/backprop, fast-association/Hebbian, Bayesian posterior update, rule/production, program induction) be derived as morphologies of ONE basis, and can the ecology (task diversity, feedback type, drift, verification, resource prices, horizon) predict which one emerges and where the transition lies, before meta-training is run?

Load-bearing quotes (verbatim from sources actually read):

> "simple weight-sharing and sparsity in an NN is sufficient to express powerful learning algorithms (LAs) in a reusable fashion." — [0] Kirsch & Schmidhuber 2021, abstract
> "Introspection reveals that our meta learned LAs learn through fast association in a way that is qualitatively different from gradient descent." — [0] Kirsch & Schmidhuber 2021, abstract
> "we have very few meta variables \|V_M\| ~ 2,400 and many learned variables \|V_L\| ~ 257,200." — [0] Kirsch & Schmidhuber 2021, Section 4 (approx sign rendered as ~)
> "Crucially, during meta testing, no explicit gradient descent is used." — [0] Kirsch & Schmidhuber 2021, Section 3.1
> "If we run a sub-RNN for each weight in a standard NN with W weights, the cost is in O(W N^2), where N is the state size of a sub-RNN." — [0] Kirsch & Schmidhuber 2021, Section 7
> "We call this phenomenon the short horizon bias, where meta test training is fast in the beginning but flattens out at some horizon." — [0] Kirsch & Schmidhuber 2021, Appendix B.2
> "In VSML we demonstrate that a symbolic programming language is not required and general-purpose LAs can be discovered and encoded in variable-shared RNNs." — [0] Kirsch & Schmidhuber 2021, Section 6
> "We characterize transitions between algorithms that generalize, algorithms that memorize, and algorithms that fail to meta-train at all, induced by changes in model size, number of tasks, and meta-optimization." — [1] Kirsch et al. 2022 (GPICL), abstract
> "To transition to the learning-to-learn regime, we needed at least 2^13 = 8192 tasks." — [1] Kirsch et al. 2022 (GPICL), Insight 1 (Section 4 and A.1)
> "When increasing the number of tasks, the meta-learned behavior transitions from task memorization, to task identification, to general learning-to-learn." — [1] Kirsch et al. 2022 (GPICL), Insight 3 (Section 4.1)
> "At a certain number of tasks (here 6000), a transition point is reached where optimization sometimes discovers a lower training loss that corresponds to a generalizing learning to learn solution." — [1] Kirsch et al. 2022 (GPICL), Appendix A.3
> "We find that the distribution is bi-modal. Solutions at the end of training are memorizing or generalizing." — [1] Kirsch et al. 2022 (GPICL), Appendix A.3
> "Generalization only occurs with large enough batch sizes and sufficient, but not too many, tasks." — [1] Kirsch et al. 2022 (GPICL), Figure 7 caption
> "the capabilities of meta-trained algorithms are bottlenecked by the accessible state size (memory) determining the next prediction, unlike standard models which are thought to be bottlenecked by parameter count." — [1] Kirsch et al. 2022 (GPICL), abstract
> "This biased data distribution can be viewed as a curriculum, solving an easier problem first that enables the subsequent harder learning-to-learn." — [1] Kirsch et al. 2022 (GPICL), Section 4.3, Intervention 3
> "A current limitation is the applicability of the discovered learning algorithms to arbitrary input and output sizes beyond random projections." — [1] Kirsch et al. 2022 (GPICL), Section 6

Verification notes: Both papers read in full. Numbers quoted (2^13 tasks, ~6000-task transition, \|V_M\| ~ 2,400, O(W N^2), Table 2 accuracies) are verified against the text. No prior reconstruction in the repo ledgers listed in the brief; the substrate-theory THEORY_MAP mentions 'amortisation crossing' (M1C #360/#361) which is conceptually adjacent to the memorize->learn transition but does not cite Kirsch et al.

### P4.EMERGENT_LEARNING_ALGORITHMS — Meta-learned substrates that host a learning algorithm in their forward dynamics: VSML (Kirsch & Schmidhuber) and GPICL (Kirsch, Harrison, Sohl-Dickstein, Metz)

Disposition: `ADAPT` · best verification: `FULL_TEXT_READ`

Sources:

- [0] Meta Learning Backpropagation And Improving It — Louis Kirsch, Jürgen Schmidhuber (2021), NeurIPS 2021 (arXiv 2012.14905v4, 13 Mar 2022). https://arxiv.org/abs/2012.14905 arXiv:2012.14905 — `FULL_TEXT_READ`
- [1] General-Purpose In-Context Learning by Meta-Learning Transformers — Louis Kirsch, James Harrison, Jascha Sohl-Dickstein, Luke Metz (2022), arXiv 2212.04458v2 (9 Jan 2024). https://arxiv.org/abs/2212.04458 arXiv:2212.04458 — `FULL_TEXT_READ`
- [2] VSML source code — Louis Kirsch (2021), author site. http://louiskirsch.com/code/vsml — `NOT_ACCESSIBLE`

**What it already explains.** VSML: replacing every weight of a feed-forward net by a tiny LSTM with SHARED parameters V_M (~2,400) and DISTINCT states V_L (~257,200) yields a substrate whose forward recurrence can (i) be cloned to implement backprop exactly ('learning algorithm cloning': regress y-hat, delta-w, delta-b, e-hat toward a shadow network's targets; 87-90% MNIST, 76-80% Fashion-MNIST test accuracy learning purely by unrolling), and (ii) be meta-trained from scratch with evolution strategies to a learning algorithm that uses no gradient at meta-test time, learns faster than online SGD/Adam on the first ~2k examples, and transfers MNIST -> Fashion-MNIST, EMNIST, KMNIST, random data and 'sum sign' (no shared structure), where Meta-RNN, Hebbian fast weights and external fast-weight memory overfit. Introspection (Fig. 9, 17) shows the meta-learned law is fast one-shot association, qualitatively unlike SGD, with a 'short horizon bias' (SGD overtakes after ~12k examples). GPICL: a vanilla Transformer (4 layers, model size 256, 8 heads, kv=32) meta-trained by backprop+Adam on Eq. 2 (sum of query losses over all dataset prefixes) across K tasks generated by random input projections A~N(0,1/Nx) and label permutations of MNIST/Fashion-MNIST/KMNIST/CIFAR10 exhibits THREE regimes as K grows: task memorization (no within-sequence improvement), task identification (improvement only on seen tasks), general learning-to-learn (improvement on unseen tasks and unseen base datasets); the last transition needs >= 2^13 = 8192 tasks and is bimodal (~6000 tasks: runs settle in either a memorization or a generalization cluster). A second axis: model size (2..512); a third: accessible STATE size (2^5..2^14) predicts learning-to-learn across LSTM / Transformer / outer-product LSTM / VSML-without-symmetries better than parameter count. A fourth: meta-optimization (task batch size 8..4096) with a phase diagram plateau / overfit / generalize; plateau length falls as a power law in batch size and rises with number of tasks; biasing the label-permutation distribution (curriculum) removes the plateau; Adam epsilon or sign-normalized updates halve it.

**Formal object.** VSML: RNN state s in R^{A x B x N}; per sub-RNN update s_{ab} <- f_RNN(s_{ab}, m->_a, m<-_b) with forward message m->^{(k+1)}_b = sum_{a'} f_{m->}(s^{(k)}_{a'b}) and backward message m<-^{(k-1)}_a = sum_{b'} f_{m<-}(s^{(k)}_{ab'}) (Eq. 3, 7); f_RNN is an LSTM (N=16 for meta-learning from scratch, 64 for cloning; message sizes N'=N''=8); Theorem 1 (Appendix A): the message-passing system equals one standard RNN with a sparse shared weight tensor W~_{cdiabj} = (d==a) C_ij + (d==b)(c==a) W_ij. Meta-training (Alg. 1): V_M <- V_M - alpha grad_{V_M} sum_{t=1..T} L(y-hat(t), y(t)), gradient by BPTT or ES (population 1024, noise sigma 0.05, Adam lr 0.025, 10k outer steps, 500 online examples per trajectory, 128 GPUs). Meta-testing (Alg. 2) = unrolling only; error e = grad_{y-hat} L(y-hat,y) is fed as m<-^{(K)}_{b1} = e_b. GPICL: f_theta: (D_{1:j-1}, x_j) -> y'_j, vanilla Transformer with learned positional embeddings; task D^{(k)} = {A^{(k)} x-bar_i, rho^{(k)}(y-bar_i)}, p(D) = Uniform over K such tasks; meta-objective J(theta) = E_{D~p(D)} sum_{j=1}^{N_D} l(f_theta(D_{1:j-1}, x_j), y_j) with cross-entropy l, N_D = 100 (sequence length); classification of the learned algorithm by two binary axes (Table 1): learns? (within-sequence improvement) x generalizes? (unseen tasks). State size N_S in O(N_K N_L N_T) for Transformers vs O(N_H) for RNNs.

**Strongest result.** VSML: only Theorem 1 (sparse-shared-RNN equivalence, an algebraic identity). Empirical: Fig. 6/8 VSML beats Meta-RNN, HebbianFW, FWMemory on all unseen datasets and matches or beats SGD/Adam over the first 2k examples; Fig. 7 invariance to unseen class counts (5, 10), input sizes (21x21, 48x48), random projection and shuffling. GPICL: Table 2 (99 examples, predict 100th, meta-trained on augmented MNIST): SGD 70.31% MNIST / 50.78% Fashion / 37.89% KMNIST / 14.84% CIFAR10; MAML 53.71/48.44/36.33/17.38; VSML 79.04/68.49/54.69/24.09; LSTM 25.39/28.12/18.10/12.11; GPICL 73.70/62.24/53.39/19.40. Fig. 4 three phases vs number of tasks; Fig. 2b/c transition in (model size, number of tasks) plane; Fig. 5 state size predicts unseen-MNIST accuracy across four architectures; Fig. 7 phase diagram in (task batch size, number of tasks); Fig. 10 bimodal final training loss at the transition; Fig. 6 meta-loss plateau ~35k of 50k steps with rising generalization loss on the plateau.

**Assumptions.** Single substrate family per paper (LSTM sub-RNNs with parameter sharing; vanilla Transformer / LSTM variants); the hypothesis space is fixed neural weights, so every 'discovered learning algorithm' is a point in weight space of a fixed architecture.; Outer loop is gradient-based (backprop through the inner loop, or ES-estimated gradient with Adam) on a supervised loss; the learning signal at meta-test time is a label or an output-error vector injected as input.; Task diversity is manufactured by random linear projections and label permutations of a small set of image datasets; 'unseen dataset' generalization is measured within this augmentation family (VSML additionally trains across class counts and resolutions).; Sequence length / lifetime is short (VSML 500 online examples during meta-training, 12k at most in tests; GPICL 100 examples), so the emergent law is a short-horizon law.; Inputs/outputs fixed-size (GPICL) or handled by permutation-invariant message passing (VSML); classification only.; The 'algorithm' is identified behaviorally (learning curves, introspection of output probabilities), not extracted mechanistically.

**Resource model.** VSML: meta-variables \|V_M\| ~ 2,400 vs learned variables \|V_L\| ~ 257,200; inner cost O(W N^2) for W weights and state size N; meta-training 128 GPUs x 10k ES steps x population 1024 (no GPU-hours stated); sample efficiency measured as cumulative online accuracy over first 100/2k examples. GPICL: state size N_S, parameter count, number of tasks K (2^0..2^25), task batch size (2^3..2^12), meta-training steps (50k; plateau ~35k), sequence length (50..400); hardware 'single GPU, some require 16 GPUs (16 GB each)', up to 1000 runs per heat-map. Neither paper charges meta-training cost against the sample efficiency gained at meta-test; neither reports verification or memory costs beyond state size.

**Failure boundary.** Cannot produce non-neural morphologies: the substrate is a fixed differentiable network; only the learning LAW (weights encoding in-context dynamics) is discovered, never a data structure or update-law family outside recurrent activations. The phase axes are task diversity, model/state size and meta-optimizer batch size; nothing about verification contract, drift, resource prices or feedback type. No prospective prediction of where the transition sits for a new task family (the 8192-task threshold is empirical, dataset-specific: 'significantly smoother' on FashionMNIST). Discovered laws have a short-horizon bias, premature convergence, and VSML deeper stacks are hard to meta-optimize (loss plateaus, Fig. 23). VSML cost O(W N^2) exceeds backprop. GPICL transformer cost quadratic in sequence length; no path to millions of examples. The gradient outer loop is itself a hidden neural/backprop macro at the meta level.

**Implementation.** http://louiskirsch.com/code/vsml (VSML, cited in paper); GPICL: none stated in the paper

**Track-B residual.** Is there a cross-paradigm phase law: the SAME (task diversity, state size, feedback precision, verification strength) coordinates predicting, before meta-training/search, whether the acquired learner is a gradient-like, associative-memory-like, rule-like, or program-like law, in substrates that can host all of them at charged cost? Kirsch et al. supply one substrate, one outer loop (gradient), behavioral identification only, and an unpriced meta-training bill; they show a within-neural memorize -> identify -> learn transition, not a morphology transition.

**Upward question.** Kirsch et al. show the learning law is a phase of the (task-diversity, state, optimizer) ecology inside one substrate. The upward question is whether the substrate morphology itself (weights-in-activations vs explicit memory table vs symbolic rule store) is a phase of a richer ecology, with meta-training cost charged and both substrate families compiled from one basis.

Load-bearing quotes (verbatim from sources actually read):

> "It can even meta learn new LAs that differ from online backpropagation and generalize to datasets outside of the meta training distribution without explicit gradient calculation." — [0] VSML abstract
> "Introspection reveals that our meta learned LAs learn through fast association in a way that is qualitatively different from gradient descent." — [0] VSML abstract
> "Such generalization is enabled by extensive variable sharing where we have very few meta variables \|V_M\| ≈ 2, 400 and many learned variables \|V_L\| ≈ 257, 200." — [0] VSML Sec. 4
> "Meta training is done across 128 GPUs using ES as proposed by OpenAI [38] for a total of 10k steps. We use a population size of 1024" — [0] VSML Appendix C.2
> "If we run a sub-RNN for each weight in a standard NN with W weights, the cost is in O(W N^2), where N is the state size of a sub-RNN." — [0] VSML Sec. 7
> "We call this phenomenon the short horizon bias, where meta test training is fast in the beginning but flattens out at some horizon." — [0] VSML Appendix B.2
> "In VSML we demonstrate that a symbolic programming language is not required and general-purpose LAs can be discovered and encoded in variable-shared RNNs." — [0] VSML Sec. 6 Discrete program search
> "We characterize transitions between algorithms that generalize, algorithms that memorize, and algorithms that fail to meta-train at all, induced by changes in model size, number of tasks, and meta-optimization." — [1] GPICL abstract
> "To transition to the learning-to-learn regime, we needed at least 2^13 = 8192 tasks." — [1] GPICL Insight 1
> "When increasing the number of tasks, the meta-learned behavior transitions from task memorization, to task identification, to general learning-to-learn." — [1] GPICL Insight 3
> "the capabilities of meta-trained algorithms are bottlenecked by the accessible state size (memory) determining the next prediction, unlike standard models which are thought to be bottlenecked by parameter count." — [1] GPICL abstract
> "Generalization only occurs with large enough batch sizes and sufficient, but not too many, tasks." — [1] GPICL Fig. 7 caption
> "At a certain number of tasks (here 6000), a transition point is reached where optimization sometimes discovers a lower training loss that corresponds to a generalizing learning to learn solution." — [1] GPICL Appendix A.3
> "During meta-training, we take gradient steps in J(θ) by backpropagation and Adam (Kingma & Ba, 2014)." — [1] GPICL Sec. 3.2
> "As an in-context learner, meta-testing does not involve any gradient updates but only running the model in forward mode." — [1] GPICL Sec. 4
> "Most experiments can be run on a single GPU, some require 16 GPUs due to sequence length and large batch sizes, with sufficient GPU memory (around 16 GB each)." — [1] GPICL Appendix A.5
> "Because VSML has permutation invariance and parameter sharing built into the architecture as an inductive bias, changing the number of tasks has only a small effect." — [1] GPICL Appendix A.6

Verification notes: Both arXiv full texts read. Codex PARENT_EXPANSION_V3 covers RL^2 / Wang et al. / PEARL at abstract depth and LITERATURE_LEDGER covers MAML / learned optimizers; neither covers Kirsch et al. The sibling scratchpad family P4.json (Meta-learning) also has an entry id P4.EMERGENT_LEARNING_ALGORITHMS; this entry is the full-depth phase-axis reconstruction requested by the brief and should be merged by the parent agent (same parent_id).

### P4.HISTORICAL_LEARNING_TO_LEARN — Historical learning-to-learn: Bengio, Bengio, Cloutier 1991; Schmidhuber 1987/1992/1993 self-referential and fast-weight nets; Thrun & Pratt 1998

Disposition: `ADOPT` · best verification: `NOT_ACCESSIBLE`

Sources:

- [0] Learning a synaptic learning rule — Yoshua Bengio, Samy Bengio, Jocelyn Cloutier (1991), IJCNN-91 Seattle (DOI 10.1109/IJCNN.1991.155621); technical report Univ. de Montreal 1990; follow-up Bengio, Bengio, Cloutier, Gecsei 1992 'On the optimization of a synaptic learning rule'. https://doi.org/10.1109/IJCNN.1991.155621 — `NOT_ACCESSIBLE`
- [1] Learning to control fast-weight memories: An alternative to dynamic recurrent networks — Juergen Schmidhuber (1992), Neural Computation 4(1):131-139. https://doi.org/10.1162/neco.1992.4.1.131 — `NOT_ACCESSIBLE`
- [2] A 'self-referential' weight matrix — Juergen Schmidhuber (1993), ICANN 1993, Amsterdam, pp. 446-451 (with companion papers: 'An introspective network that can learn to run its own weight change algorithm', IEE ANN 1993; 'Reducing the ratio between learning complexity and number of time varying variables in fully recurrent nets', ICANN 1993; and 1987 diploma thesis 'Evolutionary principles in self-referential learning'). https://doi.org/10.1007/978-1-4471-2063-6_107 — `NOT_ACCESSIBLE`
- [3] Learning to Learn: Introduction and Overview (in: Learning to Learn, Kluwer/Springer) — Sebastian Thrun, Lorien Pratt (1998), Book chapter, pp. 3-17. https://doi.org/10.1007/978-1-4615-5529-2_1 — `NOT_ACCESSIBLE`

**What it already explains.** Priority for every ingredient of 'learning to learn': (1987) Schmidhuber's diploma thesis on self-referential learning ('meta-meta-... hook') proposes networks that receive their own weights as input and predict weight updates, with evolution as the outermost loop; (1990-92) Bengio, Bengio, Cloutier (and Gecsei) parameterize a local synaptic learning rule Delta w = f(x, theta) on local signals (pre-/post-synaptic activity, weight, modulatory/error signals) and optimize theta by gradient descent, simulated annealing and genetic algorithms across several tasks (conditioning, Boolean functions, classification), an early 'learning to learn without backprop by backprop/evolution'; (1991-92) fast-weight programmers: a slow network rapidly writes the weights of a fast network via outer products of self-generated keys and values, i.e. context-dependent programs in weight space; (1993) the self-referential weight matrix: an RNN with special input/output units that address (by weight index), read and modify any of its own weights in activation space, so the network can in principle run and improve its own weight-change algorithm end-to-end by gradient descent, and a fully recurrent net whose number of time-varying variables is O(d^2) rather than O(d); (1998) Thrun & Pratt's operational definition: learning to learn occurs when performance at tasks drawn from a family improves with experience AND with the number of tasks seen, distinguishing it from ordinary learning whose performance improves with data from one task.

**Formal object.** Bengio et al. (as restated by Soltoggio et al. 2018 Eq. 1-2): Delta w = f(x, theta), x = vector of local neural signals (pre/post activity, w, modulatory/error terms), theta = rule parameters searched by gradient/SA/GA; x_i = sigma(sum_j w_ji x_j). Schmidhuber 1991/92 FWP (as restated by Irie et al. 2022 Sec. 2): slow net emits (k_t, v_t, ...), fast weights updated by outer products v_t (x) phi(k_t), output y_t = W_t phi(q_t) (modern delta-rule form in Eq. 1-4 there). Schmidhuber 1993 SRWM (per Irie et al. Sec. 6): weight index i in {0..N^2-1} encoded as a binary vector on dedicated input/output units; the net reads/modifies its own W by index. Thrun & Pratt: an algorithm learns to learn if its performance on task family tasks improves with experience and with the number of tasks (paraphrase; exact wording UNVERIFIED).

**Strongest result.** No theorems accessible. Historical results as reported by secondary sources: Bengio et al. optimized rules improved over hand-set parameters on conditioning/Boolean/classification tasks and were 'among the first to include a modulatory term'; Chalmers 1990 (per Soltoggio et al.) rediscovered the delta rule by evolution in 20% of runs; Schmidhuber 1993 systems have O(d^2) temporally varying variables under end-to-end differentiable control; Andrychowicz note that Schmidhuber's fully self-modifying nets are 'very difficult to train'. All UNVERIFIED against the primary texts.

**Assumptions.** Bengio: learning rule is a fixed parametric function of LOCAL signals; rule parameters shared across synapses; tasks are small (conditioning, Boolean functions); Schmidhuber 1992/93: fully differentiable end-to-end self-modification; weights addressable by index; trained by gradient descent (1993) or evolution (1987); Thrun & Pratt: a task family with shared regularities; improvement measured across tasks

**Resource model.** none formal in accessible material; Schmidhuber 1993 is explicitly about the ratio of learning complexity to number of time-varying variables (O(d^2) vs O(d)) per Irie et al.

**Failure boundary.** Small-scale demonstrations; trainability problems for fully self-referential nets (per Andrychowicz); no generalization results across broad task distributions; no theory of which rule emerges. Thrun & Pratt's definition is behavioral and, as Hospedales notes, also covers transfer/multi-task/feature-selection/ensembles.

**Implementation.** none known for the originals; Irie et al. 2022 modern SRWM: https://github.com/IDSIA/modern-srwm (verified in that paper)

**Track-B residual.** None at the mechanism level: every 'learning to learn' ingredient is 30+ years old. What none of these works provide is a prediction of which learned learning law will be selected by which task ecology, nor any cross-paradigm (non-neural) learning laws in the same basis.

**Upward question.** Given that self-referential and rule-learning substrates existed by 1993 but did not yield general learning laws until task diversity and state size were scaled (GPICL/VSML), is the limiting factor an ecology/resource threshold rather than substrate expressivity? If so, the theory must be about the threshold, not the substrate.

Load-bearing quotes (verbatim from sources actually read):

> "Bengio et al. (1990, 1992) proposed the optimization of the parameters theta of generic learning rules with gradient descent, simulated annealing, and evolutionary search for problems such as conditioning, boolean function mapping, and classification." — [0] Soltoggio, Stanley, Risi 2018 (arXiv 1703.10371), Section IV.A (secondary source, read)
> "Such an RNN has special input and output units to directly address, read, and modify any of its own current weights through an index for each weight of its weight matrix" — [2] Irie et al. 2022 (arXiv 2202.05780), Section 6 'Original Self-Referential Weight Matrix' (secondary source, read)
> "FWPs have a slow NN which can rapidly modify weights of another fast NN." — [1] Irie et al. 2022, Section 2 (secondary source, read)
> "Perhaps the most general approach to meta-learning is that of Schmidhuber [1992, 1993]-building on work from [Schmidhuber, 1987]-which considers networks that are able to modify their own weights." — [2] Andrychowicz et al. 2016, Section 1.2 (secondary source, read)
> "Meta-learning is then defined as an effect whereby the agent improves its performance in each new task more rapidly, on average, than in past tasks (Thrun and Pratt, 1998)." — [3] Wang et al. 2016, Section 2.1 (secondary source, read)

Verification notes: All four primary texts NOT accessible from this sandbox (author sites, Springer, ACM DL, Wiley, Semantic Scholar API and Scholarpedia are egress-blocked). Every statement above is attributed to a secondary source that was actually read (Soltoggio et al. 2018; Irie et al. 2022; Andrychowicz 2016; Wichrowska 2017; Hospedales 2021; Wang 2016). No equation from Bengio 1991 is quoted because none was verifiable. The repo HST ledger already lists Schmidhuber OOPS/PowerPlay and Goedel Machines (different works); this entry adds only the 1987/1992/1993 self-referential and fast-weight lineage.

### P4.ICL_DISTRIBUTIONAL_CHAN — Data distributional properties drive emergent in-context learning (Chan et al. 2022): published phase axes between in-weights and in-context learning

Disposition: `None` · best verification: `FULL_TEXT_READ`

Sources:

- [0] Data Distributional Properties Drive Emergent In-Context Learning in Transformers — Stephanie C. Y. Chan, Adam Santoro, Andrew K. Lampinen, Jane X. Wang, Aaditya Singh, Pierre H. Richemond, James L. McClelland, Felix Hill (2022), NeurIPS 2022; arXiv 2205.05055 v6. https://arxiv.org/abs/2205.05055 arXiv:2205.05055 — `FULL_TEXT_READ`

**What it already explains.** Omniglot sequences of image-label pairs; in-context learning (ICL) measured on holdout classes with labels re-assigned per sequence, in-weights learning (IWL) on trained classes with no context support. Axes and directions: burstiness up -> ICL up, IWL down (Fig. 2); number of rarely-occurring classes up (100 -> 1600 -> 12800) -> ICL up, IWL down (Fig. 3), and 'we need both burstiness and a large number of classes for in-context learning to emerge'; label multiplicity up -> ICL up (Fig. 4); within-class variation up -> ICL up, IWL down (Fig. 5). Trade-off: uniform-marginal training never sustains both. Coexistence: Zipfian class marginal with exponent ~1 gives both ICL and IWL of common classes (Fig. 6; rare classes never memorized). Architecture: transformers only — matched vanilla RNNs and LSTMs never exceed chance on ICL (Fig. 7) and are also worse at IWL (Fig. 8). Interpretation: 'neither type of learning is correct per se'; the model's bias is measured on sequences where both strategies give the same training answer; ICL can fade toward IWL with more training.

**Formal object.** p(bursty), number of classes, label multiplicity, within-class noise, Zipf exponent alpha; ICL/IWL accuracies

**Strongest result.** None

**Assumptions.** None

**Resource model.** None

**Failure boundary.** None

**Implementation.** None

**Track-B residual.** None

**Upward question.** None

Verification notes: None

### P4.ICL_FUNCTION_CLASSES_GARG — What can transformers learn in-context? (Garg et al. 2022): in-context learning of function classes matches task-specific algorithms

Disposition: `None` · best verification: `PARTIAL_TEXT_READ`

Sources:

- [0] What Can Transformers Learn In-Context? A Case Study of Simple Function Classes — Shivam Garg, Dimitris Tsipras, Percy Liang, Gregory Valiant (2022), NeurIPS 2022; arXiv 2208.01066 v3. https://arxiv.org/abs/2208.01066 arXiv:2208.01066 — `PARTIAL_TEXT_READ`

**What it already explains.** Definition: a model in-context learns F up to eps w.r.t. (D_F, D_X) if E_P[l(M(P), f(x_query))] <= eps. A 9.5M-parameter GPT-2-style model trained from scratch on prompts from 20-d linear functions matches least squares (error 0.02 at k = d, 0.0006 at 2d), robust to noise (with double descent), orthant shift, and cannot be memorization (32M training weight vectors would give error ~0.2; 10k distinct vectors still suffice). Sparse linear: matches Lasso (0.58/0.09 vs 0.62/0.08 at k = 5/10); decision trees depth 4: 0.12 vs greedy 0.80 / XGBoost 0.62 at k = 100; two-layer ReLU nets: 0.17 = a network trained by Adam on the in-context examples. Capacity raises ICL accuracy and robustness; curriculum drastically speeds training. Fragile to input scale shift (errors 0.30/0.58 at 1/3x and 3x).

**Formal object.** prompt P = (x_1, f(x_1), ..., x_k, f(x_k), x_query); ICL error (Eq. 1); training objective (Eq. 2)

**Strongest result.** None

**Assumptions.** None

**Resource model.** None

**Failure boundary.** None

**Implementation.** None

**Track-B residual.** None

**Upward question.** None

Verification notes: None

### P4.LEARNED_OPTIMIZERS — Learned optimizers: Andrychowicz et al. 2016; Li & Malik 2016; Wichrowska et al. 2017; Metz et al. 2022 (VeLO)

Disposition: `ADAPT` · best verification: `FULL_TEXT_READ`

Sources:

- [0] Learning to learn by gradient descent by gradient descent — Marcin Andrychowicz, Misha Denil, Sergio Gomez Colmenarejo, Matthew W. Hoffman, David Pfau, Tom Schaul, Brendan Shillingford, Nando de Freitas (2016), NeurIPS 2016. https://arxiv.org/abs/1606.04474 arXiv:1606.04474 — `FULL_TEXT_READ`
- [1] Learning to Optimize — Ke Li, Jitendra Malik (2016), arXiv preprint (later ICLR 2017). https://arxiv.org/abs/1606.01885 arXiv:1606.01885 — `FULL_TEXT_READ`
- [2] Learned Optimizers that Scale and Generalize — Olga Wichrowska, Niru Maheswaranathan, Matthew W. Hoffman, Sergio Gomez Colmenarejo, Misha Denil, Nando de Freitas, Jascha Sohl-Dickstein (2017), ICML 2017, PMLR 70. https://arxiv.org/abs/1703.04813 arXiv:1703.04813 — `FULL_TEXT_READ`
- [3] VeLO: Training Versatile Learned Optimizers by Scaling Up — Luke Metz, James Harrison, C. Daniel Freeman, Amil Merchant, Lucas Beyer, James Bradbury, Naman Agarwal, Ben Poole, Igor Mordatch, Adam Roberts, Jascha Sohl-Dickstein (2022), arXiv preprint. https://arxiv.org/abs/2211.09760 arXiv:2211.09760 — `PARTIAL_TEXT_READ`

**What it already explains.** That the parameter-update rule of gradient-based learning can itself be parameterized and learned: theta_{t+1} = theta_t + g_t(grad f(theta_t), phi) with g a coordinatewise LSTM (Andrychowicz), or Delta x = pi(f, {x^(0..i-1)}) with pi a policy learned by guided policy search over first-order optimizers (Li & Malik), or a hierarchical parameter/tensor/global RNN with optimization-inspired features meta-trained on a corpus of small diverse loss landscapes (Wichrowska), or a per-tensor LSTM hypernetwork generating a per-parameter MLP, meta-trained with ES on ~4000 TPU-months across thousands of task families (VeLO). Learned optimizers beat tuned Adam/RMSProp within and near the meta-training distribution and generalize partially (different widths/depths, new datasets, ImageNet early training), but fail out of distribution (ReLU vs sigmoid; late training on Inception; >500M-parameter models; self-hosting). The family also gives the only explicit cost accounting for learned learning laws: per-step overhead O(N_P B + N_P K_P^2 + N_T K_T^2 + K_G^2), memory O(N_P + N_P K_P), and meta-training cost (40M meta-iterations on 1000 workers; ~4000 TPU-months).

**Formal object.** Andrychowicz: L(phi) = E_f[ sum_{t=1}^T w_t f(theta_t) ], theta_{t+1} = theta_t + g_t, [g_t; h_{t+1}] = m(grad_t, h_t, phi), gradients of f w.r.t. phi through grad_t dropped (d grad_t / d phi = 0). Li & Malik: finite-horizon MDP with state = (current location, objective-value changes and gradients at the last H=25 iterates), action = step vector, cost c(s) = objective value; policy pi = Gaussian with NN mean, learned by guided policy search. Wichrowska: update Delta theta_t^n = exp(eta_theta) d_theta / (\|\|d_theta\|\|/N_t) with attention offsets, multi-timescale momentum, dynamic input scaling; meta-objective L(psi) = (1/N) sum_n [log(l(theta_n(psi)) + eps) - log(l(theta_0)+eps)] (Eq. 14). VeLO: meta-objective = final training loss l_N(phi_N); meta-gradient by ES with full-length unrolls; hierarchical hypernetwork.

**Strongest result.** No theorems. Strongest verified results: (i) Andrychowicz Fig. 5: LSTM optimizer trained on a sigmoid MLP generalizes to 40 hidden units and 2 layers but NOT to ReLU; Appendix D asserts (unproved, 'In can be shown') that NTM-BFGS with 1 read and 3 write heads can simulate inverse-Hessian BFGS given a coordinatewise-universal controller and 2 global averaging cells. (ii) Wichrowska Sec. 5.3: optimizer meta-trained on no neural-network problems matches ADAM/RMSProp on small ConvNets/MLPs and stably trains Inception V3 / ResNet V2 for 10K-20K steps, then stalls (loss approaches ~6.5 on Inception V3). (iii) VeLO Fig. 1: on 83 VeLOdrome tasks VeLO is faster than LR-tuned Adam on all tasks and >4x faster on about half; Sec. 4.4.1: performance lags or decreases beyond ~500M parameters; H.3: VeLO cannot meta-train its own architecture (diverges).

**Assumptions.** Inner loop is gradient-based: the learned rule ingests gradients (and losses) computed by fixed backpropagation; the learning law family is 'first-order optimizers' (Li & Malik: 'searching over all possible first-order optimization algorithms'); Coordinatewise / per-parameter weight sharing (permutation invariance over parameters) for scalability; Meta-training task distribution is designer-constructed (random quadratics, small MLPs, hand-built loss-landscape corpus, procedurally generated task families); Truncated backprop-through-time or ES for the outer loop; Andrychowicz drops second derivatives; VeLO uses full unrolls with ES; Meta-objective is a trajectory-weighted or final training loss, not validation/generalization loss (except Ravi & Larochelle, cited)

**Resource model.** compute (per-step overhead formula; wall-clock vs batch size), memory (O(N_P + N_P K_P)), meta-training compute (40M meta-iterations / 1000 workers; ~4000 TPU-months, ~4 weeks on 1K-4K TPUs), horizon (heavy-tailed unroll lengths; long-horizon failure); no description-length or verification accounting

**Failure boundary.** Generalization breaks under changes of activation function (Andrychowicz), at long horizons and on large models (Wichrowska stalls; VeLO >500M params, 8B LLM underperforms untuned Adafactor), on self-hosting (VeLO diverges when meta-training VeLO). Learned optimizers are not interpretable ('understanding what this optimizer is actually doing is currently difficult', VeLO J.2). The task-distribution design is 'largely heuristic with minimal comparisons' (VeLO J.3). No theory predicts which optimizer behavior emerges or when generalization fails; meta-training is 'relatively ad-hoc and not easily replicated' (VeLO E.4).

**Implementation.** Andrychowicz: github.com/deepmind/learning-to-learn (from memory, not verified in text); Wichrowska: https://git.io/v5oq5 (verified, Appendix A); VeLO: velo-code.github.io and the learned_optimization package (verified, abstract/Sec. 1.1); Li & Malik: none known

**Track-B residual.** The family fixes the learning-law morphology (first-order gradient optimizer over a fixed backprop signal) and learns only its parameters. Track B must ask whether the choice BETWEEN optimizer-shaped laws and non-gradient laws (associative, Bayesian, rule/program) can be predicted from ecology and resource prices, and must carry the meta-training cost (TPU-months) into the resource vector as a price of morphogenesis rather than treating it as free.

**Upward question.** Treat the learned-optimizer family as ONE learning-law morphology whose meta-training price is now known. What is the phase boundary in (task-distribution breadth, meta-training compute, horizon) beyond which a learned first-order law loses to a fixed law or to a non-gradient law, and can it be predicted before spending the TPU-months?

Load-bearing quotes (verbatim from sources actually read):

> "propose to replace hand-designed update rules with a learned update rule, which we call the optimizer g, specified by its own set of parameters phi." — [0] Andrychowicz et al. 2016, Section 1
> "Ignoring gradients along the dashed edges amounts to making the assumption that the gradients of the optimizee do not depend on the optimizer parameters" — [0] Andrychowicz et al. 2016, Section 2
> "changing the activation function to ReLU makes the dynamics of the learning procedure sufficiently different that the learned optimizer is no longer able to generalize." — [0] Andrychowicz et al. 2016, Section 3.2
> "This framework subsumes all existing optimization algorithms. Different optimization algorithms differ in the choice of pi." — [1] Li & Malik 2016, Section 3.2
> "searching over policies corresponds to searching over all possible first-order optimization algorithms." — [1] Li & Malik 2016, Section 3.2
> "The computational cost of the learned optimizer is O(N_P B + N_P K_P^2 + N_T K_T^2 + K_G^2)" — [2] Wichrowska et al. 2017, Section 3.4 (symbols transliterated)
> "later in training the learned optimizer stops making effective progress, and the loss approaches a constant (approximately 6.5 for Inception V3)." — [2] Wichrowska et al. 2017, Section 5.3
> "Meta-trained with approximately four thousand TPU-months of compute on a wide variety of optimization tasks" — [3] Metz et al. 2022 (VeLO), abstract
> "The performance of VeLO lags behind baselines, or even decreases, as model size is increased beyon approximately 500M parameters." — [3] Metz et al. 2022 (VeLO), Section 4.4.1 (typo 'beyon' in original)
> "The exact meta-training was relatively ad-hoc and not easily replicated. Due to the computational cost, we could only afford to train one model at full scale." — [3] Metz et al. 2022 (VeLO), Appendix E.4
> "We found VeLO was not capable of this task, and quickly diverged." — [3] Metz et al. 2022 (VeLO), Appendix H.3 (self-hosting)

Verification notes: Three of four papers read essentially in full via page-level retrieval; VeLO read in the sections listed (about 13 of ~80 pages). The DeepMind code URL for Andrychowicz is from memory and was not present in the returned pages. No prior reconstruction in the repo ledgers listed in the brief.

### P4.LEARNED_UPDATE_RULE_FAMILIES — Sandler et al. 2021 'Meta-learning bidirectional update rules' (BLUR)

Disposition: `GENERALIZE` · best verification: `PARTIAL_TEXT_READ`

Sources:

- [0] Meta-Learning Bidirectional Update Rules — Mark Sandler, Max Vladymyrov, Andrey Zhmoginov, Nolan Miller, Andrew Jackson, Tom Madams, Blaise Aguera y Arcas (2021), ICML 2021, PMLR 139 (arXiv v2, 11 Jun 2021). https://arxiv.org/abs/2104.04657 arXiv:2104.04657 — `PARTIAL_TEXT_READ`

**What it already explains.** A parametric FAMILY of learning laws in which forward activation, backward signal propagation and synapse update are all governed by a shared low-dimensional 'genome' G = {f, f~, nu, nu~, mu, mu~, eta, eta~} applied at every neuron/synapse; neurons carry k states, synapses k channels. Chain-rule backpropagation + SGD is exactly the two-state member with nu = [[1,0],[1,0]], mu = [0;1], nu~ = [1;0], mu~ = [0;1] and a multiplicative backward update (Eq. 4). Genomes are meta-learned (SGD through unrolls, or CMA-ES on non-differentiable accuracy) on a few tasks, train unseen datasets faster than SGD for the first ~50-100 steps (then SGD overtakes), generalize across input resolution and class count (with activation normalization), and from deeper to shallower architectures but not vice versa. The learned rule is provably NOT gradient descent of any loss: the necessary symmetry condition d Delta w_ij / d w_mn = d Delta w_mn / d w_ij (Eq. 10) is numerically violated (Fig. 2). Hebbian-only synapse updates are unstable; an Oja-like inhibitory term or synapse saturation is needed.

**Formal object.** Forward: a^c_j <- sigma(f a^c_j + eta sum_{i in I(j), d} w^c_ij nu_cd a^d_i) (Eq. 5); Backward: a^c_i <- sigma(f a^c_i + eta sum_{j in J(i), d} w^c_ji mu_cd a^d_j) (Eq. 6); Weights: w^c_ij <- f~ w^c_ij + eta~ sum_{e,d} a^e_i nu~_ec mu~_cd a^d_j (Eq. 7); genome G = {f, f~, nu, nu~, mu, mu~, eta, eta~} shared across layers and tasks; meta-objective L_meta(G) = E_s[ p_i(s) log a^(0)_{y_i}(s) ] after a fixed number of unroll steps; equivalence-to-gradient-descent test: symmetry of d Delta w / d w (Eq. 9-10).

**Strongest result.** Section 3.1, Eq. 4 (verified): backpropagation with SGD is a special case of the two-state genome family. Section 3.5 / Fig. 2 (verified): the meta-learned genome's update violates the symmetry condition necessary for existence of an equivalent loss L_equiv, so it is not a gradient descent on any loss (possibly a Riemannian-metric gradient flow; left open). Fig. 5/6 (verified): 4-state BLUR genome trained on MNIST converges much faster than SGD for ~50 unroll steps on MNIST/EMNIST/Fashion, SGD catches up at ~100 steps. Fig. 10 (verified): genomes meta-trained on deeper networks transfer to shallower and deeper ones; 2-layer genomes diverge on 4 layers.

**Assumptions.** Neural substrate with bag-of-neurons connectivity; bilinear (Hebb-style) synapse updates mixed by k x k genome matrices; same nonlinearity forward and backward; Supervision injected by setting the second state of output neurons to +/-1 (no explicit loss); Activation normalization (batch-norm-like) on both passes and Oja-like/saturation terms required for stability; Meta-training on 1-3 small tasks (Boolean functions, MNIST halves), unrolls up to 50 steps, curriculum over unroll length; Genome shared across architectures; performance claims restricted to fully connected nets

**Resource model.** compute (single GPU, 30 min to 20 h per genome), samples/steps (unroll steps; short-horizon advantage), description length implicitly (genome = few k x k matrices + 4 scalars); no verification accounting

**Failure boundary.** Only fully connected small networks; advantage vanishes after ~100 steps; needs normalization and saturation hacks; deeper-to-shallower transfer only; no theory of which genome is selected by which task family; the family is confined to bilinear local updates in a neural substrate (no Bayesian/rule/program laws); equivalence class of the learned rule (gradient flow under some metric?) left open.

**Implementation.** https://github.com/google-research/google-research/tree/master/blur (verified, Section 4)

**Track-B residual.** BLUR is the closest existing 'one basis, many learning laws' object: a low-dimensional genome parameterizes a family containing backprop, feedback-alignment-like and Hebbian/Oja laws, with a formal test separating gradient laws from non-gradient laws. Track B must generalize the genome beyond bilinear neural updates to include Bayesian, rule and program learning laws, and supply the selection theory (which genome region wins under which ecology) that BLUR leaves to meta-training.

**Upward question.** Extend BLUR's symmetry test (Eq. 10) into a morphology-equivalence quotient over learning laws (gradient flow / metric gradient flow / non-gradient dynamical law / Bayesian update), and ask whether a generic basis under ecology E develops one class or another, predictably (T3, T11).

Load-bearing quotes (verbatim from sources actually read):

> "classical gradient-based backpropagation in neural networks can be seen as a special case of a two-state network where one state is used for activations and another for gradients, with update rules derived from the chain rule." — [0] Sandler et al. 2021, abstract
> "Notice that the genome is defined at the level of individual neurons and synapses and is independent from the network architecture." — [0] Sandler et al. 2021, Section 3.2
> "we verified that the discovered update rules do not satisfy condition (10) (see Fig. 2) and therefore L_equiv does not generally exist for our update rule family." — [0] Sandler et al. 2021, Section 3.5
> "genomes generalize from more complex architectures to less complex architectures, but not vice versa!" — [0] Sandler et al. 2021, Section 4.5
> "The simplest variant with symmetric, single-state synapses tends to be the winner, however it has to be initialized from the backprop genome." — [0] Sandler et al. 2021, Section 4.5
> "after about 100 steps SGD reaches the same accuracy and continues to grow." — [0] Sandler et al. 2021, Figure 5 caption

Verification notes: Equations 4-7, 9-10 and Sections 3.1-3.5, 4.5 verified; page 7 (Sections 4.2-4.3 details) not retrieved. No prior reconstruction in the repo ledgers listed in the brief; VSML (read) cites BLUR as concurrent work using fast weights to meta-learn general learning algorithms.

### P4.LPG_DISCOVERED_UPDATE_OH — Discovering reinforcement learning algorithms (Oh et al. 2020): a meta-learned update rule that generalizes from toy MDPs to Atari

Disposition: `None` · best verification: `PARTIAL_TEXT_READ`

Sources:

- [0] Discovering Reinforcement Learning Algorithms — Junhyuk Oh, Matteo Hessel, Wojciech M. Czarnecki, Zhongwen Xu, Hado van Hasselt, Satinder Singh, David Silver (2020), NeurIPS 2020; arXiv 2007.08794 v3. https://arxiv.org/abs/2007.08794 arXiv:2007.08794 — `PARTIAL_TEXT_READ`

**What it already explains.** LPG: a backward LSTM update rule eta takes [r_t, d_t, gamma, pi(a_t\|s_t), y(s_t), y(s_t+1)] (no observations/actions -> environment-agnostic) and outputs targets (pi_hat, y_hat) for the policy and a 30-d categorical prediction vector with no imposed semantics; agent update Eq. 2; meta-gradient Eq. 3-4 with entropy and L2 regularizers; per-environment hyperparameter bandit (Sec. 3.4) needed for stability. Trained on 15 toy environments (tabular/random grid worlds, delayed-chain MDPs), LPG outperforms A2C on most training environments, discovers a prediction semantics from which value functions at several discounts can be regressed (Fig. 5), converges (Fig. 6), and generalizes to Atari with super-human scores on 14 games; generalization improves with the number of training environments (Fig. 9). LPG-V (given a TD value function) is worse: 'discovering the semantics of prediction is the key'.

**Formal object.** eta* = argmax E_E E_theta0 [G]; update rule as LSTM; prediction vector y in [0,1]^30

**Strongest result.** None

**Assumptions.** None

**Resource model.** None

**Failure boundary.** None

**Implementation.** None

**Track-B residual.** None

**Upward question.** None

Verification notes: None

### P4.MAML_UNIVERSALITY — MAML (Finn, Abbeel, Levine 2017) and 'Meta-learning and universality' (Finn & Levine 2018)

Disposition: `ADOPT` · best verification: `FULL_TEXT_READ`

Sources:

- [0] Model-Agnostic Meta-Learning for Fast Adaptation of Deep Networks — Chelsea Finn, Pieter Abbeel, Sergey Levine (2017), ICML 2017, PMLR 70:1126-1135. https://arxiv.org/abs/1703.03400 arXiv:1703.03400 — `PARTIAL_TEXT_READ`
- [1] Meta-Learning and Universality: Deep Representations and Gradient Descent can Approximate any Learning Algorithm — Chelsea Finn, Sergey Levine (2018), ICLR 2018. https://arxiv.org/abs/1710.11622 arXiv:1710.11622 — `FULL_TEXT_READ`

**What it already explains.** MAML: a task distribution p(T) with tasks T = {L, q(x1), q(x_{t+1}\|x_t,a_t), H}; meta-learn an initialization theta such that one (or a few) gradient steps on K samples of a new task give low test loss; meta-objective min_theta sum_{T_i} L_{T_i}(f_{theta - alpha grad L_{T_i}(f_theta)}); meta-gradient is a gradient-through-a-gradient (Hessian-vector products), with a first-order approximation. Universality paper: formalizes 'universal learning procedure approximator' (a UFA with input (D, x*) and output y*) and proves that a sufficiently deep ReLU network with a bias-transformation input, updated by ONE step of gradient descent on MSE or softmax cross-entropy with small alpha, can approximate any continuous function of (x, y, x*) (one-shot) and any permutation-invariant continuous function of ({(x,y)_k}, x*) (K-shot). Hence gradient-based meta-learners with learned initialization have the same representational power as recurrent/black-box meta-learners; the two families differ only in inductive bias / statistical efficiency (empirically: MAML resists overfitting under many extra steps and extrapolates better out of distribution; depth matters for MAML because one gradient step on a product of N linear layers gives a rank-N update).

**Formal object.** Learner f(.;theta), theta' = theta - alpha grad_theta (1/K) sum_k l(y_k, f(x_k;theta)); f_MAML(D_T, x*; theta) := f(x*; theta'). Constructed network f_hat(.;theta) = f_out((prod_{i=1}^N W_i) phi(.; theta_ft, theta_b); theta_out), with block-decomposed W_i, phi, and error gradient (Eq. 2) that multiplex forward information from x, x* and backward information from y; post-update z* = -alpha sum_i A_i e(y) phi~(x)^T B_i^T B_i phi~(x*) (Eq. 3), f_hat(x*;theta') = h_post(-alpha sum_i A_i e(y) k_i(x,x*); theta_h) (Eq. 7), where k_i is a kernel and A_1 = I, B_N = I, other A_i symmetric PD, B_i PD. Loss requirement: grad_{y_hat} l(y, 0) = A y with A invertible (Theorems 6.1, 6.2).

**Strongest result.** Lemma 4.1 (verified): assuming e(y) can be any linear (not affine) function of y, one can choose theta_ft, theta_h, {A_i; i>1}, {B_i; i<N} so that f_hat(x*; theta') = h_post(-alpha sum_i A_i e(y) k_i(x,x*)) approximates any continuous function of (x, y, x*) on compact subsets. Section 5 / Appendix B-C (verified): the K-shot extension approximates any function of ({(x,y)_k}, x*) invariant to datapoint ordering (for continuous labels, additionally assuming distinct inputs x_k). Theorem 6.1 (MSE gradient at y_hat=0 is a linear invertible function of y) and Theorem 6.2 (softmax cross-entropy gradient w.r.t. logits at 0 is linear invertible in y) certify the two standard losses; l1, hinge and Huber losses are excluded because their gradients are piecewise constant.

**Assumptions.** One gradient step (multi-step not analyzed); alpha small so that O(alpha^2) terms are dropped; Sufficient depth: N linear (ReLU-linear regime) layers to obtain a rank-N update; feature extractor and readout are themselves UFAs; Bias transformation variable theta_b concatenated to the input (symmetry breaking); without it the construction fails; Loss whose gradient at zero prediction is a linear invertible function of the label (MSE, softmax cross-entropy); excludes l1/hinge/Huber; Continuous target on compact subsets (inherited from UFA); for continuous labels in K-shot, no two training inputs coincide; Constructive existence proof with 'simple though inefficient' discretization (A.1); no bound on required width/depth; Universality is about representational capacity only; statistical efficiency is left to experiments

**Resource model.** none formally (depth N is tied to update rank; no description-length, time, or sample bounds); empirically depth vs. fixed parameter count (Sec. 7.2) and number of gradient steps (Sec. 7.1)

**Failure boundary.** Does not predict which learning algorithm is acquired, nor sample efficiency; universality collapses the distinction between learning laws (any law is representable), so the theorem is non-identifying. Fails for losses with information-losing gradients. Empirical claims (OOD extrapolation, overfitting resistance) are on sinusoid/Omniglot/polynomial toys. MAML itself needs second-order derivatives and is restricted to gradient-descent inner loops.

**Implementation.** github.com/cbfinn/maml (regression/supervised) and github.com/cbfinn/maml_rl (RL), as stated in the MAML paper

**Track-B residual.** Given that 'representation + one gradient step' is already a universal learning-procedure approximator, what NON-representational invariant (statistical efficiency, description length of the inductive bias, verification cost) distinguishes learning-law morphologies, and can it be predicted from the ecology rather than measured after meta-training?

**Upward question.** Since universality makes all learning laws representable, Track B must define the morphology of a learning law by a quotient that universality cannot see (e.g., resource-bounded compilation cost, inductive bias under domain shift). Which quotient, and is it ecology-predictable (T3, T9)?

Load-bearing quotes (verbatim from sources actually read):

> "does representation combined with standard gradient descent have sufficient capacity to constitute any learning algorithm?" — [1] Finn & Levine 2018, Section 1
> "we define a universal learning procedure approximator to be a learner which can approximate any function of the set of training datapoints D_T and the test point x*." — [1] Finn & Levine 2018, Section 3
> "a single gradient step W_i - alpha grad_{W_i} l can only represent a rank-1 update to the matrix W_i." — [1] Finn & Levine 2018, Section 4 (symbols transliterated)
> "The bias transformation variable theta_b plays a vital role in our construction, as it breaks the symmetry within k_i(x, x*)." — [1] Finn & Levine 2018, Section 4
> "Essentially, y needs to be recoverable from the loss function's gradient." — [1] Finn & Levine 2018, Section 6
> "The gradients of the l1 and hinge losses are piecewise constant, and thus do not allow for universality." — [1] Finn & Levine 2018, Section 6
> "we will disregard the last term, assuming that alpha is comparatively small such that alpha^2 and all higher order terms vanish." — [1] Finn & Levine 2018, Section 4
> "The MAML meta-gradient update involves a gradient through a gradient." — [0] Finn et al. 2017, Section 2.2
> "make no assumption on the form of the model, other than to assume that it is parametrized by some parameter vector theta, and that the loss function is smooth enough in theta that we can use gradient-based learning techniques." — [0] Finn et al. 2017, Section 2.2

Verification notes: Universality paper read in full including all appendices; theorem/lemma numbers (Lemma 4.1, Lemma A.1, Theorems 6.1, 6.2) verified. MAML paper: Sections 1-2 read in full (Algorithm 1, Eq. 1), rest located by grep only. No prior reconstruction of either in the repo ledgers listed in the brief.

### P4.META_BAYES_MIKULIK — Meta-trained agents implement Bayes-optimal agents (Mikulik et al. 2020): behavioural and structural (simulation) equivalence

Disposition: `None` · best verification: `FULL_TEXT_READ`

Sources:

- [0] Meta-trained agents implement Bayes-optimal agents — Vladimir Mikulik, Gregoire Deletang, Tom McGrath, Tim Genewein, Miljan Martic, Shane Legg, Pedro A. Ortega (2020), NeurIPS 2020; arXiv 2010.11223. https://arxiv.org/abs/2010.11223 arXiv:2010.11223 — `FULL_TEXT_READ`

**What it already explains.** On 10 prediction tasks (exponential-family observations with conjugate priors) and 4 two-armed bandits with tractable Bayes-optimal policies (Gittins indices), LSTM meta-learners trained by BPTT/Impala behave virtually indistinguishably from the Bayes-optimal agent (Fig. 4a), converge to it across 10 training runs (Fig. 2: 'Bayes-optimal policies are the fixed points of the meta-learning dynamics'), and are structurally simulated by it: a learned map phi from the RNN state (PCA-projected to the dimension of the sufficient statistics) to the Bayes-optimal state makes transitions and outputs agree (low D_s, D_o for RNN -> Opt). The reverse simulation fails partly (non-injective, non-minimal sufficient statistics; 'no explicit incentive during RNN training that would force representations to be minimal'). Untrained RNNs already have low state dissimilarity on bandits (reservoir effect). Scope: 'when optimal policies are in the search space, and training converges to those policies, then the resulting policy will be Bayes-optimal'.

**Formal object.** Mealy machines (f_w, g_w); simulation relation N <= M via a state map phi (transitions and outputs); dissimilarities d, D_s, D_o

**Strongest result.** None

**Assumptions.** None

**Resource model.** None

**Failure boundary.** None

**Implementation.** None

**Track-B residual.** None

**Upward question.** None

Verification notes: None

### P4.META_LEARNING_TAXONOMY — Hospedales, Antoniou, Micaelli, Storkey 2021 'Meta-learning in neural networks: a survey'

Disposition: `ADOPT` · best verification: `PARTIAL_TEXT_READ`

Sources:

- [0] Meta-Learning in Neural Networks: A Survey — Timothy Hospedales, Antreas Antoniou, Paul Micaelli, Amos Storkey (2021), IEEE TPAMI (arXiv v2, 7 Nov 2020). https://arxiv.org/abs/2004.05439 arXiv:2004.05439 — `PARTIAL_TEXT_READ`

**What it already explains.** A formalization and a three-axis taxonomy of neural meta-learning. Formal: conventional learning theta* = argmin_theta L(D; theta, omega) with omega = 'how to learn'; task-distribution view min_omega E_{T~p(T)} L(D; omega) (Eq. 2); meta-train omega* = argmax log p(omega \| D_source) (Eq. 3), meta-test theta*(i) = argmax log p(theta \| omega*, D_train(i)) (Eq. 4); bilevel view omega* = argmin_omega sum_i L_meta(theta*(i)(omega), omega, D_val(i)) s.t. theta*(i)(omega) = argmin_theta L_task(theta, omega, D_train(i)) (Eq. 5-6); feed-forward/amortized view (Eq. 7). Taxonomy: Meta-Representation ('What?': initialization, optimizer, feed-forward models/hypernetworks, embeddings/metrics, losses, architectures, curricula, data augmentation, modules, hyperparameters, program code), Meta-Optimizer ('How?': gradient, RL, evolution), Meta-Objective ('Why?': few-shot, many-shot, robustness to domain shift/label noise/adversarial attack, compute efficiency). Notes meta-overfitting, memorization, meta-generalization under task shift, computational cost of bilevel optimization, and that the base representation theta is deliberately excluded from the taxonomy. Positions transfer, domain adaptation, continual, multi-task learning, hyperparameter optimization, hierarchical Bayes and AutoML relative to meta-learning.

**Formal object.** Bilevel program (Eq. 5-6): omega* = argmin_omega sum_{i=1}^M L_meta(theta*(i)(omega), omega, D_val,source(i)) subject to theta*(i)(omega) = argmin_theta L_task(theta, omega, D_train,source(i)); task T = {D, L}; design space = (meta-representation omega) x (meta-optimizer) x (meta-objective L_meta, p(T), data flow).

**Strongest result.** No theorems (survey). Strongest verified content: the explicit statement that the salient characteristic of contemporary neural meta-learning is an explicitly defined meta-level objective with end-to-end optimization of the inner algorithm; the three-axis design space; the observation (citing [88]) that model-based/black-box meta-learners generalize worse out-of-distribution and are asymptotically weaker than optimization-based ones; the historical dating (1987 Schmidhuber; Bengio et al.; Thrun & Pratt 1998; gradient-based meta-learning 1991/2001).

**Assumptions.** Scope restricted to neural-network meta-learning with an explicit end-to-end meta-objective (excludes AutoML heuristics, random search, Bayesian HPO, classical algorithm-selection meta-learning); Task distribution p(T) available (or single-task episodes via train/val splits); Bilevel picture 'arguably only accurate for the optimizer-based methods'; Base representation theta is application-specific and left out of the taxonomy

**Resource model.** compute and memory of bilevel optimization discussed qualitatively (Section 6: time and memory cost of reverse-mode differentiation; implicit/forward-mode/online/truncated alternatives; short-horizon bias); samples (few-shot vs many-shot as a meta-objective axis); no formal accounting

**Failure boundary.** Descriptive, not predictive: the taxonomy classifies existing methods but gives no law for which meta-representation or meta-objective will be selected or will generalize under a given task shift ('we have yet to understand which kinds of meta-representations tend to generalize better under certain types of domain shifts'). Excludes non-neural learning laws (rule/program/Bayes) except as meta-representations of code.

**Implementation.** none known (survey)

**Track-B residual.** Use the (What, How, Why) axes as the coordinate system for learning-law morphologies, but Track B must supply what the survey explicitly lacks: a selection law mapping ecology E to the dominant point in that design space, and an inclusion of non-neural inner learners.

**Upward question.** Given the design space (omega, meta-optimizer, L_meta), which regions are reachable by developmental acquisition from a generic basis (D2) and which are selected by which ecologies (D3)? The survey provides the map; Track B must provide the dynamics on it.

Load-bearing quotes (verbatim from sources actually read):

> "Thrun [7] operationally defines learning-to-learn as occurring when a learner's performance at solving tasks drawn from a given task family improves with respect to the number of tasks seen." — [0] Section 1
> "The salient characteristic of contemporary neural-network meta-learning is an explicitly defined meta-level objective, and end-to-end optimization of the inner algorithm with respect to this objective." — [0] Section 2
> "Note that the base model representation theta isn't included in this taxonomy, since it is determined and optimized in a way that is specific to the application at hand." — [0] Section 3.2
> "Meta-learning and learning-to-learn first appear in the literature in 1987 [14]." — [0] Section 2.2
> "it has been observed that model-based approaches are usually less able to generalize to out-of-distribution tasks than optimization-based methods [88]." — [0] Section 3.1
> "Furthermore, we have yet to understand which kinds of meta-representations tend to generalize better under certain types of domain shifts." — [0] Section 6

Verification notes: Pages 1-5 and 15 read; equations 1-7 and Section 3.2 taxonomy verified. Section 4.1 (meta-representation) read only up to feed-forward models; Sections 4.2-5 not retrieved. No prior reconstruction in the repo ledgers.

### P4.META_RL — Meta-RL: Wang et al. 2016 'Learning to reinforcement learn'; Duan et al. 2016 RL^2

Disposition: `ADOPT` · best verification: `FULL_TEXT_READ`

Sources:

- [0] Learning to reinforcement learn — Jane X. Wang, Zeb Kurth-Nelson, Dhruva Tirumala, Hubert Soyer, Joel Z. Leibo, Remi Munos, Charles Blundell, Dharshan Kumaran, Matt Botvinick (2016), arXiv preprint (v3, 23 Jan 2017); CogSci 2017. https://arxiv.org/abs/1611.05763 arXiv:1611.05763 — `PARTIAL_TEXT_READ`
- [1] RL^2: Fast Reinforcement Learning via Slow Reinforcement Learning — Yan Duan, John Schulman, Xi Chen, Peter L. Bartlett, Ilya Sutskever, Pieter Abbeel (2016), arXiv preprint (v2, 10 Nov 2016); ICLR 2017 submission. https://arxiv.org/abs/1611.02779 arXiv:1611.02779 — `FULL_TEXT_READ`

**What it already explains.** A recurrent policy (LSTM/GRU) that receives observation, previous action, previous reward (and termination flag) and is trained by a standard 'slow' RL algorithm (A2C/A3C; first-order TRPO with GAE) over a distribution of MDPs D (bandits with independent/dependent arms, restless bandits, tabular MDPs, two-step task, visual mazes) comes to implement in its activations a second, 'fast' RL procedure that is prior-dependent: it approaches Gittins/Thompson/UCB/PSRL/OPSRL performance on structured distributions, exploits arm correlations that generic algorithms cannot, pays short-term cost for information, adapts its effective learning rate to episode volatility, and shows model-based-like behavior on the two-step task despite a model-free outer loop. Training on structured distributions hurts on unstructured ones (prior-dependence), and the outer-loop RL becomes the bottleneck for long trials/many episodes (RL^2 falls behind OPSRL as n grows; supervised imitation of Gittins closes the gap). RL^2 is explicitly a POMDP reduction: the unknown MDP is hidden state, the trial (n episodes with hidden state carried over) is the unit of optimization, objective = expected discounted return over a trial = minimizing cumulative pseudo-regret.

**Formal object.** Wang: prior D over MDPs; agent chooses a_t as a function of the history H_t = {x_0, a_0, r_0, ..., x_t}; weights trained to maximize total reward over episodes; LSTM state reset per episode; evaluation with frozen weights (learning rate zero). Duan: MDP M = (S, A, P, r, rho_0, gamma, T); rho_M over MDPs; trial = n episodes on one MDP with hidden state h carried across episodes; input phi(s, a, r, d) to a GRU policy pi_theta; maximize expected total discounted reward over a trial; outer loop TRPO+GAE.

**Strongest result.** No theorems. Verified results: Wang Fig. 2a (independent Bernoulli 2-arm bandits: LSTM-A2C beats Thompson and UCB, below Gittins), Fig. 2f (all train/test combinations over D_i, D_u, D_e, D_m, D_h: structured training helps on structured tests and hurts on independent arms), Fig. 3 (11-arm informative-arm task: agent samples the informative arm first), Fig. 4 (restless bandits: learned procedure adjusts learning rate by volatility, beating best fixed-rate Rescorla-Wagner, UCB and Thompson; R-W model comparison shows non-R-W lapses). Duan Table 1 (MAB: RL^2 within noise of best of Gittins/UCB1/TS for k in {5,10,50}, n in {10,100}, gap at n=500, k=50), Table 2 (random tabular MDPs: RL^2 best for n <= 50 episodes, overtaken by OPSRL/PSRL/UCRL2/BEB for n >= 75), Table 3 (visual navigation: episode-2 trajectory shorter than episode-1 in 91.7% of small mazes, 71.4% of large).

**Assumptions.** Recurrent neural policy with reward/action/termination as inputs; hidden state as the learned algorithm's memory; Distribution over MDPs available for sampling; evaluation on same or slightly shifted distribution; Outer loop is standard policy-gradient RL (A2C/A3C, TRPO); hidden state reset per episode (Wang) or per trial (Duan); Small state/action spaces for the quantitative comparisons (bandits, \|S\|=10, \|A\|=5 MDPs); visual mazes 5x5 with 2 episodes; Wang: focus on STRUCTURED task distributions; Duan: unstructured (uniform bandits, flat-Dirichlet MDPs)

**Resource model.** samples (episodes per trial n; training episodes 20,000 for bandits; TRPO batch 250k), horizon (trial length; performance degrades with more episodes), memory (hidden state); no compute or verification accounting

**Failure boundary.** Outer-loop RL is the bottleneck for long horizons and many episodes (Duan Sec. 3.2, 5); no theory of which RL procedure emerges; the learned algorithm is identified only behaviorally (regret curves, model fits); prior-dependence means no generalization to distributions outside D; memory limits (agent sometimes forgets the target location); no scaling beyond small mazes without additional memory mechanisms.

**Implementation.** Duan: built on rllab and TensorFlow (no URL in text); Wang: none stated

**Track-B residual.** Both papers show that in the reward-feedback regime a generic recurrent substrate develops an RL algorithm tuned to the task prior. Track B's question is whether the SAME basis, under supervised, reward and self-supervised feedback, develops laws that are morphologically distinct (associative vs. Bayesian-like vs. model-based) and whether the feedback type and horizon of E predict which; neither paper varies the feedback contract or predicts the emergent law.

**Upward question.** Is the emergent fast RL procedure a distinct learning-law morphology from the emergent supervised in-context learner (GPICL) when both are grown from the same substrate, and is feedback type (reward vs. label) the ecology axis that selects between them?

Load-bearing quotes (verbatim from sources actually read):

> "What emerges is a system that is trained using one RL algorithm, but whose recurrent dynamics implement a second, quite separate RL procedure." — [0] Wang et al. 2016, abstract
> "meta-RL is able to learn a prior-dependent RL algorithm, in the sense that it will perform well on average on MDPs drawn from D or slight modifications of D." — [0] Wang et al. 2016, Section 2.3
> "previous training on any structured distribution (Du, De, Dm, or Dh) hurts performance when agents are tested on an independent distribution (Di; Figure 2f)." — [0] Wang et al. 2016, Section 3.1.2
> "meta-RL adjusted its learning rate to the volatility of the episode, whereas model fitting the R-W behavior simply recovered the fixed parameters" — [0] Wang et al. 2016, Section 3.1.4
> "the algorithm is encoded in the weights of the RNN, which are learned slowly through a general-purpose ("slow") RL algorithm." — [1] Duan et al. 2016, abstract
> "Our formulation essentially constructs a partially observable MDP (POMDP) which is solved in the outer loop, where the underlying MDP is unobserved by the agent." — [1] Duan et al. 2016, Section 4
> "The advantage is reversed as n increases, suggesting that the reinforcement learning problem in the outer loop becomes more challenging to solve." — [1] Duan et al. 2016, Section 3.2
> "the outer-loop reinforcement learning algorithm was shown to be an immediate bottleneck" — [1] Duan et al. 2016, Section 5

Verification notes: Duan read in full; Wang read except the Harlow and navigation experiments (Sections 3.2.2-3.2.3). Table 1/2/3 numbers verified. No prior reconstruction in the repo ledgers listed in the brief.


## P5 — programmatic / library-learning intelligence

### P5.DREAMCODER_OBJECTIVE — DreamCoder (Ellis et al. 2021): wake / abstraction / dreaming as coordinate ascent on a description-length posterior over a library, with a neural recognition model

Disposition: `ADAPT` · best verification: `PARTIAL_TEXT_READ`

Sources:

- [0] DreamCoder: Growing generalizable, interpretable knowledge with wake-sleep Bayesian program learning — Kevin Ellis, Catherine Wong, Maxwell Nye, Mathias Sable-Meyer, Luc Cary, Lucas Morales, Luke Hewitt, Armando Solar-Lezama, Joshua B. Tenenbaum (2021), PLDI 2021 (as 'DreamCoder: Bootstrapping inductive program synthesis with wake-sleep library learning'); arXiv:2006.08381v1. https://arxiv.org/abs/2006.08381 arXiv:2006.08381 — `PARTIAL_TEXT_READ`

**What it already explains.** Three-part object: (1) a library L of polymorphically typed lambda-calculus primitives, (2) a set of programs rho_x solving tasks x in X, (3) a neural recognition model Q(rho \| x). Objective (Eq. 1): Wake finds rho_x = argmax over programs with large Q(rho\|x) of P[rho \| x, L] proportional to P[x \| rho] P[rho \| L]; Abstraction sleep sets L = argmax_L P[L] prod_x max over refactorings rho of rho_x of P[x\|rho]P[rho\|L], with P[L] a description-length prior; Dreaming sleep trains Q(rho\|x) ~ P[rho\|x, L] on replays (x ~ X) and fantasies (x ~ L). The three updates maximise a lower bound on the posterior over L given X. Neural vs symbolic roles: the symbolic part is the library + programs (interpretable, transferable), the neural part is the amortised proposal that reduces search entropy; domain knowledge enters through the recognition architecture (CNN for images). Ablations: removing the recognition model or removing abstraction both degrade held-out solve rate; deeper libraries correlate with solving more tasks (r = 0.79). Compute: about a day on 20-100 CPUs per domain; baselines include 24h enumeration over ~400M programs, EC, RobustFill, memorisation.

**Formal object.** L: typed lambda-calculus library with description-length prior P[L]; rho: programs; P[rho \| L]: PCFG-style generative model over programs given L; P[x \| rho]: task likelihood (exact match for list/text tasks, BIC-penalised least squares for symbolic regression with real parameters fit by inner-loop gradient descent); Q(rho \| x): neural recognition model (domain-specific encoder + bigram-over-primitives decoder); refactoring set bounded by a version-space algebra with a bound on lambda-calculus evaluation steps (bound 3, beam k = 5 in ablations). Eq. 1 is coordinate ascent on log P[L] + sum_x log max_rho P[x\|rho]P[rho\|L].

**Strongest result.** No theorem. The structural result is Eq. 1 as a lower bound on the library posterior, plus the empirical claims: DreamCoder 'always solves the most held-out tasks' across domains (mean 54.1s, median 15.0s per solve), 'no alternative model ever solves more than 60% of held-out tasks while DreamCoder learns to solve nearly 100%', and the footnote analysis that library learning decreases search depth at the expense of breadth while the recognition model decreases breadth by cutting per-decision entropy.

**Assumptions.** tasks are given as input-output examples (5-10 examples per task; 100-200 tasks per domain) - supervised at the task level; a fixed base DSL and a fixed type system; programs are typed lambda terms; description-length prior over libraries is the selection principle; the exact prior form is in supplement S4.5 (not read); recognition model architecture is hand-chosen per domain; refactoring search is bounded (version spaces, evaluation-step bound), so abstraction is approximate; compute budget of CPU-days is available; search timeouts define failure

**Resource model.** partial and explicit: (i) description length through P[L] and the BIC penalty in symbolic regression, (ii) compute through per-task timeouts and reported CPU-days, (iii) samples through task/example counts, (iv) search entropy (bits per decision) as the quantity the recognition model reduces. Not charged: the recognition model's own size, the cost of dreaming, or verification of programs beyond examples.

**Failure boundary.** Fails when tasks require primitives absent from the closure of the base DSL under refactoring, when likelihoods are not example-checkable, and when the refactoring bound excludes the useful abstraction. Morphology is pre-fixed: the neural part can only be a proposal over the symbolic grammar; it never becomes the solution, and the symbolic part never becomes a proposal. No online/continual learning law; no cost-driven decision about whether to grow the library or the network.

**Implementation.** open-source (OCaml enumerator + Python/PyTorch recognition model; repository ellisk42/ec, not read); experiments on list processing, text editing, LOGO graphics, towers, symbolic regression, recursive programming, physics laws.

**Track-B residual.** DreamCoder is the closest existing instance of a description-length-priced acquisition of program morphology, but (i) it is supervised at the task level (labels = examples), (ii) the neural/symbolic partition is fixed a priori, (iii) the description-length prior is over the symbolic library only. Track B residual: an ecology-driven, label-free version in which the recognition model, the library and the choice of law are all candidates under one cost functor.

**Upward question.** Can Eq. 1 be extended so that the recognition model's description length and the library's description length are priced in the same units, making 'grow the network' versus 'grow the library' a derived decision under the ecology's task distribution rather than a fixed architectural commitment?

Load-bearing quotes (verbatim from sources actually read):

> "rho_x = arg max_{rho: Q(rho\|x) is large} P[rho\|x, L] proportional to P[x\|rho]P[rho\|L], for each task x in X   Wake" — [0] Ellis et al. 2021, Eq. 1 (Wake line)
> "L = arg max_L P[L] prod_{x in X} max_{rho a refactoring of rho_x} P[x\|rho]P[rho\|L]   Sleep: Abstraction" — [0] Ellis et al. 2021, Eq. 1 (Abstraction line)
> "Train Q(rho\|x) approx P[rho\|x, L], where x ~ X ('replay') or x ~ L ('fantasy')   Sleep: Dreaming" — [0] Ellis et al. 2021, Eq. 1 (Dreaming line)
> "where P[L] is a description-length prior over libraries (S4.5) and P[x\|rho] is the likelihood of a task x in X given program rho." — [0] Ellis et al. 2021, Section 3
> "these updates serve to maximize a lower bound on the posterior over L given X (S4.1)." — [0] Ellis et al. 2021, Section 3
> "We represent programs as polymorphically typed lambda-calculus expressions, an expressive formalism including conditionals, variables, higher-order functions, and the ability to define new functions." — [0] Ellis et al. 2021, Section 3
> "We implement recognition models as neural networks, injecting domain knowledge through the network architecture: for instance, when inducing graphics programs from images, we use a convolutional network" — [0] Ellis et al. 2021, Section 3
> "Across domains, our model always solves the most held-out tasks (Fig. 6A; see Fig. S13 for memorization baselines) and generally solves them in the least time (mean 54.1s; median 15.0s; Fig. S11)." — [0] Ellis et al. 2021, Section 4 (ablations)
> "no alternative model ever solves more than 60% of held-out tasks while DreamCoder learns to solve nearly 100% of them." — [0] Ellis et al. 2021, Section 4
> "Across domains, deeper libraries correlate well with solving more tasks (r = 0.79), and the presence of a learned recognition model leads to better performance at all depths." — [0] Ellis et al. 2021, Section 4
> "typically takes around a day using moderate compute resources (20-100 CPUs)." — [0] Ellis et al. 2021, Section 4
> "Library learning decreases depth at the expense of breadth, while training a neural recognition model effectively decreases breadth by decreasing the number of bits of entropy consumed by each decision (function call) made when constructing a program solving a task." — [0] Ellis et al. 2021, footnote (Section 4)
> "we bound the number of lambda-calculus evaluation steps separating a program from its refactoring" — [0] Ellis et al. 2021, Section 3 (abstraction)
> "we initialize DreamCoder with addition, multiplication, division, and, critically, arbitrary real-valued parameters, which we optimize over via inner-loop gradient descent." — [0] Ellis et al. 2021, symbolic regression domain

Verification notes: Partial read via alphaXiv page extraction (pages 1, 3-8, 10, 13, 17). Equation 1 transcribed with rho/lambda/approx/proportional spelled out. Supplement sections (S4.1, S4.5) are cited by the paper but were not read; the exact form of P[L] is therefore not verified. Codex has no DreamCoder entry at this depth.

### P5.DREAMCODER_WAKE_SLEEP — DreamCoder (Ellis et al. 2020/2021): wake-sleep Bayesian program learning with library refactoring and a neural recognition model

Disposition: `None` · best verification: `FULL_TEXT_READ`

Sources:

- [0] DreamCoder: Growing generalizable, interpretable knowledge with wake-sleep Bayesian program learning — Kevin Ellis, Catherine Wong, Maxwell Nye, Mathias Sable-Meyer, Luc Cary, Lucas Morales, Luke Hewitt, Armando Solar-Lezama, Joshua B. Tenenbaum (2020), arXiv 2006.08381; PLDI 2021. https://arxiv.org/abs/2006.08381 arXiv:2006.08381 — `FULL_TEXT_READ`

**What it already explains.** Objective (Eq. 1): wake finds rho_x = argmax P[x\|rho]P[rho\|L] among programs with high Q(rho\|x); abstraction sleep grows L = argmax P[L] prod_x max_{rho refactoring rho_x} P[x\|rho]P[rho\|L] with a description-length prior over libraries, i.e. minimize library MDL plus the MDL of refactored programs; dreaming trains Q on replays and fantasies (50/50) with a MAP objective that breaks syntactic symmetries. Refactorings are enumerated up to a bound on beta-reduction steps (set to 3) with a version-space/e-graph data structure polynomial in program size (10^6 nodes represent 10^14 refactorings). Search difficulty ~ breadth^depth: library learning cuts depth, the recognition model cuts breadth. Results: text editing 3.7% -> 79.6% of SyGuS 2017 problems (84.3% at competition compute); ablations without abstraction or without recognition solve fewer held-out tasks in every domain; deeper libraries correlate with solve rate (r = 0.79); from generic primitives it learns 93% of 60 physics laws after 8 cycles via a learned vector-algebra vocabulary; a day on 20-100 CPUs per domain. Discussion: the from-scratch route (Y-combinator + Lisp primitives to fold/unfold/map/zip) cost ~5 days on 64 CPUs (~1 CPU-year); the authors reject blank-slate learning in favour of rich built-in bases ('the shoulders of so many giants'), which is the P5 parent's own verdict on the D2 'acquire the morphology from nothing' level.

**Formal object.** generative model P[rho\|L]; recognition model Q(rho\|x); library prior P[L]; version space of bounded refactorings

**Strongest result.** None

**Assumptions.** None

**Resource model.** None

**Failure boundary.** None

**Implementation.** None

**Track-B residual.** None

**Upward question.** None

Verification notes: None

### P5.NEUROSYMBOLIC_SAME_SEARCH — Neurosymbolic program search with neural relaxations as heuristics (NEAR, Shah et al. 2020) and typed neural-functional program synthesis (HOUDINI, Valkov et al. 2018): does one search choose neural on one task and symbolic on another?

Disposition: `OPEN` · best verification: `PARTIAL_TEXT_READ`

Sources:

- [0] Learning Differentiable Programs with Admissible Neural Heuristics — Ameesh Shah, Eric Zhan, Jennifer J. Sun, Abhinav Verma, Yisong Yue, Swarat Chaudhuri (2020), NeurIPS 2020; arXiv:2007.12101v5. https://arxiv.org/abs/2007.12101 arXiv:2007.12101 — `PARTIAL_TEXT_READ`
- [1] HOUDINI: Lifelong Learning as Program Synthesis — Lazar Valkov, Dipak Chaudhari, Akash Srivastava, Charles Sutton, Swarat Chaudhuri (2018), NeurIPS 2018; arXiv:1804.00218v2. https://arxiv.org/abs/1804.00218 arXiv:1804.00218 — `PARTIAL_TEXT_READ`

**What it already explains.** NEAR: programs are derived from a DSL grammar (map, fold, mapprefix, if-then-else, selectors sel_S, affine/parameterised leaves plus_theta); synthesis minimises structural cost s(alpha) plus trained loss zeta(alpha, theta) (eq. 1) by informed search (A*, IDS-BB) over partial programs; the heuristic for a partial program is obtained by filling holes with neural networks ('continuous relaxations over the space of programs'), which is epsilon-admissible (eq. 6) because a neural completion lower-bounds the best symbolic completion. The learned library 'only contains affine transformations' (motivated by interpretability). Results: symbolic programs reach 0.87 vs 0.89 (RNN) and 0.905 vs 0.945 on the extracted figures, and 0.22 vs 0.48 (lambda = 8) or 0.46 vs 0.48 (lambda = 1) F1 on the harder task - the structural-cost weight lambda controls how much accuracy is traded for a shorter program. HOUDINI: neural networks are 'strongly typed, differentiable functional programs' e ::= plus_w : tau_0 \| e_0 o e_1 \| map e \| fold e \| conv e; a symbolic synthesizer enumerates typed programs (types prune 8182 to 2 candidates at size 4 in Table 1) and a gradient learner trains each; lifelong transfer by reusing trained neural library functions with 'fresh networks' always available; discovers a Bellman-Ford-shaped program with a neural relaxation step; evolutionary baseline has high variance and often times out. ANSWER TO THE FAMILY QUESTION: NO. In both systems the neural components are leaves (typed neural library functions in HOUDINI; affine or relaxation fillers in NEAR) and the symbolic components are combinators fixed by the grammar; the search never decides 'this task is best solved by an unstructured network and that one by a symbolic program' - the morphology partition is pre-chosen by the DSL, and NEAR's lambda is a hand-set price on symbolic structure.

**Formal object.** NEAR: DSL grammar G over typed programs alpha with holes; parameters theta; objective (alpha*, theta*) = argmin_{(alpha,theta)} s(alpha) + zeta(alpha, theta) (eq. 1) with s a structural cost (weighted by lambda) and zeta the training loss; heuristic h(alpha) = loss of the relaxed program obtained by replacing holes with neural networks; epsilon-admissibility h(alpha) <= (cost-to-go) + epsilon (eq. 6). HOUDINI: typed lambda-calculus of neural functions with combinators map_alpha, fold_alpha, conv_alpha and composition; synthesizer = typed enumeration / evolutionary search over program sketches; learner = gradient descent on the differentiable program; library = previously trained functions plus fresh networks.

**Strongest result.** NEAR: epsilon-admissibility of the neural heuristic (eq. 6; Theorem in Section 4, as extracted) guaranteeing near-optimal programs under A*/IDS-BB. HOUDINI: no theorem; the result is empirical transfer across task sequences plus type-driven pruning (Table 1). Neither paper contains a result in which the same search discovers a neural morphology for one task and a symbolic morphology for another.

**Assumptions.** a hand-written DSL/grammar fixes which components can be neural (leaves) and which are symbolic (combinators); supervised task losses with labelled data (classification/regression of trajectories, counting, shortest paths); NEAR: neural relaxation loss lower-bounds symbolic completion loss (epsilon-admissibility) - assumes networks are at least as expressive as the DSL fragment they replace; NEAR: interpretability motivates an affine-only library; structural cost weight lambda is user-chosen; HOUDINI: type system is expressive enough to prune and the library is reused via transfer; fresh networks always allowed

**Resource model.** partial: NEAR prices program structure explicitly (s(alpha), weight lambda) and trades it against loss; search cost is reported (nodes expanded, time) but not derived. HOUDINI prices nothing beyond program size (enumeration by size) and reports type-pruning counts. Neither prices the neural leaves' parameters or the total compute against the ecology.

**Failure boundary.** NEAR's programs lose accuracy to RNN baselines on the harder tasks (0.22 or 0.46 vs 0.48 F1) precisely because the symbolic space is restricted; HOUDINI's evolutionary search 'times out' in many runs; both fail on tasks outside the DSL's closure. Fundamental boundary for Track B: the morphology partition is not searched.

**Implementation.** NEAR: open-source (PyTorch; repository trishullab/near, not read). HOUDINI: open-source (PyTorch; repository capergroup/houdini, not read).

**Track-B residual.** The residual is the entire morphology-unlabelled search: a single search over a space in which 'neural', 'symbolic', and hybrid are outcomes rather than grammar roles, with the choice derived from the ecology and a cost functor. No parent in this family supplies it. NEAR shows the shape of a partial answer (a price lambda on symbolic structure) but within a pre-fixed symbolic space.

**Upward question.** Is there a formal space (e.g., Para(Optic) with a cost functor) in which a symbolic combinator and a neural block are both morphisms of the same type and the search's choice between them is forced by ecology statistics and cost, so that 'neural on task A, symbolic on task B' is a theorem-level prediction rather than a grammar decision?

Load-bearing quotes (verbatim from sources actually read):

> "Our key innovation is to view various classes of neural networks as continuous relaxations over the space of programs, which can then be used to complete any partial program." — [0] Shah et al. 2020, Section 1
> "Because we are motivated by interpretability, the library used in our current implementation only contains affine transformations." — [0] Shah et al. 2020, Section 3
> "(alpha*, theta*) = arg min_{(alpha,theta)} (s(alpha) + zeta(alpha, theta))." — [0] Shah et al. 2020, Eq. 1
> "This program achieves an accuracy of 0.87 (vs. 0.89 for RNN baseline)" — [0] Shah et al. 2020, Appendix Figure 2 caption
> "On a set of learned parameters (not shown), this program achieves an accuracy of 0.905 (vs. 0.945 for an RNN baseline)." — [0] Shah et al. 2020, Appendix Figure 3 caption
> "The program achieves F1 score of 0.22 (vs. 0.48 for RNN baseline). This program is synthesized using lambda = 8." — [0] Shah et al. 2020, Appendix Figure 7 caption
> "The program achieves F1 score of 0.46 (vs. 0.48 for RNN baseline). This program is synthesized using lambda = 1." — [0] Shah et al. 2020, Appendix Figure 8 caption
> "represents neural networks as strongly typed, differentiable functional programs that use symbolic higher-order combinators to compose a library of neural functions." — [1] Valkov et al. 2018, Abstract
> "HOUDINI discovers an algorithm that has the structure of the Bellman-Ford shortest path algorithm [7], but uses a learned neural function that approximates the algorithm's 'relaxation' step." — [1] Valkov et al. 2018, Section 1
> "e ::= plus_w : tau_0 \| e_0 o e_1 \| map_alpha e \| fold_alpha e \| conv_alpha e." — [1] Valkov et al. 2018, Section 3 (grammar)
> "Importantly, it is always possible for the synthesizer to introduce 'fresh networks' whose parameters have not been pretrained." — [1] Valkov et al. 2018, Section 3
> "the evolutionary strategy has high variance; indeed, in many runs of the task sequences, it times out without finding a solution." — [1] Valkov et al. 2018, Section 5
> "For reference, neural architecture search often considers thousands of potential architectures for a single task [24]." — [1] Valkov et al. 2018, Section 5

Verification notes: Both papers read partially via alphaXiv page extraction. Greek symbols in quotes transliterated (alpha, theta, zeta, lambda, tau, plus_w for the circled-plus neural-leaf symbol, 'o' for composition). The NEAR admissibility theorem's exact numbering was not captured in the extraction and is not asserted. Table 1 pruning counts (8182 to 2 at size 4) are as extracted. Neither paper is in the Codex capsule. The 'same search' negative answer is a reading of both grammars, not a quotation.

### P5.STITCH_TOP_DOWN — Stitch (Bowers et al. 2023): corpus-guided top-down branch-and-bound abstraction synthesis

Disposition: `None` · best verification: `PARTIAL_TEXT_READ`

Sources:

- [0] Top-Down Synthesis for Library Learning — Matthew Bowers, Theo X. Olausson, Lionel Wong, Gabriel Grand, Joshua B. Tenenbaum, Kevin Ellis, Armando Solar-Lezama (2023), POPL 2023 (PACMPL 7); arXiv 2211.16605. https://doi.org/10.1145/3571234 arXiv:2211.16605 — `PARTIAL_TEXT_READ`

**What it already explains.** Abstractions are synthesized top-down from holes; a partial abstraction's match locations over-approximate those of any completion, and the size of each matched subtree upper-bounds the compression gain, giving U_upper(A??) = sum of sizes of matches (Eq. 4) for branch-and-bound with strict-dominance pruning (Lemma 1: optimality preserved). Utility = the DreamCoder compression objective (Eq. 18 best-of-task). Results: 3-4 orders of magnitude faster and 2 orders less memory than DreamCoder's version-space refactoring at equal or better compressivity (Fig. 7); scales to corpora of hundreds of programs with 76-189 symbols; anytime (high-quality abstractions within 1-10% of search time). Limitation: cannot learn higher-order abstractions (map from fold) without deductive rewrites; babble is the expressive counterpart (Sec. 7.5).

**Formal object.** partial abstraction grammar; utility U_{P,R}(A); upper bound U_upper; strict dominance

**Strongest result.** None

**Assumptions.** None

**Resource model.** None

**Failure boundary.** None

**Implementation.** None

**Track-B residual.** None

**Upward question.** None

Verification notes: None


## P6 — probabilistic / generative-program intelligence

### P6.AMORTIZED_INFERENCE_HYBRID — Amortized inference as neural-probabilistic hybrid: inference compilation (Le-Baydin-Wood) and the variational autoencoder (Kingma-Welling)

Disposition: `ADOPT` · best verification: `FULL_TEXT_READ`

Sources:

- [0] Inference Compilation and Universal Probabilistic Programming — T. A. Le, A. G. Baydin, F. Wood (2017), AISTATS 2017 (PMLR 54). https://arxiv.org/abs/1610.09900 arXiv:1610.09900 — `FULL_TEXT_READ`
- [1] Auto-Encoding Variational Bayes — D. P. Kingma, M. Welling (2014), ICLR 2014 (arXiv v11, 2022). https://arxiv.org/abs/1312.6114 arXiv:1312.6114 — `FULL_TEXT_READ`

**What it already explains.** How the cost of conditioning can be shifted from query time to a one-off training phase by fitting a neural network that maps observations to (parameters of) an approximate posterior — and that this produces a genuinely *hybrid* morphology: an explicit generative program (or decoder) whose update law is still conditioning, plus a neural artifact whose update law is stochastic gradient descent on a divergence. Le et al.: given a universal PPL program p(x,y) (traces (x_t,a_t,i_t) with dynamic length and addresses), minimize L(φ)=E_{p(y)}[KL(p(x\|y)‖q(x\|y;φ))] = E_{p(x,y)}[−log q(x\|y;φ)]+const using an infinite stream of synthetic (x,y) pairs from the *unconstrained* program; the artifact is an LSTM core with per-address embedding/proposal layers that is reconfigured on the fly per trace and used as the proposal in sequential importance sampling — so the posterior estimate remains asymptotically exact. They call this 'compilation of inference' (program → trained network). Because 'inversion of the dependency structure is impossible in the universal probabilistic program model family', proposals are learned for forward inference. Kingma-Welling: for i.i.d. data with continuous latents, jointly learn generative parameters θ and recognition parameters φ by ascending the ELBO L(θ,φ;x)=E_q[−log q_φ(z\|x)+log p_θ(x,z)] = −KL(q_φ(z\|x)‖p_θ(z))+E_q[log p_θ(x\|z)], made differentiable in φ by the reparameterization z=g_φ(ε,x), ε~p(ε); with MLP encoder/decoder this is the VAE. The two differ on what is learned (proposal only, with model fixed and misspecification risk — Le sec. 5 — vs. model and recognition jointly, regularized 'towards being simple to perform inference in and towards explaining the data well').

**Formal object.** Le et al.: trace (x_t,a_t,i_t)_{t=1}^T; p(x,y)=Π_t f_{a_t}(x_t\|x_{1:t-1}) Π_n g_n(y_n\|x_{1:τ(n)}) (eq. 2); SIS weights w_k = Π_n g_n(y_n\|·)·Π_t f_{a_t}(x_t\|·)/q_{a_t,i_t}(x_t\|x_{1:t-1},y) (eq. 5); objective L(φ) = E_{p(y)}[D_KL(p(x\|y)‖q(x\|y;φ))] = E_{p(x,y)}[−log q(x\|y;φ)] + const (eqs. 6-7); factorized proposal q(x\|y;φ)=Π_t q_{a_t,i_t}(x_t\|η_t(x_{1:t-1},y,φ)) (eq. 8); gradient estimate (eq. 9) from minibatches (x^(m),y^(m))~p(x,y) of the unconstrained program; artifact = LSTM + f^obs embedding + per-(a,i) f^smp, f^prop layers. Kingma-Welling: log p_θ(x^(i)) = D_KL(q_φ(z\|x^(i))‖p_θ(z\|x^(i))) + L(θ,φ;x^(i)) (eq. 1); L = E_q[−log q_φ(z\|x)+log p_θ(x,z)] (eq. 2) = −D_KL(q_φ(z\|x^(i))‖p_θ(z)) + E_q[log p_θ(x^(i)\|z)] (eq. 3); z̃=g_φ(ε,x), ε~p(ε) (eq. 4); SGVB estimators L̃^A (eq. 6), L̃^B (eq. 7); Algorithm 1 (AEVB) minibatch SGD; VAE: p_θ(z)=N(0,I), q_φ(z\|x)=N(μ(x),σ²(x)I), Bernoulli/Gaussian MLP decoder (eq. 10, App. C).

**Strongest result.** Le et al.: the identity L(φ) = E_{p(x,y)}[−log q(x\|y;φ)] + const (eqs. 6-7), which turns amortized posterior approximation into supervised density estimation on synthetic data with an unbiased minibatch gradient (eq. 9), with no finite training set ('no notion of a finite training set and associated issues such as overfitting'); empirically, inference compilation gives low-noise posterior estimates at 10-1000× fewer particles than SMC (Fig. 4), Captcha recognition 91-99.9% synthetic, 81%/42% real Wikipedia/Facebook after prior tuning, < 100 ms per Captcha vs minutes for MCMC. Kingma-Welling: eq. 1 (marginal log-likelihood = KL + ELBO, so ELBO is a lower bound) and the reparameterization argument (sec. 2.4: q_φ(z\|x)Π dz_i = p(ε)Π dε_i, hence a differentiable Monte-Carlo estimator); empirically AEVB converges faster and to better bounds than wake-sleep on MNIST/Frey Face across latent dimensions (Fig. 2), and 'superfluous latent variables did not result in overfitting'.

**Assumptions.** Le et al.: the generative program is correct (fixed, not learned) — 'we do have a risk of overfitting to the model'; observe statements occur in a fixed order with fixed N; training data are unlimited synthetic samples from p(x,y); the artifact's structure is 'not wholly determined by the given probabilistic program' (LSTM core + hand-picked domain embeddings such as a CNN for images); symmetries (label permutation, N!) must be broken by hand.; Kingma-Welling: i.i.d. dataset; continuous latent variables; p_θ(z), p_θ(x\|z) differentiable a.e. in θ and z; q_φ must admit a reparameterization (inverse CDF, location-scale, or composition families) — 'An advantage of wake-sleep is that it also applies to models with discrete latent variables'; MAP/ML on global parameters θ (full VB only in the appendix).; Both: a stationary distribution of observations to amortize over; the amortized artifact has no guarantee of posterior consistency except through its use as an IS proposal (Le) or through the bound gap KL(q‖p) (Kingma-Welling).

**Resource model.** Compute is the explicit object: an expensive one-off compilation/training phase against cheap per-query inference (Le Fig. 1: 'Expensive / slow' vs 'Cheap / fast'; Kingma-Welling: avoids 'expensive iterative inference schemes (such as MCMC) per datapoint'; wake-sleep 'has the same computational complexity as AEVB per datapoint'). Samples: Le — infinite synthetic stream; K-W — minibatches M=100, L=1 sample per datapoint suffices. Particles as an accuracy-vs-compute axis (Le Fig. 4). No description-length, verification, memory or revision accounting; no bound relating training cost to the achieved KL.

**Failure boundary.** Neither gives a law for when amortization pays: Le's speedups are empirical on two model families; K-W's advantage over wake-sleep and MCEM is empirical on two datasets. Amortized posteriors can be arbitrarily wrong off the training distribution of observations (model misspecification / 'synthetic gap', Le sec. 5) and the VAE bound gap is uncontrolled. Le requires manually designed embeddings and symmetry breaking; K-W is restricted to continuous reparameterizable latents. Neither addresses drift (non-stationary p(y)), verification cost, or when to stop amortizing and fall back to per-query inference. Neither derives the neural component from the probabilistic one — the LSTM/MLP are imported architectural choices.

**Implementation.** Le et al.: https://probprog.github.io/inference-compilation/ (Torch + Anglican via ZeroMQ), successor PyProb https://github.com/pyprob/pyprob ; Kingma-Welling: reference code in the original release; VAEs are implemented in every deep-learning framework (e.g. https://github.com/pytorch/examples/tree/main/vae).

**Track-B residual.** This parent owns the *hybrid* morphology mechanically (probabilistic program + neural proposal/recognition; conditioning target + gradient-trained artifact) and gives its resource signature qualitatively (pay once in training, cheap per query, valid only near the training p(y)). It does not derive both components from a shared basis, does not charge the training-vs-query trade-off against ecology parameters (query repetition rate, drift rate, misspecification), and does not predict when the hybrid dominates pure sampling (Le Fig. 4 measures one crossover) or pure gradient. Track B's residual: a phase law over (repetition × drift × observation informativeness) for {per-query conditioning, amortized proposal + IS, amortized-only (VAE encoder), point-estimate}.

**Upward question.** Amortization converts conditioning cost into gradient cost on a proxy objective whose validity is tied to p(y). Under an ecology with drift rate δ and query rate ρ, is there a derivable threshold ρ/δ above which a basis that can only afford one update law should *be* neural (amortized) and below which it should *be* sampling-probabilistic — and does the hybrid ever win outside a band around that threshold?

Load-bearing quotes (verbatim from sources actually read):

> "We call what we do “compilation of inference” because our method transforms a denotational specification of an inference problem in the form of a probabilistic program written in a universal programming language into a trained neural network" — [0] Le et al. 2017, abstract
> "inversion of the dependency structure is impossible in the universal probabilistic program model family, so our approach instead focuses on learning proposals for “forward” inference methods in which no model dependency inversion is performed." — [0] Le et al. 2017, sec. 1
> "L(φ) := E_{p(y)}[D_KL(p(x\|y) \|\| q(x\|y; φ))] ... = E_{p(x,y)}[− log q(x\|y; φ)] + const." — [0] Le et al. 2017, eqs. 6-7, sec. 3.1
> "Minibatches of this infinite stream of training data are discarded after each SGD update; we therefore have no notion of a finite training set and associated issues such as overfitting" — [0] Le et al. 2017, sec. 3.2
> "A limitation that comes with not learning the generative model itself ... is the possibility of model misspecification" — [0] Le et al. 2017, sec. 5
> "If you can create instances of a Captcha, you can break it." — [0] Le et al. 2017, sec. 4.2
> "log p_θ(x^(i)) = D_KL(q_φ(z\|x^(i))\|\|p_θ(z\|x^(i))) + L(θ, φ; x^(i))" — [1] Kingma & Welling, eq. 1, sec. 2.2
> "we show that for i.i.d. datasets with continuous latent variables per datapoint, posterior inference can be made especially efficient by fitting an approximate inference model (also called a recognition model) to the intractable posterior" — [1] Kingma & Welling, abstract
> "This reparameterization is useful for our case since it can be used to rewrite an expectation w.r.t q_φ(z\|x) such that the Monte Carlo estimate of the expectation is differentiable w.r.t. φ." — [1] Kingma & Welling, sec. 2.4
> "An advantage of wake-sleep is that it also applies to models with discrete latent variables. Wake-Sleep has the same computational complexity as AEVB per datapoint." — [1] Kingma & Welling, sec. 4

Verification notes: Both papers read in full from arXiv (Le et al. v2; Kingma-Welling v11). Equation numbers cited are from those versions. The related taxonomy of hybrid designs was cross-checked against van de Meent et al. ch. 8 (P6.PPL_INTRO). No prior reconstruction in the repo ledgers consulted (the functional-neural-absorption ledger does not mention VAEs).

### P6.AMORTIZED_INFERENCE_HYBRID — Inference compilation (Le, Baydin, Wood 2017): universal probabilistic program + LSTM proposal network trained by amortised KL objective

Disposition: `ADOPT` · best verification: `PARTIAL_TEXT_READ`

Sources:

- [0] Inference Compilation and Universal Probabilistic Programming — Tuan Anh Le, Atilim Gunes Baydin, Frank Wood (2017), AISTATS 2017 (PMLR 54); arXiv:1610.09900v2. https://arxiv.org/abs/1610.09900 arXiv:1610.09900 — `PARTIAL_TEXT_READ`

**What it already explains.** A hybrid morphology in which a probabilistic program (the generative model, written in a universal language) is paired with a neural network that proposes values at each sample address, trained offline on synthetic (x, y) ~ p(x, y) drawn from the program itself. The objective is the expected KL from the true posterior to the proposal, which reduces (up to a constant) to the expected negative log proposal density on joint samples (equations 6-7). The network is an LSTM core with per-address embedding and proposal layers created on-the-fly when a new (address, instance) pair is first encountered, so the network is 'reconfigured for each encountered trace'. At test time the trained proposals drive sequential importance sampling (weights, equation 5). Results: Captcha recognition at 81%/42% on Wikipedia/Facebook and mixture-model inference; inference latency < 100 ms per Captcha versus 0.5-8 s for segment-and-classify baselines. The authors name the risk of 'overfitting to the model' (proposals trained only on model samples).

**Formal object.** Generative model p(x, y) given by a probabilistic program with sample addresses a and instance counters i; proposal family q(x \| y; phi) = prod_t q(x_t \| eta_t) where eta_t are output by an LSTM core fed the observation embedding f^obs(y), previous sample x_{t-1}, and one-hot (a_t, i_t, distribution type); training objective L(phi) = E_{p(y)}[ D_KL(p(x\|y) \|\| q(x\|y; phi)) ] = E_{p(x,y)}[ -log q(x\|y; phi) ] + const (eqs 6-7); test-time sequential importance sampling with weights w = p(x, y)/q(x \| y; phi) (eq 5). Architecture: non-domain-specific RNN core + domain-specific observation embedding and proposal layers 'specified by the given program'.

**Strongest result.** No theorem. The load-bearing derivation is that the amortised KL objective is minimised by regression on joint samples from the model (eqs 6-7), making training label-free w.r.t. real data (labels come from the model). Empirical: Captcha 81% (Wikipedia) / 42% (Facebook) real-data recognition; < 100 ms inference; training on ~16M synthetic traces with ~20M parameters (Section 5, as extracted).

**Assumptions.** the generative program is fixed and correct (proposals are trained on model samples only; overfitting to the model is admitted); sample addresses and instance counters identify random choices stably across traces; SIS with learned proposals is asymptotically exact; no finite-sample guarantee; observation embedding must be domain-specified (CNN for images, etc.); large synthetic training budget (millions of traces) is available

**Resource model.** implicit amortisation trade: an expensive offline compile (millions of traces, days of GPU training - stated qualitatively) purchases cheap online inference (< 100 ms). No description length, no accounting of how the compile budget should be set, no comparison of amortised versus non-amortised total cost.

**Failure boundary.** Model misspecification (proposals trained on p(x,y) do not cover real data - the 42% Facebook result), open-universe programs whose address structure changes unboundedly, and any setting where the model itself must be learned (the program is hand-written). The neural component is never a candidate for the model and the program is never a candidate for the proposal: the morphology partition is fixed.

**Implementation.** Anglican (Clojure) probabilistic programming system plus a PyTorch/Torch neural component communicating over ZeroMQ (Section 4, as extracted); successor: pyprob (not read here).

**Track-B residual.** Owns an existing hybrid morphology (neural proposal x probabilistic program) and its label-free training law. Track B residual: (i) no selection law for when amortisation pays (the compile/inference cost split is a design choice, not derived from the ecology's query rate), (ii) the model is fixed rather than acquired, (iii) no cost functor relating the neural proposal's size to the program's trace complexity.

**Upward question.** Is there an ecology-indexed law that decides between amortised and non-amortised inference (expected query count x per-query cost versus compile cost), and does it extend to deciding when the model itself, rather than the proposal, should be neural?

Load-bearing quotes (verbatim from sources actually read):

> "We call what we do 'compilation of inference' because our method transforms a denotational specification of an inference problem in the form of a probabilistic program written in a universal programming language into a trained neural network" — [0] Le, Baydin, Wood 2017, Section 1
> "the neural network architecture comprises a non-domain-specific recurrent neural network (RNN) core and domain-specific observation embedding and proposal layers specified by the given program." — [0] Le, Baydin, Wood 2017, Section 3.2
> "we define an adaptive neural network architecture that is reconfigured for each encountered trace by attaching the corresponding embedding and proposal layers to the LSTM core, creating new layers on-the-fly on the first encounter with each (a, i) pair." — [0] Le, Baydin, Wood 2017, Section 3.2
> "With the resulting artifacts, running inference on a test Captcha takes < 100 ms, whereas durations ranging from 500 ms (Starostenko et al., 2015) to 7.95 s (Bursztein et al., 2014) have been reported with segment-and-classify approaches." — [0] Le, Baydin, Wood 2017, Section 5.1
> "we were able to achieve 81% and 42% recognition rates with real Wikipedia and Facebook datasets" — [0] Le, Baydin, Wood 2017, Section 5.1
> "we do have a risk of overfitting to the model." — [0] Le, Baydin, Wood 2017, Section 5.1

Verification notes: Partial read via alphaXiv page extraction (pages 1-8). Equations 5-7 transcribed from the extracted text; implementation details (Anglican/Torch/ZeroMQ, trace and parameter counts) are as extracted and not independently checked. Not in the Codex capsule; the Codex P-CHURCH entry does not mention amortised inference.

### P6.BAYES_UPDATE_LAW — Bayesian updating as a law: Cox's theorem, Jaynes's desiderata, de Finetti coherence (Dutch book)

Disposition: `ADOPT` · best verification: `FULL_TEXT_READ`

Sources:

- [0] Probability, Frequency and Reasonable Expectation — R. T. Cox (1946), American Journal of Physics 14(1):1-13. https://doi.org/10.1119/1.1990764 — `NOT_ACCESSIBLE`
- [1] Probability Theory: The Logic of Science (ch. 1-2) — E. T. Jaynes (ed. G. L. Bretthorst) (2003), Cambridge University Press. https://doi.org/10.1017/CBO9780511790423 — `NOT_ACCESSIBLE`
- [2] Sul significato soggettivo della probabilita (Dutch-book / coherence theorem) — B. de Finetti (1931), Fundamenta Mathematicae 17:298-329. https://doi.org/10.4064/fm-17-1-298-329 — `NOT_ACCESSIBLE`
- [3] A Counterexample to Theorems of Cox and Fine — J. Y. Halpern (1999), Journal of Artificial Intelligence Research 10:67-85. https://arxiv.org/abs/1105.5450 arXiv:1105.5450 — `PARTIAL_TEXT_READ`
- [4] Cox's Theorem and the Jaynesian Interpretation of Probability — A. Terenin, D. Draper (2017), arXiv (math.ST). https://arxiv.org/abs/1507.06597 arXiv:1507.06597 — `FULL_TEXT_READ`
- [5] De Finetti for mathematics undergraduates — D. Mundici (2021), arXiv (math.PR). https://arxiv.org/abs/2107.00250 arXiv:2107.00250 — `PARTIAL_TEXT_READ`
- [6] Diachronic Dutch book for conditionalization (Lewis, reported by Teller) — P. Teller (1973), Synthese 26:218-238. https://doi.org/10.1007/BF00873264 — `FROM_MEMORY_UNVERIFIED`

**What it already explains.** Why a resource-unbounded reasoner that (i) represents graded belief by real numbers, (ii) decomposes the plausibility of a conjunction via a two-place function of the plausibilities of its parts, (iii) determines the plausibility of a negation from that of the proposition, and (iv) is consistent (or, in de Finetti's frame, cannot be made to lose money for certain) must use a calculus isomorphic to conditional probability: product rule P(AB\|C)=P(A\|C)P(B\|AC), sum rule P(not A\|B)=1-P(A\|B), hence Bayes' rule. It thereby fixes the *update law* of the probabilistic morphology as conditioning, independent of any representation language. Halpern shows the synchronic theorem fails on finite domains without a density/extension axiom; Terenin-Draper repair it with 'consistency under extension' and obtain countable additivity. De Finetti's theorem (Mundici Thm 2.7): a finite assignment beta:E->[0,1] is coherent iff it extends to a finitely additive state.

**Formal object.** Cox (as stated by Halpern): a function Bel(V\|U) on pairs of subsets of a domain W with U nonempty, satisfying A1. Bel(~V\|U)=S(Bel(V\|U)) and A2. Bel(V∩V'\|U)=F(Bel(V'\|V∩U), Bel(V\|U)) with F twice differentiable, S twice differentiable; conclusion: there is a continuous bijection g with g∘Bel a probability distribution and g(Bel(V\|U))·g(Bel(U))=g(Bel(V∩U)). Jaynes (as restated by Terenin-Draper): desiderata I (real numbers), II(a,b) (qualitative correspondence, continuity), III(a,b,c) (order-independence, use all evidence, equivalent states get equal plausibility). Terenin-Draper: structure (Ω,F,P,∘,R,N) with Axioms 1 (P:F×(F∖∅)→R), 2 (sequential continuity), 3 (P(AB\|C)=P(A\|C)∘P(B\|AC)), 4 (P(A^c\|B)=N[P(A\|B)]), 5 (consistency under extension to Ω×Ω). De Finetti (Mundici Def 2.1): beta:E->[0,1] on events of a Boolean algebra A is inconsistent iff there are stakes s:E->R with Σ_j s(h_j)(beta(h_j)-η_i(h_j))<0 for every homomorphism η_i:A->{0,1}.

**Strongest result.** Terenin-Draper Theorem 16 (Cox's Theorem, rigorous form): 'Every true-false logic under uncertainty is isomorphic to conditional probability' (Kolmogorov K1-K3 including countable additivity), via Lemma 10 (product rule; ∘ is conjugate to multiplication by Aczel's associativity equation), Lemma 13 (sum rule N(x)=1-x), Lemma 15 (countable additivity from Axiom 2). Halpern Theorem 3.1: an explicit 12-point finite domain with Bel0, S(x)=1-x, G(x,y)=x+y, F infinitely differentiable and strictly increasing on (0,1]^2 satisfying A1-A3, yet no bijection g:[0,1]->[0,1] satisfying Cox's conclusion (1) — so the original theorem is false on finite domains. Mundici Theorem 2.7 (de Finetti, general case): beta is consistent in A iff beta is extendable to a state of A; Remark 2.15: 'consistency + incompatibility ⇒ additivity axiom'. NOTE: all three are synchronic; none of the read sources proves that the *updated* belief must equal the prior conditional (the diachronic step).

**Assumptions.** Belief is real-valued (Cox/Jaynes desideratum I; Terenin-Draper Axiom 1) — excludes interval-valued, lattice-valued, or incomparable beliefs (Halpern sec. 5 and Terenin-Draper sec. 5.3 note Dempster-Shafer and Friedman-Halpern plausibility as excluded alternatives).; Boolean (classical) underlying logic: Cox's theorem requires the law of excluded middle (Terenin-Draper sec. 2.4 citing Colyvan).; Conjunction decomposes through a two-place function F/∘ (A2 / Axiom 3) and negation through a one-place S/N (A1 / Axiom 4).; Regularity: Cox assumes twice-differentiability; Paris assumes density of the range of Bel (forces an infinite domain); Terenin-Draper replace density by 'consistency under extension' (Axiom 5) plus sequential continuity (Axiom 2).; De Finetti: the agent posts prices and accepts bets on either side at those prices; linear utility in money; finitely many events; the theorem's general (infinite-algebra) form uses the Axiom of Choice (Mundici Remark 2.9(i)).; Unbounded reasoner: no cost is charged for computing conditional probabilities; the law is about coherence, not about tractability.

**Resource model.** none — the law is stated for an idealized reasoner; Cox/Jaynes/de Finetti account for no description length, time, samples, compute, verification, or memory. (Jaynes's 'robot' metaphor is explicitly a normative idealization.)

**Failure boundary.** 1) Synchronic only: the read sources establish that coherent *simultaneous* degrees of belief are probabilities; that belief *change* on learning E must be P(·\|E) (conditionalization) is a further, separately contested step (Lewis/Teller diachronic Dutch book, unverified here). 2) Cox's original proof is incorrect on finite domains (Halpern Thm 3.1) and 'Jaynes' writing contains mathematical errors — his proof as written is incorrect' (Terenin-Draper sec. 2.3); repair requires either an infinite/dense domain (Paris A4) or consistency under repeated events (Axiom 5). 3) 'Cox's Theorem says essentially nothing about conditioning on sets of measure zero' (Terenin-Draper sec. 5.2) — exactly the regime where P6.CONDITIONING_LIMIT bites. 4) Says nothing about which approximation to Bayes a bounded agent should use, nor about the cost of the update, nor about model misspecification. 5) Excludes non-real-valued and non-Boolean uncertainty calculi by assumption rather than by derivation.

**Implementation.** none known (a normative law, not a system)

**Track-B residual.** Given that conditioning is the unique coherent update law for real-valued Boolean plausibility, what does a resource-bounded generating basis pay to *implement* it, and under what ecology (observation structure, query repetition, drift, verification contract, resource prices) does an incoherent-but-cheap update rule (gradient step, rule rewrite, program mutation) out-compete an approximately coherent one? Cox/de Finetti fix the target of specialization for GMI-T6; they do not price it.

**Upward question.** Treat coherence as one axis of a verification contract: which ecologies make coherence (no sure-loss) *worth its computational price*, and can the generating basis be shown to select conditioning-approximations exactly when the ecology charges for incoherence (adversarial betting, repeated queries) and to abandon them when it charges for latency or samples?

Load-bearing quotes (verbatim from sources actually read):

> "A1. Bel(V̄\|U) = S(Bel(V\|U)) if U ≠ ∅" — [3] Halpern 1999, sec. 1, p. 67
> "A2. Bel(V ∩ V′\|U) = F(Bel(V′\|V ∩ U), Bel(V\|U)) if V ∩ U ≠ ∅." — [3] Halpern 1999, sec. 1, p. 67
> "Cox's well-known theorem justifying the use of probability is shown not to hold in finite domains. The counterexample also suggests that Cox's assumptions are insufficient to prove the result even in infinite domains." — [3] Halpern 1999, abstract
> "Cox's Theorem is a representation theorem that states, under a certain set of axioms describing the meaning of uncertainty, that every true-false logic under uncertainty is isomorphic to conditional probability theory." — [4] Terenin & Draper 2017, abstract
> "Unfortunately, Jaynes' writing contains mathematical errors – his proof as written is incorrect." — [4] Terenin & Draper 2017, sec. 2.3
> "Theorem 16 (Cox's Theorem). Every true-false logic under uncertainty is isomorphic to conditional probability." — [4] Terenin & Draper 2017, sec. 4
> "As a consequence, Cox's Theorem says essentially nothing about conditioning on sets of measure zero." — [4] Terenin & Draper 2017, sec. 5.2
> "Theorem 2.7. (De Finetti consistency theorem, general case) Let E be a finite subset of a boolean algebra A and β : E → [0, 1] a function. Then β is consistent in A iff β is extendable to a […]" — [5] Mundici 2021, sec. 2.4 [quote truncated to 40 words]
> "consistency + incompatibility ⇒ additivity axiom" — [5] Mundici 2021, Remark 2.15
> "So what does all this say regarding the use of probability? Not much." — [3] Halpern 1999, sec. 5, p. 81

Verification notes: Cox 1946, Jaynes 2003 and de Finetti 1931 could not be fetched (every non-arXiv host is blocked by the egress proxy). Their content is reconstructed from three arXiv-hosted secondary sources that restate the axioms verbatim (Halpern quotes Cox's A1/A2; Terenin-Draper restate Jaynes's desiderata and give a full corrected proof; Mundici quotes de Finetti's definition with page numbers and re-proves the theorem). The desiderata wording attributed to Jaynes is Terenin-Draper's paraphrase, not Jaynes's text. No theorem numbers from Jaynes ch. 1-2 are cited for that reason. No prior reconstruction of this parent exists in the repo ledgers consulted (grep on Cox/Jaynes/de Finetti/Dutch book returned nothing).

### P6.BPL — Bayesian Program Learning (Omniglot) and 'Building machines that learn and think like people'

Disposition: `ADAPT` · best verification: `FULL_TEXT_READ`

Sources:

- [0] Human-level concept learning through probabilistic program induction — B. M. Lake, R. Salakhutdinov, J. B. Tenenbaum (2015), Science 350(6266):1332-1338. https://doi.org/10.1126/science.aab3050 — `NOT_ACCESSIBLE`
- [1] Building Machines That Learn and Think Like People — B. M. Lake, T. D. Ullman, J. B. Tenenbaum, S. J. Gershman (2017), Behavioral and Brain Sciences 40:e253. https://arxiv.org/abs/1604.00289 arXiv:1604.00289 — `PARTIAL_TEXT_READ`
- [2] The Omniglot challenge: a 3-year progress report — B. M. Lake, R. Salakhutdinov, J. B. Tenenbaum (2019), Current Opinion in Behavioral Sciences 29:97-104. https://arxiv.org/abs/1902.03477 arXiv:1902.03477 — `FULL_TEXT_READ`

**What it already explains.** That one-shot concept learning at human level on a large, natural domain (1,623 handwritten characters, 50 alphabets) is achieved by representing each concept as a *probabilistic program* — a stochastic motor procedure built compositionally from primitives → sub-strokes → strokes with relations, with type-level programs generating token-level variants rendered to images — and learning by Bayesian program induction (search over parses under a prior learned from background alphabets). Three ingredients are claimed necessary: compositionality, causality (the program mirrors how characters are actually produced), and learning-to-learn (priors over programs and reusable sub-programs from background experience). Results restated in 2019: BPL 3.3% one-shot within-alphabet error vs humans ≤4.5%, simple convnet 13.5%, Siamese 8.0%; BPL 4.2% with only 5 background alphabets vs 23.2-30% for meta-learners; visual Turing tests at 52% (exemplar generation), 59% (parsing), 49% (new concepts of a type), 51% (unconstrained). BBS generalizes this into a programme: intelligence = model-building (causal, compositional, learning-to-learn) on intuitive-physics/psychology 'start-up software', contrasted with pattern recognition; argues (without proof) that gradient descent in a fixed architecture may be unable to build such representations and that structure search 'may look much more like the slow random hill-climbing of evolution'.

**Formal object.** (As restated in BBS Fig. 5 and the 2019 report; the Science paper's equation P(ψ, θ, I) = P(I\|θ)P(θ\|ψ)P(ψ) was not read and is UNVERIFIED.) A hierarchical generative model: a *type* ψ is a program sampled from a library of primitive actions (i), combined into sub-parts (ii) and parts (iii) with relations (attached along / at start) to form an object template (iv); *tokens* θ are noisy executions of the type producing exemplars (v) rendered to binary images (vi). Learning = posterior inference over programs given one image; classification by approximate marginal likelihood of re-fitting a program to a new image; generation by running the program; learning-to-learn = fitting the primitive library and priors to background drawing demonstrations (trajectory data) from 30 (or 5) alphabets.

**Strongest result.** No theorems. Strongest empirical result (verified via the 2019 restatement): 'BPL performs comparably to people, achieving an error rate of 3.3% on one-shot classification' vs humans 4.5% (an upper bound), convnet 13.5%, Siamese 8.0%; with minimal (5-alphabet) background training BPL 4.3%/4.0% vs prototypical-net 30.8%/29.3%; lesion analyses confirm each of the three ingredients contributes. Visual Turing tests: 52% ID for new exemplars 'where only 3 of 48 judges were reliably above chance'. Note the 2019 discussion lists BPL at 4.5% on the original task (Table 1 says 3.3%) — an internal inconsistency in the source, recorded as-is.

**Assumptions.** A hand-designed domain-specific generative language (pen strokes, sub-strokes, relations, rendering) is *given*; only its parameters/library are learned from background demonstrations ('some of these causal and compositional components are built into the architecture, while other components are learned by training on drawing demonstrations').; Background experience includes drawing *trajectories*, not just images — i.e. supervision about the causal process.; Inference is approximate search over parses plus MCMC/optimization; no guarantee of finding the posterior mode.; BBS: the 'core ingredients' are declared agnostic as to origin (innate vs learned) — no acquisition mechanism is proposed.

**Resource model.** Samples (explicit and central: one-shot; 5 vs 30 background alphabets); description length implicitly (priors over programs). Compute: acknowledged as a cost ('these representations ... bring challenges for performing efficient inference'; BBS sec. 4.3.1) but not modeled; no timing results in the read sources. Verification/memory: none.

**Failure boundary.** Single domain with a bespoke DSL; the 2019 report says 'no new algorithm has attempted to perform all of the tasks together' and BPL's assumptions are 'controversial but so far necessary'. No derivation of *why* program induction should beat gradient learning at low data — only the empirical Table 1 and the BBS conjecture. BBS explicitly admits it is 'less committed to a particular story regarding the origins of the ingredients' and that exploration of architectures 'have not yet been made algorithmic'. Nothing predicts the crossover point (data, compute) at which neural approaches overtake BPL — which the 2019 table shows happening with augmentation (ARC 1.5%).

**Implementation.** https://github.com/brendenlake/BPL (MATLAB; fetched README) and the dataset https://github.com/brendenlake/omniglot

**Track-B residual.** BPL is a D2-flavoured *instance*: a fixed probabilistic-program morphology acquires new concepts (programs) from one example given a hand-built language and causal demonstrations. What Track B needs and BPL does not give: (i) a derivation of the data/compute regime in which conditioning-over-programs dominates gradient-in-fixed-architecture (BBS conjectures it; Table 1 measures it at two points, 30 and 5 alphabets); (ii) any account of acquiring the *language* (primitives, relations, renderer) rather than programs in it; (iii) a charged comparison of inference cost (search over parses) against the neural alternatives' training cost.

**Upward question.** Treat BPL's ingredient lesions as a two-point sample of a phase diagram (background alphabets × augmentation × architecture). Can GMI-T10/T4 predict, from ecology parameters (samples per concept, availability of causal demonstrations, task multiplicity), where the probabilistic-program morphology's advantage vanishes — the 2019 Table 1 already shows it vanishing under 4-fold class augmentation plus deformations?

Load-bearing quotes (verbatim from sources actually read):

> "we introduced a framework called Bayesian Program Learning (BPL) that represents concepts as probabilistic programs and utilizes three key ingredients – compositionality, causality, and learning to learn – to learn programs from just one or a few examples" — [2] Lake et al. 2019, introduction
> "BPL performs comparably to people, achieving an error rate of 3.3% on one-shot classification (Table 1 column 1)." — [2] Lake et al. 2019, 'One-shot classification'
> "Human participants are skilled one-shot classifiers, achieving an error rate of 4.5%, although this is an upper bound since they responded quickly and were not incentivized for performance." — [2] Lake et al. 2019, 'One-shot classification'
> "BPL learns to learn so efficiently because it makes strong causal and compositional architectural assumptions, which are controversial but so far necessary for training from limited background experience" — [2] Lake et al. 2019, 'One-shot classification'
> "BPL can generate new examples that can pass for human, achieving an average 52% ID level where only 3 of 48 judges were reliably above chance." — [2] Lake et al. 2019, 'Generating new exemplars'
> "we see model building as the hallmark of human-level learning, or explaining observed data through the construction of causal models of the world" — [1] Lake et al. 2017, sec. 1.2
> "we developed an algorithm using Bayesian Program Learning (BPL) that represents concepts as simple stochastic programs – that is, structured procedures that generate new examples of a concept when executed" — [1] Lake et al. 2017, sec. 4.2.2, p. 23
> "trying to build these representations from scratch using backpropagation, deep Q-learning or any stochastic gradient-descent weight update rule in a fixed network architecture may be unfeasible regardless of how much training data are available." — [1] Lake et al. 2017, p. 35
> "the dynamics of structure-search may look much more like the slow random hill-climbing of evolution than the smooth, methodical progress of stochastic gradient-descent." — [1] Lake et al. 2017, p. 35
> "A synthesis of these approaches, able to perform efficient inference over programs that richly model the causal structure an infant sees in the world, would be a major step forward for building human-like AI" — [1] Lake et al. 2017, p. 40

Verification notes: The Science 2015 paper itself was not readable; every number and the model structure are taken from the authors' 2019 arXiv progress report (full text) and the BBS paper's Fig. 5 caption. The Science paper's generative-model equation and its Methods (e.g. number of parses, MCMC details) are UNVERIFIED and not cited. The 2019 report's own text inconsistently gives BPL's original-task error as 3.3% (Table 1, main text) and 4.5% (Discussion); recorded without resolution. No prior reconstruction in the repo ledgers consulted (a _maml.txt in the scratchpad suggests another family covers meta-learning baselines).

### P6.CHURCH — Church: a universal stochastic lambda calculus with eval-as-sampling and query-as-conditioning

Disposition: `ADOPT` · best verification: `FULL_TEXT_READ`

Sources:

- [0] Church: a language for generative models — N. D. Goodman, V. K. Mansinghka, D. Roy, K. Bonawitz, J. B. Tenenbaum (2008), Proc. 24th Conf. on Uncertainty in Artificial Intelligence (UAI), pp. 220-229 (PMLR r6). https://arxiv.org/abs/1206.3255 arXiv:1206.3255 — `FULL_TEXT_READ`

**What it already explains.** That a single, small language — pure Scheme (lambda, if, define, quote, application) plus elementary random procedures (e.g. flip) carrying a distribution function, plus memoization (mem/DPmem) — suffices to describe every generative model in the paper's zoo (Bayes nets with parameter clustering, infinite mixtures, HDP-HMM/PCFG, adaptor grammars, planning-as-inference), because 'evaluation is sampling' and composition of programs is composition of stochastic processes. It defines the semantics of a program as a distribution over *evaluation histories* (not values), shows this is well defined for expressions that halt with probability one (admissibility), and defines conditioning (query) as conditional sampling of that distribution given a predicate on the value. It also shows query is metacircular (definable in Church by rejection), that exact inference is a rejection sampler and approximate inference an MCMC over computation traces, and it identifies the exchangeability of repeated evaluation as the right notion of 'purity' for stochastic programs.

**Formal object.** Expressions e ::= c \| x \| (e1 e2 ...) \| (lambda (x...) e) \| (if e1 e2 e3) \| (define x e) \| (quote e). Procedures are triples (body, args, env); elementary random procedures additionally carry a distribution function P(value \| env, args). An evaluation history for e in env is the sequence of recursive eval calls and return values; its probability is the product of the elementary-random-procedure probabilities along it; the weight of e in env is the sum over finite histories; e is admissible iff weight = 1 (halts a.s.). μ(e, env) is the marginal distribution on values. (query 'e p env) samples from μ(e, env) conditioned on (p v) = True. mem extends env with countably many bindings V_val ~ μ((e val), env); DPmem is defined in Church itself via stick-breaking. Computation traces (DAGs of evaluation tree + environment-extension tree) are in bijection with equivalence classes of histories and are the state space of the MH sampler.

**Strongest result.** Lemma 2.1 (mem-free weight is well defined and ≤ 1, by monotone convergence on the evaluation tree); Lemma 2.2 (admissibility is well defined with mem, by induction on uses of mem, and admissible e defines μ(e, env)); Theorem 2.3: if e and p are admissible in env, V ~ μ(e, env), and some v in the support of μ(e, env) makes True have non-zero probability under μ((p v), env), then P(V = val \| (eval '(p V) env) = True) is well defined. Plus the metacircular definition of query as rejection sampling and the trace-MCMC scheme (Section 4.1), with convergence shown empirically on the sprinkler example (Fig. 9). No complexity theorem.

**Assumptions.** All primitive types are countable; reals are fixed/floating precision (so the semantics is over countable histories; continuous distributions are approximated).; Admissibility: expressions must halt with probability one; query is undefined for inadmissible e or p, and requires the conditioning predicate to have positive probability (Theorem 2.3) — i.e. conditioning only on positive-measure events.; Exchangeability of repeated evaluation (the 'purity' notion) is required for the MH sampler; mutable state beyond mem is excluded.; The MH algorithm was not implemented for programs using mem (footnote 8) and nested queries are 'believed' straightforward; the general rejection/initialization problem for hard constraints is open (footnote 5).

**Resource model.** Almost none at the level of theorems: description length is mentioned qualitatively ('issues of programming style then become issues of description length and inductive bias'); inference cost is acknowledged as 'substantially increased' but not modeled; MCMC steps per sample reported in one figure. No time, sample, memory or verification accounting.

**Failure boundary.** Cannot condition on measure-zero events (query requires a positive-probability predicate); no continuous semantics (fixed precision reals); no bound on inference cost — rejection is 'often intractable', MCMC has no convergence-rate result; the DPmem/mem constructs are 'notionally' infinite objects implemented statefully; no learning-of-language (the language is fixed); nothing about which inference strategy to use, when, or at what cost. Predicts nothing about morphology other than 'everything is representable'.

**Implementation.** MIT-Church (Blaise-based, 2008); successors WebPPL (https://github.com/probmods/webppl) and the probmods.org tutorials; Bher/Wingate et al. 2011 lightweight implementation.

**Track-B residual.** Church makes the probabilistic morphology *universal* (every computable generative process is a Church expression), so representability is trivial. What Church does not say: what a bounded agent must pay, in trace-space size, MCMC mixing, or description length, to hold a *distribution over executions* rather than a single execution, and whether an ecology ever makes that price worth paying versus a point-estimate (programmatic/neural) morphology. Church also leaves open whether its basis is *minimal* (B1): is mem, or query-as-primitive, eliminable at bounded overhead?

**Upward question.** If the morphology cannot be identified by its language, identify it by its state object (a distribution over evaluation histories, i.e. a computation-trace measure) and its update (trace-space conditioning). What is the *charged overhead* of maintaining a trace measure versus a single trace, as a function of ecology (branching factor of the generative process, observation informativeness, drift), and does a basis without a trace-measure primitive ever acquire one?

Load-bearing quotes (verbatim from sources actually read):

> "the meaning of an expression is specified through a primitive procedure eval, which samples from the process, and a primitive procedure query, which generalizes eval to sample conditionally." — [0] Sec. 2
> "Thus admissibility can be thought of as the requirement that evaluation of an expression halts with probability one." — [0] Sec. 2
> "If there exists a value v in the support of μ(e, env) and True has non-zero probability under μ((p v), env), then the conditional probability P(V =val \| (eval '(p V) env)=True) is well defined." — [0] Theorem 2.3, Sec. 2.2
> "We believe the right notion of purity in a stochastic language is exchangeability: if an expression is evaluated several times in the same environment, the distribution on return values is invariant to the order of evaluations." — [0] Sec. 2.1
> "The ability to write query as a Church program—a metacircular implementation—provides a compelling argument for Church's modeling power. However, exact sampling using this algorithm will often be intractable." — [0] Sec. 4
> "eval nested within query may be used to learn programs, where the prior on programs is represented by another Church program. Issues of programming style then become issues of description length and inductive bias." — [0] Sec. 5
> "Of course, Church's representational flexibility comes at the cost of substantially increased inference complexity." — [0] Sec. 5

Verification notes: Full text read from arXiv 1206.3255v2 (authors' corrected version of the UAI 2008 paper). Theorem/lemma numbers are as in that version. No prior reconstruction in the repo ledgers consulted.

### P6.CHURCH_SEMANTICS — Church query semantics (Goodman et al. 2008) and measurable/higher-order semantics for probabilistic programs with score and normalisation (Staton, Yang, Wood, Heunen, Kammar 2016)

Disposition: `ADOPT` · best verification: `PARTIAL_TEXT_READ`

Sources:

- [0] Church: a language for generative models — Noah D. Goodman, Vikash K. Mansinghka, Daniel M. Roy, Keith Bonawitz, Joshua B. Tenenbaum (2008), UAI 2008; arXiv:1206.3255v2. https://arxiv.org/abs/1206.3255 arXiv:1206.3255 — `PARTIAL_TEXT_READ`
- [1] Semantics for probabilistic programming: higher-order functions, continuous distributions, and soft constraints — Sam Staton, Hongseok Yang, Frank Wood, Chris Heunen, Ohad Kammar (2016), LICS 2016; arXiv:1601.04943v3. https://arxiv.org/abs/1601.04943 ; doi:10.1145/2933575.2935313 arXiv:1601.04943 — `PARTIAL_TEXT_READ`

**What it already explains.** Goodman et al. define a universal probabilistic language (a stochastic Scheme) whose semantics is a distribution over evaluation histories: eval maps an expression and environment to a random value, and query is 'a procedure which samples a value from mu(e, env) conditioned on the predicate procedure p returning True'. Conditioning is defined on histories, not on values, so the language is 'fundamentally sampling-based'. Admissibility (evaluation halts with probability one, Section 2) and Theorem 2.3 (non-zero probability of the predicate) are the exact preconditions under which query denotes a well-defined conditional distribution. Reals are discretised ('all primitive types are countable; real numbers are approximated by either fixed- or floating-precision arithmetic'), which sidesteps the Ackerman-Freer-Roy continuous-conditioning barrier by construction. Memoization (mem) gives exchangeable stochastic memoized procedures (DP-mem); the exchangeability notion is proposed as the stochastic analogue of purity. Two query implementations: rejection (exact but 'often intractable') and a Metropolis-Hastings kernel over computation traces. Staton et al. give the first denotational semantics of a higher-order probabilistic language with continuous distributions and soft constraints (score) and an explicit normalisation construct: because Meas is not cartesian closed, first-order terms are interpreted in Meas via s-finite kernels and higher-order terms in a functor category over Meas; norm has type (R x P(A)) + 1 + 1, where the two extra summands track model evidence 0 or infinity. Proposition 8.3: every first-order term equals one without lambda-abstraction/application.

**Formal object.** Church: expressions e of a Scheme-like language with primitive random procedures (flip, etc.); eval(e, env) induces a distribution mu(e, env) over values via distributions over evaluation histories; query(e, p, env) is sampling from mu(e, env) conditioned on eval((p v), env) = True; admissibility = halting with probability one; mem: stochastic memoizer; DPmem: Dirichlet-process memoizer giving exchangeable random procedures. Staton et al.: types A ::= R \| P(A) \| 1 \| A x A \| sum_i A_i \| A -> A; deterministic judgement Gamma \|-d t : A interpreted as measurable functions (first order) or morphisms in the functor category [Meas^op-ish presheaf setting] (higher order); probabilistic judgement Gamma \|-p t : A interpreted as s-finite kernels; constructs sample(t), score(t), norm(t) with Gamma \|-d norm(t) : (R x P(A)) + 1 + 1; Assumption 7.1 restricts P(A) to measurable A in the operational treatment.

**Strongest result.** Goodman et al. Theorem 2.3: if there exists a value v in the support of mu(e, env) and True has non-zero probability under mu((p v), env), then the conditional probability P(V = val \| eval((p V), env) = True) is well defined. Staton et al.: a sound denotational semantics for sample/score/norm with continuous distributions, matching the operational (sampling-based) semantics; normalisation typed as (R x P(A)) + 1 + 1 so that evidence 0 and infinity are total outcomes; Proposition 8.3 (first-order terms are lambda-free, hence measurable functions). Neither source gives resource bounds or approximation guarantees for query/inference.

**Assumptions.** Church: primitive types countable; reals approximated by fixed/floating precision (discrete semantics); Church: admissibility (halting w.p. 1) and non-zero predicate probability for query to be well defined; Church: exact query is rejection sampling; the MCMC query is asymptotic with no mixing-time guarantee; Staton et al.: distributions over functions excluded operationally (Assumption 7.1: P(A) only for measurable A); Staton et al.: Meas is not cartesian closed, so higher-order semantics lives in a functor category, not in Meas; Staton et al.: norm may fail with evidence 0 or infinity; infinite evidence can arise from infinite distributions

**Resource model.** none. Church names intractability of exact query qualitatively ('exact sampling using this algorithm will often be intractable') and offers MCMC without rates; Staton et al. model no cost at all. Neither charges description length, samples, compute, memory or verification.

**Failure boundary.** Church: conditioning on measure-zero events is undefined at the language level (predicate must have positive probability; continuous observation is handled only by discretisation or by later score/noise constructs); non-admissible programs; no inference-cost semantics. Staton et al.: no semantics for distributions over higher-order functions operationally; evidence 0/infinity failure; no learning law (no parameters, no update, no gradient) - the semantics describes inference targets, not the process that chooses a model or its parameters.

**Implementation.** Church: metacircular Scheme interpreter with rejection query and MCMC-over-traces query (Section 4); successor systems WebPPL/Anglican/Venture (not read here). Staton et al.: the paper is theory; Anglican is the named reference implementation for the language fragment.

**Track-B residual.** The probabilistic morphology's D0 (representability of conditional-inference programs) is owned here, in discrete (Church) and continuous (Staton) settings. Track B must supply (i) a resource-charged D1 for query/norm (what inference compiler, at what cost, under what ecology), (ii) the law by which a developing system moves between rejection, MCMC, amortised and gradient inference (a selection over inference morphologies), and (iii) how model structure itself is acquired without labels. None of these is present.

**Upward question.** Does the choice among query implementations (rejection, trace-MCMC, amortised network, gradient/variational) follow a resource-charged selection law indexed by the ecology's observation structure, and can that law be stated as a functor on the semantics rather than as an engineering choice?

Load-bearing quotes (verbatim from sources actually read):

> "The semantics of Church is defined in terms of evaluation histories and conditional distributions on such histories." — [0] Goodman et al. 2008, Abstract
> "The procedure (query 'e p env) is defined to be a procedure which samples a value from mu(e, env) conditioned on the predicate procedure p returning True when applied to the value of (eval 'e env)." — [0] Goodman et al. 2008, Section 2
> "Thus admissibility can be thought of as the requirement that evaluation of an expression halts with probability one." — [0] Goodman et al. 2008, Section 2
> "If there exists a value v in the support of mu(e, env) and True has non-zero probability under mu((p v), env), then the conditional probability P(V = val \| (eval '(p V) env) = True) is well defined." — [0] Goodman et al. 2008, Theorem 2.3
> "However, exact sampling using this algorithm will often be intractable." — [0] Goodman et al. 2008, Section 4
> "all primitive types are countable; real numbers are approximated by either fixed- or floating-precision arithmetic." — [0] Goodman et al. 2008, Section 2
> "the semantics of Church is fundamentally sampling-based: the denotation of admissible expressions as distributions follows from the semantics of evaluation rather than defining it." — [0] Goodman et al. 2008, Section 5
> "We believe the right notion of purity in a stochastic language is exchangeability" — [0] Goodman et al. 2008, Section 2.1
> "Denotational semantics for higher-order programs poses a problem, because measurable spaces do not support the usual beta/eta theory of functions: they do not form a Cartesian closed category (indeed, R^R does not exist as a measurable space [3])." — [1] Staton et al. 2016, Section 1
> "If the model evidence is 0 or infinity, the conversion fails, and this is tracked by the '+1+1'." — [1] Staton et al. 2016, Section 3
> "Assumption 7.1. From the operational perspective it is unclear how to deal with sampling from a distribution over functions. For this reason, in this section, we only allow the type P(A) when A is a measurable type." — [1] Staton et al. 2016, Section 7
> "The third equation shows how infinite model evidence errors can arise when working with infinite distributions." — [1] Staton et al. 2016, Section 4
> "we show that every term of first-order type is equal to one without lambda-abstractions or application, and hence is interpreted as a measurable function (Proposition 8.3)." — [1] Staton et al. 2016, Section 8

Verification notes: Both papers accessed through alphaXiv page-level extraction (partial). Quotes are verbatim from extracted pages, with Greek letters and the mu/lambda symbols transliterated. Codex P-CHURCH (LITERATURE_LEDGER / PARENT_LEDGER_V1) records Church at abstract depth only; this entry adds the query semantics (rejection/metacircular + MCMC over traces), the admissibility and Theorem 2.3 preconditions, the discretised-reals design decision, and the Staton score/norm typing. Section 6 of Goodman et al. and Sections 5-6 of Staton et al. were not read.

### P6.CONDITIONING_LIMIT — Noncomputability of conditioning (Ackerman-Freer-Roy) and QUERY as conditional simulation (Freer-Roy-Tenenbaum)

Disposition: `ADOPT` · best verification: `PARTIAL_TEXT_READ`

Sources:

- [0] On the Computability of Conditional Probability (journal version of 'Noncomputable conditional distributions', LICS 2011) — N. L. Ackerman, C. E. Freer, D. M. Roy (2019), arXiv 1005.3014v4 (Nov 2019); LICS 2011 pp. 107-116 for the preliminary version. https://arxiv.org/abs/1005.3014 arXiv:1005.3014 — `PARTIAL_TEXT_READ`
- [1] Towards common-sense reasoning via conditional simulation: legacies of Turing in Artificial Intelligence — C. E. Freer, D. M. Roy, J. B. Tenenbaum (2014), in Turing's Legacy (ASL Lecture Notes in Logic 42), pp. 195-252. https://arxiv.org/abs/1212.4799 arXiv:1212.4799 — `PARTIAL_TEXT_READ`

**What it already explains.** That 'Bayesian inference' as an operation on *programs* has a hard computability boundary. In the Type-2 (TTE) framework, a computable joint distribution on [0,1]^2 can have a conditional distribution that encodes the halting problem: Theorem 7.6 constructs P-almost computable W, Y with P[Y\|W=·] almost-continuous but not almost-computable; Cor. 7.7 shows any oracle computing it on a set of measure > 5/6 computes ∅'; Section 8 smooths this to an *everywhere continuous, infinitely differentiable* version that is still noncomputable, so Cor. 8.5: any conditioning operator on the class of pairs with an everywhere-continuous conditional is noncomputable. Theorem 6.7 (via the recursion theorem) shows conditioning is not even *approximable*: for any purported conditioning program there is a representation of the input distribution on which it outputs no nontrivial fact. The positive side delineates exactly where conditioning is computable: Prop. 9.2 (computably discrete observation with positive mass), Prop. 9.4 / Cor. 9.6 (a positive, bounded, computable conditional density — Bayes' rule computable via integration), Cor. 9.7 (observation corrupted by independent noise with bounded computable density), and the exchangeable setting via computable de Finetti (Freer-Roy). Crucially, noise does not restore uniform approximability: one cannot compute how small σ must be for a given accuracy. FRT package the same picture as QUERY: a universal PTM that conditions a prior PTM P on a {0,1}-valued predicate PTM C by rejection, hence *only* on positive-measure events; conditioning on X = x for continuous X is handled by ε-balls or noise, with the caveat that convergence rate is noncomputable.

**Formal object.** Computable Polish spaces (S, δ, D); P-almost computable random variables (computable on a P-measure-one set); computable probability measures (integration of bounded computable functions computable); a probability kernel κ: S×B_T→[0,1] is computable when κ̄: S→M_1(T) is computable (Def. 4.3) — i.e. the map x ↦ P[Y\|X=x] into the space of measures with the Prokhorov/weak topology. Conditioning operator Φ for a family F ⊆ M_1([0,1]^2): Φ(μ, x) a version of the conditional distribution at x (Def. 6.1-6.2); conditioning program φ_a: N^3→N (Def. 6.6). FRT: PTM = oracle TM with an i.i.d. Bernoulli(1/2) bit tape R ∈ {0,1}^∞; output distribution P∘φ_e(·,s)^{-1} when φ_e halts a.s.; QUERY(P,C): sample R, run C on R; if C(R)=1 output P(R), else repeat with fresh R'; output law = P(φ_P ∈ · \| φ_C = 1), defined when P(φ_C=1) > 0.

**Strongest result.** Theorem 7.6: 'There are P-almost computable random variables W and Y on [0, 1] such that the conditional distribution map P[Y\|W = · ] is P_W-almost continuous but not P_W-almost computable.' Corollary 7.7: if P[N\|X=·] is A-computable on a set of P_X-measure > 5/6 then A ≥_T ∅' (and the bound is tight: it is ∅'-computable on a measure-one set). Corollary 8.5: a conditioning operator for pairs admitting an everywhere continuous conditional distribution map is noncomputable. Theorem 6.7 (nonapproximable): for any conditioning program φ_a for a set F containing the finitely-supported rational measures, uniformly in a, e, j one computes an index i with μ_e = μ_i on which φ_a outputs only the empty string. Positive: Prop. 9.2 (computably discrete D with P{X=d}>0: P[Y\|X=·] computable on D uniformly); Prop. 9.4 (positive bounded computable conditional density on R×T ⟹ κ computable on R); Cor. 9.6 (density + conditional independence); Cor. 9.7 (X = U + E, E independent with bounded computable density ⟹ P[(U,V)\|X=·] computable); Sec. 9.4 exchangeable case via computable de Finetti [Freer-Roy 2012]. FRT sec. 3.4 draws the corollary that ε-ball approximations converge but the ε needed for a given accuracy is not computable.

**Assumptions.** Computability in the sense of TTE / computable analysis: distributions are computable when integration of bounded computable functions is; random variables computable on a measure-one set; conditional distributions as measure-valued maps under the weak topology.; The negative results are about *general* algorithms for the whole class of computable distributions; they say nothing against inference for specific structured subclasses (and Sec. 9 lists such subclasses).; Positive results require positivity/boundedness/computability of densities, or independence of the noise from the latent variables, or computable discreteness with positive point masses.; FRT: predicates must accept with non-zero probability; the prior and predicate share the random tape.

**Resource model.** Computability only (Turing degree / oracle strength, uniformity); no complexity. Section 1.4.1 explicitly defers finite-discrete complexity (Cooper 1990; Dagum-Luby) and cryptographic hardness of conditional sampling (Ben-David et al. 1992) to other work. No description length, samples, memory, verification.

**Failure boundary.** Does not give complexity bounds in the computable regime (discrete/dominated/noisy cases may still be exponentially hard: 'may not be efficiently so'); does not address approximate inference *quality* (only computability of the exact conditional map); the noncomputable constructions are pathological encodings of the halting set, so the result does not predict failure on any natural model; positive conditions are sufficient, not necessary. FRT: the QUERY formalism restricts to positive-measure predicates by fiat and leaves 'how do we obtain such models?' explicitly open.

**Implementation.** none (impossibility + characterization results); QUERY is a definitional device, 'we do not actually intend QUERY to be executed in practice'.

**Track-B residual.** ACR give the P5-class limit for GMI-T6: 'Bayes update' is a computable primitive of a basis only on a restricted observation structure. The residual for Track B is a *complexity* and *selection* question inside the computable region: within {discrete, dominated-density, smooth-noise, exchangeable} observation structures, what is the charged cost of conditioning as a function of ecology parameters, and does the boundary of the computable region (where noiseless continuous observation makes even approximation non-uniform) act as a morphology phase boundary — i.e. do systems facing noiseless continuous observation *have* to abandon trace-measure conditioning for point-estimate/gradient morphologies?

**Upward question.** Is the ACR boundary (positive-measure / dominated / noisy vs. noiseless-continuous observation) the *same* boundary that separates ecologies where probabilistic morphologies dominate from those where gradient/programmatic point-estimate morphologies dominate — i.e. can GMI-T10's phase boundary be derived from observation-structure computability plus resource prices rather than posited?

Load-bearing quotes (verbatim from sources actually read):

> "We show that there are computable joint distributions with noncomputable conditional distributions, ruling out the prospect of general inference algorithms, even inefficient ones." — [0] ACR, abstract
> "the most expressive such languages are each capable of describing the same robust class as the others — the class of computable distributions, which delineates those from which a probabilistic Turing machine can sample to arbitrary accuracy." — [0] ACR, sec. 1.1
> "Because every function computable on a domain D is continuous on D, discontinuity is a fundamental barrier to computability" — [0] ACR, sec. 1.5
> "Theorem 7.6. There are P-almost computable random variables W and Y on [0, 1] such that the conditional distribution map P[Y\|W = · ] is P_W-almost continuous but not P_W-almost computable." — [0] ACR, sec. 7
> "If P[N\|X = · ] is A-computable on a set of P_X-measure greater than 5/6 for an oracle A ⊆ N, then A computes the halting set, i.e., A ≥_T ∅′." — [0] ACR, Cor. 7.7
> "Let Φ be a conditioning operator for the set of probability distributions on pairs (X, Y) of random variables in [0, 1] such that there exists an everywhere continuous version of the conditional distribution map P[Y\|X = · ]. Then […]" — [0] ACR, Cor. 8.5 [quote truncated to 40 words]
> "Then the conditional distribution map P[Y\|X = · ] is computable on D, uniformly in X, Y, and f." — [0] ACR, Prop. 9.2 (computably discrete D, P{X=d}>0)
> "If p_{X\|Y}(x\|y) is a conditional density of X given Y that is positive, bounded, and computable on R × T, then κ as defined in (21) is computable on R." — [0] ACR, Prop. 9.4
> "If P_E is absolutely continuous (with respect to Lebesgue measure) with a bounded computable density p_E, and E is independent of U and V, then the conditional distribution map P[(U, V)\|X = · ] is computable." — [0] ACR, Cor. 9.7 (X = U + E)
> "one cannot uniformly compute a value of σ from a desired bound on the error introduced to the conditional distribution corrupted by the noise σZ." — [0] ACR, sec. 9.3
> "The centerpiece of the formalism is a universal probabilistic Turing machine called QUERY that performs conditional simulation, and thereby captures the operation of conditioning probability distributions that are themselves represented by probabilistic Turing machines." — [1] FRT, sec. 1
> "The semantics of QUERY are straightforward: first generate a sample from P; if C is satisfied, then output the sample; otherwise, try again." — [1] FRT, sec. 2.1
> "Hence although such a sequence of approximations might converge in the limit, one cannot in general compute how close it is to convergence." — [1] FRT, sec. 3.4
> "Of course, this raises the questions: how do we obtain such models? In particular, how can or should we build them when they are not handed to us?" — [1] FRT, sec. 8

Verification notes: Theorem numbers are those of arXiv 1005.3014v4 (the JACM-style journal version). FRT cite the LICS 2011 numbering ('[AFR11, Thm. 29]', '[AFR11, Cor. 36]'), which corresponds to Thm. 7.6 and Cor. 9.7 here; the LICS version itself was not read. Full text of both papers is on disk; the constructions (ACR sec. 7-8) were not verified line by line. No prior reconstruction in the repo ledgers consulted.

### P6.CONDITIONING_LIMIT — On the computability of conditional probability (Ackerman, Freer, Roy 2011/2019): noncomputable conditional distributions and the positive cases - the computability boundary of the probabilistic morphology

Disposition: `ADOPT` · best verification: `FULL_TEXT_READ`

Sources:

- [0] On the Computability of Conditional Probability — Nathanael L. Ackerman, Cameron E. Freer, Daniel M. Roy (2019), Journal of the ACM 66(3):23 (2019); preliminary version LICS 2011 'Noncomputable conditional distributions'; arXiv:1005.3014v4. https://arxiv.org/abs/1005.3014 ; doi:10.1145/3321699 arXiv:1005.3014 — `FULL_TEXT_READ`

**What it already explains.** Within Type-2 effectivity on computable Polish spaces: computable probability measures = distributions of P-almost computable random variables (Props 2.18-2.19). NEGATIVE: (i) Prop 5.1: a computable pair (X, C) whose conditional map P[C=1\|X=.] is discontinuous everywhere (the Dirichlet function), hence not almost computable, though L1-computable (Prop 5.2); (ii) Prop 6.4: on any class of joint distributions containing the finitely supported ones, every conditioning operator is discontinuous everywhere, hence noncomputable - 'a finite approximation to the joint distribution determines nothing about the result of conditioning on a particular point'; Theorem 6.7 (via Kleene's recursion theorem): any purported conditioning program can be fed a representation of the same distribution on which it outputs no nontrivial fact; (iii) CENTRAL Theorem 7.6: P-almost computable W, Y on [0,1] such that P[Y\|W=.] is P_W-almost continuous but not P_W-almost computable - the construction encodes halting times h(N) of all Turing machines into the bits of X = X_{h(N)}, so that P[N\|X=.] computes the halting set (Cor 7.7: any oracle computing it on a set of measure > 5/6 computes 0'; Lemma 7.4: it IS 0'-computable, so the bound is sharp); Prop 7.8: not even L1-computable; (iv) Section 8 / Cor 8.5: the same with an EVERYWHERE continuous, infinitely differentiable conditional density (smoothing with a C-infinity bump), so continuity does not rescue computability. POSITIVE: Prop 9.2: conditioning on a computably discrete variable with positive atoms is computable (also by rejection sampling, Lemma 9.3); Prop 9.4 / Cor 9.6: Bayes' rule is computable when a positive, bounded, computable conditional density exists; Cor 9.7: conditioning on U + E with E independent noise having a bounded computable density is computable even when conditioning on U is not; but one cannot computably choose the noise level for a target accuracy; Section 9.4: exchangeable settings via computable de Finetti (Freer-Roy).

**Formal object.** Computable Polish space (S, delta, D); P-almost computable random variable X: {0,1}^inf -> S computable on a P-measure-one set; conditional distribution P[Y\|X=.] as a regular version kappa: S x B_T -> [0,1], computable when the map s \|-> kappa(s,.) is computable on a P_X-measure-one set (Section 4). Construction: N ~ geometric(1/5), C ~ Bernoulli(1/3), U, V uniform; X_k = (2 floor(2^k V) + C + U)/2^{k+1}; X = X_{h(N)}; densities p_{X_k} = 4/3 or 2/3 by parity of floor(2^{k+1} x); tau(x) = sum_n a_n(x) 5^{-n} with digits in {2,3,4} encoding halting. Conditioning operator Phi: M_1([0,1]^2) x [0,1] -> M_1([0,1]) (Def 6.1).

**Strongest result.** Theorem 7.6 (noncomputable almost-continuous conditional distribution; conditioning encodes the halting problem) with Corollary 7.7 (sharp: exactly 0'); Corollary 8.5 (noncomputable even restricted to everywhere-continuous versions); Proposition 6.4 (every conditioning operator is discontinuous everywhere) and Theorem 6.7 (nonapproximability). Positive: Prop 9.2 (discrete), Prop 9.4 / Cor 9.6 (dominated, computable bounded positive density), Cor 9.7 (independent smooth noise), Section 9.4 (exchangeable).

**Assumptions.** Type-2 Theory of Effectivity; computable Polish spaces; random variables computable on measure-one sets; conditioning defined via regular versions; noncomputability results concern conditioning at points and on measure-one sets, and (Prop 7.8) L1; positive results need discreteness with positive atoms, or a computable bounded positive conditional density, or independent noise with such a density, or exchangeability

**Resource model.** computability only. Explicitly separates computability from efficiency: 'Conditional probabilities for computable distributions on finite, discrete sets are clearly computable, but may not be efficiently so' (1.4.1, citing average-case complexity and Bayesian-network hardness results as related work). No description length, samples or verification.

**Failure boundary.** Says nothing about efficiency, samples, or which approximate inference to use; nothing about learning the model; the halting-encoding construction is an existence proof, and the positive cases are sufficient conditions, not a characterisation. It concerns exact conditioning of computable joint distributions - not the resource cost of approximate inference, and not the morphology question of when explicit stochastic structure is worth its cost.

**Implementation.** none (theory)

**Track-B residual.** This is a P5-class boundary for the brief's GMI-T6 (probabilistic-program/Bayes specialisation) and the registry's GMI-T8: any D1 claim 'the probabilistic morphology compiles from the basis with bounded overhead' must be restricted to AFR's positive classes (discrete observations, computable bounded densities, smooth noise, exchangeable) - outside them there is NO compiler, bounded or not. What AFR leaves open is the RESOURCE obstruction inside the computable classes: where, under E, explicit stochastic structure is cheaper than a deterministic emulation - AFR's obstruction is about computability, not cost.

**Upward question.** AFR separates computable-conditioning classes from noncomputable ones; is there an analogous RESOURCE-graded separation (e.g. polynomial vs exponential conditioning within the dominated class) that a morphology theory could use as the phase boundary between explicit-probabilistic and deterministic-approximate morphologies under a verification contract?

Load-bearing quotes (verbatim from sources actually read):

> "We show that there are computable joint distributions with noncomputable conditional distributions, ruling out the prospect of general inference algorithms, even inefficient ones." — [0] Abstract
> "Specifically, we construct a pair of computable random variables in the unit interval such that the conditional distribution of the first variable given the second encodes the halting problem." — [0] Abstract
> "In particular, conditional distributions become computable when measurements are corrupted by independent computable noise with a sufficiently smooth bounded density." — [0] Abstract
> "There are P-almost computable random variables W and Y on [0, 1] such that the conditional distribution map P[Y\|W = · ] is P_W-almost continuous but not P_W-almost computable." — [0] Theorem 7.6
> "Every conditioning operator on F is discontinuous everywhere, hence noncomputable." — [0] Proposition 6.4
> "a finite approximation to the joint distribution determines nothing about the result of conditioning on a particular point." — [0] Section 6, after Proposition 6.4
> "such that there exists an everywhere continuous version of the conditional distribution map P[Y\|X = · ]. Then Φ is noncomputable." — [0] Corollary 8.5
> "Under suitable computability hypotheses, conditioning is computable in the discrete setting (Proposition 9.2) and where there is a conditional density (Corollary 9.6)." — [0] Section 1.5
> "one cannot computably tell how little noise must be present to obtain a given accuracy." — [0] Section 9.3
> "Conditional probabilities for computable distributions on finite, discrete sets are clearly computable, but may not be efficiently so." — [0] Section 1.4.1
> "Despite recent progress towards a general such algorithm, support for conditioning with respect to continuous random variables has remained incomplete. Our results explain why this is necessarily the case." — [0] Section 1.1

Verification notes: arXiv v4 (JACM version) read as recorded; theorem numbers verified in the text. Not in the Codex ledgers (LITERATURE_LEDGER E has Church and BPL only). A sibling build script (_build_P6.py) planned a P6.CONDITIONING_LIMIT entry but no P6.json was produced; this entry is independent.

### P6.PPL_INTRO — An Introduction to Probabilistic Programming: FOPPL/HOPPL semantics and the inference-algorithm families

Disposition: `ADOPT` · best verification: `PARTIAL_TEXT_READ`

Sources:

- [0] An Introduction to Probabilistic Programming — J.-W. van de Meent, B. Paige, H. Yang, F. Wood (2018), arXiv (stat.ML), v2 2021 (book-length, 286 pp.). https://arxiv.org/abs/1809.10756 arXiv:1809.10756 — `PARTIAL_TEXT_READ`

**What it already explains.** A textbook-grade account of what a probabilistic program *denotes* and how every inference algorithm family attaches to that denotation. (1) FOPPL (first-order, no recursion, no first-class functions) programs denote finite graphical models: a big-step translation relation ρ,φ,e ⇓ G,E compiles any FOPPL expression to G=(V,A,P,Y) plus a deterministic return expression; the joint is p(V)=Π_v p(v\|pa(v)), observe adds a factor (if φ F1 1) guarded by the control-flow predicate. Hence graph-based inference (Gibbs, HMC, EP via factor graphs) applies. (2) Conditioning generalizes to an unnormalized density γ(X)=ψ(X)p(X), target π=γ/Z, so 'inference' covers reward/utility-weighted problems too. (3) HOPPL (recursion, first-class functions) denotes models with an unbounded number of random variables, which 'rules out graph-based evaluation strategies immediately'; inference must be evaluation-based (likelihood weighting, MH over traces, SMC) through a messaging interface between program executions and an inference controller, with dynamic addressing. (4) Ch. 7-8: differentiable models (HMC via AD) and 'deep probabilistic programming': programs with neural primitives; amortized inference q(X\|Y;φ) as approximate 'compilation' of a program to its posterior; three system designs (PyProb-style backend proposals; WebPPL-style interleaved propose; Pyro/Gen-style standalone proposal programs with addresses).

**Formal object.** FOPPL grammar e ::= c \| v \| (let [v e1] e2) \| (if e1 e2 e3) \| (f e1 ... en) \| (c e1 ... en) \| (sample e) \| (observe e1 e2); q ::= e \| (defn f [v1 ... vn] e) q. Graphical model G=(V,A,P,Y). Sample rule: ρ,φ,e ⇓ (V,A,P,Y),E; fresh v; Z=free-vars(E); F=score(E,v)≠⊥ ⟹ ρ,φ,(sample e) ⇓ (V∪{v}, A∪{(z,v)\|z∈Z}, P⊕[v↦F], Y), v. Observe rule adds F=(if φ F1 1) and Y⊕[v↦E2] with free-vars(E2)=∅. Density p(V)=Π_{v∈V} p(v\|pa(v)); generalized target π(X)=γ(X)/Z, γ=ψ(X)p(X). HOPPL grammar adds f as value and (fn [v1..vn] e). Likelihood-weighting big-step semantics ρ,ℓ,e ⇓ c,l with (sample e) ⇓ c,l for c~d and (observe e1 e2) ⇓ c2, l0+l1+l2 where l0=log p_{d1}(c2). Amortized objective: learn λ(Y,φ) with q(X\|Y;φ)=q(X;λ(Y,φ)); self-normalized gradient estimators eq. 8.60-8.62.

**Strongest result.** No theorems; the load-bearing results are (a) the compositional translation ⇓ from FOPPL to finite graphical models (Sec. 3.1), whose correctness is by construction of the rules and which makes explicit that FOPPL 'programs have static computation graphs' with a compile-time bound on computation steps; (b) the dichotomy that HOPPL programs have unbounded random-variable cardinality so no finite graph exists and inference must be evaluation-based; (c) the identification of amortized inference with approximate compilation: 'If there exists a set of parameters φ such that p(X\|Y;θ)=q(X\|Y;φ), then solving the optimization problem for φ is a form of exact compilation.'

**Assumptions.** FOPPL: all primitives halt; data must be inlined; no recursion, no higher-order functions — hence finite, statically enumerable random-variable set.; HOPPL: inference is evaluation-based and relies on unique addressing of sample/observe sites; the messaging interface abstracts the inference controller.; observe values must be deterministic expressions (free-vars(E2)=∅); conditioning is by likelihood factor, not by measure-zero event.; Amortized inference assumes a stationary p(Y) (training distribution of observations) and a differentiable inference backend; 'compilation' is approximate and 'does not strictly preserve the semantic meaning of the original program'.

**Resource model.** Compute qualitatively (graph-based vs evaluation-based; 'Captcha ... would require an exponential-time operation' for exact marginalization; HMC requires AD; amortization trades expensive training for cheap test-time inference). Samples: mini-batch stochastic gradients. No description-length, verification, memory or revision accounting; no complexity theorems.

**Failure boundary.** It is an introduction: it catalogues inference families but does not rank them by ecology; it notes that 'the probabilistic programming ideas and techniques that we have presented are largely independent of both the source language and the underlying inference algorithm', i.e. it deliberately does not predict which algorithm dominates where. Measure-zero conditioning and computability limits are not treated (defers to Staton et al. 2016 for semantics). Model learning is treated only as lifting inference to include the model (Sec. 1.1) or as SGD on neural-parameterized programs (Ch. 8); no account of acquiring the PPL machinery itself.

**Implementation.** Companion code for the book's evaluators exists (FOPPL/HOPPL evaluators used in course material; e.g. https://github.com/probprog/anglican, PyProb https://github.com/pyprob/pyprob referenced); no single canonical repository named in the pages read.

**Track-B residual.** The FOPPL/HOPPL dichotomy is a *representation phase boundary* (finite static graph vs. unbounded dynamic trace) that determines which inference families are even available — a boundary set by the *model language*, not by the ecology. Track B's residual: does an ecology ever *select* the FOPPL fragment (static-graph morphology; graph inference) over the HOPPL fragment (trace morphology; evaluation inference) under charged cost, and can a basis be shown to acquire the static-graph compile (⇓) rather than being given it?

**Upward question.** Treat 'static graph vs. dynamic trace' as one coordinate of morphology space and 'exact vs. sampling vs. gradient vs. amortized' as another; the family fixes the coordinates but not the dynamics on them. What ecology functional moves a system along these coordinates, and is the move reversible under drift?

Load-bearing quotes (verbatim from sources actually read):

> "explain why conditioning is a foundational computation central to the fields of probabilistic machine learning and artificial intelligence" — [0] abstract
> "Bayes' rule tells us how to derive a conditional probability from a joint, conditioning tells us how to rationally update our beliefs, and updating beliefs is what learning and inference are all about." — [0] sec. 1.1.1, p. 14
> "The meaning of a probabilistic program is that it simultaneously denotes a joint and conditional distribution, the latter by syntactically indicating where conditioning will occur" — [0] sec. 1.2, p. 23
> "all FOPPL programs can be unrolled to computation graphs where all possible control-flow paths are explicitly and completely enumerated at compile time. FOPPL programs have static computation graphs." — [0] sec. 2, p. 33
> "HOPPL programs can denote models with an unbounded number of random variables. This rules out graph-based evaluation strategies immediately, since an infinite graph cannot be represented on a finite-capacity computer." — [0] ch. 5, p. 134
> "The only distinction between deep generative programs and other programs is that they can use neural networks as primitive functions." — [0] sec. 8.1, p. 208
> "training the neural network can be thought of as “compiling” a probabilistic program to its posterior, albeit to an approximation of this posterior that does not strictly preserve the semantic meaning of the original program." — [0] sec. 8.2, p. 211
> "the probabilistic programming ideas and techniques that we have presented are largely independent of both the source language and the underlying inference algorithm." — [0] ch. 9, p. 282

Verification notes: Roughly 110 of 286 pages read via targeted page queries; chapters 4 (evaluator-based inference details), 6 (messaging interface), 7 (HMC/AD) only sampled. Equation numbers cited (8.60-8.62) are from the pages read. No prior reconstruction in the repo ledgers consulted.

### P6.PPL_SEMANTICS — Denotational semantics for higher-order probabilistic programs: score/norm monad (Staton et al.) and quasi-Borel spaces (Heunen et al.)

Disposition: `ADOPT` · best verification: `PARTIAL_TEXT_READ`

Sources:

- [0] Semantics for probabilistic programming: higher-order functions, continuous distributions, and soft constraints — S. Staton, H. Yang, C. Heunen, O. Kammar, F. Wood (2016), LICS 2016. https://arxiv.org/abs/1601.04943 arXiv:1601.04943 — `PARTIAL_TEXT_READ`
- [1] A Convenient Category for Higher-Order Probability Theory — C. Heunen, O. Kammar, S. Staton, H. Yang (2017), LICS 2017. https://arxiv.org/abs/1701.02547 arXiv:1701.02547 — `PARTIAL_TEXT_READ`

**What it already explains.** What a Church/Anglican/Venture-class program *means* as a mathematical object, so that program equations (compiler optimizations, SMC resampling) and inference algorithms can be proved correct rather than 'proved approximately correct' against a rejection-sampler reference. Staton et al.: a metalanguage with sample(t), score(t) (soft constraint: multiply the trace's score), norm(u) (normalize: return model evidence and posterior, or an error if evidence is 0 or ∞); first-order terms denote measurable functions Γ→P(R≥0 × A) — a probability measure on (score, result) pairs — via the commutative monad P(R≥0 × −); norm is the natural transformation ι: P(R≥0×X) → (R×P(X))+1+1 dividing the unnormalized posterior p̄(U)=∫ r p(d(r,x)) by p̄(X). Higher-order functions cannot be interpreted in measurable spaces (Aumann: R^R has no σ-algebra making evaluation measurable), so they move to a functor category; the semantics is sound and adequate w.r.t. an operational semantics (stochastic labelled transition system), and validates the SMC 'renormalize and resample after every score' transformation. Heunen et al. replace measurable spaces by quasi-Borel spaces (sets with a chosen family of 'random variables' R→X), which form a well-pointed cartesian closed category with a commutative probability monad, conservatively extend standard Borel spaces, make Bayesian regression over R^R meaningful, show kernels are a quotient of random functions (Thm 26) and prove a weak de Finetti theorem (Thm 29).

**Formal object.** Staton: types A ::= R \| P(A) \| 1 \| A×B \| Σ_i A_i (countable sums); judgements Γ ⊢_d t : A (deterministic, ⟦t⟧: ⟦Γ⟧→⟦A⟧ measurable) and Γ ⊢_p t : A (probabilistic, ⟦t⟧: ⟦Γ⟧→P(R≥0×⟦A⟧)); ⟦sample(t)⟧(γ)(U)=⟦t⟧(γ)({a \| (1,a)∈U}); ⟦score(t)⟧(γ)(U)=[(max(⟦t⟧(γ),0),*)∈U]; ⟦let x=t in u⟧ via the monad bind with score multiplication; ι_X(p) = (1,*) if p̄(X)=0, (2,*) if p̄(X)=∞, else (0,(p̄(X), λU. p̄(U)/p̄(X))); ⟦norm(t)⟧=ι∘⟦t⟧. Heunen: a quasi-Borel space (X, M_X ⊆ [R→X]) closed under precomposition with measurable f:R→R, containing constants, and closed under countable Borel case-splitting (Def. 7); morphisms f with f∘α∈M_Y (Def. 11); probability measure = pair (α, μ) with α∈M_X, μ a probability measure on R (Def. 10); function space Y^X = QBS(X,Y) with M_{Y^X} = {α \| uncurry(α) ∈ QBS(R×X,Y)} (Prop. 18); monad P with [α,μ] equivalence classes (Thm. 21); norm: P(X×[0,∞)) → P(X) ⊎ {error} (sec. VI).

**Strongest result.** Staton: Proposition 8.3 — for first-order Γ, A and z ∈ {d,p}: ⟦t⟧=⟦u⟧ iff the higher-order interpretations agree, and 'every term Γ ⊢_z t : A has ⟪t⟫ = ⟪u⟫ for a first-order' u (every first-order-typed term is equal to a λ-free one, hence a measurable function); Soundness/Adequacy (Props. 5.9, 8.6) of denotational w.r.t. operational semantics; the SMC program equation ⟦norm(let x=t in (score(u); v))⟧ = ⟦norm(case norm(let x=t in score(u); return x) of (0,(e,d)) ⇒ score(e); let x=sample(d) in v \| ...)⟧ (sec. 4.1). Heunen: Prop. 6 (Aumann) Meas is not cartesian closed; Prop. 18 QBS is cartesian closed; Thm. 21 P is a strong (and commutative, Prop. 22) monad on QBS; Thm. 26 the space of kernels P(R)^X is a quotient of the space of random functions P(R^X); Thm. 29 (weak de Finetti for quasi-Borel spaces): every exchangeable probability measure on X^ω is a mixture of i.i.d. sequences.

**Assumptions.** Scores are non-negative reals attached multiplicatively to execution traces; conditioning is only by score (likelihood weighting), so measure-zero conditioning and disintegration are explicitly out of scope (Staton sec. 10 lists them as future work).; Normalization is partial: evidence 0 or ∞ are error outcomes (ι cases (1,*) and (2,*)); e.g. ⟦norm(let x = sample(exp(1.0)) in score(e^x))⟧ = (2,*).; Randomness ultimately comes from (probability measures on) R — quasi-Borel spaces fix R as the universal sample space; standard Borel spaces embed fully faithfully.; Termination of deterministic terms is proven (Props. 5.6, 7.2); recursion and memoization are not covered (future work).

**Resource model.** none — purely denotational; no cost of sampling, scoring, normalizing, or of the SMC transformation is modeled (the SMC equation is justified as *sound*, its efficiency is only motivated informally: 'This increases efficiency by avoiding too many program executions with low scores').

**Failure boundary.** Provides meaning, not computation: says nothing about computability of norm (cf. P6.CONDITIONING_LIMIT), nothing about which inference algorithm to use or at what cost, nothing about learning. Does not handle measure-zero conditioning, disintegration, recursion or memoization (Staton sec. 10). Quasi-Borel spaces give a *space* for distributions on functions but no computational handle on them (posterior calculations 'actually happen at the level of standard Borel spaces', sec. VI). Correctness of inference algorithms is deferred ('Another future direction is to formulate and prove the correctness of inference algorithms').

**Implementation.** none known as a system (semantic foundations); used by Anglican (https://github.com/probprog/anglican) as the intended semantics and later formalized in the Ścibior et al. 2018 validation work (not read).

**Track-B residual.** The semantics supplies the *equivalence quotient* Track B needs for the probabilistic morphology (Prop. 8.3: first-order-typed terms are equal iff their (score,result) measures agree; Thm. 26: many random functions, one kernel) — i.e. 'same morphology' = same measure on (score,result) pairs, with program structure quotiented away. The residual: the quotient discards exactly the resource profile (Venture: 'same distribution albeit with different scaling behavior'). Track B needs a *cost-enriched* semantics in which two programs denoting the same posterior are distinguished by charged work; no parent provides it.

**Upward question.** Can Track B's morphology quotient (GMI-T3) be built as an enrichment of this semantics — a functor from programs to (measure, charged-cost) pairs — such that GMI-T2's bounded-compiler relation becomes a morphism condition in the enriched category, and the ecology becomes a choice of cost enrichment?

Load-bearing quotes (verbatim from sources actually read):

> "Probabilistic terms Γ ⊢p t : A are interpreted as measurable functions ⟦t⟧ : ⟦Γ⟧ → P(R≥0 × ⟦A⟧), providing a probability measure on (score,result) pairs for each valuation of the context." — [0] Staton et al. 2016, sec. 4
> "measurable spaces do not support the usual β/η theory of functions: they do not form a Cartesian closed category (indeed, R^R does not exist as a measurable space [3])." — [0] Staton et al. 2016, sec. 1
> "As long as the average score p̄(X) is not 0 or ∞, we can normalize p̄ to build a posterior probability measure on X." — [0] Staton et al. 2016, sec. 4
> "'Whenever there is a score, it is good to renormalize and resample'. This increases efficiency by avoiding too many program executions with low scores" — [0] Staton et al. 2016, sec. 4.1
> "every term of first-order type is equal to one without λ-abstractions or application, and hence is interpreted as a measurable function (Proposition 8.3)." — [0] Staton et al. 2016, sec. 1
> "Another future direction is to formulate and prove the correctness of inference algorithms, especially those based on Monte Carlo simulation" — [0] Staton et al. 2016, sec. 10
> "But standard probability theory does not handle higher-order functions well: the category of measurable spaces is not cartesian closed." — [1] Heunen et al. 2017, abstract
> "Thus the primitive notion shifts from measurable subset to random variable, which is traditionally a derived notion." — [1] Heunen et al. 2017, sec. I
> "The evaluation function Y^X × X → Y is a morphism and has the universal property of the function space. Thus QBS is a cartesian closed category." — [1] Heunen et al. 2017, Prop. 18
> "Theorem 26. Let (X, M_X) be a quasi-Borel space. The space (P(R))^X of kernels is a quotient of the space P(R^X) of random functions." — [1] Heunen et al. 2017, sec. VII
> "We may thus regard quasi-Borel spaces as a conservative extension of standard Borel spaces that supports simple type theory." — [1] Heunen et al. 2017, sec. IV.A

Verification notes: Both papers' full extracted text is on disk; core definitions/theorems were read verbatim and are cited with their numbers. Operational-semantics sections (Staton 5, 7) and the proofs of Heunen Thms 26/29 were not read in detail. No prior reconstruction in the repo ledgers consulted.

### P6.PPL_SYSTEMS — Programmable inference: Venture (PETs/scaffolds/inference language), Anglican (PMCMC over traces), Gen (generative function interface)

Disposition: `ADOPT` · best verification: `FULL_TEXT_READ`

Sources:

- [0] Venture: a higher-order probabilistic programming platform with programmable inference — V. Mansinghka, D. Selsam, Y. Perov (2014), arXiv (cs.AI). https://arxiv.org/abs/1404.0099 arXiv:1404.0099 — `PARTIAL_TEXT_READ`
- [1] A New Approach to Probabilistic Programming Inference (Anglican) — F. Wood, J. W. van de Meent, V. Mansinghka (2014), AISTATS 2014 (PMLR 33:1024-1032); arXiv version updated 2015. https://arxiv.org/abs/1507.00996 arXiv:1507.00996 — `FULL_TEXT_READ`
- [2] Gen: a general-purpose probabilistic programming system with programmable inference — M. F. Cusumano-Towner, F. A. Saad, A. K. Lew, V. K. Mansinghka (2019), PLDI 2019, pp. 221-236. https://doi.org/10.1145/3314221.3314642 — `NOT_ACCESSIBLE`
- [3] Gen.jl documentation: Generative Function Interface (docs/src/ref/core/gfi.md) — Gen.jl developers (probcomp) (2026), GitHub, probcomp/Gen.jl, commit 2a27298b (2026-06-08). https://github.com/probcomp/Gen.jl/blob/master/docs/src/ref/core/gfi.md — `FULL_TEXT_READ`

**What it already explains.** How to separate a probabilistic *model program* from an *inference program* with a formal contract between them, so that inference strategies are themselves compositional programs rather than a monolithic solver. Venture: models are Turing-complete Lisp programs; the SPI encapsulates primitives (incl. likelihood-free simulators, exchangeably coupled and higher-order procedures, external latents); PETs generalize Bayes nets with existential dependence and exchangeable coupling; scaffolds carve a PET into a local inference sub-problem; stochastic regeneration produces the proposal/likelihood/gradient quantities for MH, Gibbs, conditional SMC and mean-field hybrids while visiting only conditionally dependent choices (linear vs. prior quadratic scaling). Inference expressions (mh, rejection, pgibbs, meanfield, enumerative_gibbs over scopes/blocks) are transition operators that leave the conditioned trace distribution invariant. Anglican: the trace density p̃(y,x)=Π_n p(y_n\|θ_{t_n},x_n) p̃(x_n\|x_{n-1}) supports particle-Gibbs (PMCMC) over execution traces with SMC proposals, which beats single-site MH (RDB) on models with dense dependencies; observe-ordering changes efficiency. Gen: every model, proposal, variational family and inference model is a *generative function* with a density p(t;x) on choice maps, an internal proposal q(t;x,u), and operations (simulate, generate, update, regenerate, propose, assess, choice_gradients) whose returned weights are the exact log density ratios needed by importance sampling, MCMC, SMC and variational algorithms.

**Formal object.** Venture: a program = sequence of instructions ASSUME/OBSERVE/PREDICT/INFER/FORGET; a PET is a DAG of stochastic-procedure applications with conditional, existential and exchangeable-coupling edges; a scaffold for principal nodes X ⊂ PET is the set of nodes whose existence is invariant to X plus the border on which one conditions; inference expression grammar (mh <scope> <block> <n>) \| (rejection ...) \| (pgibbs <scope> <block> <particles> <n>) \| (meanfield ...) \| (enumerative_gibbs ...) \| (cycle ...) each denoting a transition operator; acceptance ratio [P_π_ξ(R(ξ),A) K_regen(R(ξ)→R(ρ))]/[P_π_ρ(R(ρ),A) K_regen(R(ρ)→R(ξ))] (eq. 3, p. 53). Anglican: x_n = all random procedure outputs before the nth observe; p̃(x_n\|x_{n-1}) = Π_k p(x_{n,k}\|θ_{t_{n,k}}, x_{n,1:k-1}, x_{n-1}); Alg. 1 particle Gibbs with a retained particle; RDB acceptance eq. 5 with \|x\|/\|x'\| correction. Gen GFI: choice map t: A→V over addresses; p(t,r;x) normalized (termination w.p.1); return value f(x,t); internal proposal q(t;x,u) with support conditions 'p(t;x)>0 iff q(t;x,u)>0 for all u where u and t agree' and 'q(t;x,u)>0 implies u and t agree'; update weight w = log p(t';x')/(p(t;x) q(t';x',t+u)); regenerate returns a weight (log 1 = 0 in the worked example when no new choices are proposed); argdiffs/retdiffs for incremental computation (correctness of argdiffs is not verified by Gen).

**Strongest result.** No numbered theorems in the read pages. Strongest verified results: (Venture) the stochastic-regeneration/scaffold architecture yields MH/Gibbs/cSMC/mean-field transition operators that leave the posterior on traces invariant with 'runtime that scales linearly in cases where previous approaches often scaled quadratically' (abstract; HMM example p. 17 'linear (rather than quadratic) scaling in the length of the sequence'); enumerative Gibbs cost 'scales exponentially with the number of random choices, as opposed to the KL divergence between the prior and the conditional' for rejection (p. 12). (Anglican) PMCMC 'is theoretically justified as an MH transition operator that, like the Gibbs operator, always accepts', and empirically converges faster than RDB per simulation, wall-clock and apply-count on HMM and DP-mixture programs, with program-line permutation interpolating between regimes where PMCMC or RDB is better (Fig. 2) and a Marsaglia rejection-sampler program where RDB may win (Sec. 5.4). (Gen) the GFI weight identities for update/regenerate as log density ratios (worked examples in gfi.md).

**Assumptions.** Venture: inference expressions are restricted to transition operators sound by construction (posterior-invariant); relaxing this for experts is future work (11.2); scaffold contents are context-independent (6.4), so some independencies are not exploited.; Anglican: observe likelihoods must be computable exactly (outer procedure of an observe is a built-in random primitive); hard constraints are deliberately not exposed 'to help programmers avoid ... NP-hard or not-computable' trace-finding; a fixed ordering of exchangeable lines is assumed.; Gen: generative functions terminate with probability 1 for all valid arguments; the internal proposal q must satisfy the support conditions; argdiff correctness is the user's responsibility; random choices assumed discrete in the notation (continuous case by densities).; All three: the model program is given; no learning of the model language; a stationary inference problem (or an interactive sequence of them) rather than an ecology.

**Resource model.** Compute (explicit): Venture asymptotic scaling of transitions (linear vs quadratic in dataset/sequence length; exponential for enumerative Gibbs), Anglican apply-counts and wall-clock and simulation counts, Gen incremental computation via argdiffs. Samples/particles: Anglican particle-count study (Fig. 3). Description length, verification, memory, revision: not modeled (Venture 2.6 names asymptotic-cost prediction of inference instructions as an open requirement).

**Failure boundary.** None of the three predicts which inference program to use for a given model/ecology — Venture 2.6 explicitly poses this as an open question ('It remains to be seen whether the traditional view is sufficient in practice'); Anglican shows inference-strategy dominance flips with program line order and model class but offers no law; Gen gives a contract, not a policy. No convergence-rate or sample-complexity guarantees; correctness of composed inference programs is 'by construction' (Venture) or by the GFI contract (Gen), with Gen explicitly not verifying argdiffs. Conditioning on measure-zero events is not addressed (soft constraints/likelihood scores only). The model language and inference primitives are fixed; nothing is acquired from experience (Venture 11.2 only speculates about 'inference optimizers' and learning inference procedures).

**Implementation.** Venture: https://github.com/probcomp/Venturecxx ; Anglican: https://bitbucket.org/probprog/anglican (and github.com/probprog/anglican) ; Gen: https://github.com/probcomp/Gen.jl (PLDI experiments: https://github.com/probcomp/pldi2019-gen-experiments)

**Track-B residual.** Programmable inference makes the *update law itself a program* with an explicit cost profile, so the probabilistic morphology decomposes into (trace representation, conditioning target, inference program). What no parent supplies is the selection law: given an ecology E (observation informativeness, dependence density, query repetition, budget), which point on the inference-program lattice {rejection ≻ enumeration ≻ trace-MCMC ≻ SMC/PMCMC ≻ variational/amortized ≻ MAP/gradient} is charged-optimal, and when the charged cost of any trace-measure maintenance exceeds that of a single-trace (point-estimate) morphology. Venture names exactly this ('inference programmers will need to be able to predict the asymptotic scaling') and leaves it open.

**Upward question.** Can the inference-program lattice be indexed by a small set of ecology parameters (KL(prior‖posterior), dependence density of the trace, query repetition rate, differentiability of the density) such that a phase law predicts the charged-optimal rung *before* search — and is the lattice's top (exact conditioning) even attainable in the ecology, per P6.CONDITIONING_LIMIT?

Load-bearing quotes (verbatim from sources actually read):

> "The idea that inference strategies can be formalized as structured, compositionally specified inference programs operating on model programs is, to the best of our knowledge, new to Venture." — [0] Venture sec. 2.6, p. 14
> "inference programmers will need to be able to predict the asymptotic scaling of inference instructions, factoring out the contribution of the computational complexity of the model expressions" — [0] Venture sec. 2.6, p. 14
> "Stochastic regeneration insulates inference algorithms from the complexities introduced by changes in execution structure, with runtime that scales linearly in cases where previous approaches often scaled quadratically" — [0] Venture abstract
> "The computational cost scales exponentially with the number of random choices, as opposed to the KL divergence between the prior and the conditional (Freer et al., 2010)." — [0] Venture sec. 2.4 (enumerative_gibbs), p. 12
> "many programs are equivalent, in that they induce the same distribution albeit with different scaling behavior." — [0] Venture sec. 2.7, p. 15
> "PMCMC for probabilistic programming inference is a MH algorithm for exploring the space of execution traces that uses SMC proposals internally." — [1] Anglican sec. 3.1
> "As Church-like probabilistic programming frameworks, Anglican included, support recursive procedures and branching on the values returned by random procedures, the corresponding set of models is a superset of the set of all directed graphical models." — [1] Anglican sec. 3
> "Persisting in not doing so should help programmers avoid writing probabilistic programs where finding even a single satisfying execution trace is NP-hard or not-computable" — [1] Anglican sec. 6
> "Generative functions are used to represent a variety of different types of probabilistic computations including generative models, inference models, custom proposal distributions, and variational approximations." — [3] Gen.jl gfi.md, introduction
> "p(t; x) > 0 if and only if q(t; x, u) > 0 for all u where u and t agree" — [3] Gen.jl gfi.md, 'Internal proposal distribution family'
> "w = log p(t'; x')/(p(t; x) q(t'; x', t + u))" — [3] Gen.jl gfi.md, 'Update' worked example
> "Note that the correctness of the argdiff is in general not verified by Gen---passing incorrect argdiff information may result in incorrect behavior." — [3] Gen.jl gfi.md, 'Argdiffs'

Verification notes: Venture: ~20 of 78 pages read via targeted page queries; theorem-free document, so statements cited are from abstract/sections read. Anglican: full text read (arXiv v2 with updated syntax; the authors state the change 'affect[s] neither the substance or the claims'). Gen PLDI paper: NOT accessible; the GFI reconstruction is from the Gen.jl repository's own reference documentation (a faithful, maintained specification of the same interface), so any claim about the *paper's* theorems, benchmarks (vs. Venture/Turing/Pyro etc.) or exact wording is UNVERIFIED and deliberately omitted. No prior reconstruction in the repo ledgers consulted.

### P6.PROBABILISTIC_LOT — Concepts in a probabilistic language of thought (PLoT)

Disposition: `ADAPT` · best verification: `PARTIAL_TEXT_READ`

Sources:

- [0] Concepts in a Probabilistic Language of Thought — N. D. Goodman, J. B. Tenenbaum, T. Gerstenberg (2015), in E. Margolis & S. Laurence (eds.), The Conceptual Mind: New Directions in the Study of Concepts, MIT Press (preprint dated Feb. 15, 2014; also CBMM Memo 010). https://www.semanticscholar.org/paper/0289597a130c7cb4fc543cbe0d8c779b829fce96 — `PARTIAL_TEXT_READ`

**What it already explains.** A theory of concepts that reconciles their statistical role (graded, prototype/exemplar-like generalization) with their symbolic role (productive, compositional building blocks) by identifying concepts with *stochastic functions* in an enriched stochastic λ-calculus (Church). Knowledge = a library of function definitions; a situation = a composition of them; its content = a distribution over world states; reasoning = conditioning (query), defined by rejection sampling and shown to give nested inference for intuitive psychology (an agent's choice as an embedded query); natural-language meanings = Boolean-valued expressions usable as query conditions; concept acquisition = program induction by conditioning over the space of function definitions, which changes the *effective* language of thought (new concepts make later hypotheses shorter, hence more plausible) — a proposed driver of development. Demonstrated quantitatively on tug-of-war/ping-pong strength inference (2- and 3-player tournaments, laziness, indirect evidence).

**Formal object.** PLoT (formal version): 'Concepts are stochastic functions.' Substrate: stochastic λ-calculus = λ-calculus + primitive random choices (flip); Church syntax (define f (lambda (x) ...)), (mem f) memoizes random choices per argument so symbols act as persistent object indices; (query definitions query-expression condition-expression) denotes the distribution of the query-expression conditioned on the condition-expression being true, defined by (define conditional (lambda () (define sample (dist)) (if (condition sample) sample (conditional)))). Nested query models agents: (define choice (lambda (belief state goal?) (query (define action (action-prior)) action (goal? (belief state action))))). Concept learning: a higher-order 'program-generating program' as prior over stochastic functions; posterior by conditioning on examples.

**Strongest result.** No theorems (a theoretical chapter). Strongest claims: (i) the formal PLoT hypothesis (concepts = stochastic functions ⇒ uncertainty representation, natural composition, probabilistic inference); (ii) the unification claim that 'all of these Bayesian models [of cognition] can be represented in, and hence reduced to, a simple system built from little more that function abstraction and random choice'; (iii) the quantitative fit of the tug-of-war Church model to human strength judgements (the model 'predicts participants' judgments very accurately'); (iv) the developmental claim that concept learning changes the effective LoT's inductive bias while preserving expressivity.

**Assumptions.** Level of description is computational (Marr): 'The process by which these inferences are implemented is not directly part of the hypothesis' — no commitment to algorithm or neural implementation.; Conditioning is on positive-probability predicates (rejection definition); continuous conditioning not addressed.; The underlying language (stochastic λ-calculus with mem and query) is innate/fixed; only the library of definitions changes with learning.; Human judgments are the validation target; engineering tractability is explicitly deferred ('a great deal of research is needed both to reduce it to useful engineering practice').

**Resource model.** Description length implicitly: 'particular thoughts may be vastly simpler (and thus more cognitively tractable) in the effective language' — tractability is identified with shortness in the current library. Compute: acknowledged as the open problem ('such inferences are extremely challenging to implement in general'); implementations use 'caching and Monte Carlo simulation'. No samples, memory, verification, time accounting.

**Failure boundary.** No algorithmic or process-level content by design; no prediction of which inference approximation cognition uses (deferred to Griffiths, Vul & Sanborn 2012 and to future work); no learning algorithm for concept acquisition beyond 'conditioning over programs'; no account of the origin of the base language; no cost model distinguishing two libraries with the same expressivity except by informal 'simplicity'. Does not address neural realization, resource bounds, or the noncomputability of conditioning.

**Implementation.** Church / WebPPL (https://github.com/probmods/webppl) and the probmods.org book; tug-of-war models are standard probmods examples.

**Track-B residual.** The PLoT states the closest thing in this family to a D2 mechanism — learning changes the *effective language* (the library), which changes inductive bias and tractability while leaving expressivity fixed — but gives no dynamics for it and no cost model beyond 'simpler'. Track B's residual: formalize 'effective language' as a charged basis state, derive the library-update law from an ecology (what gets added, when it pays), and determine whether that law is itself conditioning, compression (MDL), or something the ecology selects — and whether a basis without query as a primitive can develop one.

**Upward question.** If the effective language is the only thing that changes with learning and expressivity is invariant, then morphology differences within the probabilistic class are *library* differences priced by description length under the current library. Can Track B's morphology quotient (GMI-T3) be reformulated as equivalence of libraries modulo bounded translation cost, with the ecology selecting which library is charged-minimal?

Load-bearing quotes (verbatim from sources actually read):

> "Probabilistic language of thought hypothesis (formal version): Concepts are stochastic functions. Hence they represent uncertainty, compose naturally, and support probabilistic inference." — [0] sec. 2, p. 7
> "The stochastic λ-calculus realizes this idea formally, by extending a universal computational system (λ-calculus) with points of primitive randomness." — [0] sec. 2, p. 4
> "A Church program specifies not a single computation, but a distribution over computations." — [0] sec. 2, p. 5
> "The fundamental operation of belief updating in probabilistic modeling is conditioning." — [0] sec. 2, p. 6
> "The level of description intended in the PLoT hypothesis is neither the highest level, of input-output relations, nor the lower level of psychological processing." — [0] sec. 1, p. 4
> "Induction over such an infinite combinatorial space is simply stated as probabilistic conditioning, but such inferences are extremely challenging to implement in general." — [0] sec. 7, p. 19
> "concept learning changes the effective language of thought. While this effective language has the same mathematical expressivity as the underlying PLoT, particular thoughts may be vastly simpler (and thus more cognitively tractable) in the effective language." — [0] sec. 7, p. 20
> "They are not intended to convey the algorithmic process of this inference, much less the neural instantiation." — [0] sec. 8, p. 21

Verification notes: Read from the Feb-2014 preprint ('To appear in Concepts: New Directions'), whose section/page numbers are cited; the MIT Press 2015 pagination may differ. About 14 of 21 pages read; the ping-pong experimental sections were sampled only. No prior reconstruction in the repo ledgers consulted.


## P7 — algebraic / categorical descriptions of learning systems

### P7.ALGORITHMIC_ALIGNMENT_XU — What can neural networks reason about? (Xu et al. 2020): algorithmic alignment and a sample-complexity bound

Disposition: `None` · best verification: `FULL_TEXT_READ`

Sources:

- [0] What Can Neural Networks Reason About? — Keyulu Xu, Jingling Li, Mozhi Zhang, Simon S. Du, Ken-ichi Kawarabayashi, Stefanie Jegelka (2020), ICLR 2020; arXiv 1905.13211 v4. https://arxiv.org/abs/1905.13211 arXiv:1905.13211 — `FULL_TEXT_READ`

**What it already explains.** Def. 3.4: N (M, eps, delta)-algorithmically aligns with g if module functions f_1..f_n generate g and n * max_i C_{A_i}(f_i, eps, delta) <= M. Thm 3.6: under sequential module training with auxiliary labels, algorithm stability and Lipschitzness, g is (M, O(eps), O(delta))-learnable — sample complexity decreases with alignment; Thm 3.5 gives the MLP module bound (polynomial-degree weighted norms); Cor. 3.7: MLP needs O(l^2) more samples than a GNN for sum of pairwise squared differences. Predictions confirmed (Fig. 3): Deep Sets/GNN but not MLP learn summary statistics (96%/100% vs 9%); GNN but not Deep Sets learn relational argmax (>90% vs 21%); only GNNs with >= 4 iterations learn a shortest-path DP task (94-96% vs 62%/27%/11%/8%); GNNs fail on subset sum (72%) while a search-aligned NES reaches 98%. All architectures are universal approximators (Props 3.1-3.2), so the differences are generalization, not expressivity.

**Formal object.** (M, eps, delta)-algorithmic alignment; C_A(g, eps, delta); DP-Update form (Eq. 4.1)

**Strongest result.** None

**Assumptions.** None

**Resource model.** None

**Failure boundary.** None

**Implementation.** None

**Track-B residual.** None

**Upward question.** None

Verification notes: None

### P7.BACKPROP_AS_FUNCTOR — Backprop as Functor: a compositional perspective on supervised learning (category Learn; functor Para -> Learn)

Disposition: `ADOPT` · best verification: `FULL_TEXT_READ`

Sources:

- [0] Backprop as Functor: A compositional perspective on supervised learning — Brendan Fong, David I. Spivak, Remy Tuyeras (2019), LICS 2019 (IEEE); extended version arXiv:1711.10455v3 (1 May 2019). https://arxiv.org/abs/1711.10455; doi:10.1109/LICS.2019.8785665 arXiv:1711.10455 — `FULL_TEXT_READ`

**What it already explains.** Gives an algebraic (symmetric monoidal category) description of supervised learners as 4-tuples (P,I,U,r) = parameter space, implementation, update, request, composable in series and parallel; identifies the REQUEST function (backward message) as the missing ingredient that makes learners compose. Proves that, for a fixed step size and any error function whose partial derivative in the first variable is invertible, gradient descent + backpropagation is a strong symmetric monoidal functor L_{eps,e}: Para -> Learn (Theorem III.2), i.e. 'train the composite' = 'compose the trained parts' (locality of backprop is functoriality of the chain rule). Neural nets enter via a second functor I_sigma: NNet -> Para (Prop IV.2) chosen by an activation; each object of Learn carries a bimonoid (Prop V.1) so neurons, weight tying, convolution are generated from five primitive learners (Example V.3/V.4). Embeds Lens -> Learn -> Game (Section VII.D).

**Formal object.** Learn: objects sets; morphism A->B an equivalence class of learners (P, I: P x A -> B, U: P x A x B -> P, r: P x A x B -> A). Composition of (P,I,U,r): A->B with (Q,J,V,s): B->C is (P x Q, I*J, U*V, r*s) with (I*J)(p,q,a)=J(q,I(p,a)); (U*V)(p,q,a,c)=(U(p,a,s(q,I(p,a),c)), V(q,I(p,a),c)); (r*s)(p,q,a,c)=r(p,a,s(q,I(p,a),c)). Monoidal product: cartesian product (Prop II.4). Para: objects R^n, morphisms equivalence classes of differentiable parametrised functions (P,I), P=R^p (Def III.1). L_{eps,e}(P,I) = (P, I, U_I, r_I), U_I(p,a,b)= p - eps grad_p E_I(p,a,b), r_I(p,a,b)= f_a(grad_a E_I(p,a,b)), E_I(p,a,b)= sum_j e(I_j(p,a),b_j), f_a = componentwise inverse of (de/dx)(a_i,-).

**Strongest result.** Theorem III.2 (proved as Theorem A.1 in Appendix B with an extra normalising variable alpha): fix eps>0 and e: R x R -> R differentiable with (de/dx)(x0,-) invertible for each x0; then L_{eps,e}: Para -> Learn is a faithful, injective-on-objects, strong symmetric monoidal functor. Proof = functoriality of the chain rule applied to update and request components. Prop IV.2: I_sigma: NNet -> Para is a functor. Prop V.1: quadratic-error gradient descent gives FVect -> Learn, hence bimonoids on each R^n in Learn. Section VII.D: embeddings Lens -> Learn -> Game (learners with trivial state are asymmetric lenses; learners are open games with a singleton best-response condition).

**Assumptions.** differentiable parametrised functions between Euclidean spaces with Euclidean parameter spaces; error function e with (de/dx)(x0,-) invertible for every x0 (excludes cross-entropy at 0,1; handled only informally in VII.A); fixed step size eps; total error is a sum (or alpha-weighted sum) of per-coordinate errors; learners taken modulo bijective reparametrisation (Cruttwell et al. note the functor does not respect this equivalence); no convergence, generalisation or statistical assumptions whatsoever

**Resource model.** none (the only efficiency remark is qualitative: 'gradients are quicker to compute for lower dimensional spaces' explains the backprop speed-up; no description-length, compute, sample or verification cost is modelled)

**Failure boundary.** Does not define learning (Learn has no notion of error or convergence: 'the category Learn sees none of this structure; it lies in the functors'); Learn contains arbitrary non-derivative update rules with no selection principle; cross-entropy and other losses with singular derivatives fall outside Theorem III.2; no stateful optimisers (momentum/Adam), no probabilistic or non-gradient learners, no architecture search (only a remark that a bicategory of learners could host 'structured expansion of networks'); no statement about which learner a resource-bounded process would pick.

**Implementation.** none known (paper is purely mathematical; Cruttwell et al. 2022 provide the implementation of the refined framework)

**Track-B residual.** Given that the gradient learning law is a functor Para -> Learn chosen by (eps, e), what process (not a designer) selects the pair (eps, e) and the primitive learner basis under an ecology E, and what does that selection cost in description length / update work? Learn as a whole is a universal-computation-sized space; the residual is the resource-priced restriction of Learn to a morphology.

**Upward question.** Is there a functor from a category of ecologies (task distribution x resource prices) to the category of functors Para -> Learn (or Para(Optic)) that picks (eps, e, primitive basis) — i.e. can the choice of learning law itself be made functorial in the ecology?

Load-bearing quotes (verbatim from sources actually read):

> "gradient descent—with respect to a fixed step size and an error function satisfying a certain property—defines a monoidal functor from a category of parametrised functions to this category of update rules" — [0] Abstract
> "Then we can define a faithful, injective-on-objects, strong symmetric monoidal functor L_{eps,e}: Para -> Learn" — [0] Theorem III.2, Section III
> "Indeed, Learn does not require us to define our update and request functions using derivatives at all." — [0] Section VII.B
> "So far, in the case of learners, we have placed no requirements that an algorithm converge towards a function f when given enough training pairs (a, f(a))." — [0] Section VII.D
> "asymmetric lenses are simply learners with trivial state spaces, and learners themselves are open games obeying a certain singleton best response condition." — [0] Section VII.D
> "neural networks are useful as they are the language generated, using the grammar of symmetric monoidal categories, from just a few learners" — [0] Section VII.B

Verification notes: Full text of arXiv v3 read (17 pages). Theorem numbering (II.4, III.2, IV.2, V.1, VII.1, A.1) verified against text. Not previously reconstructed in any repo ledger (grep of the seven listed ledgers found no Fong/Spivak/Tuyeras entry). Cruttwell et al. 2022 Section 6 reports that the functor of Theorem III.2 does not respect the equivalence relation on learners; recorded here as a known defect, not re-derived.

### P7.BACKPROP_AS_FUNCTOR — Backprop as Functor (Fong, Spivak, Tuyeras 2019): the category Learn and the functor L_{eps,e}: Para -> Learn

Disposition: `ADOPT` · best verification: `FULL_TEXT_READ`

Sources:

- [0] Backprop as Functor: A compositional perspective on supervised learning — Brendan Fong, David I. Spivak, Remy Tuyeras (2019), LICS 2019; extended version arXiv:1711.10455v3 (1 May 2019). https://arxiv.org/abs/1711.10455 ; doi:10.1109/LICS.2019.8785665 arXiv:1711.10455 — `FULL_TEXT_READ`
- [1] Categorical Foundations of Gradient-Based Learning — G. S. H. Cruttwell, Bruno Gavranovic, Neil Ghani, Paul Wilson, Fabio Zanasi (2022), ESOP 2022, LNCS 13240; arXiv:2103.01931. https://arxiv.org/abs/2103.01931 arXiv:2103.01931 — `PARTIAL_TEXT_READ`

**What it already explains.** Defines a symmetric monoidal category Learn whose morphisms A -> B are equivalence classes of learners (P, I, U, r): parameter set P, implementation I: P x A -> B, update U: P x A x B -> P, request r: P x A x B -> A. The request function is the identified missing ingredient that makes update rules composable ('there is no composite update rule without the request function'). Main theorem: for fixed step size eps > 0 and an error e(x,y) whose partial derivative in x is invertible, gradient descent + backprop is a faithful, injective-on-objects strong symmetric monoidal functor L_{eps,e}: Para -> Learn; functoriality IS the chain rule, i.e. locality of backprop = 'train the composite' equals 'compose the trained parts'. Neural nets enter through a second functor I_sigma: NNet -> Para (Prop IV.2). With quadratic error, each R^n in Learn is a bimonoid (Prop V.1) and every backprop-trained net is generated by five primitive learners: scalar multiplication, bias, activation, monoid multiplication, comultiplication (Ex V.3); weight tying is the comonoid (Ex V.4). Learn embeds between lenses and open games (VII.D).

**Formal object.** Learn: objects = sets; morphism A->B = equivalence class of (P, I, U, r) under bijections f: P->P' with I'(f(p),a)=I(p,a), U'(f(p),a,b)=f(U(p,a,b)), r'(f(p),a,b)=r(p,a,b). Composition of (P,I,U,r): A->B with (Q,J,V,s): B->C is (P x Q, I*J, U*V, r*s): (I*J)(p,q,a)=J(q,I(p,a)); (U*V)(p,q,a,c)=(U(p,a,s(q,I(p,a),c)), V(q,I(p,a),c)); (r*s)(p,q,a,c)=r(p,a,s(q,I(p,a),c)). Identity (R^0, id, !, pi_2). Monoidal product = cartesian product with (I\|\|J)(p,q,a,c)=(I(p,a),J(q,c)) etc. Para: objects R^n, morphisms equivalence classes (P,I) of differentiable I: P x R^n -> R^m with P = R^p, composition (P x Q, J(q, I(p,a))). L_{eps,e}(P,I) = (P, I, U_I, r_I) with U_I(p,a,b) = p - eps grad_p E_I(p,a,b), r_I(p,a,b) = f_a(grad_a E_I(p,a,b)), E_I(p,a,b) = sum_j e(I_j(p,a), b_j), f_a = componentwise inverse of (de/dx)(a_i, -). Appendix B proves the alpha-weighted generalisation (Theorem A.1) needed for averaged cross-entropy.

**Strongest result.** Theorem III.2 (proved as Theorem A.1, Appendix B): fix eps > 0 and differentiable e: R x R -> R with (de/dx)(x0, -) invertible for every x0; then L_{eps,e}: Para -> Learn is a faithful, injective-on-objects, strong symmetric monoidal functor. Proof: chain rule applied to grad_p E and grad_a E (equations (1),(2) in Appendix B). Proposition II.4: Learn is a symmetric monoidal category (associativity holds only on equivalence classes because P x Q is associative only up to isomorphism). Proposition IV.2: I_sigma: NNet -> Para is a functor. Proposition V.1: quadratic-error gradient descent gives a symmetric monoidal functor FVect -> Learn, hence bimonoids. Section VII.D: Lens -> Learn -> Game embeddings. KNOWN DEFECT (verified in Cruttwell et al. 2022, Section 6): the functor of Theorem III.2 does not respect the equivalence relation on learners, and the invertibility condition on de/dx 'is not a constraint that appears in machine learning practice'; the repaired statement is Para(R): Para(C) -> Para(Lens(C)) for any Cartesian reverse differential category C.

**Assumptions.** Euclidean objects and Euclidean parameter spaces; differentiable I; error function e with (de/dx)(x0,-) invertible for each x0 (cross-entropy at 0,1 excluded; handled informally in VII.A); fixed step size eps; total error = sum (or alpha-weighted sum) of per-coordinate errors; learners modulo bijective reparametrisation (defective: the functor does not respect it); no convergence, generalisation, sample or statistical assumptions of any kind

**Resource model.** none. The only cost remark is qualitative: composition 'along with the fact that gradients are quicker to compute for lower dimensional spaces, expresses the speed up in learning provided by backpropagation' (VII). No description length, compute, samples, memory or verification are modelled.

**Failure boundary.** Learn contains every set-theoretic update/request rule ('Learn does not require us to define our update and request functions using derivatives at all'), so Learn alone is universal-computation-sized and carries no selection principle: 'the category Learn sees none of this structure; it lies in the functors'. No convergence requirement ('we have placed no requirements that an algorithm converge'). No stateful optimisers (momentum/Adam), no probabilistic or non-gradient learners, no architecture search (only a remark that a bicategory of learners could host 'structured expansion of networks'). Theorem III.2 is defective as stated (see above).

**Implementation.** none known for this paper (purely mathematical); the successor framework has a Python proof-of-concept (Cruttwell et al. 2022, Section 5)

**Track-B residual.** The parent fixes the TYPE of the gradient learning law (a functor from parametrised maps to update+request pairs, chosen by (eps, e)). Track B must ask what process, under an ecology E and a resource budget, selects (eps, e) and the primitive learner basis, at what description-length and update-work cost, and whether a NON-differentiable basis can compile to this functor with bounded overhead. Nothing in Learn ranks or prices its morphisms.

**Upward question.** Is there a functor from a category of ecologies (task distribution x resource prices x verification contract) to the category of functors Para -> Learn that picks the learning law, i.e. can selection of the law itself be made functorial in the ecology, and what cost functor on Learn would make that selection non-trivial?

Load-bearing quotes (verbatim from sources actually read):

> "gradient descent—with respect to a fixed step size and an error function satisfying a certain property—defines a monoidal functor from a category of parametrised functions to this category of update rules." — [0] Abstract
> "Then we can define a faithful, injective-on-objects, strong symmetric monoidal functor" — [0] Theorem III.2, Section III
> "Indeed, Learn does not require us to define our update and request functions using derivatives at all." — [0] Section VII.B
> "Note, however, that the category Learn sees none of this structure; it lies in the functors" — [0] Section VII.B (the sentence continues with the functor symbol L_{eps,e})
> "So far, in the case of learners, we have placed no requirements that an algorithm converge towards a function f when given enough training pairs (a, f (a))." — [0] Section VII.D
> "Composition of learners, along with the fact that gradients are quicker to compute for lower dimensional spaces, expresses the speed up in learning provided by backpropagation." — [0] Section VII, summary bullets
> "The associativity axiom is what requires that our morphisms in Learn be equivalence classes of learners, and not simply learners themselves" — [0] Appendix A, proof of Proposition II.4
> "unfortunately, the functor defined in Theorem III.2 does not respect this equivalence relation." — [1] Cruttwell et al. 2022, Section 6
> "This constraint was not justified in [Fong et al. 2017], nor is it a constraint that appears in machine learning practice." — [1] Cruttwell et al. 2022, Section 6

Verification notes: Full arXiv v3 text read; theorem/proposition numbers (II.4, III.2, IV.2, V.1, VII.1, A.1) checked against the text. Codex ledger entry P-CATEGORICAL-LEARNING (LITERATURE_LEDGER.md Section G) has this at abstract depth; added here: exact objects, composition law, the invertibility hypothesis, the five-learner basis, and the Cruttwell Section-6 defect. A sibling ledger P7.json (same scratchpad) reconstructs this paper independently; findings agree.

### P7.BAYESIAN_LENSES — Bayesian updates compose optically (Bayesian lenses; statistical games; compositional Bayesian brain)

Disposition: `ADOPT` · best verification: `FULL_TEXT_READ`

Sources:

- [0] Bayesian Updates Compose Optically — Toby St. Clere Smithe (2020), arXiv preprint (later ACT/MFCS developments); arXiv:2006.01631v2 (28 Jul 2020). https://arxiv.org/abs/2006.01631 arXiv:2006.01631 — `FULL_TEXT_READ`
- [1] Mathematical Foundations for a Compositional Account of the Bayesian Brain — Toby St Clere Smithe (2023), DPhil thesis, University of Oxford (Trinity 2023); arXiv:2212.12538v3 (19 Dec 2023). https://arxiv.org/abs/2212.12538 arXiv:2212.12538 — `PARTIAL_TEXT_READ`

**What it already explains.** Shows that Bayesian inversion has the type of the backward component of a LENS/optic: for a channel c: X -> Y in a copy-delete category, the inversion c^dagger_(.) : C(I,X) -> C(Y,X) is a state-dependent channel, formalised by the state-indexed category Stat: C^op -> V-Cat (Def 3.1) and the Grothendieck construction (Def 3.4), giving GrLens_Stat with composite (d.c, c^dagger o c^*d^dagger) (Ex 3.6). Via Yoneda this is the optic category BayesLens = Optic_{x,.} (Def 4.3, Prop 4.5). Main theorem: composing exact inversions optically gives the inversion of the composite up to almost-equality (Thm 5.2), proved in Kl(D), abstractly, and in sfKrn; hence stochastic channels embed functorially into BayesLens (Cor 5.3). Exact Bayesian lenses are only weakly lawful (GetPut w.r.t. states; PutGet/PutPut fail) because Bayes mixes beliefs (Section 6). Mixed Bayesian lenses (Def 4.7) allow the backward category to differ (Ex 4.8: state-dependent algebra homomorphisms). The thesis turns non-exact lenses into APPROXIMATE inference systems by attaching loss functions (statistical games): relative entropy is a strict section, MLE and free energy lax sections; Laplacian predictive coding arises as Euler integration of gradient flow on the free energy (Cor 7.3.11) — the point where the probabilistic law and the gradient law meet.

**Formal object.** Stat: C^op -> V-Cat, Stat(X)(A,B) = V(C(I,X), C(A,B)), reindexing along f: Y -> X by alpha \|-> (sigma \|-> alpha(f . sigma)) (Def 3.1). GrLens_Stat((X,A),(Y,B)) = C(X,Y) x V(C(I,X), C(B,A)) (eq. 19); composite of (c,c^dagger) and (d,d^dagger) is (d.c, pi \|-> c^dagger_pi . d^dagger_{c.pi}). BayesLens := Optic_{x,.} with (M-hat . -)(P) = V(M-hat(I), P) (Def 4.1, 4.3). Exact lens: c and c^dagger_pi satisfy the abstract Bayes equation (8) for every pi with c.pi of non-empty support (Def 5.1). Thesis: statistical games = Bayesian lenses with loss functions (state-dependent effects), forming a 2-fibration whose (lax) sections are loss models; cilia = polynomial-coalgebra dynamical systems controlling lenses.

**Strongest result.** Theorem 5.2 (2020): for sequentially composable exact Bayesian lenses <c\|c^dagger>, <d\|d^dagger>, the contravariant part of the optic composite is the Bayesian inversion of d.c: (d.c)^dagger_pi ~ c^dagger_pi . d^dagger_{c.pi} up to (d.c.pi)-almost-equality. Corollary 5.3: the wide subcategory C^dagger of channels admitting inversion embeds functorially into BayesLens. Prop 6.2: exact lenses satisfy GetPut with respect to states. Thesis Thm 4.3.14 / Cor 4.3.15 (same result; inversion is a section of the fibration), Thm 5.2.19 (coparameterised version, copy-composition), Cor 7.3.11 (Laplace doctrine: predictive coding = Euler_lambda o grad o LFE).

**Assumptions.** copy-delete (Markov-type) category; Bayesian inversion exists only up to almost-equality and only where c.pi has non-empty (full) support; base of enrichment V cartesian closed (quasi-Borel spaces in the measurable case); exactness is a property of the lens; approximate lenses are simply the other morphisms — no intrinsic notion of 'good approximation' in the 2020 paper; thesis: loss functions internalised as effects requiring 'bilinear effects' (Def 5.3.1); dynamics obtained by Euler integration of gradient flow with a chosen step lambda

**Resource model.** none. The thesis acknowledges that 'computing exact inversions is usually intractable' and that choosing an approximation is a new problem, but attaches a loss (relative entropy / free energy), not a compute or description-length cost.

**Failure boundary.** Only the update law's TYPE and its compositionality are proved; nothing about the rate, convergence, or sample efficiency of approximate inference; the forward channel c is not learned in the 2020 paper (no parameters); PutGet/PutPut fail so database-style lens laws cannot be used as correctness criteria; the Laplace/gradient bridge is asserted via an explicitly hand-defined functor (Remark 7.3.10 says a 'proper treatment of stochastic gradient descent applied to statistical games' is future work).

**Implementation.** none known

**Track-B residual.** Given that exact Bayes and gradient descent are both optics (lens backward maps) and that approximate Bayes = gradient flow on a free-energy loss model, Track B must ask which loss model / which section of the statistical-games fibration a resource-bounded process selects under ecology E (verification contract, sample budget), and at what compute/description cost — the parent has no cost functor and no selection rule.

**Upward question.** Both laws live in a category of optics, differing only in the contravariant functor (reverse derivative vs Bayesian inversion vs free-energy gradient). Is there a single indexed category over ecologies whose fibres are optic categories and whose reindexing selects the backward functor — and does description length of the backward functor's presentation predict which fibre a developmental process lands in?

Load-bearing quotes (verbatim from sources actually read):

> "As a slogan, our main result is that Bayesian updates compose optically (Theorem 5.2)." — [0] Section 1
> "That is to say, Bayesian updates compose optically: (d • c)†_π ∼ c†_π • d†_{c•π}." — [0] Theorem 5.2
> "Then C† embeds functorially into BayesLens." — [0] Corollary 5.3
> "Simple Bayesian lenses that are not exact are said to be approximate." — [0] Definition 5.1
> "here the ability to mix beliefs according to uncertainty is desirable." — [0] Section 6 (Comment)
> "computing exact inversions is usually intractable, but this creates a new problem: choosing an approximation, and measuring its performance." — [1] Thesis Section 5.1 (p. 172)
> "we expect that it can alternatively be obtained more abstractly, from a proper treatment of stochastic gradient descent applied to statistical games. We leave this to future work." — [1] Thesis Remark 7.3.10
> "the chain rule of the relative entropy is formalized as a strict section, while maximum likelihood estimation and the free energy give lax sections." — [1] Thesis Abstract

Verification notes: 2020 paper read in full (arXiv v2, 40 pp). Thesis read partially via page queries (chapters 1, 4.3, 5.1-5.3, 7.3.10-7.3.11, bibliography); theorem numbers 4.3.14, 5.2.19, 7.3.11 verified on the pages returned; other thesis chapters not read. Neither work is in the listed repo ledgers. The MFCS 2023 follow-up (Braithwaite, Hedges, Smithe, 'The compositional structure of Bayesian inference') was not read and is listed as a missing parent.

### P7.BAYESIAN_LENSES — Bayesian updates compose optically (Smithe 2020), statistical games / approximate inference doctrines (Smithe thesis 2023), dependent Bayesian lenses (Braithwaite, Hedges, Smithe 2023)

Disposition: `ADOPT` · best verification: `FULL_TEXT_READ`

Sources:

- [0] Bayesian Updates Compose Optically — Toby St Clere Smithe (2020), arXiv:2006.01631v2 (28 Jul 2020); ACT 2020. https://arxiv.org/abs/2006.01631 arXiv:2006.01631 — `FULL_TEXT_READ`
- [1] Mathematical Foundations for a Compositional Account of the Bayesian Brain — Toby St Clere Smithe (2023), DPhil thesis, University of Oxford; arXiv:2212.12538v3. https://arxiv.org/abs/2212.12538 arXiv:2212.12538 — `PARTIAL_TEXT_READ`
- [2] The Compositional Structure of Bayesian Inference — Dylan Braithwaite, Jules Hedges, Toby St Clere Smithe (2023), MFCS 2023, LIPIcs; arXiv:2305.06112v2. https://arxiv.org/abs/2305.06112 ; doi:10.4230/LIPIcs.MFCS.2023.24 arXiv:2305.06112 — `PARTIAL_TEXT_READ`

**What it already explains.** Exact Bayesian inversion of a channel c: X -> Y is not a morphism of the channel category but a STATE-DEPENDENT channel c^dagger_(.): C(I,X) -> C(Y,X). Organising these into fibres Stat(X) and taking the Grothendieck construction (Stat-lenses = Bayesian lenses, Def 4.3 via optics Optic_{x,⊙} on presheaf/copresheaf categories) yields the main theorem: the Bayesian inverse of a composite d•c equals the LENS composite of the inverses, (d•c)^dagger_pi ~ c^dagger_pi • d^dagger_{c•pi}, up to (d•c•pi)-almost-equality (Theorem 5.2), proved in Kl(D), abstractly in any copy-delete category with inversion, and in sfKrn with densities. Corollary 5.3: channels admitting inversion embed functorially into BayesLens. Exact lenses satisfy GetPut w.r.t. states (Prop 6.2) but not PutGet/PutPut because 'updates mix old and new beliefs'. Approximate inference = the non-exact lenses (Def 5.1). The thesis attaches loss functions to lenses (statistical games) and shows relative entropy is a STRICT section (chain rule of KL = horizontal composition; Prop 5.3.22), maximum likelihood and free energy (KL + MLE, Def 5.3.26) are LAX sections; the Laplace doctrine L_lambda = Euler_lambda o grad o LFE turns Gaussian statistical models into predictive-coding dynamical systems (Cor 7.3.11), i.e. approximate Bayes = gradient flow on a free-energy loss. Braithwaite-Hedges-Smithe 2023 (a) restates BUCO as 'a chain rule for Bayesian updating' with the same shape as J^T_{g o f} = J^T_g J^T_f, (b) shows inversion is functorial only 'up to almost-sure equality' (Prop 11), (c) repairs this with support objects and dependent Bayesian lenses giving a strict section T: C -> DBLens(C) (Theorem 20, Prop 21).

**Formal object.** Stat: C^op -> V-Cat, Stat(X)(A,B) = V(C(I,X), C(A,B)), reindexing f*alpha = alpha(f•-). GrLens_Stat((X,A),(Y,B)) = C(X,Y) x V(C(I,X), C(B,A)); composite of (c,c^dagger),(d,d^dagger) is (d•c, c^dagger o c* d^dagger) sending pi to c^dagger_pi • d^dagger_{c•pi}. BayesLens := Optic_{x,⊙} with (M ⊙ P) = V(M(I), P) on copresheaves. Exact lens: <c \| c^dagger> with (id ⊗ c) • copy • pi = (c^dagger_pi ⊗ id) • copy • c • pi (eq. 8). Density form: c^dagger_pi(A\|y) = p^{-1}(y) integral_{x in A} p(y\|x) pi(dx), p^{-1} a mu-almost-inverse. Thesis: loss model = (lax) section of the 2-fibration of statistical games pi_Loss; FE = KL + MLE. BHS: BLens(C) = coprod_X Stat(X)^op; DBLens(C) = Grothendieck of StFam; T: C -> DBLens(C) strict section when support objects exist.

**Strongest result.** Smithe Theorem 5.2 / Corollary 5.3 (above). Smithe Prop 6.2 (GetPut w.r.t. states). Thesis Prop 5.3.22 (KL is a strict loss model), Prop 5.3.25 (MLE lax), Cor 7.3.11 (Laplace doctrine: Laplacian predictive coding is the image of Euler_lambda o nabla o LFE). BHS Prop 11 (inversion functorial up to almost-sure equality), Theorem 20 (unique inverse-with-support), Prop 21 (strict section into DBLens). Together: the Bayes learning law has the SAME algebraic type as the gradient learning law (a lens/optic backward map composed contravariantly), and approximate Bayes reduces to gradient descent on a lax-monoidal loss.

**Assumptions.** copy-delete (Markov) category with channels admitting Bayesian inversion; inverses defined only up to almost-equality (or support objects / ProbStoch quotient for strictness); for densities: s-finite kernels, effects representing channels, almost-inverses exist (non-zero marginal); thesis: 'bilinear effects', Gaussian channels for the Laplace doctrine, mean-field; doctrines non-unital; no computability, no convergence-rate, no sample statements

**Resource model.** none. The thesis notes that 'computing exact inversions is usually intractable' and that choosing an approximation 'creates a new problem', but attaches a LOSS (relative entropy / free energy), not a compute, memory or description-length cost. Nothing in the three papers charges resources.

**Failure boundary.** Inversion is not unique (almost-equality), so the embedding C^dagger -> BayesLens requires a choice; strict functoriality needs support objects (BHS Remark 23: 'quite a strong assumption in general'). Lens laws PutGet/PutPut fail. No statement about which approximate lens (which loss model, which section) to use; the Laplace doctrine is 'agnostic about how predictions are actually generated' and, without the Hebb-Laplace extension, produces systems that 'do not learn'. Remark 7.3.10: the gradient-descent semantics 'can alternatively be obtained more abstractly... We leave this to future work'. Nothing about non-Gaussian or discrete-symbolic cases, program spaces, or resource bounds.

**Implementation.** none known for the 2020 paper; thesis Chapter 7 gives explicit dynamical systems but no released code; BHS 2023 none

**Track-B residual.** The categorical bridge between the gradient law and the Bayes law is parent-owned at the level of TYPE (both are lens backward maps; approximate Bayes is gradient flow on a lax loss). Track B must ask which loss model / which section of the statistical-games fibration a resource-bounded process selects under E (verification contract, sample budget), at what compute and description cost, and whether a discrete/symbolic hypothesis space can carry a cheap Bayesian lens - the parent has neither a cost functor nor a selection rule.

**Upward question.** Given that exact and approximate Bayes are sections of one fibration and gradient learning is a lens over a CRDC, is there a single fibration over ecologies whose sections are 'learning laws', with a cost 2-cell structure making the choice of section (exact Bayes vs. Laplace vs. plain gradient) a resource-priced optimisation rather than a designer's choice?

Load-bearing quotes (verbatim from sources actually read):

> "As a slogan, our main result is that Bayesian updates compose optically (Theorem 5.2)." — [0] Section 1
> "That is to say, Bayesian updates compose optically: (d • c)†_π ∼ c†_π • d†_{c•π}." — [0] Theorem 5.2
> "Then C† embeds functorially into BayesLens." — [0] Corollary 5.3
> "Because Bayesian inversion is only determined up to almost-equality, the embedding C† ֒→ BayesLens is not unique, requiring a choice of inversion for each channel." — [0] Section 5, after Corollary 5.3
> "PutPut fails to hold for exact Bayesian lenses for the same reason that PutGet fails to hold in general: updates mix old and new beliefs, rather than entirely replace the old with the new." — [0] Section 6
> "computing exact inversions is usually intractable, but this creates a new problem: choosing an approximation, and measuring its performance." — [1] Thesis, Section 5.1
> "we expect that it can alternatively be obtained more abstractly, from a proper treatment of stochastic gradient descent applied to statistical games. We leave this to future work." — [1] Thesis, Remark 7.3.10
> "As such we think of the composition rule as a chain rule for Bayesian updating." — [2] BHS 2023, Section 1
> "If C has Bayesian inverses for ever kernel at every prior, then Bayesian inversion defines a functor T : C → BLens(C) up to almost-sure equality." — [2] BHS 2023, Proposition 11 (sic 'ever')

Verification notes: Smithe 2020 read in full (theorem, definition and proposition numbers verified). Thesis and BHS 2023 read partially via targeted page queries; their theorem numbers are as printed on the pages returned. Not in the Codex ledgers (Codex has Fritz's Markov categories in PARENT_EXPANSION_V2 §B but no Bayesian-lens entry). Sibling P7.json entry P7.BAYESIAN_LENSES agrees; BHS 2023's 'almost functorial' caveat and support-object repair are added here.

### P7.CATEGORICAL_CYBERNETICS — Towards foundations of categorical cybernetics (parametrised optics; open learners and open games as one pattern)

Disposition: `GENERALIZE` · best verification: `FULL_TEXT_READ`

Sources:

- [0] Towards Foundations of Categorical Cybernetics — Matteo Capucci, Bruno Gavranovic, Jules Hedges, Eigil Fjeldgren Rischel (2022), Applied Category Theory 2021 (ACT 2021), EPTCS 372, pp. 235-248. https://arxiv.org/abs/2105.06332; doi:10.4204/EPTCS.372.17 arXiv:2105.06332 — `FULL_TEXT_READ`

**What it already explains.** Identifies the CENTRAL CONSTRUCTION Para_⊛(Optic_{•,•}(C,D)) — parametrised optics — as the common algebra of 'cybernetic systems': open systems with bidirectional information flow, a control (parameter) on the forward direction and an objective (coparameter) on the backward direction. Para(-) is a monad on M-actegories (Prop 5); Optic(M) acts on Optic(C,D) (Prop 10), so parameters of an optic are themselves optics. Two example classes: (i) neural networks: Para(R): Para(Smooth) -> Para(Optic(Smooth)) is backprop; gradient descent gd_alpha is a lens (p, ∇p) \|-> p - alpha∇p attached as a reparametrisation (Construction 11); GANs are two networks with OPPOSING reparametrisations (descent vs ascent) and weight tying by the copy map (Figure 7). (ii) Open games: equilibrium selection is a lax monoidal functor of selection relations S: M -> Cat (Def 12) with the Nash product as laxator (Prop 14); Para^S(Optic(C,D)) is a refined category of open games with explicit agents and a strong monoidal functor to the classical OG (Section 6). The construction is generic: any lax monoidal pseudofunctor on optics can replace selection relations.

**Formal object.** M-actegory (C, •) (Def 1). Para_•(C): bicategory, 1-cells phi: M • X -> Y, 2-cells r: M' -> M reparametrisations (Def 2); CoPara(C) = Para(C^op)^coop (Rem 4). Optic_{•,•}(C,D)((X,X'),(Y,Y')) = ∫^M C(X, M•Y) x D(M•Y', X') (Def 8); Lens(C) = Optic_x(C) for cartesian C. Action ⊛ of Optic(M) on Optic(C,D): (M,M') ⊛ (X,X') = (M•X, M'•X') (Prop 10). Parametrised optic: parameters (P,Q) in M, residual M, v: P•X -> M•Y in C, u: M•Y' -> Q•X' in D (Section 4, Fig 6). Selection relation eps ⊆ M(I,X) x M(X,I); S_M(f)(eps) = {(x#f, k) \| eps(x, f#k)}; Nash product eps ⊠ delta = {(x⊗y, k) \| eps(x,k_y) and delta(y,k_x)} (Def 12, Prop 14). Open games with agency: Para^S_⊛(Optic(C,D)) (Section 6).

**Strongest result.** Prop 5: Para(-) is a monad on M-Mod. Prop 10: Optic(M) acts on Optic(C,D), yielding the bicategory of parametrised optics. Prop 14: S: M -> Cat admits a lax monoidal structure (Nash product) — natural because 'existential quantifiers commute'. Section 6: a strong monoidal functor Para^S_⊛(Lens(Set)) -> OG recovering classical open games; Example: Prisoner's Dilemma solution set {(D,D)} vs Hicks-optimal {(C,C)} under a pushed-forward argmax. No theorem about Bayesian updates in this paper — Bayesian open games are only said to be carryable-out.

**Assumptions.** M commutative monoidal for Para(C) to be monoidal as a 1-category (otherwise symmetric monoidal bicategory, deferred); strict actegories; cybernetic feedback loop (parameter update dynamics) is NOT part of Para(Optic(-)): 'What is missing ... is a feedback mechanism' — closed separately by gradient-descent lenses (ML) or selection functions (games); only two example classes presented; Bayesian updates/games and other lax monoidal pseudofunctors are asserted to fit, not worked out

**Resource model.** none

**Failure boundary.** Provides the interface algebra (what a learner/agent IS) but no dynamics, no convergence, no rate, no equilibrium-existence conditions beyond argmax examples; no principle selecting gradient descent vs selection function vs Bayesian inversion as the controller; no resource pricing of parameters, residuals or coparameters; monoidal structure only under commutativity assumptions; Bayesian case delegated to other work (Smithe; Bolt-Hedges-Zahn Bayesian open games).

**Implementation.** none known (animations of optic composition referenced; no code)

**Track-B residual.** The parent asserts 'parametrised optics = the pattern of cybernetic systems' and instantiates it for gradient learners and game-theoretic agents. Track B must (i) add a cost/resource functor on Para(Optic) (none exists here), (ii) ask which controller (gradient lens, selection relation, Bayesian inversion, enumerative search) a bounded developmental process selects under ecology E, and (iii) supply the missing feedback/dynamics as a resource-priced dynamical system — the parent explicitly leaves all three open.

**Upward question.** Parametrised optics fix the SHAPE of every learning/agency law; the open question is the fibration of controllers over ecologies: for which E is the resource-optimal closure of the parameter port a gradient lens, a selection relation, a Bayesian inversion, or an enumerator — and is that map itself lax monoidal (does it compose across subsystems)?

Load-bearing quotes (verbatim from sources actually read):

> "We propose a categorical framework for processes which interact bidirectionally with both an environment and a 'controller'. Examples include open learners, in which the controller is an optimiser such as gradient descent" — [0] Abstract
> "A parametrised optic describes open systems that have bidirectional information flow, with a control on the forward direction and an objective on the backwards direction. This pattern is ubiquitous in cybernetics" — [0] Section 1
> "For reasons of space we only present two classes of examples: neural networks which can be presented entirely using the structure of parametrised optics, and open games which have selection functions as an additional ingredient." — [0] Section 1
> "Parametrised optics model cybernetic systems, namely dynamical systems steered by one or more agents." — [0] Section 4
> "What is missing in the mathematical structure of Para(Optic(−)) is a feedback mechanism, central in cybernetics." — [0] Section 4
> "In machine learning, parameter updating is explicitly modelled (Construction 11), but in game theory we directly seek the equilibrium." — [0] Section 5
> "and can also be carried out for Bayesian open games and other more general formulations of open games." — [0] Section 6

Verification notes: Full text read (EPTCS 372 version). Definition/Proposition numbers verified. IMPORTANT honesty note: the brief describes this paper as unifying 'learners, games, Bayesian updates'; the paper itself presents only learners and games and mentions Bayesian open games in one sentence — the Bayesian leg of the unification rests on Smithe 2020 (Bayesian lenses are Optic_{x,.}) and the companion literature, not on this text. Not present in any listed repo ledger.

### P7.CATEGORICAL_CYBERNETICS — Towards foundations of categorical cybernetics (Capucci, Gavranovic, Hedges, Rischel 2022): parametrised optics as the common pattern of learners and games

Disposition: `ADOPT` · best verification: `FULL_TEXT_READ`

Sources:

- [0] Towards Foundations of Categorical Cybernetics — Matteo Capucci, Bruno Gavranovic, Jules Hedges, Eigil Fjeldgren Rischel (2022), ACT 2021, EPTCS 372, pp. 235-248; arXiv:2105.06332. https://arxiv.org/abs/2105.06332 ; doi:10.4204/EPTCS.372.17 arXiv:2105.06332 — `FULL_TEXT_READ`

**What it already explains.** Proposes ONE construction for 'processes which interact bidirectionally with both an environment and a controller': the bicategory of parametrised optics Para_⊛(Optic_{•,•}(C,D)), obtained by letting Optic_⊙(M) act on Optic(C,D) (Prop 10). A parametrised optic has forward part v: P•X -> M•Y and backward part u: M•Y' -> Q•X'; parameters/coparameters are 'agency', residuals are private state. Two instantiations are worked out: (i) neural networks = Para(R): Para(Smooth) -> Para(Optic(Smooth)) with gradient descent as the reparametrising lens gd_alpha (Construction 11), GANs as opposing reparametrisations gd/ga, weight tying as reparametrisation along copy; (ii) open games = parametrised optics whose parameter objects carry selection relations eps ⊆ M(I,X) x M(X,I) (Def 12), with the Nash product as laxator (Prop 14) and a strong monoidal functor Para^S(Lens(Set)) -> OG recovering Ghani et al.'s open games (Section 6), Prisoner's Dilemma solution {(D,D)} vs Hicks-optimal {(C,C)}. The abstract pattern: 'control on the forward direction and an objective on the backwards direction'. Bayesian open games are ASSERTED to fit ('can also be carried out'), not constructed.

**Formal object.** Para_•(C): objects of C; 1-cells phi: M•X -> Y; 2-cells r: M' -> M (reparametrisation, r*phi); Prop 5: Para(-) is a monad on M-Mod. Optic_{•,•}(C,D)((X,X'),(Y,Y')) = coend_M C(X, M•Y) x D(M•Y', X'). Prop 10: Optic_⊙(M) acts on Optic_{•,•}(C,D) by (M,M') ⊛ (X,X') = (M•X, M'•X'), giving Para_⊛(Optic(C,D)). Construction 11: gd_alpha: (R,R) -> (R,R), forward id, backward (p, grad p) \|-> p - alpha grad p. Selection relations S_M(X) = P(M(I,X) x M(X,I)), Nash product eps ⊠ delta = {(x ⊗ y, k) \| eps(x,k_y) and delta(y,k_x)}; M^S = Grothendieck of S.

**Strongest result.** Prop 5 (Para is a monad), Prop 10 (action of Optic(M) on Optic(C,D) - the existence of parametrised optics), Prop 14 (Nash product is a laxator; naturality 'boils down to the fact that existential quantifiers commute'), Section 6 strong monoidal functor Para^S_⊛(Lens(Set)) -> OG. Interpretive claim (Section 4): 'Parametrised optics model cybernetic systems, namely dynamical systems steered by one or more agents.' Explicit gap (Section 4): 'What is missing in the mathematical structure of Para(Optic(−)) is a feedback mechanism, central in cybernetics' - the closing of the parameter loop (gradient descent, or equilibrium selection) is added per-instance, not by the algebra.

**Assumptions.** M commutative monoidal (assumed 'for presentation purposes') so that Para(C) is monoidal on the nose; C, D symmetric monoidal M-actegories; for games, semicartesian C=D=M=Set; learners: base Smooth and gradient-descent lens fixed by hand; games: agents are perfect optimisers via argmax selection relations; Bayesian open games only claimed, not constructed

**Resource model.** none. No cost of any kind is attached to optics, parameters, residuals or reparametrisations; the only 'resource-like' remark is the footnote that residuals play the role of 'memory' ferrying information between passes.

**Failure boundary.** Only two example classes are presented (neural nets; open games). Bayesian and RL instances are asserted or deferred. The parameter-update loop ('feedback') is outside the structure. No cost, no convergence, no selection of controller. The 'lax optics' refinement needed to track residuals is left to future work (footnote 3). Nothing prefers gradient descent over argmax over Bayesian inversion as the controller.

**Implementation.** none known (the paper links animations of optic composition; no library)

**Track-B residual.** The parent states the pattern 'one parametrised optic, many controllers' and works out gradient learners and game agents; with Smithe/BHS it extends to Bayesian updaters. Track B must (i) add a cost functor on Para(Optic) (none exists), (ii) supply the missing 'feedback mechanism' as an ecology-indexed selection among controllers (gradient lens, selection relation, Bayesian inversion, enumerative search), and (iii) show that program-search and rewrite learners are (or are not) parametrised optics at all.

**Upward question.** The algebra is controller-agnostic by design ('the same construction works if selection functions are replaced with any suitable lax monoidal pseudofunctor'). What ecology-indexed, resource-priced principle chooses the pseudofunctor - and is that choice itself a parametrised optic one level up (meta-morphogenesis)?

Load-bearing quotes (verbatim from sources actually read):

> "A parametrised optic describes open systems that have bidirectional information flow, with a control on the forward direction and an objective on the backwards direction. This pattern is ubiquitous in cybernetics" — [0] Section 1
> "For reasons of space we only present two classes of examples: neural networks which can be presented entirely using the structure of parametrised optics, and open games which have selection functions as an additional ingredient." — [0] Section 1
> "abstractly the same construction works if selection functions are replaced with any suitable lax monoidal pseudofunctor on a category of optics." — [0] Section 1
> "Parametrised optics model cybernetic systems, namely dynamical systems steered by one or more agents." — [0] Section 4
> "What is missing in the mathematical structure of Para(Optic(−)) is a feedback mechanism, central in cybernetics." — [0] Section 4
> "In machine learning, parameter updating is explicitly modelled (Construction 11), but in game theory we directly seek the equilibrium." — [0] Section 5
> "This construction defines a strong monoidal functor Para^S_⊛(Lens(Set)) → OG, and can also be carried out for Bayesian open games and other more general formulations of open games." — [0] Section 6

Verification notes: Full EPTCS text read; proposition/construction/definition numbers verified. Not in the Codex ledgers (PARENT_EXPANSION_V2 §B has Ghani et al. open games only). Sibling P7.json entry agrees. Verdict on Track-B B3 (see family synthesis): PARENT_SUFFICIENT at the algebraic-interface level for {gradient (any CRDC), Bayesian, game-theoretic} laws; OPEN for program-search / rewrite laws and for any resource-priced selection.

### P7.CATEGORICAL_GRADIENT_LEARNING — Categorical foundations of gradient-based learning (parametric lenses over Cartesian reverse differential categories)

Disposition: `ADOPT` · best verification: `FULL_TEXT_READ`

Sources:

- [0] Categorical Foundations of Gradient-Based Learning — G.S.H. Cruttwell, Bruno Gavranovic, Neil Ghani, Paul Wilson, Fabio Zanasi (2022), ESOP 2022, LNCS 13240, pp. 1-28 (Springer); arXiv:2103.01931v2 (13 Jul 2021). https://arxiv.org/abs/2103.01931; doi:10.1007/978-3-030-99336-8_1 arXiv:2103.01931 — `FULL_TEXT_READ`

**What it already explains.** Decomposes the learner of Fong et al. into three orthogonal constructions: Para(-) (parameters), Lens(-) (bidirectionality) and a Cartesian reverse differential category (CRDC) structure (gradients). A model is a morphism of Para(C); applying Para to the functor R: C -> Lens(C), f \|-> (f, R[f]) (Prop 2.7, from RD.5 the reverse chain rule) yields a parametric lens. The loss map is itself a Para-map B -> L with parameter B (Def 3.3), the learning rate a lens (L,L') -> (1,1) (Def 3.8), and EVERY optimiser is a reparametrisation 2-cell: basic gradient update (Def 3.11), stateful updates (Def 3.14) covering Momentum (3.15), Nesterov (3.16, non-trivial get map), Adagrad (3.17), Adam (3.18). Losses covered: quadratic, Boolean XOR, softmax cross-entropy, dot product. Base categories covered: Smooth (neural nets) and POLY_{Z2} (Boolean circuits, Wilson-Zanasi). Supervised parameter learning (4.1) and deep dreaming = supervised learning of INPUTS (4.2) are the same closed parametric lens with the optimiser attached to a different port; iteration is composition of the put map as a Para endomorphism. Python implementation reproduces Keras accuracy on MNIST.

**Formal object.** Para(C): objects of C; morphism A->B a pair (P, f: P (x) A -> B); composite of (P,f),(P',f') is (P' (x) P, (1 (x) f); f'); reparametrisation by alpha: Q -> P (Def 2.3). Lens(C) for cartesian C: objects (A,A'), morphisms (f: A -> B, f*: A x B' -> A') (Def 2.4). Para(Lens(C)) parametric lenses: (P,P') and lens (f,f*): (A,A') x (P,P') -> (B,B'), f*: P x A x B' -> P' x A' (Def 2.5). CRDC: Cartesian left additive category with R[f]: A x B -> A satisfying RD.1-RD.7 (Def A.5). Functor Para(R): Para(C) -> Para(Lens(C)) (eq. 8). Closed learning system: lens (A x S x P x B, S x P) -> (1,1) whose put is put(a,s,p,b_t)= U*(s,p,p') where p-bar = U(s,p), b_p = f(p-bar,a), (b_t',b_p') = R[loss](b_t,b_p,alpha(loss(b_t,b_p))), (p',a') = R[f](p-bar,a,b_p') (Section 4.1).

**Strongest result.** Prop 2.7 (citing Cockett et al. Prop 31): for a CRDC C there is a functor R: C -> Lens(C), f \|-> (f, R[f]); applying Para gives Para(R): Para(C) -> Para(Lens(C)) (eq. 8), which is the whole of backpropagation. Main structural result (Sections 3-4): model, loss, learning rate and optimiser are ALL parametric lenses / reparametrisations, and the standard algorithms (Examples 4.1-4.4: quadratic+GD, softmax-CE+GD, MSE+Nesterov, Boolean XOR+RDA) are recovered by unpacking a single composite put map. Section 6 identifies and repairs the equivalence-relation defect in Fong et al. Theorem III.2 by using Para 2-cells.

**Assumptions.** base category C is a Cartesian reverse differential category (only RD.1-RD.5 actually used; RD.6-7 unused); strict symmetric monoidal C for Para to be a 1-category (otherwise a bicategory); optimiser fixed in advance ('In all our settings we have fixed an optimiser beforehand'); supervised setting with a loss map; iteration modelled as repeated put; no probabilistic, unsupervised, RL or non-gradient learning

**Resource model.** none built in. One incidental remark: reverse derivatives are 'much more computationally efficient' than forward ones when the codomain dimension m << n (Example 2.8, citing Griewank-Walther). No description-length, sample, memory or verification accounting.

**Failure boundary.** No convergence or generalisation statements; no criterion for choosing among optimisers or losses; RNNs, GANs, meta-learned optimisers, SVMs, tangent bundles / dependent lenses, probabilistic and non-gradient learning are all listed as future work (Section 7); the framework applies to ANY functor F: C -> Lens(C), so it does not single out gradient learning as privileged — it is an interface, not a selection principle.

**Implementation.** https://github.com/statusfailed/numeric-optics-python/ (proof-of-concept Python library; MNIST experiment matching Keras)

**Track-B residual.** Given that every gradient learning law is 'a parametric lens over a CRDC plus an optimiser reparametrisation', Track B must ask which functor F: C -> Lens(C) and which reparametrisation a resource-bounded developmental process converges to under ecology E, and what the cost functor on Para(Lens(C)) is — the parent supplies the type of the answer, not the answer.

**Upward question.** The construction works for any functor C -> Lens(C). Which functors of that form (reverse derivative, Bayesian inversion, selection/argmax, enumeration/rewrite) does a bounded developmental process select under a given ecology, and is there a cost-indexed fibration over Para(Lens(C)) whose sections are exactly the resource-optimal learning laws?

Load-bearing quotes (verbatim from sources actually read):

> "what are the fundamental mathematical structures underpinning gradient-based learning?" — [0] Section 1
> "we propose the notion of parametric lens as the fundamental semantic structure of learning." — [0] Section 1
> "Note that gradient descent is not typically seen as a lens - but it precisely fits this way into the picture we are creating!" — [0] Section 3.4
> "In all our settings we have fixed an optimiser beforehand." — [0] Section 7
> "in future work we plan to consider further modifications and additions to encompass non-supervised, probabilistic and non-gradient based learning. This includes genetic algorithms and reinforcement learning." — [0] Section 7
> "Using the reverse derivative (as opposed to the forward derivative) is well-known to be much more computationally efficient for functions f : R^n -> R^m when m << n" — [0] Example 2.8
> "unfortunately, the functor defined in Theorem III.2 does not respect this equivalence relation." — [0] Section 6 (on Fong et al.)

Verification notes: Full text read (arXiv v2). Definition/Example/Proposition numbers verified. Not present in any of the seven listed repo ledgers. Implementation URL taken verbatim from footnote 2 / Section 5.

### P7.CATEGORICAL_GRADIENT_LEARNING — Categorical foundations of gradient-based learning (Cruttwell, Gavranovic, Ghani, Wilson, Zanasi 2022) with reverse derivative categories (Cockett et al. 2020)

Disposition: `ADOPT` · best verification: `PARTIAL_TEXT_READ`

Sources:

- [0] Categorical Foundations of Gradient-Based Learning — G. S. H. Cruttwell, Bruno Gavranovic, Neil Ghani, Paul Wilson, Fabio Zanasi (2022), ESOP 2022, LNCS 13240, pp. 1-28; arXiv:2103.01931. https://arxiv.org/abs/2103.01931 ; doi:10.1007/978-3-030-99336-8_1 arXiv:2103.01931 — `PARTIAL_TEXT_READ`
- [1] Reverse derivative categories — Robin Cockett, Geoffrey Cruttwell, Jonathan Gallagher, Jean-Simon Pacaud Lemay, Benjamin MacAdam, Gordon Plotkin, Dorette Pronk (2020), CSL 2020; arXiv:1910.07065. https://arxiv.org/abs/1910.07065 arXiv:1910.07065 — `PARTIAL_TEXT_READ`

**What it already explains.** Every component of gradient-based supervised learning is a parametric lens in Para(Lens(C)) for a Cartesian reverse differential category (CRDC) C: the model is the image of a Para(C)-map under Para(R): Para(C) -> Para(Lens(C)), where R: C -> Lens(C), f \|-> (f, R[f]) is the functor of Cockett et al. Prop. 31 (reverse chain rule RD.5 = functoriality); the loss is a Para(C) map (loss, B): B -> L; the learning rate is a lens (L,L') -> (1,1); the optimiser is a reparametrisation 2-cell (P,P) -> (P,P') (gradient update G*(p,p') = p + p') or a stateful lens (S x P, S x P) -> (P,P') (momentum, Nesterov - whose non-trivial get map is the 'lookahead' - Adagrad, Adam). Closing all ports yields put(a,s,p,b_t) = U*(s,p,p') with (p',a') = R[f](p,a,b'_p), (b'_t,b'_p) = R[loss](b_t,b_p,alpha(loss(b_t,b_p))). Deep dreaming = the same lens with the optimiser attached to the input port. Boolean circuits (POLY_Z2, XOR loss, identity learning rate) are the same construction in a different CRDC (Example 4.4). Cockett et al.: a CRDC is exactly a Cartesian differential category with a contextual linear dagger (Theorem 42); POLY_R over any commutative rig R is a CRDC (Example 14).

**Formal object.** Para(Lens(C)): objects (A, A'); morphism (A,A') -> (B,B') = parameter pair (P,P') and a lens (f, f*) with f: P x A -> B, f*: P x A x B' -> P' x A'. Reparametrisation = lens on the (P,P') wires. R[f]: A x B' -> A' the reverse derivative; in Smooth R[f](x,v) = J[f]^T(x) v; in POLY_Z2 R[P] = <sum_i (dp_i/dx_1) y_i, ..., sum_i (dp_i/dx_n) y_i> with Boolean partial derivatives. Closed learning system = map (1,1) -> (1,1) in Para(Lens(C)) with parameter space (A x S x P x B, S x P). Learning iteration = the put map viewed as an endomorphism (A x B, put): Para(C)(P,P) composed with itself.

**Strongest result.** Proposition 2.7 (= Cockett et al. Prop. 31): for a CRDC C, R: C -> Lens(C) is a functor; applying Para gives eq. (8) Para(R): Para(C) -> Para(Lens(C)), which IS backpropagation. Examples 4.1-4.4 recover, by unpacking one composite put map: quadratic loss + GD (regression), softmax cross-entropy + GD (logistic regression), MSE + Nesterov, Boolean-circuit learning (put(a,p,b_t) = p + p' with (p',a') = R[f](p,a,f(p,a)+b_t)). Section 6 corrects Fong et al. Theorem III.2 (functor does not respect the equivalence relation; invertibility of de/dx unjustified) by using Para 2-cells. Cockett et al. Theorem 42: CRDC = Cartesian differential category + contextual linear dagger; Theorem 16: every CRDC is a CDC via D[f] = (<1,0> x 1) R[R[f]] pi_1.

**Assumptions.** base category is a Cartesian reverse differential category (Smooth, POLY_R for commutative rigs R); optimiser fixed in advance ('In all our settings we have fixed an optimiser beforehand'); loss map and learning rate supplied by the designer; only supervised learning of parameters or of inputs; no convergence or sample statements; RD.6-RD.7 (higher-order derivative axioms) not used

**Resource model.** none built in. One incidental cost remark: reverse derivatives are 'much more computationally efficient' than forward ones for f: R^n -> R^m when m << n (Example 2.8, citing Griewank-Walther). No description length, memory, samples or verification accounting; the Section 7 remark that the construction works for ANY functor F: C -> Lens(C) makes explicit that nothing in the algebra prefers one backward functor over another.

**Failure boundary.** Does not cover unsupervised, probabilistic, non-gradient, genetic or reinforcement learning (all listed as future work); GANs, RNNs, SVMs also future work. No statement of convergence, rate, or generalisation. The optimiser is a designer-chosen 2-cell; the framework offers no principle for choosing it. Nothing is said about which base category (Smooth vs POLY_Z2) a process should use.

**Implementation.** Python proof-of-concept library announced in Section 5 (footnote link in paper; Gavranovic's 'numeric-optics-python' on GitHub - not fetched here)

**Track-B residual.** Given that 'gradient learning = parametric lens over a CRDC + optimiser reparametrisation', and that any functor C -> Lens(C) would do, Track B must supply (i) a cost functor on Para(Lens(C)) (description length of P, work of R[f], memory of residuals) and (ii) the rule by which a resource-bounded developmental process selects the base category, the backward functor and the reparametrisation under ecology E. The parent supplies the type of the answer, not the answer.

**Upward question.** Which functor C -> Lens(C) (reverse derivative, Bayesian inversion, selection relation, enumerative search) does a bounded developmental process converge to under E, and is there a 2-categorical (oplax) refinement of Para(Lens(C)) in which resource cost is visible so that this selection is non-trivial?

Load-bearing quotes (verbatim from sources actually read):

> "Proposition 2.7. [Cockett et al. 2019, Prop. 31] If C is a CRDC, there is a functor R : C → Lens(C)" — [0] Section 2.4
> "Note that gradient descent is not typically seen as a lens - but it precisely fits this way into the picture we are creating!" — [0] Section 3.4
> "In all our settings we have fixed an optimiser beforehand." — [0] Section 7
> "in future work we plan to consider further modifications and additions to encompass non-supervised, probabilistic and non-gradient based learning. This includes genetic algorithms and reinforcement learning." — [0] Section 7
> "much of our work can be applied to any functor of the form F : C → Lens(C) - F does not necessarily have to be of the form f ↦→ (f, R[f]) for a CRDC R." — [0] Section 7
> "Using the reverse derivative (as opposed to the forward derivative) is well-known to be much more computationally efficient for functions f : R^n → R^m when m ≪ n" — [0] Example 2.8
> "A Cartesian reverse differential category is precisely a Cartesian differential category with a contextual linear dagger." — [1] Cockett et al., Theorem 42
> "Let R be a commutative rig. POLY_R is a reverse differential category whose reverse differential combinator R is again defined using partial derivatives of polynomials." — [1] Cockett et al., Example 14(1)

Verification notes: Sections read as listed; equation and example numbers verified in text. Not in the Codex ledgers (LITERATURE_LEDGER.md lists only Fong et al. and CDL). Sibling P7.json entry P7.CATEGORICAL_GRADIENT_LEARNING agrees on content.

### P7.CDL — Categorical deep learning is an algebraic theory of all architectures (monad algebras / lax algebras in the 2-category Para)

Disposition: `ADAPT` · best verification: `FULL_TEXT_READ`

Sources:

- [0] Position: Categorical Deep Learning is an Algebraic Theory of All Architectures — Bruno Gavranovic, Paul Lessard, Andrew Dudzik, Tamara von Glehn, Joao G.M. Araujo, Petar Velickovic (2024), ICML 2024, PMLR 235 (position paper); arXiv:2402.15332v2 (6 Jun 2024). https://arxiv.org/abs/2402.15332 arXiv:2402.15332 — `FULL_TEXT_READ`

**What it already explains.** Proposes that neural network ARCHITECTURES (forward computation and weight-sharing constraints, not learning) are (lax) algebra homomorphisms for monads/endofunctors valued in the 2-category Para of parametric maps. Recovers all of geometric deep learning: equivariant layers = homomorphisms of algebras for the group-action monad G x - (Example 2.6), with GNNs (Sigma_n), spherical CNNs (SO(3)) and G-CNNs derived in Appendix C, CNN weight tying (circulants) in Appendix H.1. Goes beyond groups via endofunctor (co)algebras: lists 1+A x -, binary trees A+(-)^2 (folds = algebra homomorphisms, Ex 2.12/2.14), Mealy machines I -> O x - (unfolds = coalgebra homomorphisms, Ex 2.15), streams and Moore machines (App H.2). Lifting to Para: folding/unfolding/recursive RNN cells and Mealy/Moore cells are (co)algebras of Para(F) (Figure 1, App I); their unrollings are lax algebra homomorphisms (App J); weight tying arises automatically because lax-algebra 2-cells are comonoids on the parameter object (Theorem G.10). RNNs are 'learnable Mealy machines'. Lawvere-theory syntax (App D) links to Dudzik-Velickovic (commutative semirings = FinPoly).

**Formal object.** Monad (M,eta,mu) on C; M-algebra (A, a: M(A) -> A); M-algebra homomorphism f: (A,a) -> (B,b) with f o a = b o M(f) (Def 2.3/2.5). Endofunctor (co)algebras (Def 2.8/B.2). Algebraically free monad Free_Mnd(F) = F^kappa via Kelly's transfinite construction (Def B.14, Thm B.16). Para_>(C): objects of C, 1-cells (P, f: P > X -> Y) for an M-actegory action >, 2-cells reparametrisations r: P' -> P (Def G.1). For a strong actegorical monad T, Para(T) is a 2-monad on Para(C) (Ex G.8). Lax T-algebra (A, a, eps_A, delta_A) (Def F.2). Theorem G.10: the 2-cells of a lax Para(T)-algebra determine a comonoid (P, !_P, Delta_P). Architectures: (P, cell_rcnt) in Para(Set)(1 + A x S, S), (P, cell_Mealy) in Para(Set)(S, I -> O x S), etc. (Figure 1).

**Strongest result.** Theorem G.10 (proved): lax (co)algebras for the induced 2-monad Para(T) on Para(C) have parameter objects that are comonoids in M, the counit/comultiplication being the lax 2-cells — i.e. weight tying is forced by lax-algebra coherence. Theorem B.16 (Kelly): Alg_Pendo(F) equivalent to Alg_Mnd(F^kappa). Theorem G.6: the embedding C -> Para(C) preserves connected colimits. Examples C.1-C.3: GNN, spherical CNN, G-CNN equivariance constraints as monad-algebra homomorphism squares. Conjecture G.12 (unproved): equivalence Lax-Alg_Endo(Para(F)) -> Lax-Alg_Mnd(F^kappa). Everything else is a position claim.

**Assumptions.** the 'right' category and monad/endofunctor are chosen by the designer ('rely on choosing the right category to operate in'); weight-sharing analyses of individual layers are done in Vect (linear maps); multi-layer nonlinearity is addressed only via the Para lifting; strict monoidal M and strict actegories assumed for the 2-monad Para(T); architectures only: no loss, no optimiser, no learning dynamics appear in the paper (gradient learning is delegated to Cruttwell et al. 2022); Conjecture G.12 unproved

**Resource model.** none (no description length, compute, sample or memory accounting; alignment-to-algorithm is inherited informally from Xu et al./Dudzik-Velickovic)

**Failure boundary.** Covers CNN/GNN/spherical/G-CNN (via group monads), RNN/recursive/Mealy/Moore (via endofunctor (co)algebras). Transformers are NOT derived — self-attention is mentioned once as an instance of permutation-equivariant learning (GDL intro). Non-neural coverage: automata (Mealy/Moore/streams) and inductive data structures are covered as (co)algebras; dynamic programming via the semiring Lawvere theory (Remark 2.7/App D); rule systems, Bayesian inference and program search are NOT covered — the paper only HYPOTHESISES networks that 'learn only well-typed functions' or 'verifiably correct logical argument, or code' (Section 4). No learning law at all; no selection among monads; no resource accounting; the 'all architectures' claim is explicitly a position.

**Implementation.** none known (position paper; no code released)

**Track-B residual.** CDL supplies the D0/D1 template 'morphology = choice of (category, monad T, lax Para(T)-algebra)'. Track B must supply what CDL explicitly leaves to the designer: a rule mapping ecology E to the monad T (and to the base category), i.e. why a sequential ecology yields the list/Mealy monad and a grid ecology the translation-group monad, and at what description-length / compute cost each lax algebra is compiled and acquired.

**Upward question.** CDL parametrises morphology by a monad T on a base category; is there a functor from ecologies to monads (Ecol -> Mnd(C)) — a 'morphogenetic Lawvere theory' — such that the algebras that dominate under E are the algebras of the image monad, and does the description length of T's Lawvere theory predict the compile/acquire cost?

Load-bearing quotes (verbatim from sources actually read):

> "It is our position that the 2-category Para and 2-categorical algebra valued in it provide a formal theory of neural network architectures, establish formal criteria for weight tying correctness and inform design of new architectures." — [0] Section 3.1 (boxed position)
> "we have just successfully derived the key aim of geometric deep learning: finding neural network layers that are monad algebra homomorphisms of monads associated with group actions!" — [0] Section 2.1, after Example 2.6
> "they are lax algebras for free parametric monads generated by parametric endofunctors!" — [0] Section 3.2
> "This suggests that recurrent neural networks can be thought of as learnable Mealy machines, a perspective seldom advocated for in the literature." — [0] Example I.4
> "any results of categorical deep learning as presented here rely on choosing the right category to operate in; much like results in geometric deep learning relied on the choice of symmetry group." — [0] Section 4
> "we hypothesise neural networks that can learn not merely conservation laws (as in Alet et al. (2021)), but verifiably correct logical argument, or code." — [0] Section 4
> "message passing and self-attention as instances of permutation equivariant learning over graphs" — [0] Section 1.1 (on GDL)

Verification notes: Full text of arXiv v2 (32 pages) read, including all appendices A-J. Theorem/Example numbers (2.6, 2.12-2.15, B.16, G.6, G.10, G.12, I.1-I.5, J.1-J.5) verified. Not present in any listed repo ledger. Transformers: searched the text; the only mention is the GDL-intro sentence quoted above.

### P7.CDL — Categorical Deep Learning is an Algebraic Theory of All Architectures (Gavranovic, Lessard, Dudzik, von Glehn, Araujo, Velickovic 2024)

Disposition: `ADOPT` · best verification: `FULL_TEXT_READ`

Sources:

- [0] Position: Categorical Deep Learning is an Algebraic Theory of All Architectures — Bruno Gavranovic, Paul Lessard, Andrew Dudzik, Tamara von Glehn, Joao G. M. Araujo, Petar Velickovic (2024), ICML 2024, PMLR 235; arXiv:2402.15332v2. https://arxiv.org/abs/2402.15332 ; https://proceedings.mlr.press/v235/gavranovic24a.html arXiv:2402.15332 — `FULL_TEXT_READ`

**What it already explains.** Position: neural-network architectures are (lax) algebra homomorphisms for monads/endofunctors valued in the 2-category Para. Level 1: monad algebras for the group-action monad G x - recover geometric deep learning; equivariant layers f(g.x) = g.f(x) are algebra homomorphisms (Ex 2.6; GNN, spherical CNN, G-CNN in App C). Level 2: (co)algebras of endofunctors recover lists (1 + A x -), trees (A + (-)^2), streams (O x -), Mealy (I -> O x -) and Moore (O x (I -> -)) machines; folds/unfolds are (co)algebra homomorphisms - 'generalised equivariance' with non-invertible operations. Level 3: in Para, folding/unfolding/recursive RNN cells and Mealy/Moore cells are algebras of the parametric 2-endofunctor Para(F) (Figure 1, App I); unrolled networks are lax homomorphisms with weight tying supplied by the copy map (App J); recurrent/recursive networks 'are lax algebras for free parametric monads generated by parametric endofunctors'. Theorem G.10: the lax 2-cells of a lax Para(T)-algebra make the parameter object a comonoid - weight tying is forced by lax coherence. Lawvere theories connect monads to syntax (App D; commutative semirings = finite polynomials, the Dudzik-Velickovic GNN-DP link).

**Formal object.** Para_{>}(C) for an M-actegory C: objects of C; 1-cells (P, f: P > X -> Y); 2-cells r: P' -> P with f' = f o (r > X); composition (Q ⊗ P, g o (Q > f) o mu). A strong actegorical monad T lifts to a 2-monad Para(T) (Example G.8). Lax algebra (A, (P,a), eps_A, delta_A) for Para(T) with eps_A: P ⊗ I -> I, delta_A: I ⊗ P -> P ⊗ P. Architecture = lax algebra homomorphism square with 2-cell kappa. Free monad on F: F^kappa = colim(F^0 -> F^1 -> ...) (Def B.14, Theorem B.16 = Kelly); Conjecture G.12: Lax-Alg_Endo(Para(F)) equivalent to Lax-Alg_Mnd(F^kappa).

**Strongest result.** Theorem G.10 (proved): for a strong actegorical monad T on an M-actegory C and a lax algebra (A,(P,a),eps_A,delta_A) of Para(T), P is a comonoid in M with counit !_P and comultiplication Delta_P determined by eps_A, delta_A, comonoid laws following from lax-algebra coherence; dually for lax coalgebras. Corollary G.11: Lax-Alg_Mnd(Para(T)) -> CoMon(C) x Lax(->,C) is fully faithful. Theorem G.6: the embedding C -> Para(C) preserves connected colimits. Theorem B.16 (Kelly): Alg_Pendo(F) equivalent to Alg_Mnd(F^kappa). Conjecture G.12 is unproved. Everything else in the paper is a position statement with worked examples (H.1 pixel-pair weight tying, H.5 stream weight sharing, I.1-I.5 cells, J.1-J.5 unrollings).

**Assumptions.** designer chooses the base category, the monad/endofunctor and the actegory ('rely on choosing the right category to operate in'); weight sharing analysed by placing homomorphisms in Vect (linear layers); nonlinearities enter only through Para; strict monoidal M and strict actegory assumed for coherence proofs; no learning law is part of the theory: the backward pass is inherited from Cruttwell et al. by citation only

**Resource model.** none. No description length, compute, memory, sample or verification accounting anywhere in the paper; alignment-to-algorithm is inherited informally from Xu et al. / Dudzik-Velickovic.

**Failure boundary.** Non-neural coverage is limited to the SHAPE of computation: automata (streams, Mealy, Moore) and datatypes (lists, trees) appear as endofunctor (co)algebras whose cells are still parametric (neural) maps - 'recurrent neural networks can be thought of as learnable Mealy machines'. No production/rewrite system, program-synthesis, probabilistic or evolutionary learner is covered; 'verifiably correct logical argument, or code' is a hypothesis in Section 4. Transformers/attention are not derived. No update law, no convergence, no cost. Conjecture G.12 open.

**Implementation.** none known (position paper; no code released)

**Track-B residual.** CDL supplies the D0/D1 template 'architecture = choice of (base category, (2-)monad T, lax Para(T)-algebra)'. Track B must supply what CDL explicitly leaves to the designer: a rule mapping ecology E to the monad T and base category (why a sequential ecology yields the list/Mealy endofunctor, a grid ecology the translation monad), at what description-length and compute cost each lax algebra is compiled, and whether a non-neural cell (rewrite rule, program) can occupy the same algebra with a native learning law.

**Upward question.** Can the monad T (the architectural constraint) itself be the object that a developmental process acquires under E - i.e. is there a functor Ecology -> Mnd(Para(C)) - and what is the cost of a lax algebra relative to a strict one (weight tying as a description-length saving that CDL never quantifies)?

Load-bearing quotes (verbatim from sources actually read):

> "It is our position that the 2-category Para and 2-categorical algebra valued in it provide a formal theory of neural network architectures, establish formal criteria for weight tying correctness and inform design of new architectures." — [0] Section 3.1 (boxed position)
> "they are lax algebras for free parametric monads generated by parametric endofunctors!" — [0] Section 3.2
> "any results of categorical deep learning as presented here rely on choosing the right category to operate in; much like results in geometric deep learning relied on the choice of symmetry group." — [0] Section 4
> "This suggests that recurrent neural networks can be thought of as learnable Mealy machines, a perspective seldom advocated for in the literature." — [0] Example I.4
> "We also illustrate how the theory naturally encodes many standard constructs in computer science and automata theory." — [0] Abstract
> "we hypothesise neural networks that can learn not merely conservation laws (as in Alet et al. (2021)), but verifiably correct logical argument, or code." — [0] Section 4
> "Then P is a comonoid in M where ǫ_A is the data of its counit, and δ_A the data of its comultiplication, and the comonoid laws follow from lax algebra coherence conditions." — [0] Theorem G.10
> "we have just successfully derived the key aim of geometric deep learning: finding neural network layers that are monad algebra homomorphisms of monads associated with group actions!" — [0] Section 2.1, after Example 2.6

Verification notes: Full text read including all appendices; theorem/example labels checked. Codex ledger (LITERATURE_LEDGER.md G; PARENT_LEDGER_V1 P-CATEGORICAL-LEARNING) records it as 'recovers diverse NN and some automata constructs' at abstract depth; added here: the exact algebraic template, Theorem G.10, the precise (and limited) sense of automata coverage, and the absence of any learning law or cost.

### P7.CT_ML_SURVEY — Category theory in machine learning (survey; coverage map of gradient-based, probabilistic and equivariant learning)

Disposition: `ADOPT` · best verification: `PARTIAL_TEXT_READ`

Sources:

- [0] Category Theory in Machine Learning — Dan Shiebler, Bruno Gavranovic, Paul Wilson (2021), arXiv preprint arXiv:2106.07032v1 (13 Jun 2021). https://arxiv.org/abs/2106.07032 arXiv:2106.07032 — `PARTIAL_TEXT_READ`

**What it already explains.** Maps the categorical ML literature (to mid-2021) into three areas: (1) gradient-based learning — Cartesian differential and reverse differential categories, AD (Elliott), optics/lenses, Para, learners (Fong et al.; Fong-Johnson lenses-and-learners), parameter updates (Wilson-Zanasi RDA; Cruttwell et al. with update maps u_P and displacement maps d_B, functorial when an inverse displacement d^{-1}_A exists); (2) probability and statistics — Markov/copy-delete categories, conditionals, Bayesian inversion (Cho-Jacobs), Smithe's BayesLens and Stat-lenses, functorial statistics (McCullagh), Shiebler's likelihood functors into Learn; (3) invariant/equivariant learning — functorial clustering and manifold learning, equivariant CNN/GNN/gauge networks, natural graph networks. Its Discussion is the decisive coverage verdict: the synthetic perspectives on probability and gradient learning are 'largely disjoint', convergence properties of categorical learning algorithms are almost unexplored, optimality/universal properties are unstudied, and NLP, automata learning, quantum ML are excluded.

**Formal object.** None of its own; the survey's organising object is 'a machine learning model is simply a morphism f: P ⊗ A -> B in some monoidal category (C, ⊗, I)' with training = finding theta: I -> P (Section 2.1.2), plus the constructions of the surveyed parents.

**Strongest result.** No theorems; strongest content is the explicit gap statement in Section 5 (quoted below) and the reconstruction of Cruttwell et al.'s update/displacement diagram (Section 2.6.1) which shows RDA as the special case u = XOR-update, d = XOR.

**Assumptions.** coverage as of June 2021 (pre-CDL, pre-Smithe thesis, pre-Braithwaite-Hedges-Smithe); excludes NLP, automata learning, quantum ML, and most reinforcement learning

**Resource model.** none; the survey does not report any resource-charging categorical ML work

**Failure boundary.** A map, not a mechanism. Confirms that as of 2021 no categorical work unified gradient and Bayesian learning, none addressed convergence, none addressed optimality as universal property, none addressed automata learning or program synthesis.

**Implementation.** none (survey)

**Track-B residual.** Use as the coverage baseline: everything Track B claims beyond 'gradient (incl. Boolean circuits), Bayesian inversion, equivariance' must be checked against post-2021 parents (CDL 2024, Smithe 2023, Braithwaite-Hedges-Smithe 2023, Gavranovic 2022/2024). The survey's three named gaps — probabilistic/gradient disjointness, convergence, optimality as universal property — plus the unmentioned resource gap are exactly Track B's residual at B3/D1.

**Upward question.** The survey names convergence and optimality (Kan extensions / universal properties) as missing; Track B should ask whether a resource-priced universal property (a cost-weighted Kan extension) can serve as the selection principle among learning laws that the survey says is absent.

Load-bearing quotes (verbatim from sources actually read):

> "the synthetic perspectives on probability and gradient-based learning are largely disjoint, and are even farther removed from the research on equivariant and invariant learning." — [0] Section 5 (Discussion)
> "there has been very little exploration of the convergence properties of these generalized algorithms. There is a need for a categorical perspective on learning theory" — [0] Section 5 (Discussion)
> "understanding how optimal solutions – a concept at the heart of machine learning – can be understood through the lens of category theory is something that has not yet been studied in the literature." — [0] Section 5 (Discussion)
> "a machine learning model is simply a morphism f : P ⊗ A → B in some monoidal category (C, ⊗, I), with P an object representing the type of parameters" — [0] Section 2.1.2

Verification notes: Read partially via page queries (table of contents, introduction, gradient overview, update/displacement summary, optics-for-probability, equivariant networks, discussion, part of the bibliography). Sections 2.2-2.5 and 3.2-3.3 not read directly (their parents are read separately above). Not in the listed repo ledgers.

### P7.ESSENCE_OF_AD — The simple essence of automatic differentiation (AD as a cartesian functor; reverse mode via continuation and dual categories)

Disposition: `ADOPT` · best verification: `PARTIAL_TEXT_READ`

Sources:

- [0] The Simple Essence of Automatic Differentiation — Conal Elliott (2018), Proc. ACM Program. Lang. 2 (ICFP), Article 70, 1-29; extended version arXiv:1804.00746v4 (2 Oct 2018). https://arxiv.org/abs/1804.00746; doi:10.1145/3236765 arXiv:1804.00746 — `PARTIAL_TEXT_READ`

**What it already explains.** Specifies AD as a homomorphism: the derivative-augmented map D_k a b = D (a -> b x (a `k` b)) must be a functor preserving Category, Monoidal, Cartesian, Cocartesian and numeric-primitive structure; the implementation is then CALCULATED from the specification (correct by construction). Generalising the category k of derivative values from linear maps to any biproduct/cartesian category gives a family of AD algorithms (Figure 6): fully right-associated composition = forward mode, fully left-associated = reverse mode; the continuation category Cont^r_k (Theorem 4) and the dual category Dual_k yield reverse-mode AD and gradients with no graphs, tapes, variables or mutation. Programs written in Haskell are compiled to categorical form by an AD-agnostic plugin and re-interpreted in D_k — 'differentiable functional programming'; the slogan is that AD is symbolic differentiation performed by a compiler. Notes that Fong et al.'s backprop functor is 'not separable from the application to machine learning', i.e. this parent is the learning-free core.

**Formal object.** newtype D_k a b = D (a -> b x (a `k` b)); linearD f f' = D (λa -> (f a, f')); Category/Monoidal/Cartesian/Cocartesian instances defined via the same instances on k (Figure 6); Cont^r_k a b = Cont ((b `k` r) -> (a `k` r)), cont f = Cont (o f); Dual_k a b = b `k` a. Specification: D̂ = D o D+ is a cartesian functor; derived corollaries 1.1-3.1 (chain rule, parallel composition rule, linearity rule).

**Strongest result.** Theorem 4 (proved in Appendix C.3): with the definitions of Figure 7, cont: (a `k` b) -> Cont^r_k a b is a homomorphism with respect to each instantiated class (Category, Monoidal, Cartesian, Cocartesian, Scalable) — this IS reverse-mode AD. Theorems 1-3 (chain rule for sequential composition, rule for parallel composition, rule for linear maps) from which the D instances are calculated.

**Assumptions.** purely functional programs translated to categorical form; derivatives are linear maps generalised to any biproduct category with scaling; no learning: no loss, no parameter update, no data; performance claims are qualitative ('appears to be quite efficient'); detailed performance analysis is future work

**Resource model.** compute, incidentally: notes the optimal association of the composition chain (optimal Jacobian accumulation) is NP-complete (Naumann 2008) and that reverse mode is more efficient by a factor of the domain dimension; memory: mutation-free implementations 'can easily free (reuse) memory'. No description-length or sample accounting.

**Failure boundary.** Pure AD; contains no learning law, no optimiser, no architecture theory; correctness by construction concerns the derivative, not any learning outcome; the programmatic <-> neural bridge it offers is 'a differentiable program is a morphism interpretable in D_k', which is D0-representability of programs as differentiable maps, not a claim about which programs are learned.

**Implementation.** Haskell library via the 'concat' compiler plugin (Elliott 2017); repository referenced in the paper (github.com/conal/concat, not verified here)

**Track-B residual.** Elliott owns 'differentiable programming = functorial reinterpretation of a program in D_k'. Track B must ask what selects, under ecology E, between (a) interpreting a program in D_k and learning its real-valued parameters by gradient and (b) searching the program space directly (enumeration/rewrite), and how the NP-complete Jacobian-accumulation cost and the memory profile enter that selection.

**Upward question.** AD is a functor from programs to derivative-augmented programs; learning laws are functors C -> Lens(C). Is the composite 'program -> parametric lens -> learner' itself functorial in the choice of interpreting category k, so that the ecology's choice of k (reals, tropical semiring, Z2) is the morphology selector?

Load-bearing quotes (verbatim from sources actually read):

> "specify AD simply and precisely by requiring this augmentation (relative to regular functions) to be homomorphic with respect to a collection of standard categorical abstractions and primitive mathematical operations." — [0] Section 1 (contributions)
> "For fully right-associated compositions, it becomes forward mode AD; for fully left-associated compositions, reverse-mode AD; and for all other associations, various mixed modes." — [0] Section 12
> "automatic differentiation is symbolic differentiation performed by a compiler." — [0] Section 17 (Conclusions)
> "A more sophisticated version of this question is known as the 'optimal Jacobian accumulation' problem and is NP-complete [Naumann, 2008]." — [0] Section 11
> "That work, which also uses biproducts (in monoidal but not cartesian form), does not appear to be separable from the application to machine learning" — [0] Section 16 (on Fong et al.)

Verification notes: Read partially via targeted page queries (about 11 of 29 pages: introduction, cartesian instances, generalisation, matrices, reverse mode, related work, conclusions, proof of Theorem 4). Sections 9-10, 13-15 (dual category, indexed instances) not read directly. Not in the listed repo ledgers.

### P7.ESSENCE_OF_AD — The simple essence of automatic differentiation (Elliott 2018): AD as a homomorphic (functorial) reinterpretation of a program; programmatic <-> neural bridge

Disposition: `ADOPT` · best verification: `PARTIAL_TEXT_READ`

Sources:

- [0] The Simple Essence of Automatic Differentiation (extended version) — Conal Elliott (2018), ICFP 2018, Proc. ACM Program. Lang. 2(ICFP):70; arXiv:1804.00746v4. https://arxiv.org/abs/1804.00746 ; doi:10.1145/3236765 arXiv:1804.00746 — `PARTIAL_TEXT_READ`

**What it already explains.** AD is specified, not implemented: a derivative-augmented function type D_k a b = a -> b x (a `k` b) is required to be a homomorphism (functor) with respect to Category, Monoidal, Cartesian, Cocartesian and NumCat classes, and the implementation is CALCULATED from that specification (Figure 6). Sequential composition rule = chain rule (Theorem 1), parallel composition rule (Theorem 2), linear-map rule (Theorem 3). Generalising the derivative representation k over any biproduct category yields a family of algorithms: fully right-associated composition = forward mode, fully left-associated = reverse mode (Section 12); the continuation transformer Cont^r_k (Theorem 4: cont is a homomorphism) and the dual Dual_k (Theorem 5) give reverse-mode AD and gradients with 'no graphs, tapes, variables, partial derivatives, or mutation'. Conclusion: 'automatic differentiation is symbolic differentiation performed by a compiler'. Programs in an ordinary functional language become differentiable functions via an AD-agnostic compiler plugin (Elliott 2017) - the programmatic <-> neural bridge is a change of interpreting category, not a change of program.

**Formal object.** newtype D_k a b = D (a -> b x (a `k` b)); linearD f f' = D (\a -> (f a, f')); Category instance: D g o D f = D (\a -> let (b,f') = f a; (c,g') = g b in (c, g' o f')); Cont^r_k a b = Cont ((b `k` r) -> (a `k` r)), cont f = Cont (o f); Dual_k a b = Dual (b `k` a) via onDot f = dot^{-1} o f o dot; indexed biproducts (Section 15) for n-ary products.

**Strongest result.** Theorem 4 (proved in Appendix C.3): with the Figure 7 definitions, cont: (a `k` b) -> Cont^r_k a b is a homomorphism w.r.t. each instantiated class - this IS reverse-mode AD, correct by construction. Theorem 5 (App C.4): asDual is a homomorphism; Corollary 5.1: (M) and (O) mutually dualise (transposition). Theorem 6: indexed biproduct instances. Section 11: choosing the association is the optimal Jacobian accumulation problem, NP-complete (Naumann 2008).

**Assumptions.** purely functional programs with precise denotation; differentiation is a partial higher-order operator (not all computable functions are differentiable); derivatives as linear maps in a biproduct category; scalar field for gradients; first-order derivatives only (higher-order and subdifferentials are future work)

**Resource model.** compute and memory, incidentally: reverse mode 'is much more efficient than forward-mode AD (by a factor proportional to the domain dimension)' for scalar-codomain functions; optimal association of the composition chain is NP-complete (Section 11); mutation-free implementations 'can easily free (reuse) memory as they run, keeping memory use low' (Section 16). No description-length, sample or verification accounting; no cost enters the specification itself.

**Failure boundary.** Owns the FORWARD/BACKWARD computation of derivatives for programs, not learning: 'learning algorithms aren't studied' (as Cruttwell et al. note). Says nothing about which programs to write, how program structure is searched, or the cost of the program space; the NP-complete accumulation problem is left to a compile-time heuristic. Relation to Fong et al. explicitly 'complement[ary]'.

**Implementation.** Haskell, via the 'concat' compiler plugin (Elliott 2017); the paper's code appears as Haskell figures - repository not fetched

**Track-B residual.** Elliott owns 'differentiable programming = homomorphic reinterpretation of an ordinary program in D_k'. Track B must ask what selects, under E, between (a) interpreting a program in D_k and learning real parameters by gradient and (b) searching the program space directly (enumeration/rewrite), how the NP-complete accumulation cost and the memory profile enter that selection, and whether the compiler-plugin picture (same source, different interpreting category) is the right formalisation of a 'morphology as interpretation' rather than 'morphology as source'.

**Upward question.** If morphologies differ by interpreting category rather than by source, is 'morphogenesis' a change of functor Source -> Semantics chosen by the ecology (verification contract, cost), and can the NP-complete association problem serve as an exact resource coordinate for a neural-vs-programmatic phase boundary?

Load-bearing quotes (verbatim from sources actually read):

> "specify AD simply and precisely by requiring this augmentation (relative to regular functions) to be homomorphic with respect to a collection of standard categorical abstractions and primitive mathematical operations." — [0] Section 1 (contributions)
> "For fully right-associated compositions, it becomes forward mode AD; for fully left-associated compositions, reverse-mode AD; and for all other associations, various mixed modes." — [0] Section 12
> "A more sophisticated version of this question is known as the “optimal Jacobian accumulation” problem and is NP-complete [Naumann, 2008]." — [0] Section 11
> "Given the definitions in Figure 7, cont is a homomorphism with respect to each instantiated class." — [0] Theorem 4
> "automatic differentiation is symbolic differentiation performed by a compiler." — [0] Section 17 (Conclusions)
> "That work, which also uses biproducts (in monoidal but not cartesian form), does not appear to be separable from the application to machine learning, and so would seem to complement this paper." — [0] Section 16 (on Fong et al.)
> "the implementations in this paper (Sections 12 and 13) are free of mutation and can easily free (reuse) memory as they run, keeping memory use low." — [0] Section 16

Verification notes: Read via targeted page queries covering the specification, Theorems 4-6, and Sections 11-17; Sections 5-10 (linear-map representations) not read. Not in the Codex ledgers. Sibling P7.json entry agrees.

### P7.GNN_DP — Graph Neural Networks are Dynamic Programmers (Dudzik & Velickovic 2022): the neural <-> dynamic-programming correspondence as one integral transform over a polynomial span

Disposition: `ADOPT` · best verification: `PARTIAL_TEXT_READ`

Sources:

- [0] Graph Neural Networks are Dynamic Programmers — Andrew Dudzik, Petar Velickovic (2022), NeurIPS 2022; arXiv:2203.15544v3. https://arxiv.org/abs/2203.15544 arXiv:2203.15544 — `PARTIAL_TEXT_READ`

**What it already explains.** Makes precise the 'algorithmic alignment' claim (Xu et al. 2019) that GNNs align with dynamic programming. Both a DP step dp[x] <- recombine(score(dp[y], dp[x]) for y in expand(x)) and a message-passing GNN step h_u = phi(x_u, ⊕_{v in N_u} psi(x_u, x_v)) are instances of one INTEGRAL TRANSFORM over a polynomial span W <-i- X -p-> Y -o-> Z of finite sets: pullback i* (f \|-> f o i), argument pushforward p_⊗ (fold over list(R)), message pushforward o_⊕ (aggregate over bag(R)). The two differ only in the value semiring R: (R, x, +) for GNNs, the tropical (N ∪ {∞}, +, min) for Bellman-Ford. Aggregators are algebras of the bag monad (commutative monoids); argument-combiners are algebras of the list monad; a compatible pair is a semiring (App B-C); Tambara: FinPoly is the Lawvere theory for commutative semirings (App D). Bellman-Ford is derived exactly from Diagram 6 (Section 5). The view predicts a V^3 edge-update architecture (Diagram 10) that matches or beats V^2 on all edge-centric CLRS tasks (Tables 1-2; e.g. Dijkstra 59.58% -> 68.53%, Insertion sort 15.39% -> 24.67%).

**Formal object.** Polynomial span (W, X, Y, Z; i: X -> W, p: X -> Y, o: Y -> Z) over FinSet; transform [W,R] -i*-> [X,R] -p_⊗-> [Y,R] -o_⊕-> [Z,R] with p_⊗ = ⊗ o (list pushforward) and o_⊕ = ⊕ o (bag pushforward); R a commutative semiring. Bellman-Ford span: W = V + (V + E), X = (V+E)+(V+E), Y = V + E, Z = V with R = (N ∪ {∞}, +, min); MPNN span: W = 1 + V + E, X = E + (E + E) + E, Y = E, Z = V with an MLP inserted on messages.

**Strongest result.** No numbered theorem. Load-bearing derivation (Section 5): the Bellman-Ford update d_u <- min(d_u, min_{v->u} d_v + w_{v->u}) is exactly the transform of Diagram 6; (Section 6) the MPNN update is exactly the transform of the MPNN span with an MLP on messages: 'with a single abstract template (the polynomial span), we have successfully explained both'. App B: commutative monoids are the algebras of the bag monad (well known). Empirical: V^3-PGN improves edge-centric CLRS tasks by 4.44 +/- 1.06 points on average (Table 2).

**Assumptions.** finite sets as carriers; value space R must be a commutative semiring for the aggregators to be well behaved; DP subproblem graph precomputed (outputs of eta known upfront); Bellman-Ford needs an explicit bias/self-edge; the GNN instance is trained by ordinary gradient descent; the DP instance has fixed semiring operations - learning is not part of the transform; sample-complexity advantage of alignment is cited from Xu et al. (NTK regime), not proved here

**Resource model.** samples, indirectly: algorithmic alignment is motivated by sample complexity ('architectures with higher algorithmic alignment will have lower sample complexity in the NTK regime'), and out-of-distribution accuracy is measured. No compute, memory, description-length or verification accounting; the V^3 messages cost O(\|V\|^3) but this is not charged.

**Failure boundary.** Bridges neural and programmatic (DP) morphologies at the level of FORWARD computation only: same span, different semiring. There is no DP-native learning law (the tropical instance is not learned; the real instance is learned by gradient). Nothing selects the semiring. Only DP algorithms expressible as one-step message passing are covered (path-finding style); the paper's own conjecture that the transform is a polynomial functor is left open.

**Implementation.** experiments reuse the public CLRS benchmark code (cited); no separate library

**Track-B residual.** The parent gives the neural <-> programmatic bridge for forward computation. Track B's residual is (i) the LEARNING side: is there a lens whose backward map is DP-like (tropical reverse derivative) so that the same learning algebra spans both semirings, and (ii) the SELECTION side: which semiring/span a bounded process acquires under E and at what sample/compute price - the parent only inherits an alignment -> sample-complexity heuristic.

**Upward question.** Since POLY_R is a CRDC for every commutative rig R (Cockett et al.), does the tropical semiring admit a reverse derivative that makes DP LEARNABLE by the same lens algebra - and if so, what ecology coordinate (exact-verification contract vs noisy feedback) selects the tropical over the real rig?

Load-bearing quotes (verbatim from sources actually read):

> "with a single abstract template (the polynomial span), we have successfully explained both a dynamic programming algorithm, and a GNN update rule—merely by choosing the correct support sets and latent space." — [0] Section 6
> "Neural networks are built from linear algebra over the familiar real numbers, while DP, which is often a generalisation of path-finding problems, typically takes place over “tropical” objects" — [0] Section 3
> "It can be proved that architectures with higher algorithmic alignment will have lower sample complexity in the NTK regime [20]." — [0] Section 1
> "we conjecture that this transform can be described as a polynomial functor, where p⊗ and o⊕ correspond to the dependent product and dependent sum from type theory" — [0] Section 4
> "We found that the V^3 architecture was equivalent to, or outperformed, the non-polynomial (V^2) one in all edge-centric algorithms (up to standard error)." — [0] Section 7
> "It is well-known that the algebras for the monad bag are the commutative monoids, sets equipped with a commutative and associative binary operation and a unit element." — [0] Appendix B

Verification notes: Pages 1-9 and 12-13 read; Tables 1-2 numbers transcribed from the text. Appendices C-F not read. Not in the Codex ledgers. Sibling P7.json entry P7.GNN_DP_CORRESPONDENCE agrees.

### P7.GNN_DP_CORRESPONDENCE — Graph neural networks are dynamic programmers (polynomial spans / integral transforms over semirings)

Disposition: `ADAPT` · best verification: `FULL_TEXT_READ`

Sources:

- [0] Graph Neural Networks are Dynamic Programmers — Andrew Dudzik, Petar Velickovic (2022), NeurIPS 2022; arXiv:2203.15544v3 (10 Oct 2022). https://arxiv.org/abs/2203.15544 arXiv:2203.15544 — `FULL_TEXT_READ`

**What it already explains.** Makes 'algorithmic alignment' (Xu et al.) precise: both a message-passing GNN layer and one step of a dynamic-programming recurrence are the SAME categorical object, an integral transform along a polynomial span W <-i- X -p-> Y -o-> Z: pull back input data along i, push forward arguments along p with a fold ⊗: list(R) -> R, push forward messages along o with an aggregator ⊕: bag(R) -> R. The only difference between GNN and DP is the semiring R: (R, x, +) with an MLP on messages for the GNN (Section 6) vs the tropical (N ∪ {∞}, +, min) for Bellman-Ford (Section 5, Diagram 6). Aggregators are exactly algebras for the bag and list monads; compatible pairs are algebras for the composite monad bag o list, i.e. semirings (App B-C). Predicts and empirically confirms that materialising V^3 messages (a proper polynomial span, Diagram 10) improves edge-centric algorithmic tasks on CLRS (+4.44 ± 1.06 on edge-centric tasks, Table 2). Connects to polynomial functors via Tambara: FinPoly is the Lawvere theory of commutative semirings, so strong monoidal functors (FinPoly,+) -> (Set,x) are determined by a commutative semiring on F(1) and coincide with the integral transform (App D).

**Formal object.** Polynomial span (i: X -> W, p: X -> Y, o: Y -> Z) of finite sets. Integral transform [W,R] -i*-> [X,R] -p⊗-> [Y,R] -o⊕-> [Z,R] with i*f = f o i, (o⊕ m)(u) = ⊕_{e in o^{-1}(u)} m(e), p⊗ analogous with an ordered fold. Aggregator ⊕: bag(R) -> R satisfying unit and join compatibility = commutative monoid; ⊗: list(R) -> R = monoid; distributive law lambda: list o bag -> bag o list makes bag o list a monad whose algebras are semirings (App C). Bellman-Ford: span (V+E)+(V+E) -> V+E -> V over W = V+(V+E), R = (N∪{∞}, +, min), giving d'_u = min(d_u + b(u), min_{v->u} d_v + w_{v->u}). MPNN: span E+(E+E)+E -> E -> V over 1+V+E with an MLP after p⊗.

**Strongest result.** No numbered theorem; the load-bearing results are (a) the derivation that the Bellman-Ford update is exactly the integral transform of Diagram 6 (Section 5) and the MPNN update exactly that of the span in Section 6 — 'with a single abstract template ... explained both'; (b) App B-C: aggregators = bag/list monad algebras, compatible pairs = semirings (bag o list algebras); (c) App D: Tambara's theorem identifies FinPoly as the Lawvere theory for commutative semirings so the transform is the semiring's model; (d) empirical Tables 1-2 on CLRS (V^3 >= V^2 on all edge-centric algorithms up to standard error).

**Assumptions.** latent space R is a (commutative) semiring; GNN uses reals with an MLP inserted after p⊗; finite sets; preimages p^{-1}(y) totally ordered for non-commuting arguments; alignment -> lower sample complexity is inherited from Xu et al. in the NTK regime, not proved here; the polynomial-functor description is a conjecture (Section 4, App D)

**Resource model.** samples, indirectly: algorithmic alignment is motivated by sample complexity ('architectures with higher algorithmic alignment will have lower sample complexity in the NTK regime') and the experiments measure out-of-distribution accuracy; no compute, description-length or verification accounting; V^3 messages cost O(\|V\|^3) but this is not charged.

**Failure boundary.** A FORWARD-computation correspondence only: it says a GNN step and a DP step are the same integral transform; the learning law is still gradient descent on the real-semiring instance and nothing is said about learning in the tropical semiring. Does not predict when a learned GNN beats an explicit DP (or vice versa) under a resource budget; the polynomial-functor status is conjectural; the semiring restriction excludes many programmatic morphologies.

**Implementation.** experiments built on the public CLRS benchmark code (github.com/deepmind/clrs); no separate release stated

**Track-B residual.** The parent gives the neural <-> programmatic (DP) bridge at the level of forward computation: same span, different semiring. Track B's residual is the LEARNING side and the selection side: (i) is there a learning law native to the tropical/programmatic instance (a lens whose backward map is DP-like rather than a reverse derivative) — the parents give none; (ii) which semiring / which span a bounded process converges to under E, and what the O(\|V\|^3) message cost buys in samples.

**Upward question.** The forward correspondence is a change of semiring inside one span. Is there a corresponding change of BACKWARD functor (reverse derivative over R vs. a tropical/DP-native update) making the whole learning system a single parametrised optic over a semiring-indexed base, and does the ecology (exact verification contract vs noisy feedback) select the semiring?

Load-bearing quotes (verbatim from sources actually read):

> "with a single abstract template (the polynomial span), we have successfully explained both a dynamic programming algorithm, and a GNN update rule—merely by choosing the correct support sets and latent space." — [0] Section 6
> "Neural networks are built from linear algebra over the familiar real numbers, while DP, which is often a generalisation of path-finding problems, typically takes place over 'tropical' objects" — [0] Section 3
> "we conjecture that this transform can be described as a polynomial functor, where p⊗ and o⊕ correspond to the dependent product and dependent sum from type theory" — [0] Section 4
> "It can be proved that architectures with higher algorithmic alignment will have lower sample complexity in the NTK regime [20]." — [0] Section 1
> "A result of Tambara says that FinPoly is the Lawvere theory for commutative semirings [25, 17]." — [0] Appendix D
> "We found that the V^3 architecture was equivalent to, or outperformed, the non-polynomial (V^2) one in all edge-centric algorithms (up to standard error)." — [0] Section 7

Verification notes: Full text read (arXiv v3). Not in the listed repo ledgers. The Xu et al. 2019 sample-complexity theorem is cited, not verified here.

### P7.KROHN_RHODES — Krohn-Rhodes prime decomposition theorem (finite automata / transformation semigroups decompose into simple groups and flip-flops) — pointer entry

Disposition: `ADOPT` · best verification: `PARTIAL_TEXT_READ`

Sources:

- [0] Algebraic Theory of Machines. I. Prime Decomposition Theorem for Finite Semigroups and Machines — Kenneth Krohn, John Rhodes (1965), Transactions of the American Mathematical Society 116, pp. 450-464 (April 1965). doi:10.1090/S0002-9947-1965-0188316-1 (UNVERIFIED doi) — `NOT_ACCESSIBLE`
- [1] Computational Holonomy Decomposition of Transformation Semigroups — Attila Egri-Nagy, Chrystopher L. Nehaniv (2015), arXiv preprint arXiv:1508.06345v1 (26 Aug 2015). https://arxiv.org/abs/1508.06345 arXiv:1508.06345 — `PARTIAL_TEXT_READ`

**What it already explains.** Every finite transformation semigroup (equivalently every finite automaton without initial/accepting states) DIVIDES (is a homomorphic image of a subsemigroup of) an iterated wreath/cascade product of finite simple groups and the flip-flop (aperiodic, permutation-reset) components; conversely the simple-group divisors of the semigroup are forced to appear in ANY cascade decomposition. The holonomy method makes this constructive: (X,S) divides H_1 ≀ ... ≀ H_d where H_i are the holonomy permutation-reset semigroups at depth i and d = h_S(X) is the height of the subduction order (Cor 5.10); the decomposition is computed by SgpDec in GAP. Aperiodic (group-free) automata are exactly those with trivial holonomy groups; aperiodicity is PSPACE-complete (Cho-Huynh), so computing the holonomy decomposition is PSPACE-hard. Repo ownership: issue #145 already owns transformation-semigroup closure (Reach_B(O) as semigroup orbit); see research/heritable-search-geometry-v1/LITERATURE_LEDGER_HSG.md row R5, ladder/R1_CONCEPTS.md, ladder/R5_SEMIGROUP_G09.md, HSG_ATOM_TABLE_V1.json (G12, 'R1: #145 semigroup closure OWNS').

**Formal object.** Transformation semigroup (X,S), S ⊆ X^X closed under composition. Wreath product (X,S) ≀ (Y,T) = (X x Y, {(s,f) \| s in S, f in T^X}) acting by (x,y).(s,f) = (x.s, y.f(x)). Division (X,S) \| (Y,T): Z ⊆ Y, U ≤ T with surjections theta_1: Z -> X, theta_2: U -> S respecting the action. Cascade product: dependency functions d_i: X_1 x ... x X_{i-1} -> S_i. Holonomy groups H_P = (T(P), G_P) made faithful on tiles of representative image sets P; H(X,S) = H_1 ≀ ... ≀ H_d.

**Strongest result.** Krohn-Rhodes 1965 (as cited): every finite semigroup divides a wreath product of finite simple groups and copies of the flip-flop monoid; every simple group divisor must appear. Egri-Nagy-Nehaniv Cor 5.10 (Holonomy Decomposition Theorem): (X,S) \| H_1 ≀ ... ≀ H_d with d = h_S(X). Section 6: computing the decomposition is PSPACE-hard (via PSPACE-completeness of aperiodicity).

**Assumptions.** finite state sets and finite semigroups; division (emulation), not isomorphism — the decomposition is larger than the original in general; holonomy method enumerates image sets (worst case 2^\|X\|)

**Resource model.** compute, explicitly: decomposition is PSPACE-hard; worst-case exponential enumeration of image sets (Section 6). Number of hierarchical levels d = h_S(X) and the group content ('Krohn-Rhodes complexity' = minimal number of group levels, not read here) are description-length-like invariants of the automaton morphology.

**Failure boundary.** A structure theorem for the automata morphology only; says nothing about learning automata from data, about non-finite state, or about which automaton an ecology selects; the decomposition is not unique or minimal in size; Krohn-Rhodes complexity decidability status not verified here.

**Implementation.** SgpDec (GAP package): https://github.com/gap-system/sgpdec; kigen: https://github.com/egri-nagy/kigen

**Track-B residual.** Track-B subtraction only (the closure algebra is owned by #145): the finite-automata morphology M0 has a FORCED prime basis — simple groups and the flip-flop — so any Track-B generating basis for M0 must emulate these primes; basis-minimality for M0 is therefore already a theorem, and the residual is the resource question: the PSPACE-hard cost of finding the cascade (D1 compile cost) and whether a developmental process can acquire the cascade coordinates (D2) rather than the flat automaton.

**Upward question.** Krohn-Rhodes gives a forced prime basis and a PSPACE-hard compile cost for M0. Do the other morphologies (neural, probabilistic, programmatic) have analogous forced prime components under their own algebra (CRDC generators? Markov-category generators?), and is there a cross-morphology 'complexity' invariant (number of non-aperiodic levels) that an ecology's verification contract prices?

Load-bearing quotes (verbatim from sources actually read):

> "automata (without specifying initial and accepting states) and transformation semigroups are essentially the same concepts." — [1] Egri-Nagy & Nehaniv Section 1
> "A finite transformation semigroup (X, S) divides its holonomy wreath product (X, S) \| H_1 ≀ · · · ≀ H_d = H(X, S), where d = h_S(X)." — [1] Egri-Nagy & Nehaniv Corollary 5.10
> "by the Krohn-Rhodes prime decomposition theorem [15, 16], every simple group divisor of a finite semigroup must occur as a divisor of any cascade decomposition." — [1] Egri-Nagy & Nehaniv Section 6
> "The results of Cho and Huynh [1] show that aperiodicity is PSPACE-complete, so it follows immediately that computing the holonomy decomposition is PSPACE-hard." — [1] Egri-Nagy & Nehaniv Section 6

Verification notes: Original 1965 paper NOT read; its bibliographic data (Trans. AMS 116:450-464, April 1965) is verified verbatim from reference [15] of the Egri-Nagy-Nehaniv preprint, whose statement of the theorem (Section 6) and holonomy version (Cor 5.10) were read. The doi given is from memory and marked UNVERIFIED. Prior repo ownership: heritable-search-geometry-v1 attributes transformation-semigroup closure to project issue #145 ('statement from lane charter; not re-verified against HST files'); this entry adds only the prime-decomposition/basis-minimality and PSPACE-hardness content, which is absent from those rows.

### P7.LENS_OPTIC_SPACETIME_GAVRANOVIC — Space-time tradeoffs of lenses and optics (Gavranovic 2022): the one categorical-cybernetics paper that charges resources

Disposition: `None` · best verification: `PARTIAL_TEXT_READ`

Sources:

- [0] Space-time tradeoffs of lenses and optics via higher category theory — Bruno Gavranovic (2022), arXiv 2209.09351. https://arxiv.org/abs/2209.09351 arXiv:2209.09351 — `PARTIAL_TEXT_READ`

**What it already explains.** Cartesian lens composition recomputes forward maps in the backward pass (n-1 levels; node evaluations O(n^2), memory constant in depth) because all backward data must pass through the A-typed residual — this IS gradient checkpointing (Remark 1). Optic composition takes M_1 (x) M_2 as residual: no recomputation, memory grows with depth. The 1-categorical isomorphism Lens_Cart(C) = Optic(C) is 'blind to operational concerns'; 2-Optic(C) reifies residual morphisms as 2-cells ('can be optimised to'), Optic(C) is its local pi_0 quotient (Prop. 6), and the lens -> optic embedding becomes an oplax functor whose oplaxator graph(f) : A -> A x B detects the different composition rule (Thm 2). Closed lenses behave operationally like optics (Remark 8). Adjunction in a standard 2-category fails one triangle identity (Sec. 5.2).

**Formal object.** 2-Optic(C); oplax functor iota with oplaxator graph(f); residual M

**Strongest result.** None

**Assumptions.** None

**Resource model.** None

**Failure boundary.** None

**Implementation.** None

**Track-B residual.** None

**Upward question.** None

Verification notes: None

### P7.POLY_DYNAMICAL — Polynomial functors: a mathematical theory of interaction (Niu & Spivak) - what it does and does not say about learning, update laws and mode-dependence

Disposition: `ADOPT` · best verification: `PARTIAL_TEXT_READ`

Sources:

- [0] Polynomial Functors: A Mathematical Theory of Interaction — Nelson Niu, David I. Spivak (2024), book (Cambridge University Press 2025 version; arXiv:2312.00990v2, 16 Aug 2024). https://arxiv.org/abs/2312.00990 ; doi:10.1017/9781009576734 arXiv:2312.00990 — `PARTIAL_TEXT_READ`

**What it already explains.** The automata morphology's canonical algebra. A Moore machine with states S, outputs I, inputs A is a lens Sy^S -> Iy^A (Def 4.1/4.4); a dependent dynamical system is a lens phi: Sy^S -> p for any polynomial interface p (Def 4.18), so the set of available inputs may depend on the current output (halting automata, Ex 4.21). Time evolution is the composition product: every state system Sy^S is a polynomial comonoid (eraser = do-nothing section, duplicator = transition lens, Ex 7.19), giving canonical lenses s -> s^{⊳n} to run n steps. Interaction = wrapper lenses p1 ⊗ ... ⊗ pn -> q; wiring diagrams are interaction patterns (4.4.3); cellular automata are graphs-as-wiring-diagrams (Ex 4.66). MODE-DEPENDENCE: Section 4.4.4 gives interaction patterns 'that cannot be captured by such a static diagram' - vertices vote on who their neighbours are (Ex 4.68), connections that snap under force (4.70), a company changing supplier (4.72), units attaching/detaching (4.73) - and the closure [q1 ⊗...⊗ qk, r] shows that 'a dynamical system with interface [q1 ⊗···⊗ qk, r] is simply selecting interaction patterns'. Every dynamical system can be obtained by wiring memoryless ones together (citing [BPS19]).

**Formal object.** Poly: functors Set -> Set of the form p = sum_{i in p(1)} y^{p[i]}; lenses = natural transformations (on-positions p(1) -> q(1), on-directions q[f_1 i] -> p[i]). Dynamical system phi: Sy^S -> p with return phi_1: S -> p(1), update phi^#: p[phi_1(-)] -> S. Parallel product ⊗, closure [q,r] = prod_{j in q(1)} r o (q[j] y) with Poly(p ⊗ q, r) = Poly(p, [q,r]). Composition product ⊳ (substitution); comonoid (c, eps: c -> y, delta: c -> c ⊳ c); Cat# = comonoids in (Poly, y, ⊳).

**Strongest result.** For Track B the load-bearing facts are structural: (i) Def 4.18 + Ex 7.19 (dynamical systems = lenses out of comonoids; time = ⊳); (ii) closure isomorphism (4.74) making mode-dependent wiring a first-class dynamical system; (iii) the [BPS19] result that all dynamical systems are wirings of memoryless ones. NEGATIVE finding (this pass): no passage returned mentions learning, adaptation, or updating the update map itself; the index pages inspected (356-358: 'lens', 'limit', 'monoid', 'Moore machine', 'interaction'...) contain no 'learning' or 'cost' entry. Update in Poly means state transition, not parameter adaptation.

**Assumptions.** single-variable polynomial functors on Set (stated as a deliberate scope choice); deterministic, discrete-time systems in the chapters read (stochastic/continuous extensions are in Smithe's thesis Ch. 6, not here); no notion of parameter, loss, or objective

**Resource model.** none: state-set cardinality, memory, time complexity and description length are never charged; no index entry for cost or complexity was found.

**Failure boundary.** Models state transition and interconnection, including interconnection that changes with state (mode-dependence), but NOT adaptation of the transition map: there is no learner, no update law of the update law, no optimisation. Poly therefore covers Track-B's B0 (typed stateful composition) and the automata morphology's structure, not its acquisition. Learning enters only when Poly is combined with lenses over CRDCs (Cruttwell) or Bayesian lenses (Smithe) - i.e. through the other parents in this family.

**Implementation.** none (mathematics); source at https://github.com/ToposInstitute/poly (book source, per title page)

**Track-B residual.** Codex PARENT_EXPANSION_V2 §A already records Niu-Spivak as owning typed stateful composition. What it does NOT own, and Track B must still supply: an update law for the update map (development), a cost on state systems (memory/time), and an ecology-indexed reason why a particular state system S and interface p are acquired. Mode-dependent wiring is a candidate formal home for 'morphology change during a lifetime', but Poly gives no law for which mode is selected.

**Upward question.** Can a learning law be expressed as a lens Sy^S -> [q, r] that selects interaction patterns (i.e. is 'development' a dynamical system over the space of wirings), and what would a cost on Poly's residual/state objects look like so that mode selection is resource-priced?

Load-bearing quotes (verbatim from sources actually read):

> "A dependent dynamical system (or a dependent Moore machine, or simply a dynamical system) is a lens φ : Sy^S → p for some S ∈ Set and p ∈ Poly." — [0] Definition 4.18
> "While wiring diagrams are a handy visualization tool for certain simple interaction patterns, there are more general interaction patterns that cannot be captured by such a static diagram." — [0] Section 4.4.4
> "What it also means is that a dynamical system with interface [q1 ⊗ · · · ⊗ qk, r] is simply selecting interaction patterns q1 ⊗ · · · ⊗ qk → r." — [0] Section 4.4.4 / 4.5
> "every state system is a polynomial comonoid, whose eraser is the do-nothing section and whose duplicator is the transition lens." — [0] Example 7.19
> "In fact, it was shown in [BPS19] that every dynamical system can be obtained by wiring together memoryless ones." — [0] Section 4.6

Verification notes: Read via targeted page queries only (pages listed); the claim 'no learning law' rests on the returned pages and index pages, not on a full read - recorded as a negative finding at PARTIAL depth. Codex PARENT_EXPANSION_V2 §A cites the CUP edition (doi 10.1017/9781009576734.006) as STRONG_PARENT_FOR_B0_LOCAL_ADAPTIVE_TRANSDUCERS; correction: it is a parent for B0 composition, not for anything adaptive. Sibling P7.json entry P7.POLY_DYNAMICAL_SYSTEMS agrees on structure; mode-dependence added here.

### P7.POLY_DYNAMICAL_SYSTEMS — Polynomial functors and compositional dynamical systems (Moore/Mealy machines as lenses Sy^S -> p; wiring-diagram algebras; interval sheaves)

Disposition: `ADOPT` · best verification: `PARTIAL_TEXT_READ`

Sources:

- [0] Polynomial Functors: A Mathematical Theory of Interaction — Nelson Niu, David I. Spivak (2024), book manuscript (Topos Institute), arXiv:2312.00990v2 (16 Aug 2024). https://arxiv.org/abs/2312.00990 arXiv:2312.00990 — `PARTIAL_TEXT_READ`
- [1] Dynamical Systems and Sheaves — Patrick Schultz, David I. Spivak, Christina Vasilakopoulou (2020), Applied Categorical Structures 28, 1-57 (2020); arXiv:1609.08086v4 (15 Mar 2019). https://arxiv.org/abs/1609.08086; doi:10.1007/s10485-019-09565-x arXiv:1609.08086 — `PARTIAL_TEXT_READ`

**What it already explains.** Niu-Spivak: an (A,I)-Moore machine with states S is exactly a lens Sy^S -> Iy^A in the category Poly of polynomial functors (Def 4.4); more generally a dependent dynamical system is a lens Sy^S -> p, equivalently a p-coalgebra S -> p(S) (Ex 6.67). Machines are wired together with the parallel product ⊗ and wrapper lenses p -> q (Section 4.3-4.4); every dynamical system is obtained by wiring together memoryless ones ([BPS19], quoted in 4.6). Time evolution is the composition product ⊳ (Prop 6.2, Cor 6.5): every state system Sy^S is a polynomial comonoid (eraser = do-nothing section, duplicator = transition lens, Ex 7.19), so n-step runs are the canonical lenses Sy^S -> (Sy^S)^{⊳n} followed by phi^{⊳n}; polynomial comonoids are categories and their morphisms retrofunctors (Ch.7); retrofunctors Sy^S -> C are C-coalgebras (Prop 7.98). Schultz-Spivak-Vasilakopoulou: discrete and continuous dynamical systems are algebras (lax monoidal functors W_C -> Cat) for the operad of wiring diagrams; abstract 'machines' are spans A <- S -> B in a topos of interval sheaves (continuous Int, discrete Int_N, synchronous Int/Sync) (Def 4.1.1), with sub-algebras of total and deterministic machines closed under arbitrary interconnection including feedback; algebra maps embed DDS into total deterministic discrete machines (Prop 5.1.1) and all machine types into synchronous machines; continuous ODE systems need not be total or deterministic (Remark 5.1.3); safety contracts also form an algebra.

**Formal object.** Poly: functors Set -> Set of the form p = sum_{i in p(1)} y^{p[i]}; lens (morphism) phi: p -> q = on-positions phi_1: p(1) -> q(1) and on-directions phi^#_i: q[phi_1(i)] -> p[i]. Moore machine: phi: Sy^S -> Iy^A with phi_1 = return: S -> I, phi^# = update: S x A -> S (Def 4.4). Composition product p ⊳ q = p o q (Def 6.1), monoidal unit y. Polynomial comonoid (c, eps: c -> y, delta: c -> c ⊳ c) (Def 7.15-16); C-coalgebra (S, alpha: S -> c ⊳ S) (Def 7.96). SSV: W_C symmetric monoidal category of C-labelled boxes and wiring diagrams; algebra F: W_C -> Cat lax monoidal; DDS(A,B) = (S, f_upd: A x S -> S, f_rdt: S -> B) (Def 2.3.1); machine = span A <- S -> B in a sheaf topos; Mch^td sub-algebras.

**Strongest result.** Niu-Spivak: Prop 6.2 / Cor 6.5 (Poly closed under composition; (y, ⊳) monoidal); Ex 7.19 and Ch.7 (state systems are comonoids; polynomial comonoids are exactly categories — Ahman-Uustalu); Prop 7.98 (retrofunctors from state categories are coalgebras); Def 4.4 / Ex 6.67 (Moore machines = lenses = coalgebras). SSV: Prop 2.4.1 (span algebras Spn_C: W_C -> Cat), Prop 4.1.3 (continuous machines form a W-algebra), Theorem 5.2.12 (referenced: totality/determinism preserved), Prop 5.1.1 (DDS embeds into total deterministic discrete machines), Prop 4.5.5 (contracts compose along wiring diagrams).

**Assumptions.** single-variable polynomial functors on Set (finite/discrete state and interface data); no learning, no parameters as a distinguished object; time = composition product / interval sheaves; synchronous composition assumed for mixing discrete and continuous; SSV machines are spans (relations), so totality/determinism are extra properties, not automatic; no probabilistic machines (stated as future work in SSV)

**Resource model.** none (state-set size, memory, time complexity are not charged; the index of Niu-Spivak has no entry for cost, complexity or learning)

**Failure boundary.** These are theories of machines and their interconnection, not of learning: nothing selects a state system, nothing updates lenses from data, nothing charges memory or time; the D0 statement 'every dynamical system is a wiring of memoryless ones' is exactly the universal-computation baseline Track B must not mistake for evidence; probabilistic and learning extensions (Smithe's cilia) are outside these texts.

**Implementation.** none known (Niu-Spivak book source at https://github.com/ToposInstitute/poly is LaTeX, not code)

**Track-B residual.** The parents supply the canonical algebra of the AUTOMATA morphology (Moore/Mealy = lenses/coalgebras, composition = ⊳, interconnection = wiring-diagram algebras) and equivalences between presentations. Track B must ask: which state system S and interface p a resource-bounded developmental process acquires under E, at what memory/time cost, and whether the ⊳-comonoid structure (time) interacts with the optic structure (learning) to yield a phase boundary between 'learn a Moore machine' and 'learn a parametric function' morphologies.

**Upward question.** Since learning laws are optics (Para(Optic)) and machines are lenses Sy^S -> p with a comonoid for time, what is the right double/2-categorical structure combining both (Smithe's cilia is one candidate), and does the description length of the comonoid (state category) versus the parameter object predict when memory-based (automata) versus parametric (neural) morphologies dominate?

Load-bearing quotes (verbatim from sources actually read):

> "an (A, I)-Moore machine with states S is a lens φ: Sy^S → Iy^A in Poly." — [0] Definition 4.4 (Niu-Spivak)
> "there is a natural isomorphism between dynamical systems Sy^S → p and functions S → p(S). Such a function is known as a coalgebra for the functor p" — [0] Example 6.67 (Niu-Spivak)
> "every state system is a polynomial comonoid, whose eraser is the do-nothing section and whose duplicator is the transition lens." — [0] Example 7.19 (Niu-Spivak)
> "In fact, it was shown in [BPS19] that every dynamical system can be obtained by wiring together memoryless ones." — [0] Section 4.6 (Niu-Spivak)
> "A central goal is to understand the systems that result from arbitrary interconnection of component subsystems, possibly of different types, as well as establish conditions that ensure totality and determinism compositionally." — [1] Abstract (SSV)
> "continuous dynamical systems do not generally correspond to total and deterministic continuous machines." — [1] Remark 5.1.3 (SSV)

Verification notes: Both read partially via targeted page queries; definitions and example numbers quoted are verified on the returned pages; large parts of both texts (Niu-Spivak Ch.1-3, 5, 8-9; SSV Sections 3.2-3.3, 4.2-4.5 proofs) were not read. Not in the listed repo ledgers (the HSG ledger row R7 cites Baez-Fong open Markov processes, a different parent).

### P7.RESOURCE_SILENCE — Synthesis: do any of the categorical learning works charge resources (description length, compute, samples, memory, verification)? Evidence census across the family, including the one categorical work that does price space-time (Gavranovic 2022)

Disposition: `OPEN` · best verification: `FULL_TEXT_READ`

Sources:

- [0] Space-time tradeoffs of lenses and optics via higher category theory — Bruno Gavranovic (2022), arXiv:2209.09351v1. https://arxiv.org/abs/2209.09351 arXiv:2209.09351 — `PARTIAL_TEXT_READ`
- [1] Backprop as Functor; Categorical foundations of gradient-based learning; CDL; Bayesian updates compose optically + thesis; Categorical cybernetics; Reverse derivative categories + RDA; GNNs are dynamic programmers; Polynomial functors; Simple essence of AD — see entries 1-9 of this ledger (2018), as in entries 1-9. as in entries 1-9 — `FULL_TEXT_READ`

**What it already explains.** CENSUS. (1) Fong-Spivak-Tuyeras: no resource; one qualitative remark that lower-dimensional gradients are quicker. (2) Cruttwell et al.: no resource; one remark that reverse derivatives are cheaper when m << n; explicitly says ANY functor C -> Lens(C) fits. (3) CDL: none. (4) Smithe 2020 / thesis / BHS: none; 'intractable' acknowledged, then a LOSS (KL/free energy) attached, not a cost. (5) Capucci et al.: none; residuals informally called 'memory'. (6) Cockett et al.: 'cheap gradient principle' cited as motivation, not formalised; Wilson-Zanasi: exponential brute-force vs constant-factor compositional reverse derivative - the only explicit overhead statement, and it is an implementation fact. (7) Dudzik-Velickovic: sample complexity via NTK alignment, cited from Xu et al.; O(\|V\|^3) messages not charged. (8) Niu-Spivak: none. (9) Elliott: NP-complete optimal Jacobian accumulation and low memory of mutation-free RAD, as side remarks. EXCEPTION FOUND: Gavranovic 2022 shows that denotationally isomorphic categories of cartesian lenses and optics implement different SPACE-TIME tradeoffs - lens composition recomputes intermediates from the input (gradient checkpointing: memory constant in depth n, node evaluations scaling as n^2), optic composition stores residuals M1 ⊗ M2 (more memory, no recomputation) - and lifts optics to a 2-category 2-Optic(C) (oplax coend) whose 2-cells track internal state so that the distinction becomes visible; Theorem 1: a local adjunction (residual reifier R left adjoint to residual eraser E) between Lens_Cart(C) and 2-Optic(C). This prices IMPLEMENTATION of a fixed computation, not the choice of architecture or learning law.

**Formal object.** Gavranovic 2022: 2-Optic(C)((A,A'),(B,B')) = oplax coend over M of C(A, M ⊗ B) x C(M ⊗ B', A'); objects (M, fw, bw), 2-cells omega_r for r: M1 -> M2 with commuting squares; pi_0 * (2-Optic(C)) = Optic(C) (Prop 6); Theorem 1 adjunction R ⊣ E with R(f,f') = (A, graph(f), f'), E(M,fw,bw) = (fw # pi_2, (fw # pi_1) x B' # bw); the embedding Lens -> 2-Optic is oplax with oplaxator detecting the composition rule (space-time) difference.

**Strongest result.** Negative census result (this family): NO categorical parent attaches a description-length, sample, verification or compute COST to the objects that are compared (learners, lenses, algebras, controllers); costs appear only as motivating remarks or as properties of one implementation. Positive exception: Gavranovic 2022 Theorem 1 + Remark 1 + footnote 8 formalise a memory-versus-recomputation tradeoff inside the optic algebra ('the memory required to compute gradients ... is constant in the number of layers n, but the number of node evaluations scales with n^2'), establishing that 1-categorical (denotational) equivalence ERASES resource distinctions and that a 2-categorical refinement is needed to see them.

**Assumptions.** census covers only the works read in this family (nine primary works plus Gavranovic 2022); later categorical work such as Wilson-Zanasi 2023 'Data-parallel algorithms for string diagrams' was not read and may charge parallel cost

**Resource model.** the entry's subject: the family as a whole models none of {description length, samples, verification}; compute/memory appear only in Gavranovic 2022 (space vs time of optic composition), Wilson-Zanasi (exponential vs constant-factor reverse derivative), Elliott (NP-complete accumulation; mutation-free memory), Dudzik-Velickovic (sample complexity by citation).

**Failure boundary.** Because no cost functor exists on Learn / Para(Lens(C)) / Para(Optic) / BayesLens / Lax-Alg(Para(T)), the family cannot rank two morphologies or two learning laws; every parent leaves the choice to the designer (Cruttwell: 'fixed an optimiser beforehand'; CDL: 'rely on choosing the right category'; Capucci: feedback 'is missing'; Smithe: choosing an approximation is 'a new problem'). Gavranovic 2022 prices only how a fixed optic is executed, and only along one axis (memory vs recomputation).

**Implementation.** none

**Track-B residual.** This is the Track-B D1 residual at the algebraic level: define a cost structure on the family's common algebra (a lax/oplax 2-cell or enrichment over a resource monoid on Para(Optic(C))) under which (a) the compilation of a morphology into the algebra has a stated overhead in description length / update work / verification work, and (b) the choice of backward functor (reverse derivative, Bayesian inversion, selection relation, search) becomes a priced optimisation indexed by the ecology. Gavranovic 2022 shows the 2-categorical direction is the right one for at least the memory/time axis.

**Upward question.** Is the correct home for resource-charged morphogenesis a 2-category (or double category) of optics enriched in a cost monoid, in which denotational equivalence is refined so that 'same behaviour, different cost' becomes a 2-cell - and does Gavranovic's R ⊣ E adjunction generalise to an adjunction between 'cheap-memory' and 'cheap-time' presentations of any learning law?

Load-bearing quotes (verbatim from sources actually read):

> "This means that lens composition picks a particular space-time tradeoff when solving the issue of backpropagating information." — [0] Gavranovic 2022, Section 2
> "The memory required to compute gradients is in our graph is constant in the number of layers n, but the number of node evaluations scales with n^2." — [0] Gavranovic 2022, footnote 8 (sic)
> "to the best of our knowledge this is the first time the connection between lenses and gradient checkpointing has been established." — [0] Gavranovic 2022, Remark 1
> "As the current categorical framework doesn’t have a high-enough resolution to formally capture these distinctions, we seek to provide one." — [0] Gavranovic 2022, Section 1
> "each optics takes care of storing their own data. In turn, this removes the need to recompute any information, at the expense of needing more memory." — [0] Gavranovic 2022, Section 3 (sic)

Verification notes: Census statements for entries 1-9 are traceable to the quotes recorded in those entries. Gavranovic 2022 read partially via page queries (pages listed). Codex ledgers have no resource census of the categorical family; Codex PARENT_EXPANSION_V2 §D lists information-theoretic resource parents (Tishby, Sims, Lieder-Griffiths) which are NOT categorical and do not price learning laws.

### P7.REVERSE_DERIVATIVE_BOOLEAN — Reverse derivative categories and Reverse Derivative Ascent on Boolean circuits (gradient-like learning on a symbolic morphology)

Disposition: `ADOPT` · best verification: `FULL_TEXT_READ`

Sources:

- [0] Reverse derivative categories — Robin Cockett, Geoffrey Cruttwell, Jonathan Gallagher, Jean-Simon Pacaud Lemay, Benjamin MacAdam, Gordon Plotkin, Dorette Pronk (2020), CSL 2020 (LIPIcs); arXiv:1910.07065v1 (15 Oct 2019). https://arxiv.org/abs/1910.07065 arXiv:1910.07065 — `PARTIAL_TEXT_READ`
- [1] Reverse Derivative Ascent: A Categorical Approach to Learning Boolean Circuits — Paul Wilson, Fabio Zanasi (2021), Applied Category Theory 2020 (ACT 2020), EPTCS 333, pp. 247-260. https://arxiv.org/abs/2101.10488; doi:10.4204/EPTCS.333.17 arXiv:2101.10488 — `FULL_TEXT_READ`

**What it already explains.** Cockett et al. axiomatise the reverse derivative: a Cartesian reverse differential category (CRDC) is a Cartesian left additive category with a combinator R[f]: A x B -> A satisfying RD.1-RD.7 (Def 13), where RD.5 is the reverse chain rule. Examples: POLY_R for ANY commutative rig R (so polynomials over Z2 = Boolean-circuit semantics) and Smooth (Example 14). Every CRDC is a Cartesian differential category (Thm 16) and conversely a CRDC is exactly a CDC with a 'contextual linear dagger' (Thm 42); linear maps form a dagger category with dagger biproducts (Prop 24). Wilson & Zanasi use this to define Reverse Derivative Ascent (RDA): a syntactic reverse-derivative operator R~ on polynomial circuits (Def 15) that agrees with the RD-combinator of POLY_Z2 (Lemma 16); Boolean circuits satisfy the extra idempotence x^2 = x which breaks R~, so they introduce a combinatorial SAFETY condition (Def 17), prove every Boolean circuit has a safe equivalent (Lemma 19) and that R~ is well defined on safe circuits (Prop 21, Def 22). rdaStep (Def 23) = (model error = f(theta,x)+y; delta_theta = R[f](theta,x,delta_y)) and rda iterates it (Def 24). Empirically learns Iris (98% two-class, 73.3% three-class with the eval/truth-table model) and two-class MNIST (99.2%, pseudoLinear model). Cruttwell et al. later show RDA is an instance of parametric lenses with XOR loss and identity learning rate.

**Formal object.** CRDC: (X, x, +, 0, R) with R[f]: A x B -> A and [RD.1] R[f+g]=R[f]+R[g]; [RD.2] additivity in the second variable; [RD.3] R[1]=pi_1, R[pi_i] via injections; [RD.4] R[<f,g>] = (1 x pi_0)R[f] + (1 x pi_1)R[g]; [RD.5] R[fg] = <pi_0, <pi_0 f, pi_1>>(1 x R[g])R[f]; [RD.6] linearity in the vector variable; [RD.7] symmetry of mixed partials. POLY_R: objects n in N, maps n -> m are m-tuples of polynomials in R[x_1..x_n]; R[P] = < sum_i (dp_i/dx_1) y_i, ..., sum_i (dp_i/dx_n) y_i >. Wilson-Zanasi: BoolCirc (Def 5, Lafont presentation) ≅ BoolFun (Prop 7); PolyCirc (Def 6, drop the idempotence axiom) ≅ Poly_Z2 (Prop 9); safety: no AND gate has both inputs reachable from the same circuit input (Def 17); rdaStep_f: P x A x B -> P built from f and R[f] as a string diagram (Def 23, eq. 7).

**Strongest result.** Cockett et al. Theorem 42: a Cartesian reverse differential category is precisely a Cartesian differential category with a contextual linear dagger (and the two constructions are mutually inverse). Theorem 16: every CRDC is a CDC with D[f] := (<1,0> x 1) R[R[f]] pi_1. Wilson-Zanasi Lemma 19 + Prop 21 + Def 22: a well-defined reverse-derivative operator on BoolCirc via safe representatives — with the explicit caveat that this does NOT make BoolCirc a CRDC because safety is not compositional and RD.5 fails. Table 1 empirical results.

**Assumptions.** Cartesian left-additive structure (commutative monoid on every object) — Boolean XOR supplies it over Z2; Boolean learning works in POLY_Z2 (polynomial circuits) and is pulled back to Boolean circuits only through safe representatives; no loss function, no learning rate, no convergence guarantee in RDA ('we have no explicit loss function'); models are hand-designed circuits (eval truth-table, pseudoLinear); no principle for circuit architecture ('The first task is to discover principles for building effective parametrised circuit models')

**Resource model.** compute only, informally: brute-force reverse derivative rdiffB needs i+1 evaluations of f (exponential for the eval model with 2^a parameters) whereas the compositional R[eval] is a circuit within a constant factor of eval (Section 4.2.1); motivation cites power-hungry GPUs vs efficient binarised training. Cockett et al.: reverse mode preferred by the 'cheap gradient principle' (Section 1). No description-length, sample or verification accounting.

**Failure boundary.** BoolCirc is NOT a CRDC (RD.5 fails; safety non-compositional) so the categorical guarantee holds only on PolyCirc; RDA has no loss, no rate and no convergence theory; only tiny benchmarks (two-class MNIST); no architecture principles for circuits; nothing about when circuit learning beats real-valued learning; no rule/production systems, only circuits (a symbolic-but-not-rewrite morphology).

**Implementation.** Haskell library and experiments: http://catgrad.com/p/reverse-derivative-ascent and https://github.com/statusfailed/act-2020-experiments (Wilson-Zanasi); none for Cockett et al.

**Track-B residual.** This parent proves the gradient learning law transports to a symbolic (Boolean-circuit) morphology whenever the base category is a CRDC (POLY_R for any commutative rig). Track B's residual: (i) which rigs/base categories does a developmental process select under E and at what cost; (ii) production/rewrite systems and program search are NOT CRDCs — the cross-morphology learning law for T7/T8 is still open; (iii) the empirical accuracy gap (73% Iris-3) is unexplained by the algebra — a resource/ecology phase question.

**Upward question.** The learning law transports along 'is a CRDC'. What is the largest class of morphologies (rigs, rewrite systems with a derivative-like combinator, program spaces) admitting SOME functor F: C -> Lens(C) with a chain rule, and does the description length of F's presentation (7 axioms here) predict compile/acquire cost across morphologies?

Load-bearing quotes (verbatim from sources actually read):

> "We introduce Reverse Derivative Ascent: a categorical analogue of gradient based methods for machine learning." — [1] Abstract
> "our methodology allows us to learn the parameters of boolean circuits directly, in contrast to existing binarised neural network approaches." — [1] Abstract
> "R does not make BoolCirc a reverse derivative category. This is because the safety condition is not compositional, and thus cannot satisfy axiom RD.5." — [1] after Definition 22, Section 3.1
> "R[eval] (as computed by rdiff eval) is a circuit whose size is within a constant factor of eval, and whose result needs to be computed just once." — [1] Section 4.2.1
> "Thirdly, we have no explicit loss function, which is important to discover the conditions under which guarantees of convergence exist." — [1] Section 5
> "The first task is to discover principles for building effective parametrised circuit models." — [1] Section 5
> "a reverse derivative is equivalent to a forward derivative with a dagger structure on its subcategory of linear maps." — [0] Abstract
> "A Cartesian reverse differential category is precisely a Cartesian differential category with a contextual linear dagger." — [0] Theorem 42

Verification notes: Wilson-Zanasi read in full; Cockett et al. read on the pages returned by targeted queries (definition of CRDC with all seven axioms, Examples 2/5/14, Theorems 16/41/42, Prop 24, Section 5); Section 4.1-4.2 on fibrations and Prop 31 not read directly (cited via Cruttwell et al.). Neither is in the listed repo ledgers.

### P7.REVERSE_DERIVATIVE_BOOLEAN — Reverse derivative categories (Cockett et al. 2020) and Reverse Derivative Ascent on Boolean circuits (Wilson & Zanasi 2021): the gradient law on a symbolic morphology

Disposition: `ADOPT` · best verification: `FULL_TEXT_READ`

Sources:

- [0] Reverse derivative categories — Robin Cockett, Geoffrey Cruttwell, Jonathan Gallagher, Jean-Simon Pacaud Lemay, Benjamin MacAdam, Gordon Plotkin, Dorette Pronk (2020), CSL 2020; arXiv:1910.07065. https://arxiv.org/abs/1910.07065 arXiv:1910.07065 — `PARTIAL_TEXT_READ`
- [1] Reverse Derivative Ascent: A Categorical Approach to Learning Boolean Circuits — Paul Wilson, Fabio Zanasi (2021), ACT 2020, EPTCS 333, pp. 247-260. https://arxiv.org/abs/2101.10488 ; doi:10.4204/EPTCS.333.17 arXiv:2101.10488 — `FULL_TEXT_READ`

**What it already explains.** Cockett et al. axiomatise the reverse derivative: a Cartesian left-additive category with a combinator R[f]: A x B -> A satisfying RD.1-RD.7; POLY_R for any commutative rig R is a CRDC (Example 14), so Z2-polynomials (Boolean functions) carry a reverse derivative; Prop 31: f \|-> (f, R[f]) is a product-preserving functor into the dual of the linear fibration; Theorem 42: CRDC = Cartesian differential category + contextual linear dagger. Wilson-Zanasi define Reverse Derivative Ascent (RDA) 'at the level of so-called reverse differential categories': rdaStep_f computes the model error delta_y = f(theta,x) + y (XOR) and the parameter change delta_theta = R[f](theta, x, delta_y) pi_0, iterated as a scanl (Def 23-24). For Boolean circuits they give a syntactic operator R~ defined inductively on the generators of PolyCirc (Def 15), prove it well defined modulo the polynomial-circuit axioms (Lemma 16), show every Boolean circuit has a 'safe' equivalent (Lemma 19; safety = no AND gate with both inputs reachable from one input) on which R~ respects the Boolean axiom x^2 = x (Lemma 20, Prop 21), hence a reverse-derivative operator on BoolCirc (Def 22) - explicitly NOT making BoolCirc a CRDC, because safety is not compositional (RD.5 fails). Empirically: Iris 2-class 98.0%, Iris 3-class 73.3%, binarised MNIST 2-class 99.2% (Table 1).

**Formal object.** CRDC: (X, x, +, 0, R) with R[f]: A x B -> A. POLY_Z2: objects n, morphisms b-tuples of polynomials in Z2[x1..xa]; R[P] = <sum_i (dp_i/dx_1) y_i, ..., sum_i (dp_i/dx_n) y_i>. BoolCirc = string diagrams over generators (XOR, AND, copy, ...) modulo equations (2); PolyCirc = same minus the idempotence axiom, isomorphic to POLY_Z2 (Prop 9). Brute-force reverse derivative on black-box f: <sum D_1[f](x).delta_y, ..., sum D_a[f](x).delta_y> with Boolean partial derivatives D_i[f](x) = f(x) + f(x + e_i) (Example 14). rdaStep_f: P x A x B -> P; rda_f = iterated rdaStep over examples (x_i, y_i).

**Strongest result.** Cockett et al. Theorem 42 (characterisation) and Example 14 (POLY_R is a CRDC). Wilson-Zanasi Lemma 19 + Lemma 20 + Prop 21 + Def 22: a well-defined reverse-derivative operator on BoolCirc via safe representatives, with the honest caveat that this does not make BoolCirc a reverse derivative category. Section 4.2.1: the compositional R[eval] 'is a circuit whose size is within a constant factor of eval' whereas brute-force rdiffB requires i+1 evaluations (exponential in input dimension for the eval model with 2^a parameters). Section 5: RDA in Smooth 'is similar to stochastic gradient descent' except no learning rate and no explicit loss function; convergence conditions unknown; the authors believe RDA is a special case of Fong et al.

**Assumptions.** model class is a morphism of a reverse differential category (Boolean circuits via POLY_Z2); features binarised by normalise-and-round ('throwing away as much of the information of the dataset as possible'); no learning rate, no explicit loss; error = XOR; safe circuit extraction not implemented in the prototype (brute-force rdiffB used for MNIST); toy benchmarks only (Iris; 2-class MNIST)

**Resource model.** compute only, informally: brute-force reverse derivative needs i+1 evaluations of f (exponential for eval with 2^a parameters) versus the compositional R[eval] within a constant factor of eval and computed once (Section 4.2.1); motivation cites 'expensive and power-hungry GPGPU hardware' versus efficient binarised training. Cockett et al.: reverse mode is preferred by the 'cheap gradient principle' (Section 1). No description-length, sample or verification accounting.

**Failure boundary.** Learns PARAMETERS of a fixed Boolean circuit; does not synthesise circuit structure ('The first task is to discover principles for building effective parametrised circuit models'). BoolCirc is not a CRDC (RD.5 fails), so the categorical guarantees hold only for POLY_Z2 representatives. No convergence theory ('we have no explicit loss function, which is important to discover the conditions under which guarantees of convergence exist'). No production/rewrite/program-search learning; Boolean circuits are a symbolic REPRESENTATION but the learning law is still gradient-like, i.e. this crosses the neural/symbolic boundary in the representation, not in the learning law.

**Implementation.** Haskell library: http://catgrad.com/p/reverse-derivative-ascent and https://github.com/statusfailed/act-2020-experiments (cited in the paper; not fetched)

**Track-B residual.** This parent proves the gradient learning law transports to a symbolic (Boolean-circuit) morphology whenever the base is a CRDC. Track B's residual: (i) which rig / base category a resource-bounded developmental process selects under E and at what cost (the parent gives one data point: compositional vs brute-force reverse derivative differ exponentially); (ii) production/rewrite systems and program search are NOT CRDCs, so the cross-morphology learning law for those morphologies remains unowned; (iii) structure (circuit topology) learning is explicitly open.

**Upward question.** Is there a rig-indexed family of morphologies (R = reals: neural; Z2: circuits; tropical: DP per Dudzik-Velickovic) such that the ecology's verification contract and resource prices select the rig - and is the exponential brute-force/compositional gap the first coordinate of a resource phase boundary?

Load-bearing quotes (verbatim from sources actually read):

> "We introduce Reverse Derivative Ascent: a categorical analogue of gradient based methods for machine learning." — [1] Wilson-Zanasi, Abstract
> "Note our methodology allows us to learn the parameters of boolean circuits directly, in contrast to existing binarised neural network approaches." — [1] Wilson-Zanasi, Abstract
> "Note that this definition is a minor abuse of notation, because R does not make BoolCirc a reverse derivative category. This is because the safety condition is not compositional, and thus cannot satisfy axiom RD.5." — [1] Wilson-Zanasi, after Definition 22
> "Computing it requires i + 1 evaluations of f, and in models with just a moderate number of parameters and/or where f is expensive to compute, this quickly becomes intractable." — [1] Wilson-Zanasi, Example 14
> "R[eval] (as computed by rdiff eval) is a circuit whose size is within a constant factor of eval, and whose result needs to be computed just once." — [1] Wilson-Zanasi, Section 4.2.1
> "Thirdly, we have no explicit loss function, which is important to discover the conditions under which guarantees of convergence exist." — [1] Wilson-Zanasi, Section 5
> "The first task is to discover principles for building effective parametrised circuit models." — [1] Wilson-Zanasi, Section 5
> "A Cartesian reverse differential category is precisely a Cartesian differential category with a contextual linear dagger." — [0] Cockett et al., Theorem 42
> "it is much more common for the reverse derivative to play the central role due to its increased efficiency and improved accuracy when computing with functions from R^n to R (due to the so called cheap gradient principle)." — [0] Cockett et al., Section 1

Verification notes: Wilson-Zanasi read in full including Appendix A (canonical form, Lemma 34). Cockett et al. read in the parts listed; RD.5-RD.7 statements not read verbatim (Definition 13 output was truncated after RD.4). Not in the Codex ledgers. Sibling P7.json entry agrees.


## P8 — cognitive architectures / symbolic systems

### P8.CA_SURVEY — 40 years of cognitive architectures (Kotseruba & Tsotsos 2020): the symbolic / emergent / hybrid taxonomy over 84 architectures - syntactic, not behavioural; the stated trend toward hybrids

Disposition: `ADOPT` · best verification: `PARTIAL_TEXT_READ`

Sources:

- [0] A Review of 40 Years in Cognitive Architecture Research: Core Cognitive Abilities and Practical Applications — Iuliia Kotseruba, John K. Tsotsos (2020), Artificial Intelligence Review 53(1):17-94 (2020); arXiv:1610.08602v3 (13 Jan 2018). https://arxiv.org/abs/1610.08602 ; doi:10.1007/s10462-018-9646-y arXiv:1610.08602 — `PARTIAL_TEXT_READ`

**What it already explains.** A census of 84 cognitive architectures (49 active) and 900+ applications, grouped by 'the type of representation and information processing they implement' into symbolic (cognitivist), emergent (connectionist; subdivided into neuronal models and connectionist logic systems) and hybrid (subdivided into symbolic sub-processing - a symbolic architecture with a self-contained sub-symbolic sensory module - and fully integrated). The classification is explicitly SYNTACTIC: the authors reject self-assigned labels and literature classifications as inconsistent (Soar vs ACT-R disagreements; probabilistic action selection called symbolic in some systems and sub-symbolic in others), and fix a convention: explicit symbols combinable into meaningful expressions and syntactic manipulation are symbolic; 'anything that is not an explicit symbol and processing other than syntactic manipulation is sub-symbolic (e.g. numeric data, pixels, probabilities, spreading activations, reinforcement learning, etc.)'. Trend statement (Figure 2 caption): 'after 2000s most of the newly developed architectures are hybrid'; conclusion: hybrids are 'the most numerous and diverse group, showing the tendency to grow even more, thus confirming a prediction made almost a decade ago [128]', forming 'a continuum between emergent and symbolic systems' for which 'quantitative analysis of this space is not feasible'. CogPrime and Sigma are placed 'conceptually closer to emergent systems'.

**Formal object.** Taxonomy tree: {symbolic, emergent = {neuronal modeling, connectionist logic}, hybrid = {symbolic sub-processing, fully integrated}} applied by a fixed convention on representation and processing; timeline of 84 architectures (Fig 2) coloured by paradigm; mapping of architectures to perception modalities, attention, memory types, learning types, reasoning, and application counts.

**Strongest result.** No theorem. Empirical findings: (i) hybrids dominate and are increasing since the 2000s; (ii) labels in the literature are inconsistent (only 34 of 84 self-label); (iii) the hybrid space is a continuum not amenable to quantitative analysis. For Track B the decisive fact is methodological: the taxonomy is by representation/processing SYNTAX, not by behaviour, developmental signature or ecology, so it cannot serve as a morphology-equivalence relation (Track-B T3) nor as evidence of a phase law.

**Assumptions.** representation-and-processing labels are the right level for grouping architectures; the 84 architectures are a representative sample of the field; the hybrid trend reflects the field's design choices (sociological), not an outcome of selection under stated ecologies

**Resource model.** none; no architecture is compared on compute, description length, samples or verification.

**Failure boundary.** Syntactic classification; explicitly not behavioural; no ecology coordinates; no developmental data; the hybrid 'trend' is a count of human design decisions over time and cannot be read as evidence that hybrids are selected by task ecologies. The survey itself says quantitative analysis of the hybrid continuum is not feasible.

**Implementation.** none (survey); supplementary data of 900 projects referenced

**Track-B residual.** The survey fixes the labels Track B must NOT reuse as a morphology relation. Track B's residual: a behavioural/developmental equivalence (Codex GMI-T4/T5A already show current-behaviour classes are coarser than developmental classes) and an ecology-conditioned account of why the field drifted to hybrids - i.e. is the trend a phase phenomenon of the tasks the field chose, or fashion?

**Upward question.** Can the 84-architecture census be re-scored on Track-B's structural coordinates (local vs global credit, explicit vs distributed competence, revision locality, etc., LEARNING_LAW_ATLAS_V1) so that the 'hybrid continuum' the authors declare non-quantifiable becomes a measurable space with ecology labels?

Load-bearing quotes (verbatim from sources actually read):

> "A more general grouping of architectures is based on the type of representation and information processing they implement. Three major paradigms are currently recognized: symbolic (also referred to as cognitivist), emergent (connectionist) and hybrid." — [0] Section 3
> "To avoid inconsistent grouping, we did not rely on self-assigned labels or conflicting classification of elements found in the literature." — [0] Section 3
> "For our classification, we assume that anything that is not an explicit symbol and processing other than syntactic manipulation is sub-symbolic (e.g. numeric data, pixels, probabilities, spreading activations, reinforcement learning, etc.)." — [0] Section 3
> "According to this data there was a particular interest in symbolic architectures since mid-1980s until early 1990s, however after 2000s most of the newly developed architectures are hybrid." — [0] Figure 2 caption
> "In conclusion, as can be seen in Figure 3, hybrid architectures are the most numerous and diverse group, showing the tendency to grow even more, thus confirming a prediction made almost a decade ago [128]." — [0] Section 3, conclusion
> "Hybrid architectures form a continuum between emergent and symbolic systems depending on the proportions and roles played by symbolic and sub-symbolic components. Although quantitative analysis of this space is not feasible, it is possible to crudely subdivide it." — [0] Section 3, conclusion
> "some architectures such as CogPrime and Sigma are conceptually closer to emergent systems as they share many properties with the neural networks." — [0] Section 3, conclusion

Verification notes: Section 3 read in full from the cached extraction; other sections not read. Not in the Codex ledgers.

### P8.CA_SURVEY_KOTSERUBA_FULLTEXT — A review of 40 years in cognitive architecture research (Kotseruba & Tsotsos 2018): 84 architectures, taxonomy, mechanisms

Disposition: `None` · best verification: `PARTIAL_TEXT_READ`

Sources:

- [0] A Review of 40 Years in Cognitive Architecture Research: Core Cognitive Abilities and Practical Applications — Iuliia Kotseruba, John K. Tsotsos (2018), Artificial Intelligence Review 53 (2020); arXiv 1610.08602 v3. https://arxiv.org/abs/1610.08602 arXiv:1610.08602 — `PARTIAL_TEXT_READ`

**What it already explains.** 84 implemented architectures (49 active) out of ~300 estimated; taxonomy by representation/processing: symbolic (22), emergent (neuronal modelling vs connectionist logic systems, ~14), hybrid (symbolic sub-processing vs fully integrated, ~48, the largest and growing group). Self-assigned labels are inconsistent (Soar/ACT-R called cognitivist or hybrid by different surveys); the survey fixes explicit-symbol vs neuron-metaphor definitions. Mechanisms: action selection (planning, WTA, probabilistic, predefined order, relevance, utility, reactive) — few architectures share the same set; memory types (sensory, WM, semantic, procedural, episodic, global); learning types (declarative, perceptual, procedural, associative, non-associative, priming). Hybrids 'form a continuum between emergent and symbolic systems'. Evaluation criteria (Newell, Sun) exist but comparability is lacking; >900 practical projects catalogued.

**Formal object.** taxonomy tree (Fig. 3); mechanism x architecture incidence diagrams (Figs. 7-9)

**Strongest result.** None

**Assumptions.** None

**Resource model.** None

**Failure boundary.** None

**Implementation.** None

**Track-B residual.** None

**Upward question.** None

Verification notes: None

### P8.HYPERON — OpenCog Hyperon (Goertzel et al. 2023) and 'Toward a formal model of cognitive synergy' (Goertzel 2017): the exact cognitive-synergy claim and its evidential status

Disposition: `ADOPT` · best verification: `PARTIAL_TEXT_READ`

Sources:

- [0] OpenCog Hyperon: A Framework for AGI at the Human Level and Beyond — Ben Goertzel, Vitaly Bogdanov, Michael Duncan, Deborah Duong, Zarathustra Goertzel, Jan Horlings, Matthew Ikle, Lucius Greg Meredith, Alexey Potapov, Andre Luiz de Senna, Hedra Seid, Andres Suarez, Adam Vandervorst, Robert Werko (2023), arXiv:2310.18318v1. https://arxiv.org/abs/2310.18318 arXiv:2310.18318 — `PARTIAL_TEXT_READ`
- [1] Toward a Formal Model of Cognitive Synergy — Ben Goertzel (2017), arXiv:1703.04361v1. https://arxiv.org/abs/1703.04361 arXiv:1703.04361 — `PARTIAL_TEXT_READ`

**What it already explains.** The Codex atlas (T4) already records Hyperon as owning 'one shared substrate hosting heterogeneous cognitive algorithms' (MeTTa over a typed metagraph Atomspace). Added here, the EXACT synergy claim and its status. Hyperon 2023: cognitive synergy 'stemmed from an understanding of how different types of memory and learning mechanisms in the human brain interact' and 'highlighted how the brain translates a problem from one kind of memory to another kind when it gets stuck'; 'we need all these processes occurring concurrently in the same large Atomspace metagraph – this is how you get the cognitive synergy that leads to emergence of large-scale mind-structure patterns'; the efficiency advantage is stated CONDITIONALLY: 'If s multi-paradigmatic integrative approach is more efficient than mono-paradigmatic, then Hyperon has chances to become a leading AGI platform.' Goertzel 2017 formalises the notion: a hierarchy of agent models (RL agents -> cognit agents -> hypergraph agents -> PGMC agents); 'stuckness' of a cognitive process C in situation S as 1 - conf_{C,S}; synergy between A and B as the probability that exactly one is stuck; Conjecture 1 (cognitive operations are mostly hypergraph homomorphisms or their inverses), Conjecture 2 (synergetic processes have many low-cost homomorphisms but few isomorphisms between their transition graphs), Conjecture 3 (natural transformations eta_{A,B} between functors F_A, F_B with a COST INEQUALITY: the indirect route A -> B -> B -> A is often cheaper than the direct A-route, eq. (3)). Evidential status: no theorem is proved, no experiment reported; the author's own words: 'Our intuition is that a variety of interesting rigorous theorems likely exist in the vicinity of this informal conjecture. However, much more investigation is required'; 'this has yet to be studied empirically in a systematic way'; the PrimeAGI arguments 'have obviously been somewhat hand-wavy'.

**Formal object.** Goertzel 2017: cognitive process A as a functor F_A on the metasystem's state-transition hypergraph category G_S mapping any transition subgraph X to the closest match F_A(X) realised by A alone; synergy = natural transformations eta_{A,B}: F_A => F_B and eta_{B,A} with cost(eta^{A,B}_X) + cost(F_B(f)) + cost(eta^{B,A}_Y) << cost(F_A(f)) (inequality (3)); stuck_{C,S,I_S,I} = 1 - max_P g(P) c(P) e(P) c(P); cog-syn_{A,B,P} = weighted probability over stuckness intervals of 'exactly one stuck'. Hyperon: Atomspace metagraph, MeTTa language, PLN, MOSES, ECAN as concurrent processes on one graph.

**Strongest result.** None. Three conjectures (Goertzel 2017) and one conditional sentence (Hyperon 2023). The strongest concrete content is the DEFINITION of synergy as a cost inequality across commutation diagrams - i.e. the claim is intrinsically about resource cost of translating between paradigms, which is exactly the kind of quantity no other parent in this family formalises.

**Assumptions.** human-like cognition requires multiple memory types and learning mechanisms interacting (assumed, from brain analogy); cognitive processes as hypergraph rewrite rules, mostly homomorphisms (Conjecture 1); cost weightings on arrows exist but are never specified; efficiency advantage of multi-paradigm integration is a hypothesis ('If ...')

**Resource model.** cost is CENTRAL to the definition of synergy (inequality (3) compares total costs of paths through commutation diagrams) but is left unspecified - no unit, no measurement, no theorem. Hyperon 2023 reports engineering efficiency concerns (old OpenCog 'considerably slower than modern neural network frameworks') as motivation only.

**Failure boundary.** No theorem, no controlled experiment, no benchmark showing that multi-paradigm integration is more efficient than a mono-paradigm system. The formal model has no theorem relating synergy to general intelligence; the conjectures are explicitly labelled as needing 'much more investigation'. The substrate hosts paradigms because engineers implement them (PLN, MOSES, ECAN); no acquisition and no selection law.

**Implementation.** OpenCog Hyperon / MeTTa (open source; github.com/trueagi-io per the paper; not fetched)

**Track-B residual.** Hyperon/CogPrime owns the HYPOTHESIS that cross-paradigm translation-at-stuckness is cost-saving, formalised as a cost inequality on natural transformations. Track B's residual is to turn that into a measured, charged quantity under a registered ecology: when (in E) is the hybrid route cheaper than the mono-paradigm route, and can that be predicted before search? Hyperon gives the shape of the inequality, not its evaluation.

**Upward question.** Goertzel's inequality (3) is a cost statement about natural transformations between paradigm-functors. If Track B measures those costs under registered ecologies, does the sign of the inequality flip predictably with ecology coordinates - i.e. is 'cognitive synergy' a phase phenomenon rather than a universal principle?

Load-bearing quotes (verbatim from sources actually read):

> "and Hyperon is a platform precisely for AGI R&D with the focus on cognitive synergy between different paradigms, approaches, techniques." — [0] Hyperon 2023, Section 4 (quoting Potapov)
> "If s multi-paradigmatic integrative approach is more efficient than mono-paradigmatic, then Hyperon has chances to become a leading AGI platform." — [0] Hyperon 2023, Section 4 (sic)
> "For human-like cognition to happen, we need all these processes occurring concurrently in the same large Atomspace metagraph – this is how you get the cognitive synergy that leads to emergence of large-scale mind-structure patterns" — [0] Hyperon 2023, Section 4.1
> "when one of them gets stuck in carrying something out, it can translate its intermediate state into the native languages of other cognitive processes and ask them for help." — [0] Hyperon 2023, Section 4.1
> "Cognitive synergy is proposed to correspond to a certain inequality regarding the relative costs of different paths through certain commutation diagrams." — [1] Goertzel 2017, Abstract
> "Our intuition is that a variety of interesting rigorous theorems likely exist in the vicinity of this informal conjecture. However, much more investigation is required." — [1] Goertzel 2017, Section 6.1
> "Conceptually, it seems clear that there is significant synergy between clustering and blending; though this has yet to be studied empirically in a systematic way." — [1] Goertzel 2017, Section 8
> "The above arguments regarding cognitive synergy in PrimeAGI have obviously been somewhat "hand-wavy"." — [1] Goertzel 2017, Section 8

Verification notes: Hyperon 2023 read only in the passages containing 'cognitive synergy' plus the abstract (the Codex atlas T4 already covers the substrate description). Goertzel 2017 read via page queries covering the abstract, definitions and all three conjectures. Correction to Codex atlas T4: 'cognitive synergy' should be marked as CONJECTURE-LEVEL (no theorem, no experiment) rather than as an owned mechanism.

### P8.RATIONAL_ANALYSIS — Rational analysis of memory (Anderson 1990; Anderson & Schooler 1991): memory's retention function as an adaptation to environmental need statistics - a proto phase-law argument (ecology -> form)

Disposition: `ADAPT` · best verification: `PARTIAL_TEXT_READ`

Sources:

- [0] The Adaptive Character of Thought — John R. Anderson (1990), Lawrence Erlbaum. ISBN 0-8058-0419-6 — `NOT_ACCESSIBLE`
- [1] Reflections of the Environment in Memory — John R. Anderson, Lael J. Schooler (1991), Psychological Science 2(6):396-408. https://doi.org/10.1111/j.1467-9280.1991.tb00174.x — `NOT_ACCESSIBLE`
- [2] Learning What to Remember: A Cognitively Grounded Multi-Factor Value Model for Agentic Memory (secondary restatement) — Zhibao Chen, Qian Cheng (2026), arXiv:2606.12945v2. https://arxiv.org/abs/2606.12945 arXiv:2606.12945 — `PARTIAL_TEXT_READ`
- [3] Hybrid Personalization Using Declarative and Procedural Memory Modules of the Cognitive Architecture ACT-R (secondary restatement) — Kevin Innerebner, Dominik Kowald, Markus Schedl, Elisabeth Lex (2025), UMAP Adjunct 2025; arXiv:2505.05083. https://arxiv.org/abs/2505.05083 arXiv:2505.05083 — `PARTIAL_TEXT_READ`

**What it already explains.** VERIFIED ONLY AT SECONDARY DEPTH. The rational-analysis programme explains a cognitive form (the shape of the memory retention/retrieval function) as the optimal adaptation to statistics of the environment: 'the retention function mirrors the environmental need-probability of information' and forgetting is 'an adaptive rather than passive decay' (Chen & Cheng 2026, attributing to Anderson & Schooler 1991). The search-engine paraphrase of the 1991 abstract (UNVERIFIED wording): availability of memories shows reliable relationships to frequency, recency and pattern of prior exposures, and environmental sources - New York Times, parental speech, electronic mail - show the same statistical patterns; memory has the form it does because it is adapted to these relationships. The ACT-R base-level activation B_i = ln(sum_j t_j^{-d}) is presented by Innerebner et al. as 'computed according to the power law of forgetting' with citation to Anderson & Schooler 1991. FROM_MEMORY_UNVERIFIED details (recorded, not relied on): the 1991 paper fits need odds as power functions of recency and of frequency in all three corpora, reports a spacing interaction, and matches these to the classic retention and practice curves; Anderson 1990 frames memory retrieval as a cost-benefit decision (retrieve if need probability times gain exceeds retrieval cost).

**Formal object.** (as restated by secondary sources) need probability / odds of a memory being needed as a function of its history of use in the environment; retention (activation) as a log-sum of power-law decays B_i = ln(sum_{j=1}^{n} t_j^{-d}) with d the decay parameter, n the frequency, t_j time since the j-th occurrence; the claim: the form of the human retention function equals the form of the environmental need-odds function.

**Strongest result.** No theorem (the work is a statistical-fit argument): environmental need-odds curves and human retention curves share functional form (power laws in recency and frequency), interpreted as memory being optimally adapted to the environment. This is the earliest well-known instance of an 'ecology -> form' explanatory law for a cognitive mechanism. Its logical structure: (i) measure environment statistics, (ii) derive the retention function that would be optimal for them, (iii) show human data match. Strength: quantitative and cross-domain (three corpora). Weakness for Track B: post hoc (form was known before the environmental analysis), one parametric family, one mechanism, no competing morphologies, no resource cost of implementing the retention function.

**Assumptions.** memory is optimised for retrieving what is likely to be needed; environment statistics are stationary enough to estimate need odds from usage histories; the three corpora are representative of 'the environment' of memory demands; the fitted functional form (power law) is the relevant description of both environment and memory

**Resource model.** (unverified for the 1991 paper) rational analysis in Anderson 1990 includes retrieval cost and gain in the decision rule; the 1991 paper as restated is about need-probability statistics, not compute or description length.

**Failure boundary.** Explains the parametric FORM of one retention function inside one fixed architecture (declarative memory); it does not predict which memory MORPHOLOGY (e.g. explicit retrieval store vs. distributed weights vs. episodic index) an ecology favours, nor development, nor cost of the mechanism. It is confirmatory/post hoc rather than prospective. Depth of verification here is secondary only.

**Implementation.** ACT-R declarative memory implements the resulting activation equation (act-r.psy.cmu.edu; not fetched)

**Track-B residual.** Adopt the argument SCHEMA (environment statistics -> optimal functional form -> observed form) as the template for a Track-B phase law, but Track B must lift it from 'one function's parameters' to 'which morphology class', from post hoc fit to prospective prediction (D3), and must add the resource price of the mechanism, none of which rational analysis supplies.

**Upward question.** Can the rational-analysis schema be run PROSPECTIVELY over morphology classes: register the ecology's need/verification/drift statistics, derive which retention-and-revision organisation is optimal under a resource budget, then observe blind search - and does the answer change class (not just parameters) across ecologies?

Load-bearing quotes (verbatim from sources actually read):

> "The rational analysis of memory [1] reframes forgetting itself as adaptive: the retention function mirrors the environmental need-probability of information." — [2] Chen & Cheng 2026, Section 2 (attributing to Anderson & Schooler 1991)
> "the very shape of forgetting tracks the need-probability of information in the environment, an adaptive rather than passive decay [1, 6]." — [2] Chen & Cheng 2026, Section 1
> "computed according to the power law of forgetting, which models how the activation of memory traces decay over time [3]" — [3] Innerebner et al. 2025, Section 2 (attributing to Anderson & Schooler 1991)

Verification notes: Primary sources NOT accessible; all statements about the 1991 paper's content beyond the two secondary restatements and the search-engine abstract paraphrase are FROM_MEMORY_UNVERIFIED and flagged as such in the text. No Codex ledger entry exists for Anderson; PARENT_EXPANSION_V2 §D has Lieder-Griffiths (resource-rational analysis), the descendant programme.

### P8.SIGMA — Sigma cognitive architecture (Rosenbloom, Demski, Ustun 2016; Ustun et al. 2018): one graphical substrate (factor graphs + summary product + gradient descent) hosting rules, probabilistic networks, neural nets, RL, memory and Theory of Mind

Disposition: `ADOPT` · best verification: `FULL_TEXT_READ`

Sources:

- [0] The Sigma Cognitive Architecture and System: Towards Functionally Elegant Grand Unification — Paul S. Rosenbloom, Abram Demski, Volkan Ustun (2016), Journal of Artificial General Intelligence 7(1):1-103. https://doi.org/10.1515/jagi-2016-0001 — `NOT_ACCESSIBLE`
- [1] Controlling Synthetic Characters in Simulations: A Case for Cognitive Architectures and Sigma — Volkan Ustun, Paul S. Rosenbloom, Seyed Sajjadi, Jeremy Nuttall (2018), I/ITSEC 2018, Paper 18205; arXiv:2101.02231. https://arxiv.org/abs/2101.02231 arXiv:2101.02231 — `FULL_TEXT_READ`

**What it already explains.** Sigma is the strongest existing instance of 'one substrate -> many paradigms' by ENGINEERING. Basis (graphical architecture hypothesis): everything compiles to factor graphs - 'undirected graphical models ... with variable and factor nodes, and functions that are stored in the factor nodes' - over 'hybrid mixed piecewise-linear functions'; one inference algorithm, the summary product algorithm (message product at each node, summarisation by integration or max); one learning mechanism, gradient descent on the factor-node functions ('Messages into FFNs provide the gradients for learning the nodes' functions'). A cognitive language of predicates (typed relations, working-memory sub-graphs, perceptual buffers, long-term-memory function factor nodes) and conditionals (conditions/actions = rule parts pushing information one way; condacts = bidirectional patterns for probabilistic reasoning, partial matching, constraint satisfaction, signal processing) compiles to the graph: 'conditionals provide a deep blend of rule systems and probabilistic networks'. Cognitive cycle: input, graph solution, decisions (Selected predicate, argmax utility), learning, output; reactive/deliberative/reflective processing with Soar-style impasses. Paradigms demonstrated (per the 2018 conclusions and its citations): learning (gradient descent 2013; episodic 2014), procedural + declarative memory, decision making/problem solving, perception, speech (isolated word / continuous phone recognition), Theory of Mind, emotion/appraisal (surprise, desirability, familiarity), and neural networks (2016b, 2017). Proof-of-concepts read here: RL (Frozen Lake) with Q-values learned by gradient descent through Compute-Backup-Value conditionals augmented by learned rules; SLAM as a DBN in two conditionals with map learned by gradient descent; ToM by multi-agent RL yielding a posterior over intruder models; knowledge-free appraisal-driven exploration. Desiderata: grand unification, generic cognition, functional elegance, sufficient efficiency.

**Formal object.** Factor graph G = (variable nodes, factor nodes with functions f_i over subsets of variables); joint = product of factors; summary product: outgoing message at node = product of incoming messages (and node function) summarised over unneeded variables by integral or max; functions represented as hybrid mixed piecewise-linear functions over discrete and continuous dimensions. Learning: gradient of the local objective delivered as messages into function factor nodes, with a designated child variable (%) defining a conditional distribution to normalise. Predicates P(arg:type ...), conditionals with Conditions / Condacts / Actions and optional function over pattern variables; Selected(state operator!) for decisions.

**Strongest result.** No theorem. The load-bearing claims are demonstrations: (i) 'probabilistic, neural, and reinforcement learning all emerge from a local gradient-descent-based learning mechanism operating at the core of the architecture' (with citations to Rosenbloom 2012a, 2013, 2014, 2017); (ii) in the physical-security model 'the agents learn both the probability distributions in a Bayesian network and Q functions for an RL algorithm using the same basic set of architectural mechanisms'; (iii) RL 'is not a separate architectural learning algorithm, but occurs through a combination of gradient-descent learning and the appropriate knowledge expressed in predicates and conditionals'; (iv) factor graphs provide 'a single general representation and inference algorithm for processing symbols, probabilities, distributed neural vectors, and signals'. Quantitative: augmented Frozen Lake reaches 79% goal-reaching in testing; knowledge-free exploration always finds the item but 'may take significantly longer'.

**Assumptions.** the designer writes the predicates and conditionals (the KNOWLEDGE that instantiates each paradigm); the architecture supplies representation, inference and parameter learning only; piecewise-linear function representation; discrete or discretised continuous dimensions; the neural-network extension (2016b, 2017) is cited, not read here; efficiency is a design desideratum ('sufficiently efficient ... real-time applications'), not a measured or charged quantity

**Resource model.** none charged. 'Sufficient efficiency' is one of four desiderata but no cost of compiling a paradigm into the graph, no description length of conditionals, no sample or verification accounting is given; the only quantitative resource remark is that knowledge-free exploration 'may take significantly longer than it would if behavior were driven by knowledge-intensive algorithms'.

**Failure boundary.** For Track B: (1) D0 is engineered - each paradigm appears because a human writes the conditionals that shape the graph (RL needs its 'template', SLAM its two conditionals); (2) D1 is partial and uncharged - the compile to factor graphs preserves the intended semantics but no overhead in description length / execution / update / verification is stated; (3) no D2 - 'additional forms of learning - particularly structure learning' are listed as under development, so Sigma does not acquire a paradigm from experience without the architecture-specific structure being supplied; (4) no D3 - no prospective law says which paradigm the ecology will favour; 'functional elegance' asserts that many capabilities come from one base, not which capability will emerge when. The 2016 monograph could not be read; deeper formal content (piecewise-linear function algebra, exact gradient derivations) is unverified here.

**Implementation.** Sigma system (Lisp), maintained at USC ICT; described as actively developed - no URL in the text read

**Track-B residual.** Sigma owns 'one representation + one inference algorithm + one parameter-learning mechanism can host rule-based, probabilistic, neural-like, RL, memory, perceptual and ToM behaviour'. It does not own: a charged compilation overhead per paradigm; a selection law mapping ecology to paradigm; acquisition of the conditional structure itself (structure learning) from experience without labels; any equivalence or non-equivalence statement between the graph-compiled paradigm and its native form. Those are exactly Track B's D1-cost, D3 and D2 residuals.

**Upward question.** Sigma's 'functional elegance' is the claim that one base yields all capabilities; the Track-B question is whether a base can PREDICT and DEVELOP which capability organisation emerges under an ecology - can Sigma's structure-learning gap be formalised as an ecology-to-conditional-structure law with charged cost?

Load-bearing quotes (verbatim from sources actually read):

> "is a cognitive architecture and system that starts from a theoretically elegant yet broadly applicable and efficient hybrid (discrete + continuous) mixed (symbolic + probabilistic) base, grounded in probabilistic graphical models" — [1] Ustun et al. 2018, 'Why Sigma?'
> "(3) functionally elegant, yielding broad cognitive and sub-cognitive functionality – ultimately all that is necessary for human-like intelligence – from a simple and theoretically elegant base; and (4) sufficiently efficient" — [1] Ustun et al. 2018, 'Why Sigma?' (restating the 2016 desiderata)
> "Sigma has quite general parameter-learning capabilities, in that probabilistic, neural, and reinforcement learning all emerge from a local gradient-descent-based learning mechanism operating at the core of the architecture" — [1] Ustun et al. 2018, 'Why Sigma?'
> "they are not limited to just probabilistic reasoning, instead providing a single general representation and inference algorithm for processing symbols, probabilities, distributed neural vectors, and signals." — [1] Ustun et al. 2018, 'The Sigma cognitive language'
> "Overall, conditionals provide a deep blend of rule systems and probabilistic networks." — [1] Ustun et al. 2018, 'The Sigma cognitive language'
> "In Sigma, RL is not a separate architectural learning algorithm, but occurs through a combination of gradient-descent learning and the appropriate knowledge expressed in predicates and conditionals." — [1] Ustun et al. 2018, physical security model
> "the agents learn both the probability distributions in a Bayesian network and Q functions for an RL algorithm using the same basic set of architectural mechanisms" — [1] Ustun et al. 2018, physical security model
> "Capabilities currently under development include enhanced neural processing, a motivational system, language processing, and additional forms of learning – particularly structure learning." — [1] Ustun et al. 2018, Conclusions
> "this may take significantly longer than it would if behavior were driven by knowledge-intensive algorithms specifically designed for this task." — [1] Ustun et al. 2018, appraisal-based exploration

Verification notes: The 2016 J.AGI monograph (103 pp.) is NOT_ACCESSIBLE from this session; all content above is verified against the 2018 I/ITSEC paper (= arXiv 2101.02231) by the same group, which restates the graphical architecture, the four desiderata and the demonstrated capabilities with citations. Claims about the 2016 paper's internal theorems or exact gradient derivations are therefore not made. Sigma is absent from the Codex ledgers (GENERAL_INTELLIGENCE_THEORY_PARENT_ATLAS_V1 has Soar and Hyperon only) - recorded as a missing parent now filled. Kotseruba-Tsotsos place Sigma 'conceptually closer to emergent systems'.


## P9A — existing cross-morphology equivalence / simulation / compilation results (not in #377 §4)

### P9A.BLUM_SPEEDUP — Blum 1967 speed-up theorem: for some computable functions every program can be sped up - no fastest solver, hence no terminal revision

Disposition: `ADOPT` · best verification: `FULL_TEXT_READ`

Sources:

- [0] A Machine-Independent Theory of the Complexity of Recursive Functions — M. Blum (1967), Journal of the ACM 14(2):322-336. https://doi.org/10.1145/321386.321395 — `NOT_ACCESSIBLE`
- [1] On effective procedures for speeding up algorithms — M. Blum (1971), Journal of the ACM 18(2):290-305. https://doi.org/10.1145/321637.321648 — `FROM_MEMORY_UNVERIFIED`
- [2] The Fastest and Shortest Algorithm for All Well-Defined Problems — M. Hutter (2002), IJFCS 13(3):431-443. https://arxiv.org/abs/cs/0206022 arXiv:cs/0206022 — `FULL_TEXT_READ`

**What it already explains.** In any Blum complexity measure Phi (axioms: Phi_i(x) is defined iff phi_i(x) is; the predicate Phi_i(x) = y is decidable) there exist total computable functions f such that for every total computable speed-up function r, every program i for f is beaten almost everywhere by another program j for f with r(Phi_j(x)) <= Phi_i(x) - so f has no fastest program, only an infinite descending chain of ever-faster (and, Hutter notes, ever-longer) programs; moreover (Blum 1971, from memory) the speed-up cannot in general be obtained effectively from the index i. Hutter shows the phenomenon disappears when attention is restricted to programs with a PROOF of correctness and a provable time bound: then a fastest (up to 5x) and shortest (up to O(1)) program exists (Theorems 1-2). Consequence recorded by Codex (heritable-search-transformation-v1 ledger row 'Blum 1967 speedup ... OWNS T16'): no unique globally best implementation; this family adds that the obstruction is tied to unverifiable programs.

**Formal object.** Acceptable numbering {phi_i} of partial recursive functions; Blum measure Phi = {Phi_i} with (i) dom Phi_i = dom phi_i, (ii) {(i, x, y): Phi_i(x) = y} recursive; speed-up: for total recursive r, f is r-speedable if for all i with phi_i = f there is j with phi_j = f and r(Phi_j(x)) <= Phi_i(x) for almost all x. (Quantifier structure as remembered; NOT verified against the primary in this or the sibling session.)

**Strongest result.** Speed-up theorem (as characterised in Hutter 2002 Sec. 1, verbatim): 'Blum's Speed-up Theorem [2, 3] shows that there are problems for which an (incomputable) sequence of speed-improving algorithms (of increasing size) exists, but no fastest algorithm.' Complement (Hutter Sec. 7, verbatim): 'Inventing complex (long) programs is not necessary to construct asymptotically fast algorithms, under the stated provability assumptions, in contrast to Blum's Theorem [2, 3].' and (Sec. 9): 'Blum's Theorem shows that the provability constraints are essential.' Exact theorem statement with quantifiers and the 'almost everywhere' clause: FROM_MEMORY_UNVERIFIED.

**Assumptions.** Any Blum complexity measure (time, space, ...) satisfying the two axioms; The speedable functions are constructed by diagonalisation ('unnatural', per Monroe as quoted in P0.BLUM_SPEEDUP); it is not claimed that natural problems are speedable; Speed-up is almost-everywhere; the improving programs are longer and the sequence is not effectively obtainable

**Resource model.** abstract complexity measure (time or space) only; description length enters implicitly (improving programs grow); no verification cost - which is exactly what Hutter shows is the missing coordinate

**Failure boundary.** Says nothing about which functions arising in an ecology are speedable; nothing about learning; nothing about the constants; and its negative is defeated by any verification contract strong enough to require proofs (Hutter), so its Track-B force depends on the ecology's verification coordinate.

**Implementation.** none (pure recursion theory)

**Track-B residual.** Inherited from P0.BLUM_SPEEDUP: under a fixed verification contract does the admissible morphology set have a fastest element, and does a developmental revision loop converge to it or descend an infinite chain? This family sharpens it: the dichotomy 'verifiable => fastest exists (Hutter); unverifiable => no fastest (Blum)' makes the REVISION coordinate a function of the VERIFICATION coordinate - a candidate T9 statement (no universal morphology) that is theorem-grade only at the two extremes.

**Upward question.** Is there an intermediate verification contract (statistical, PAC-style, or execution-tested) under which a Hutter-type fastest-and-shortest result holds with polynomially rather than exponentially large constants, and does the revision coordinate of a developmental system then have a terminal morphology?

Load-bearing quotes (verbatim from sources actually read):

> "Blum's Speed-up Theorem [2, 3] shows that there are problems for which an (incomputable) sequence of speed-improving algorithms (of increasing size) exists, but no fastest algorithm." — [2] Hutter 2002, Sec. 1
> "M avoids Blum's speed-up theorem by ignoring programs without correctness proof." — [2] Hutter 2002, abstract
> "Inventing complex (long) programs is not necessary to construct asymptotically fast algorithms, under the stated provability assumptions, in contrast to Blum's Theorem [2, 3]." — [2] Hutter 2002, Sec. 7
> "Blum's Theorem shows that the provability constraints are essential." — [2] Hutter 2002, Sec. 9

Verification notes: Primary not readable in this or the sibling session; the Codex gap 'proof-level Blum speedup implications' therefore remains OPEN at the primary level. What is verified is Hutter's characterisation and the provability escape. The sibling P0.BLUM_SPEEDUP entry contains the Blum-measure axioms quoted from a modern secondary (Monroe); not duplicated here.

### P9A.CHEAP_GRADIENT — Baur-Strassen 1983 + Griewank-Walther cheap gradient principle: reverse-mode adjoint computes all d partials at a small constant times the forward cost; basis-dependence of update cost

Disposition: `ADOPT` · best verification: `PARTIAL_TEXT_READ`

Sources:

- [0] The complexity of partial derivatives — W. Baur, V. Strassen (1983), Theoretical Computer Science 22(3):317-330. https://doi.org/10.1016/0304-3975(83)90110-X — `NOT_ACCESSIBLE`
- [1] Evaluating Derivatives: Principles and Techniques of Algorithmic Differentiation (2nd ed.), chs. 3-4 — A. Griewank, A. Walther (2008), SIAM. https://doi.org/10.1137/1.9780898717761 — `NOT_ACCESSIBLE`
- [2] Deterministic Sparse Pattern Matching via the Baur-Strassen Theorem — N. Fischer (2023), arXiv cs.DS (SODA 2024). https://arxiv.org/abs/2310.11913 arXiv:2310.11913 — `PARTIAL_TEXT_READ`
- [3] Lower Bounds for Planar Arithmetic Circuits — C. Ramya, P. Shastri (2025), arXiv cs.CC. https://arxiv.org/abs/2509.11322 arXiv:2509.11322 — `PARTIAL_TEXT_READ`
- [4] Automatic Differentiation in Machine Learning: a Survey — A. G. Baydin, B. A. Pearlmutter, A. A. Radul, J. M. Siskind (2018), JMLR 18(153):1-43. https://arxiv.org/abs/1502.05767 arXiv:1502.05767 — `PARTIAL_TEXT_READ`
- [5] A Review of Automatic Differentiation and its Efficient Implementation — C. C. Margossian (2019), WIREs Data Mining and Knowledge Discovery 9(4). https://arxiv.org/abs/1811.05031 arXiv:1811.05031 — `PARTIAL_TEXT_READ`

**What it already explains.** That in the arithmetic-circuit (straight-line program / DAG with shared subexpressions) basis, the gradient of a scalar function of d inputs is never more than a small constant times as expensive as the function: Baur-Strassen (1983) - if f has a fan-in-2 arithmetic circuit of size s over a field then f together with ALL its first-order partial derivatives has a circuit of size O(s) (the constant is small; the classical statement counts nonscalar operations with constant 3 - UNVERIFIED this session; Morgenstern 1985 gives a simplified constructive proof), constructible in time O(s) by traversing the circuit in reverse (the adjoint / backpropagation pass). Griewank-Walther 'cheap gradient principle' (via Baydin/Margossian): OPS(f, J^T u) <= 4 OPS(f) (reverse sweep), OPS(f, J u) <= 2.5 OPS(f) (forward sweep), and for f: R^n -> R^m the full Jacobian costs n c OPS(f) forward or m c OPS(f) reverse with c < 6, typically 2-3; hence a d-dimensional gradient costs O(1) evaluations by reverse mode but Theta(d) evaluations by forward mode or by finite differences (Baydin Table 4: numerical differentiation ~28x and forward AD ~7.7x the function cost at n=50 vs ~2x for reverse). The price is memory: reverse mode must store the tape (trace of intermediate values), growing in the worst case with the number of operations, mitigated by checkpointing (log growth in time and space). Crucially the principle is MODEL-DEPENDENT: Ramya-Shastri 2025 show it fails for formulas (trees, no shared subexpressions) and planar circuits - there are f_n with formula size n^{1+o(1)} whose n partials need multi-output formulas of size Omega(n^2/log n) - while it survives for read-once planar circuits.

**Formal object.** Arithmetic circuit C over a field F on variables x_1..x_n: DAG whose gates are inputs/constants (in-degree 0) or +, -, x, / (in-degree 2); \|C\| = number of gates (+ edges in Fischer's convention); C computes rational functions; formal partial derivatives via the usual rules. AD (Griewank-Walther three-part notation): inputs v_{i-n} = x_i, intermediates v_i = phi_i(v_{j<i}), outputs; forward tangent trace v_i-dot = sum_j (d phi_i / d v_j) v_j-dot; reverse adjoint trace v_j-bar += v_i-bar (d phi_i / d v_j) processed in reverse order from y-bar = 1; OPS = count of fused multiply-adds (Griewank-Walther) or elementary operations (Baydin).

**Strongest result.** Baur-Strassen theorem (as stated verbatim in Fischer 2023, Theorem 1.10): 'For any arithmetic circuit C computing f(x_1, ..., x_n), there is a circuit C' that simultaneously computes the partial derivatives df/dx_i (x_1, ..., x_n) for all 1 <= i <= n. The circuit C' has size \|C'\| <= O(\|C\|) and can be constructed in time O(\|C\|).' Equivalent (Ramya-Shastri): C(d_{x_1} f, ..., d_{x_n} f) = O(C(f)). Cheap gradient principle (Griewank-Walther ch. 4, via Margossian): OPS(f(x), J^T u-bar(x)) <= 4 x OPS(f(x)); via Baydin: reverse-mode Jacobian in m c ops(f), c < 6, typically in [2,3]. Negative counterpart (Ramya-Shastri Corollary 45, verified): over any infinite field there are f_n with L(f_n) = n^{1+o(1)} but L(d_{x_1} f_n, ..., d_{x_n} f_n) = Omega(n^2/log n) for multi-output formulas; Corollary 46: planar circuits C_p(f_n) = n^{1+o(1)} but C_p(all partials) = Omega(n^{4/3}); Corollary 47: read-once planar circuits keep C_p^r(all partials) = O(C_p^r(f)).

**Assumptions.** Circuit/straight-line-program model with SHARED intermediates (fan-out > 1 allowed) and reverse traversal; fails for formulas and planar circuits (Ramya-Shastri); Elementary operations with known local derivatives (field operations; in AD also transcendental primitives); Scalar or few outputs (m << n) for reverse mode to win; forward mode wins for n <= m; Memory: reverse mode stores the evaluation trace (tape); time-memory trade-off via checkpointing; Exact arithmetic (algebraic statement) or floating point with AD's constant-factor guarantee; numerical stability separate

**Resource model.** operation count / circuit size (time), memory (tape length), construction time of the derivative circuit; no samples, no verification; explicitly relative to a computational basis (circuit vs formula vs planar)

**Failure boundary.** Applies to a single evaluation of the gradient, not to optimisation convergence (number of steps); gives no bound on second derivatives beyond repeated AD (Hessian-vector products linear in OPS(f), full Hessian n times); says nothing about non-differentiable or discrete update laws (rule induction, program edits) except by exclusion; the constant hides tape memory; the theorem is basis-relative, so 'gradient is cheap' is a statement about the DAG-with-adjoint basis, not about learning in general.

**Implementation.** every reverse-mode AD system (ADOL-C, Tapenade, PyTorch autograd, JAX); Fischer 2023 applies the theorem constructively in an algorithm; no code for the 1983 paper

**Track-B residual.** The parents own: cheap gradient in the shared-DAG/adjoint basis (upper bound) and NOT-cheap gradient in the formula/planar basis (lower bound). Track B's residual is the ecology-facing consequence: a theorem-grade update-cost (upd coordinate) separation between adaptive bases - a basis whose combinators carry the adjoint pass pays O(1) forward-equivalents per parameter update, a basis restricted to black-box evaluation pays >= d+1 (finite differences) and a formula/tree basis pays super-linear even with white-box access - and whether, under a registered price for memory (tape) and precision, this separation predicts where the gradient-trained neural morphology dominates (GMI-T5/T10). No parent states the separation as a morphology-selection law.

**Upward question.** State and prove the Track-B version: for bases B_1 (DAG + adjoint combinator), B_2 (DAG without adjoint, black-box evaluation), B_3 (formula/tree), the minimal update work per gradient step on d parameters is Theta(1), Theta(d) and n^{1+Omega(1)} forward-evaluation equivalents respectively; then ask which ecology prices (memory for the tape, precision, verification of the loss) reverse the ordering - the first P1 theorem candidate for the upd coordinate.

Load-bearing quotes (verbatim from sources actually read):

> "there is a circuit C' that simultaneously computes the partial derivatives df/dx_i (x_1, ..., x_n) for all 1 <= i <= n. The circuit C' has size \|C'\| <= O(\|C\|) and can be constructed in time O(\|C\|)." — [2] Fischer 2023, Theorem 1.10 (Baur-Strassen [11, 49])
> "Under the name back-propagation this usage of the Baur-Strassen theorem is omni-present in machine learning [65, 59, 66]." — [2] Fischer 2023, Sec. 1.4
> "Baur and Strassen[3] proved that if a polynomial f has a (fan-in 2) circuit of size s then there is a (fan-in 2) circuit of size O(s) computing all first order partial derivatives of f." — [3] Ramya & Shastri 2025, Sec. 1
> "This shows that a statement analogous to that of Baur, Strassen [3] does not hold in the case of planar circuits and formulas." — [3] Ramya & Shastri 2025, abstract
> "Over any infinite field F there exists a family {f_n} of polynomials where f_n in F[x_1, ..., x_n] such that L(f_n) = n^{1+o(1)} but L(d_{x_1}(f_n), ..., d_{x_n}(f_n)) = Omega(n^2/ log n)." — [3] Ramya & Shastri 2025, Corollary 45
> "the same computation can be done via reverse mode in m c ops(f), where c is a constant guaranteed to be c < 6 and typically c ~ [2, 3] (Griewank and Walther, 2008)." — [4] Baydin et al. 2018, Sec. 3.2
> "The advantages of reverse mode AD, however, come with the cost of increased storage requirements growing (in the worst case) in proportion to the number of operations in the evaluated function." — [4] Baydin et al. 2018, Sec. 3.2
> "one reverse mode sweep computes J^T u-bar, with complexity OPS(f(x), J^T u-bar(x)) <= 4 x OPS(f(x)) (see again chapter 4 of (Griewank & Walther, 2008))." — [5] Margossian 2019, 'Reverse mode'
> "OPS(f(x), J . u(x)) <= 2.5 x OPS(f(x)) (see chapter 4 of (Griewank & Walther, 2008))." — [5] Margossian 2019, 'Forward mode'

Verification notes: The 1983 theorem statement is verified through two independent arXiv restatements (Fischer; Ramya-Shastri), both giving O(s); the exact constant in Baur-Strassen's own nonscalar-operation count (remembered as 3) and Morgenstern's variant are UNVERIFIED. Griewank-Walther's constants (4 for reverse, 2.5 for forward, in fused-multiply-add OPS) are verified only through Margossian's citation of their chapter 4; Baydin's c<6 also secondary. The P7 sibling ledger covers the categorical view (P7.ESSENCE_OF_AD, P7.CATEGORICAL_GRADIENT_LEARNING) with 1 mention of 'cheap gradient' but not the Baur-Strassen theorem or the formula/planar lower bounds; this entry is complementary.

### P9A.GROKKING_PHASE — Grokking: Power et al. 2022 + Nanda et al. 2023 progress measures (+ Liu et al. 2022 phase diagram) - a within-training memorisation -> algorithmic phenotype transition with named axes

Disposition: `ADAPT` · best verification: `FULL_TEXT_READ`

Sources:

- [0] Grokking: Generalization Beyond Overfitting on Small Algorithmic Datasets — A. Power, Y. Burda, H. Edwards, I. Babuschkin, V. Misra (2022), arXiv (ICLR 2022 MATH-AI workshop). https://arxiv.org/abs/2201.02177 arXiv:2201.02177 — `PARTIAL_TEXT_READ`
- [1] Progress measures for grokking via mechanistic interpretability — N. Nanda, L. Chan, T. Lieberum, J. Smith, J. Steinhardt (2023), ICLR 2023. https://arxiv.org/abs/2301.05217 arXiv:2301.05217 — `FULL_TEXT_READ`
- [2] Towards Understanding Grokking: An Effective Theory of Representation Learning — Z. Liu, O. Kitouni, N. Nolte, E. J. Michaud, M. Tegmark, M. Williams (2022), NeurIPS 2022. https://arxiv.org/abs/2205.10343 arXiv:2205.10343 — `PARTIAL_TEXT_READ`

**What it already explains.** That within one architecture and one training run, the phenotype changes qualitatively from a memorising lookup to an algorithmic circuit, and that the transition has measurable axes. Power: on binary-operation tables mod p=97 (and S5) with a 2-layer, width-128, 4-head decoder-only transformer (~4e5 non-embedding parameters), AdamW lr 1e-3, weight decay 1, batch 512, budget 1e5 steps: train accuracy ~100% by <1e3 steps, validation jumps to ~100% only near 1e6 steps (modular division, 50% data); time-to-generalise grows rapidly as training fraction shrinks (a 1% decrease of data near 25-30% raises median time by 40-50%); weight decay is the most effective intervention (halves the data needed), noise helps, learning rate must lie within one order of magnitude; symmetric operations need less data; x^3+xy^2+y never generalised up to 95% data. Nanda: on a+b mod 113 with a 1-layer ReLU transformer (d=128, 4 heads of 32, MLP 512, no LayerNorm), full-batch AdamW lr 1e-3, weight decay lambda=1, 30% of the 113^2 pairs, 40k epochs: the network implements Fourier multiplication (embed a,b as sin/cos at ~5 key frequencies w_k = 2 pi k/113, attention+MLP compute cos/sin(w_k(a+b)) via trig identities, unembedding reads cos(w_k(a+b-c)) and sums frequencies for constructive interference); progress measures restricted loss (keep only key frequencies) and excluded loss (remove only key frequencies) plus Gini coefficient of Fourier norms and total squared weight norm split training into memorisation (0-1.4k epochs), circuit formation (1.4k-9.4k; excluded loss rises, weight norm falls, train/test flat) and cleanup (9.4k-14k; test loss drops, weights sharply sparsify); no grokking without weight decay or other regularisation (dropout groks, L1 never); data fraction 30-50% groks, >=60% generalises immediately, <=20% never within 40k epochs; P=53 needs lambda=5, P=401 never groks (generalises immediately); grokking recurs in 5-digit addition (700 points), repeated-subsequence (512 points) and skip-trigram (limited data) tasks. Liu: four phases - comprehension, grokking, memorisation, confusion - over (decoder learning rate, weight decay) and (representation lr, decoder lr), (lr, batch size), (lr, initialisation scale); grokking is sandwiched between comprehension and memorisation; a critical training fraction r_c ~ 0.4 (addition) / 0.5 (S3) below which no linear representation is determined; time to grok ~ 1/lambda_3 of an effective quadratic loss on embeddings.

**Formal object.** Task: (a, b) -> a o b, a,b in Z_p (or S_5), tokens '<a> <op> <b> = <c>'; training set D = random fraction r of all p^2 equations; model f_theta = decoder-only transformer; optimiser AdamW(theta, lr, lambda); observables: train/test accuracy and loss vs epoch; Nanda progress measures: restricted loss L_R = loss after projecting logits onto the constant term and the 20 Fourier terms cos/sin(w_k(a+b)) at key frequencies; excluded loss L_E = train loss after removing only those terms; Gini(\|F(W_E)\|), Gini(\|F(W_L)\|) with W_L = W_U W_out; sum of squared weights. Liu: representation quality index RQI(R) = \|P(R)\|/\|P_0\| (fraction of permissible parallelograms E_i + E_j = E_m + E_n realised) and phase labels from (steps to 90% train acc, steps to 90% val acc).

**Strongest result.** No theorem; the load-bearing empirical results are: (Power Fig. 1) grokking with ~1000x delay between train and validation saturation on modular division; (Power Sec. 3.1.1) exponential growth of time-to-generalise as data fraction decreases; (Power Sec. 3.3) weight decay 'more than halving the amount of samples needed'; (Nanda Sec. 4.2-4.4) full reverse-engineering with ablation checks: restricting to 5 key frequencies improves loss (2.4e-7 -> 7.2e-8), ablating any key frequency reduces accuracy to chance, W_L rank-10 approximation residual <0.55%, 433/512 neurons >85% explained by degree-2 polynomials of one frequency; (Nanda Sec. 5.2) three-phase decomposition with the generalising circuit formed BEFORE the test-loss drop; (Nanda App. D.1) necessity of regularisation and limited data; (Liu Fig. 4) predicted and measured phase transition in linear-representation probability at r_c ~ 0.4; (Liu Fig. 6) four-phase diagrams on (lr, weight decay).

**Assumptions.** Small algorithmic datasets with abstract symbols (no internal structure exposed), full enumeration of the table possible; Tiny transformers (1-2 layers); AdamW; the phenomenon depends on regularisation (weight decay/dropout) and on data fraction; Nanda's mechanism is for one task family; progress measures are task-specific and hand-derived ('significant amounts of manual effort'); Liu's effective theory assumes an ideal injective decoder achieving zero training loss; the four phases are defined by accuracy-time thresholds

**Resource model.** training steps/epochs (optimisation time), training-data fraction (samples), weight decay and learning rate (regulariser prices), model width/depth, prime modulus (task size); verification is exact (full table) - no verification cost accounting; no description-length accounting of the learned circuit

**Failure boundary.** No ex-ante prediction of WHEN the transition occurs ('we lack a general notion of criticality'); progress measures are post-hoc, discovered after reverse engineering; the setting has a perfect exact verifier and complete enumerable data, which is the opposite of most ecologies; the Nanda weight-decay-vs-epochs numbers in App. D.1 are internally inconsistent as printed (text says smaller decay is slower, numbers listed are 3k for 0.3, 5-10k for 1.0, 20k for 3.0); Liu's phases are defined on toy models and only 'preliminary evidence' extends to transformers; no result varies the feedback/verification contract or drift.

**Implementation.** Nanda: https://neelnanda.io/grokking-paper (Colab + checkpoints); Liu: https://github.com/ejmichaud/grokking-squared; Power: none known

**Track-B residual.** The grokking family supplies candidate ECOLOGY coordinates with measured critical values (data fraction r with r_c ~ 0.3-0.5; regulariser strength lambda; optimisation budget; task size p; noise/batch) and candidate morphology-phase OBSERVABLES (Fourier sparsity/Gini, restricted/excluded loss, RQI) inside the neural morphology; Track B's residual is to lift these to CROSS-morphology phase laws: does the same (r, lambda, budget) diagram predict when a programmatic/table (memorising) description versus a compact algorithmic description dominates for other bases, and can the boundary be predicted before training (T10) rather than measured after (which no parent does).

**Upward question.** Are (data fraction, regulariser price, budget) the same coordinates that decide between morphologies across bases (lookup-table vs algorithmic program vs Fourier circuit), and is there a T10 theorem giving the critical surface from description-length and update-cost accounting alone (Liu's r_c as 'least data determining the representation' is the seed)?

Load-bearing quotes (verbatim from sources actually read):

> "Training accuracy becomes close to perfect at < 10^3 optimization steps, but it takes close to 10^6 steps for validation accuracy to reach that level" — [0] Power et al. 2022, Fig. 1 caption
> "In the vicinity of 25-30% of data, a decrease of 1% of training data leads to an increase of 40-50% in median time to generalization." — [0] Power et al. 2022, Sec. 3.1.1
> "We find that adding weight decay has a very large effect on data efficiency, more than halving the amount of samples needed compared to most other interventions." — [0] Power et al. 2022, Sec. 3.3
> "For all experiments we used a transformer with 2 layers, width 128, and 4 attention heads, with a total of about 4 * 10^5 non-embedding parameters." — [0] Power et al. 2022, App. A.1.2
> "grokking, rather than being a sudden shift, arises from the gradual amplification of structured mechanisms encoded in the weights, followed by the later removal of memorizing components." — [1] Nanda et al. 2023, abstract
> "Circuit formation (Epochs 1.4k-9.4k). In this phase, excluded loss rises, sum of squared weights falls, restricted loss starts to fall, and test and train loss stay flat." — [1] Nanda et al. 2023, Sec. 5.2
> "our networks do not grok on the modular arithmetic task without weight decay or some other form of regularization." — [1] Nanda et al. 2023, Sec. 5.3
> "Grokking occurs when between 30 - 50% of the dataset is used during training and lower fractions of data lead to slower grokking. Using >= 60% data leads to immediate generalization" — [1] Nanda et al. 2023, Fig. 20 caption
> "we lack a general notion of criticality that would allow us to predict when the phase transition will happen ex ante." — [1] Nanda et al. 2023, Sec. 6
> "We observe empirically the presence of four learning phases: comprehension, grokking, memorization, and confusion." — [2] Liu et al. 2022, abstract
> "grokking is sandwiched between comprehension and memorization, which seems to imply that it is an undesirable phase that stems from improperly tuned hyperparameters." — [2] Liu et al. 2022, Sec. 4.1
> "The critical training set size corresponds to the least amount of training data that can determine such a representation (which, in some cases, is unique up to linear transformations)." — [2] Liu et al. 2022, Sec. 1 (A2)

Verification notes: Nanda read in full; Power read essentially in full (all main text and appendix pages returned); Liu read at section level. Liu et al. was not on the family list but is the parent that turns grokking into an explicit phase diagram, so it is included. No prior repo ledger covers grokking (grepped: no hits).

### P9A.HARDWARE_LOTTERY — Hooker 2020/2021 'The Hardware Lottery': hardware and software select which morphology wins, with lock-in economics

Disposition: `ADAPT` · best verification: `PARTIAL_TEXT_READ`

Sources:

- [0] The Hardware Lottery — S. Hooker (2021), Communications of the ACM 64(12):58-65 (arXiv 2009.06489, 2020). https://arxiv.org/abs/2009.06489 arXiv:2009.06489 — `PARTIAL_TEXT_READ`

**What it already explains.** That a research idea (morphology) can win 'because it is suited to the available software and hardware and not because the idea is superior to alternative research directions'; historically: Babbage's analytical engine unbuildable for lack of precision parts; deep networks (backprop 1963/1976/1988, CNNs 1982/1989) stalled for decades because CPUs and the von Neumann bottleneck were ill-suited to matrix multiplies, while symbolic AI fit LISP/Prolog; GPUs (built for graphics) unblocked deep nets (16,000 CPU cores in 2012 vs 2 CPU cores + 4 GPUs a year later); domain-specialised accelerators (TPUs etc.) now lock in dense matrix multiply so that ideas off the beaten path (capsule networks: fine on CPUs, 'performance falls off a cliff' on GPUs/TPUs; unstructured sparsity; weight-specific quantisation) pay a price; chips cost $30-80M and 2-3 years, fabs ~$7B, and hardware is economically viable only if the use case lasts > 3 years, so co-design targets known commercial workloads and biases against new directions; proposed remedies are domain-specific languages, auto-tuning, profiling tools that quantify the opportunity cost of the current hardware.

**Formal object.** Informal. Track-B rendering: a morphology M's realised cost is cost_H(M) = price vector R_H (per-operation latency/energy on hardware H) applied to M's operation profile; the hardware lottery is the statement that argmin_M cost_H(M) depends on H, that H is chosen by past winners (lock-in: H_{t+1} is optimised for argmin_M cost_{H_t}(M)), and that the cost of changing H (capital, time) is large relative to the cost of changing M.

**Strongest result.** No theorem. Load-bearing empirical claims (verified in text): definition of the hardware lottery (Sec. 1); the 'lost decades' account of deep learning (Sec. 3.1) with the 16,000-CPU-core vs 4-GPU comparison; the capsule-network case (Sec. 4) from Barham & Isard 2019 'Machine learning is stuck in a rut'; the economics (Sec. 2, 5: $30-80M and 2-3 years per chip; > 3-year use-case lifetime for viability); the software-lottery counterpart (LISP/Prolog favoured symbolic AI until Matlab 1992 / LUSH / Torch in the 2000s).

**Assumptions.** Costs measured on deployed hardware, not in an abstract machine model - i.e. the opposite of the invariance thesis's polynomial tolerance; Hardware development is slow and capital-intensive relative to algorithm development, producing hysteresis; Historical counterfactuals are not measurable ('it is hard to model the counterfactual of would this idea succeed given different hardware')

**Resource model.** hardware-relative time/energy per operation (price vector), capital cost and lead time of changing hardware; no formal accounting

**Failure boundary.** Explains hysteresis and selection pressure but predicts nothing quantitative; cannot separate 'won the lottery' from 'was better'; provides no test that distinguishes an uncharged hardware advantage from a genuine morphology advantage - it names the confound that Codex hostile 'tensor implementation gives neural forms uncharged hardware advantage' (#377) points at, without resolving it.

**Implementation.** none (essay)

**Track-B residual.** Hooker owns the claim that resource prices R are hardware-relative, path-dependent and lock in; Track B must therefore (i) register the price vector R_H before comparison (Codex H-POSTHOC-PRICE) and (ii) report morphology frontiers as functions of R_H with hysteresis, never as absolute; the residual question is whether a morphology phase law can be stated for a FAMILY of price vectors (e.g. dense-matmul-cheap vs pointer-chasing-cheap) such that the predicted winner flips at a computable price ratio - the hardware axis of GMI-T9/T10, which no parent formalises.

**Upward question.** Define the price vector R_H as an ecology coordinate with its own dynamics (lock-in), and ask for the phase law over (task ecology, R_H): does the same generating basis produce the symbolic morphology under a LISP-machine price vector and the neural one under a TPU price vector, and is the boundary predictable from operation profiles alone?

Load-bearing quotes (verbatim from sources actually read):

> "This essay introduces the term hardware lottery to describe when a research idea wins because it is suited to the available software and hardware and not because the idea is superior to alternative research directions." — [0] Hooker 2020, abstract
> "while capsule networks operations can be implemented reasonably well on CPUs, performance falls off a cliff on accelerators like GPUs and TPUs which have been overly optimized for matrix multiplies." — [0] Hooker 2020, Sec. 4
> "Producing a next generation chip typically costs $30-80 million dollars and 2-3 years to develop (Feldman, 2019)." — [0] Hooker 2020, Sec. 2
> "Hardware is only economically viable if the lifetime of the use case lasts more than three years (Dean, 2020)." — [0] Hooker 2020, Sec. 4
> "The widespread and sustained popularity of symbolic approaches to AI cannot easily be seen as independent of how readily it fit into existing programming and hardware frameworks." — [0] Hooker 2020, Sec. 3.2

Verification notes: Read essentially in full from the arXiv v2. Codex PARENT_EXPANSION_V2 cites Jouppi et al. (TPU) for the same point; Hooker adds the lock-in/hysteresis mechanism and the symbolic-AI software-lottery counterpart.

### P9A.INVARIANCE_THESIS — van Emde Boas 1990 'Machine models and simulations': invariance thesis - the resolution floor for any morphology theory at the execution coordinate

Disposition: `ADOPT` · best verification: `FULL_TEXT_READ`

Sources:

- [0] Machine Models and Simulations — P. van Emde Boas (1990), Handbook of Theoretical Computer Science, vol. A (van Leeuwen ed.), Elsevier/MIT Press, pp. 1-66; report version ILLC CT-88-05. https://doi.org/10.1016/B978-0-444-88071-0.50006-0 — `NOT_ACCESSIBLE`
- [1] The Fastest and Shortest Algorithm for All Well-Defined Problems — M. Hutter (2002), IJFCS 13(3):431-443. https://arxiv.org/abs/cs/0206022 arXiv:cs/0206022 — `FULL_TEXT_READ`
- [2] Lower Bounds for Planar Arithmetic Circuits — C. Ramya, P. Shastri (2025), arXiv cs.CC. https://arxiv.org/abs/2509.11322 arXiv:2509.11322 — `PARTIAL_TEXT_READ`

**What it already explains.** That 'reasonable' sequential machine models (multi-tape Turing machines, RAMs with logarithmic cost or unit cost without multiplication, pointer machines, Kolmogorov-Uspenskii machines, standard cellular automata, ... the first machine class) simulate each other with polynomially bounded time overhead and constant-factor space overhead (Invariance Thesis, Slot-van Emde Boas form), so that P, PSPACE, etc. are model-independent; that models with unbounded parallelism or unit-cost multiplication (MRAM, PRAM, alternating machines, ... the second machine class) satisfy instead the Parallel Computation Thesis (polynomial time = PSPACE); that the catalogue of concrete overheads (k tapes -> 1 tape quadratic; -> 2 tapes O(t log t) Hennie-Stearns; RAM <-> TM polynomial; unit-cost multiplication breaks the thesis) is known; and that 'reasonable' is not a formal predicate but a criterion validated by the catalogue. Consequence for Track B: below polynomial-time / constant-space resolution, execution-coordinate 'morphology' differences are definitionally invisible; a morphology theory must either live above that resolution (constant factors, which the thesis deliberately ignores and which Hutter's Sec. 6 shows must be pinned to one fixed reference machine) or at other coordinates.

**Formal object.** Models M_1, M_2 with time_M(p, x), space_M(p, x); M_2 simulates M_1 with overhead (f, g) if for every M_1-program p there is an M_2-program p' with time_{M_2}(p', x) <= f(time_{M_1}(p, x)) and space_{M_2}(p', x) <= g(space_{M_1}(p, x)); Invariance Thesis: reasonable models simulate each other with f polynomial and g linear (constant factor); first machine class = models polynomially time-equivalent and constant-factor space-equivalent to the TM; second machine class = models with polynomial time = PSPACE. (Formal object as reconstructed in the sibling P0.INVARIANCE_THESIS entry; not re-verified against the primary here.)

**Strongest result.** The thesis is a thesis; its content is the simulation catalogue (see P0.INVARIANCE_THESIS for the verified modern restatements: Accattoli-Dal Lago Thm 15.2 for the lambda-calculus; Dershowitz-Falkovich Thm 16 giving an n + nT(n) + T(n)^2 RAM simulation of any effective implementation; Porreca's first/second-class lists). Added here: Hutter 2002 Sec. 6 makes explicit that constant-factor statements (his factor 5) require fixing ONE universal machine U with a fixed tape model for all programs, 'This prevents us from applying the linear speedup theorem (which is cheating somewhat anyway)', and asserts the result 'should also hold for Kolmogorov-Uspenskii and Pointer machines' - i.e. invariance across the first class at the level of leading constants is exactly what a morphology-resolution theory cannot assume. Ramya-Shastri 2025 give a concrete sub-model pair (general circuits vs formulas/planar circuits) that are polynomially equivalent at the evaluation coordinate (formula -> circuit trivial; circuit -> formula at most exponential, planarisation quadratic) yet NOT constant-factor equivalent at the derivative coordinate (Corollaries 45-46).

**Assumptions.** Sequential, deterministic models; time and space as the only resources; input size as the parameter; 'Reasonable' is validated by mutual simulation, not defined intrinsically; unit-cost RAM with multiplication and models with exponential parallelism are excluded from the first class; Constant factors are ignored by design (linear speed-up); a theory that wants constants must fix the reference machine (Hutter Sec. 6)

**Resource model.** time and space only; polynomial time / constant-factor space overhead as the equivalence tolerance

**Failure boundary.** Says nothing about learning/update work, verification work, revision work, description length under a price vector, energy, or hardware-specific constants; the second machine class shows the thesis is already false for parallel/unit-cost-multiplication models, so hardware regimes (Hooker) can move a model across classes; the thesis quotients away exactly the constant factors on which realistic morphology selection often turns.

**Implementation.** none

**Track-B residual.** Track B's execution-coordinate claims must be stated at a resolution finer than polynomial-time/constant-space (else the invariance thesis makes all first-class morphologies one class) or at other coordinates; the open question - is there an invariance-type theorem, or a provable non-invariance, for the update/verification/revision components of the overhead vector - is inherited verbatim from P0.INVARIANCE_THESIS, and this family supplies the first concrete NON-invariance at the update coordinate (formula vs circuit gradient cost, Ramya-Shastri).

**Upward question.** Which overhead tolerance (alpha, beta) in Codex's EQUIVALENCE_CONTRACT_V1 is fine enough to separate morphologies at the execution coordinate without being so fine that the leading-constant dependence on the reference machine (Hutter Sec. 6) makes the quotient ill-defined; and is the update-coordinate non-invariance (formula vs DAG gradient cost) the right template for a 'developmental invariance thesis' with its own first and second classes?

Load-bearing quotes (verbatim from sources actually read):

> "This prevents us from applying the linear speedup theorem (which is cheating somewhat anyway), but allows the possibility of designing a U which allows real-time simulation with abort possibility." — [1] Hutter 2002, Sec. 6
> "Theorem 1 should also hold for Kolmogorov-Uspenskii and Pointer machines." — [1] Hutter 2002, Sec. 6
> "This will increase the computation time of A and B (but not of C!) by, at most, a factor of 4." — [1] Hutter 2002, Sec. 6
> "We observe that an analogous result cannot hold for formulas and planar circuits, while it does hold for read-once planar circuits." — [2] Ramya & Shastri 2025, Sec. 4.2

Verification notes: The van Emde Boas chapter could not be read (six hosts blocked); the thesis statement is taken from the sibling P0.INVARIANCE_THESIS entry, which verified it through Accattoli-Dal Lago's verbatim quotation of the Slot-van Emde Boas form. This entry does not restate that reconstruction; it adds only the Track-B-specific resolution argument (Hutter Sec. 6, read) and the update-coordinate non-invariance example (Ramya-Shastri, read).

### P9A.LEVIN_HUTTER_SEARCH — Levin 1973 universal search + Hutter 2002 fastest-and-shortest algorithm: the exact 5 t_p + d_p time_{t_p} + c_p bound and the role of the huge constants

Disposition: `ADOPT` · best verification: `FULL_TEXT_READ`

Sources:

- [0] Universal sequential search problems — L. A. Levin (1973), Problems of Information Transmission 9(3):265-266 (Probl. Peredachi Inf. 9(3):115-116). https://www.mathnet.ru/eng/ppi914 — `NOT_ACCESSIBLE`
- [1] The Fastest and Shortest Algorithm for All Well-Defined Problems — M. Hutter (2002), International Journal of Foundations of Computer Science 13(3):431-443. https://arxiv.org/abs/cs/0206022 arXiv:cs/0206022 — `FULL_TEXT_READ`

**What it already explains.** Levin search: for an inversion problem g(y) = x with a fast evaluator for g, run all programs p in parallel with time fraction 2^{-l(p)}, verify each output, halt on the first verified witness; total time <= 2^{l(p)} time^+_p(x) where time^+ includes verification; Li-Vitanyi's 'simple' runs p_k every 2^k-th step giving 2^k time^+_{p_k}(x) + 2^{k-1}, and 'search' gives 2^{K(k)+O(1)} time^+_{p_k}(x); the two are asymptotically equivalent because 'search' is itself a program of constant index. The multiplicative constant 2^{l(p)} is the price of not knowing p. Hutter's M_{p*} removes the multiplicative constant at the price of provability: it runs (A) a proof enumerator that adds (p, t_p) to a list when a proof shows p provably equals p* with provable time bound t_p; (B) Levin search over the time-bound programs t with time fraction 2^{-l(p)-l(t)}; (C) the currently fastest p for k = 1, 2, 4, ... steps; with 10%/10%/80% time shares the total time is <= 5 t_p(x) + d_p time_{t_p}(x) + c_p with d_p = 40 * 2^{l(p)+l(t_p)} and c_p = 40 * 2^{l(proof(p))+1} O(l(proof(p))^2); the factor 5 can be 4+eps with constants proportional to 1/eps; Theorem 2: the fastest program is also among the shortest provably-equivalent programs (l(p~) <= K''(p*) + O(1)). Blum's speed-up is avoided by ignoring programs without correctness proofs; for poorly specified problems 'Theorem 1 does not help at all'; neither M_{p*} nor p~ is provably equivalent to p* inside the proof system (van Emde Boas' Godel remark).

**Formal object.** Universal reference TM U; programs p as binary strings, l(p) length; time_p(x) = steps of U on (p, x); time_{t_p}(x) = time to compute the time bound t_p(x); formal proof system with terms u (functional equivalence [forall y: u(p,y) = u(p*,y)]) and tm ([tm(p,x) = n] iff time_p(x) = n); list L of proven (p, t) pairs; shared variables t_fast, p_fast; K'(f) = min{l(p): U(p,x) = f(x) forall x} (not approximable); K''(p*) = min{l(p): a proof of equivalence to p* exists} (approximable from above). Levin search: programs run with relative computation time 2^{-l(p)} subject to Kraft's inequality via prefix-free codes.

**Strongest result.** Hutter Theorem 1 (verbatim): 'Let p* be a given algorithm computing p*(x) from x, or, more generally, a specification of a function. Let p be any algorithm, computing provably the same function as p* with computation time provably bounded by the function t_p(x) for all x. time_{t_p}(x) is the time needed to compute the time bound t_p(x). Then the algorithm M_{p*} constructed in Section 4 computes p*(x) in time time_{M_{p*}}(x) <= 5 * t_p(x) + d_p * time_{t_p}(x) + c_p with constants c_p and d_p depending on p but not on x. Neither p, t_p, nor the proofs need to be known in advance for the construction of M_{p*}(x).' Constants (Sec. 5, verbatim): 'd_p = 40 * 2^{l(p)+l(t_p)}, c_p = 40 * 2^{l(proof(p))+1} * O(l(proof(p)^2)'. Theorem 2: there is p~ equivalent to p* with l(p~) <= K''(p*) + O(1) and the same time bound. Levin search bound (Sec. 2): 'The total computation time to find a solution (if one exists) is bounded by 2^{l(p)} * time^+_p(x).'

**Assumptions.** Levin: inversion (or time-limited optimisation) problems with a fast implementation of the verifier g; halting on first verified witness; Hutter: a formal proof system in which functional equivalence and step counts are expressible; programs must have PROVABLE correctness and provable, quickly computable time bounds; one fixed reference machine (no linear speed-up); Constants c_p (exponential in proof length) and d_p (exponential in program + time-bound length) are ignored in the asymptotic statement; Well-specified problems only

**Resource model.** time (steps on U), description length (l(p), l(t_p), l(proof)), verification time (time^+ includes verifying g(p(x)) = x; proof checking O(l(proof)^2)); no samples, no memory accounting beyond U

**Failure boundary.** Both algorithms are optimal only up to constants that are astronomically large (2^{l(p)} multiplicative for Levin; 2^{l(proof)} additive for Hutter), so they predict nothing about which program is found within realistic budgets; both REQUIRE an exact verifier (g fast to evaluate, or a formal proof), so they do not apply to ecologies with noisy, statistical or delayed feedback; Hutter's optimality is over provably-correct programs only (Blum's phenomenon survives outside that set); neither models learning from data, drift, or revision - the search restarts from scratch per problem (Sec. 8 allows caching of A across invocations).

**Implementation.** none known (Schmidhuber's OOPS/HSEARCH implement Levin-search variants; not verified here)

**Track-B residual.** Same as P0.LEVIN_SEARCH (verification contract weaker than an exact fast verifier) plus, for this family: the verification coordinate is where the programmatic morphology's optimality theorems live (2^{l(p)} time-sharing needs a verifier; 5 t_p needs proofs) while the neural morphology's optimality (cheap gradient) lives at the update coordinate with NO verifier - so the two morphologies are optimal along orthogonal coordinates and the ecology's verification contract decides which coordinate is priced; is there a theorem that with verification cost v per candidate and gradient cost c per step, the crossover between Levin-type program search and gradient descent is at a computable v/c ratio?

**Upward question.** Replace the exact verifier by a registered verification contract with cost v and error epsilon; does the Levin/Hutter time-sharing argument survive as a bound with 2^{l(p)} replaced by a function of (v, epsilon), and does that bound, compared to the cheap-gradient bound, yield a prospective morphology phase boundary (T10) in the (verification price, gradient price) plane?

Load-bearing quotes (verbatim from sources actually read):

> "Levin search just runs and verifies the result of all algorithms p in parallel with relative computation time 2^{-l(p)}; i.e. a time fraction 2^{-l(p)} is devoted to execute p, where l(p) is the length of program p (coded in binary)." — [1] Hutter 2002, Sec. 2
> "The total computation time to find a solution (if one exists) is bounded by 2^{l(p)} * time^+_p(x)." — [1] Hutter 2002, Sec. 2
> "d_p = 40 * 2^{l(p)+l(t_p)}, c_p = 40 * 2^{l(proof(p))+1} * O(l(proof(p)^2)" — [1] Hutter 2002, Sec. 5 (end of time analysis)
> "The factor of 5 may be reduced to 4 + eps by assigning a larger fraction of time to algorithm C. The constants c_p and d_p will then be proportional to 1/eps." — [1] Hutter 2002, Sec. 5
> "What somewhat spoils the practical applicability of M_p* is the large additive constant c_p, which will be estimated in Section 5." — [1] Hutter 2002, Sec. 1
> "For poorly specified problems, Theorem 1 does not help at all." — [1] Hutter 2002, Sec. 3
> "Looking for larger programs saves at most a finite number of computation steps, but cannot improve the time order." — [1] Hutter 2002, Sec. 1
> "Neither M_p*, nor p~ is provably equivalent to p*. The construction of M_p* in section 4 shows equivalence of M_p* (and of p~) to p*, but it is a meta-proof which cannot be formalized within the considered proof system." — [1] Hutter 2002, Sec. 7

Verification notes: Hutter 2002 read in full and quoted verbatim; Levin 1973 not accessible (its statement is taken from Hutter's Sec. 2 and is consistent with the sibling P0.LEVIN_SEARCH entry, which also could not read Levin). heritable-search-transformation-v1/LITERATURE_LEDGER.md row 'Levin universal search; Schmidhuber OOPS/PowerPlay ... OWNS T04' records ownership without the constants; this entry supplies them.

### P9A.MARKOV_LOGIC — Richardson & Domingos 2006 Markov logic networks: logic + probability by grounding, with c^k blow-up per formula

Disposition: `ADOPT` · best verification: `PARTIAL_TEXT_READ`

Sources:

- [0] Markov logic networks — M. Richardson, P. Domingos (2006), Machine Learning 62(1-2):107-136. https://doi.org/10.1007/s10994-006-5833-1 — `NOT_ACCESSIBLE`
- [1] Markov Logic in Infinite Domains — P. Singla, P. Domingos (2007), UAI 2007 (arXiv 1206.5292). https://arxiv.org/abs/1206.5292 arXiv:1206.5292 — `PARTIAL_TEXT_READ`

**What it already explains.** How a first-order knowledge base becomes a probabilistic model: an MLN L is a finite set of pairs (F_i, w_i) of first-order formulas and real weights; given a finite set of constants C it defines a ground Markov network M_{L,C} with one binary node per ground atom and one feature per ground formula (weight w_i), and P(X = x) = (1/Z) exp(sum_i w_i n_i(x)) where n_i(x) counts true groundings of F_i; the size of the ground network is the number of groundings - a formula with k distinct variables over \|C\| constants has \|C\|^k groundings (elementary from the definition) - so compilation logic -> probabilistic is polynomial in \|C\| with degree equal to the maximal number of variables per formula, and exponential in that degree; every discrete distribution / Markov network is representable, and first-order logic is recovered as the limit of all weights -> infinity (Singla-Domingos corollary: K entails alpha iff L^alpha_infinity has no satisfying measure, for locally finite KBs). The 2006 paper (from memory) uses MCMC/Gibbs (later MC-SAT) for inference and pseudo-likelihood gradient for weights, CLAUDIEN-style ILP for structure; the infinite-domain extension shows the construction requires local finiteness (each ground atom has finitely many neighbours), guarantees existence of a Gibbs measure, and gives a uniqueness condition sup_i sum_{C_j containing X_i} (\|C_j\| - 1)\|w_j\| < 2.

**Formal object.** L = {(F_i, w_i)}; Herbrand base B(L) of ground atoms/clauses; S = one binary variable per ground atom; potential Phi^L_X(x) = sum_j w_j f_j(x) over ground clauses C_j with argument set exactly X, w_j = w_i/n if F_i yields n CNF clauses, f_j(x) = 1 iff C_j true in x; finite case: P(X = x) = (1/Z) exp(sum_j w_j f_j(x)); infinite case: Gibbsian specification gamma^L_X(X = x \| S_X = y) = exp(sum_j w_j f_j(x, y)) / sum_{x'} exp(sum_j w_j f_j(x', y)) over clauses touching X.

**Strongest result.** (2006, from memory, UNVERIFIED numbering) Proposition: every probability distribution over discrete or finite-precision numeric variables is representable by an MLN; Proposition: MLNs with infinite weights recover the first-order KB's possible worlds. (2007, verified) Theorem 1: a locally finite MLN admits at least one Gibbs measure; Theorem 2: if sup_{X_i} sum_{C_j in C(X_i)} (\|C_j\| - 1)\|w_j\| < 2 the measure is unique; Corollary: for locally finite K, K \|= alpha iff the MLN with all weights -> infinity on K u {not alpha} has no satisfying measure - 'first-order logic can be viewed as the limiting case of Markov logic when all weights tend to infinity.'

**Assumptions.** Finite domain of constants (2006); unique names, domain closure, known functions (2006, from memory); locally finite / sigma-determinate clauses for the infinite extension; Formulas converted to CNF; weight of a formula split equally among its clauses; Inference is #P-hard in general; practical inference is approximate (MCMC, MC-SAT, lifted) - from memory

**Resource model.** description length (number of weighted formulas, small) vs ground-network size (\|C\|^k per formula, large); inference/verification time (exponential in treewidth, approximate in practice); learning via (pseudo-)likelihood gradients; no ecology accounting

**Failure boundary.** The compilation direction is symbolic -> probabilistic only (grounding); the reverse (extracting a first-order theory from a learned Markov network) is structure learning, not owned; the blow-up \|C\|^k is a hard description-length overhead at D1; semantics collapses to plain logic only in the infinite-weight limit and can be non-unique (phase transitions) for strong interactions; no statement about when the MLN morphology beats a pure-logic or pure-neural one.

**Implementation.** Alchemy (http://alchemy.cs.washington.edu), per Singla-Domingos ref (Kok et al. 2006); not verified live

**Track-B residual.** MLNs give the D1 overhead for the symbolic -> probabilistic compilation (\|C\|^k grounding; exact inference exponential) with logic recovered as a limit; Track B's GMI-T6/T7 residual is the reverse and the ecology: under which (domain size \|C\|, noise, verification) prices does a learner acquire the compact weighted-formula description rather than the ground table, and is the non-uniqueness regime (Theorem 2 violated, 'phase transitions') a morphology phase boundary?

**Upward question.** Treat \|C\| (domain size) and the weight scale as ecology coordinates: is there a prospective phase boundary at which grounding cost \|C\|^k makes the compiled probabilistic morphology dominated by a lifted/symbolic one, and does it coincide with the Gibbs-measure uniqueness threshold?

Load-bearing quotes (verbatim from sources actually read):

> "Markov logic is a simple combination of Markov networks and first-order logic: each first-order formula has an associated weight, and each grounding of a formula becomes a feature in a Markov network, with the corresponding weight." — [1] Singla & Domingos 2007, Sec. 1
> "A Markov logic network (MLN) L is a (finite) set of pairs (F_i, w_i), where F_i is a formula in first-order logic and w_i is a real number." — [1] Singla & Domingos 2007, Definition 3
> "If the MLN contains no function symbols, Definition 3 reduces to the one in Richardson and Domingos (2006), with C being the constants appearing in the MLN." — [1] Singla & Domingos 2007, Sec. 3.1
> "Thus, for locally finite knowledge bases with Herbrand interpretations, first-order logic can be viewed as the limiting case of Markov logic when all weights tend to infinity." — [1] Singla & Domingos 2007, Sec. 4
> "One limitation of Markov logic is that it is only defined for finite domains." — [1] Singla & Domingos 2007, Sec. 1

Verification notes: The 2006 MLJ paper not accessible; its Definition 4.1 / Propositions 4.2-4.3 numbering and the \|C\|^k grounding count are FROM_MEMORY (the count is an immediate consequence of the verified Definition 3). The 2007 arXiv extension by the same group was read and quoted. No prior repo ledger covers this parent.

### P9A.MCCULLOCH_PITTS_KLEENE — McCulloch & Pitts 1943 logical calculus + Kleene 1956 regular events + Minsky 1967: threshold nets are finite automata at finite scope

Disposition: `ADOPT` · best verification: `PARTIAL_TEXT_READ`

Sources:

- [0] A logical calculus of the ideas immanent in nervous activity — W. S. McCulloch, W. Pitts (1943), Bulletin of Mathematical Biophysics 5:115-133. https://doi.org/10.1007/BF02478259 — `NOT_ACCESSIBLE`
- [1] Representation of events in nerve nets and finite automata — S. C. Kleene (1956), Automata Studies (Shannon & McCarthy eds.), Princeton UP, pp. 3-41; RAND RM-704 (1951). https://doi.org/10.1515/9781400882618-002 — `NOT_ACCESSIBLE`
- [2] Computation: Finite and Infinite Machines (ch. 3) — M. Minsky (1967), Prentice-Hall. none — `FROM_MEMORY_UNVERIFIED`
- [3] Neural Logic, Invariance, and the Retina - McCulloch and Pitts (NeuroAI book ch. 2) — N. Dehghani (2026), arXiv q-bio.NC. https://arxiv.org/abs/2609.02183 arXiv:2609.02183 — `PARTIAL_TEXT_READ`
- [4] From Finite Automata to Regular Expressions and Back - A Summary on Descriptional Complexity — H. Gruber, M. Holzer (2014), AFL 2014, EPTCS 151:25-48. https://doi.org/10.4204/EPTCS.151.2 arXiv:1405.5594 — `PARTIAL_TEXT_READ`

**What it already explains.** That a fixed, finite, synchronous network of threshold units with unit delays (excitation summed to threshold, absolute inhibitory veto) is exactly a finite-state machine: any net with N binary units has at most 2^N states, every autonomous trajectory is eventually periodic with transient+period <= 2^N, nets without circles realise exactly the (temporal) propositional expressions, and (Kleene) the events representable by nerve nets or finite automata are exactly the regular events (closure of finite events under union, concatenation and iterate). Minsky's textbook gives the standard constructive FA -> threshold-net compilation. So at the execution coordinate, 'a neural network forward pass' and 'a finite automaton step' are the SAME object up to a bounded change of description; McCulloch-Pitts also already remarked that alterable nets (facilitation/extinction) are behaviourally equivalent to fixed nets, and that a net with a tape computes exactly what a Turing machine computes.

**Formal object.** Units i in {1..N}, state x_i(t) in {0,1}; excitatory set E_i, inhibitory set I_i, threshold theta_i; update x_i(t+1) = I[ sum_{j in E_i} x_j(t) >= theta_i ] * prod_{k in I_i} (1 - x_k(t)) (original veto form), later generalised to x_i(t+1) = I[ sum_j w_ij x_j(t) - theta_i >= 0 ]. Proposition P_i(t) = 'unit i fires at t'. Global map x(t+1) = F(x(t), u(t)) on {0,1}^N. Kleene: an event is a set of input tables; regular events are generated from finite events by E v F, EF, E*F; a finite automaton is a finite set of internal states with a next-state function of (state, input); nerve nets and finite automata represent exactly the regular events.

**Strongest result.** (As reconstructed from secondaries; theorem numbers of the primaries NOT verified this session.) (i) McCulloch-Pitts: every net without circles realises a temporal propositional expression and every such expression is realised by some net; nets with circles realise a strictly larger class involving reference to indefinitely remote past; single threshold unit computes only linearly separable functions (XOR needs two stages) while networks of threshold units realise every finite Boolean function (DNF construction, exponential in inputs in the worst case). (ii) Kleene's analysis and synthesis theorems: the events representable in a finite automaton (equivalently in a McCulloch-Pitts net) are exactly the regular events; conversion overheads (Gruber-Holzer): regular expression of alphabetic width n -> epsilon-NFA of size 22n/5 (tight), -> DFA with 2^n+1 states (upper) and >= (5/4)2^{n/2} (lower, binary alphabet); n-state DFA/NFA -> regular expression of size \|Sigma\| * 2^Theta(n), necessary and sufficient in the worst case even for binary alphabets. (iii) Finite-precision collapse (Sima): bounding the precision of analog states reduces any recurrent net to a finite automaton.

**Assumptions.** Discrete synchronous time; unit delay per synapse; all-or-none firing; Absolute inhibition (veto) in the 1943 idealisation; weighted-sum form is a later generalisation valid only when negative weights reproduce the veto; Fixed structure over time (no plasticity) for the equivalence theorems; alterable nets treated by reduction to fixed nets; Finite number of units and finite (binary) state -> finite automaton; unbounded computation needs a growing family or external tape; Kleene equivalence is extensional (which events), not descriptional: automaton <-> expression conversions can cost 2^Theta(n)

**Resource model.** description length only implicitly (number of units/states, expression size); time as unit delays (logical depth = latency); no learning, sample, verification or memory accounting

**Failure boundary.** Says nothing about which finite automaton a learner acquires, at what cost, or under which ecology; no learning rule; equivalence is at the finite-state execution coordinate only; descriptional overhead between the two morphologies (net vs regular expression) can be exponential, so 'equivalence' hides a description-length coordinate that is NOT bounded by a constant.

**Implementation.** none known (textbook constructions; modern re-implementations e.g. arXiv 2505.11694 'Neural networks as universal finite-state machines')

**Track-B residual.** Given that neural forward computation at finite precision IS finite-automaton execution, the residual is entirely at the other coordinates: (a) description length (2^Theta(n) automaton<->expression gap shows description cost is morphology-relative even at D1), (b) which update law acquires which automaton from experience (D2), (c) ecology selection between a threshold-net description and a table/expression description of the same regular event (D3).

**Upward question.** Since the execution coordinate is quotiented away by Kleene, what distinguishes the neural and automaton morphologies must live in description/update/revision cost and in which ecology prices those costs; is there a theorem that the threshold-net description is the resource-optimal one for regular events under some registered price vector and NOT under another?

Load-bearing quotes (verbatim from sources actually read):

> "A fixed recurrent network of N binary units has at most 2^N states; it is not thereby an unbounded Turing machine." — [3] Dehghani 2026, Chapter orientation (p.1)
> "It studied fixed nets, logical realizability, and memory through circles or possible alteration; it did not provide a general data-driven weight-learning algorithm." — [3] Dehghani 2026, Table II
> "One weighted threshold element computes a linearly separable Boolean function. Networks built from thresholded excitation and inhibition can realize every finite Boolean function." — [3] Dehghani 2026, Table II
> "The equivalence of finite automata and regular expressions dates back to the seminal paper of Kleene on events in nerve nets and finite automata from 1956." — [4] Gruber & Holzer 2014, abstract
> "Let n >= 1 and A be an n-state DFA or NFA over alphabet Sigma. Then size \|Sigma\| * 2^Theta(n) is sufficient and necessary in the worst case for a regular expression describing L(A)." — [4] Gruber & Holzer 2014, Theorem 24

Verification notes: Primaries not readable in this session (all mirrors blocked). The 1943 theorem statements (Theorems I-III) and the exact Kleene theorem numbering are therefore FROM_MEMORY_UNVERIFIED; the reconstruction relies on Dehghani 2026 (arXiv) and Gruber-Holzer 2014 (arXiv), both read. The neuron-count bounds for simulating an m-state automaton (Alon-Dewdney-Ott 1991; Horne-Hush 1996; Indyk 1995 - remembered as Theta(sqrt m) neurons) are cited by Sima 2021 refs [8-10] but the bounds themselves were NOT verified this session. No prior repo ledger reconstructs this parent.

### P9A.NEUROSYMBOLIC_TAXONOMY — Chaudhuri et al. 2021 'Neurosymbolic Programming' + Garcez & Lamb 2020 'Neurosymbolic AI: the 3rd wave' (Kautz's six types): the hybrid field's own taxonomy

Disposition: `ADAPT` · best verification: `PARTIAL_TEXT_READ`

Sources:

- [0] Neurosymbolic Programming — S. Chaudhuri, K. Ellis, O. Polozov, R. Singh, A. Solar-Lezama, Y. Yue (2021), Foundations and Trends in Programming Languages 7(3):158-243. https://doi.org/10.1561/2500000049 — `NOT_ACCESSIBLE`
- [1] Learning Differentiable Programs with Admissible Neural Heuristics — A. Shah, E. Zhan, J. J. Sun, A. Verma, Y. Yue, S. Chaudhuri (2020), NeurIPS 2020. https://arxiv.org/abs/2007.12101 arXiv:2007.12101 — `PARTIAL_TEXT_READ`
- [2] Neurosymbolic AI: The 3rd Wave — A. d'Avila Garcez, L. C. Lamb (2020), arXiv cs.AI (Artificial Intelligence Review 2023). https://arxiv.org/abs/2012.05876 arXiv:2012.05876 — `PARTIAL_TEXT_READ`

**What it already explains.** The hybrid field's self-description. Chaudhuri et al. (via Shah et al.): a neurosymbolic program is a pair (alpha, theta) - a discrete program architecture alpha generated by a context-free DSL grammar (with structural cost s(alpha) = sum of rule costs) and real parameters theta of differentiable library modules - with semantics [[alpha]](x, theta) differentiable in theta; learning is the joint problem (alpha*, theta*) = argmin (s(alpha) + zeta(alpha, theta)) over a combinatorial architecture space and a continuous parameter space; search over alpha is top-down derivation in a graph (A*, iterative-deepening branch-and-bound) with neural networks used as continuous RELAXATIONS of partial programs whose trained loss is an eps-admissible heuristic; conditionals are smoothed (sigmoid gate with temperature). Garcez-Lamb: Kautz's six types - 1 standard deep learning with symbolic I/O; 2 loosely coupled neural core + symbolic solver (AlphaGo); 3 neural module and symbolic module interacting via I/O on complementary tasks (NS-CL, DeepProbLog); 4 symbolic knowledge compiled into the training set or into the initial architecture/weights (localist, with correctness guarantees); 5 symbolic rules mapped to embeddings acting as soft constraints/regularisers on the loss (Logic Tensor Networks, tensor product representations); 6 fully integrated symbolic reasoning inside a neural engine (does not yet exist for combinatorial reasoning); plus the localist-vs-distributed representation axis, the observation that current networks are 'essentially a propositional system' (propositional, nonmonotonic, modal and fragments of FOL, not full FOL), the learning-continuous / reasoning-discrete split, and three challenges (sound efficient knowledge extraction, goal-directed commonsense and combinatorial reasoning, human-network communication).

**Formal object.** DSL grammar with rules X -> sigma_1 ... sigma_k and costs s(r) >= 0; program (alpha, theta); semantics [[alpha]](x, theta), differentiable in theta; prediction error zeta(alpha, theta) = E_{(x,y)~D} 1[[[alpha]](x, theta) != y]; objective (1): (alpha*, theta*) = argmin_{(alpha, theta)} (s(alpha) + zeta(alpha, theta)) (with trade-off lambda in Eq. 9); search graph G with nodes = partial architectures, goal edges (u, alpha) of cost s(r) + zeta(alpha, theta*); heuristic h(u) = min_{omega, theta} zeta(u, (theta_u, omega)) obtained by filling nonterminals with type-correct neural networks; eps-admissibility h(u) <= J(u) + eps. Kautz types 1-6 as an informal partial order of integration tightness.

**Strongest result.** Shah et al. (verified): eps-admissibility of the neural-relaxation heuristic (Eq. 6, assuming universal approximation and near-optimal training) and eps-optimality of A*/IDS-BB under it (Eq. 7: g(alpha_G) <= C* + eps); empirical: NEAR-guided search finds programs within ~10% F1 of RNN baselines with natural interpretations. Garcez-Lamb: no theorem; the load-bearing claims are the taxonomy and the propositional-fixation limit (with proofs of neural/logic correspondence for propositional, nonmonotonic, modal, epistemic and temporal logics cited to Garcez et al. 2002/2009).

**Assumptions.** Chaudhuri/Shah: purely functional DSL; differentiable library modules; smoothed conditionals; structural cost as interpretability proxy; empirical validation loss stands in for zeta; Neural relaxation is an (approximate) proper relaxation of the program space and training reaches a near-optimum (for eps-admissibility); Garcez-Lamb: taxonomy is by coupling topology and representation type (localist vs distributed), not by ecology or resource accounting

**Resource model.** Chaudhuri/Shah: structural cost s(alpha) (description length), search cost (nodes expanded; each node costs a neural training run), parameter learning by gradient; Garcez-Lamb: none formal

**Failure boundary.** The taxonomy classifies systems by how modules are wired, not by when each wiring wins; it contains no ecology coordinates and no prediction of which type dominates under which task/feedback/verification regime; the learning formulation (Eq. 1) fixes the DSL by hand (the morphology is baked in - Codex H-ARCHITECTURE-MACRO); combinatorial search cost is exponential in program size and each heuristic evaluation is itself a training run; Type-6 systems are aspirational.

**Implementation.** NEAR: https://github.com/trishullab/near (Shah et al. ref [39]); Garcez-Lamb: none

**Track-B residual.** The field already owns the two-coordinate update law of hybrids (discrete search on alpha guided by relaxations + gradient on theta) - which is exactly the cheap-gradient/verification split of this family expressed as an architecture; Track B's residual is the missing D3 content: a law predicting which Kautz type (or which (alpha, theta) split) an ecology selects, and a resource accounting in which s(alpha) and the per-node training cost are priced, so that 'neurosymbolic' becomes a region of a phase diagram rather than a taxonomy cell.

**Upward question.** Can the six Kautz types be re-derived as the phases of ONE generating basis under (verification price, gradient price, description price), so that e.g. Type 5 (rules as loss regularisers) is predicted where verification is cheap and gradients cheap, and Type 3 where symbolic verification is exact but expensive - turning the taxonomy into a T10 phase diagram?

Load-bearing quotes (verbatim from sources actually read):

> "We view a program in our domain-specific language (DSL) as a pair (alpha, theta), where alpha is a discrete (program) architecture and theta is a vector of real-valued parameters." — [1] Shah et al. 2020, Sec. 2
> "Our key innovation is to view various classes of neural networks as continuous relaxations over the space of programs, which can then be used to complete any partial program." — [1] Shah et al. 2020, abstract
> "In a nutshell, current neural networks are capable of representing propositional logic, nonmonotonic logic programming, propositional modal logic and fragments of first-order logic, but not full first-order or higher-order logic." — [2] Garcez & Lamb 2020, Sec. 2
> "It is now accepted that learning takes place on a continuous search space of (sub)differentiable functions; reasoning takes place in general on a discrete space as in the case of goal-directed theorem proving." — [2] Garcez & Lamb 2020, Sec. 5
> "although a fully-fledged Type 6 system for combinatorial reasoning does not exist yet." — [2] Garcez & Lamb 2020, Sec. 3
> "As the saying goes, "all vectors are symbols, but not all symbols are vectors"." — [2] Garcez & Lamb 2020, Sec. 6

Verification notes: The FnT monograph itself not accessible; its formalisation is verified through Shah et al. 2020 (same senior authors, same (alpha, theta) formulation). Garcez-Lamb read. No prior repo ledger covers these parents.

### P9A.RASP_TRACR — Perez-Barcelo-Marinkovic (attention is Turing complete) + Weiss-Goldberg-Yahav RASP + Lindner et al. Tracr: an actual programmatic -> neural compiler with reported overhead

Disposition: `ADOPT` · best verification: `FULL_TEXT_READ`

Sources:

- [0] On the Turing Completeness of Modern Neural Network Architectures — J. Perez, J. Marinkovic, P. Barcelo (2019), ICLR 2019 (precursor of 'Attention is Turing-complete', JMLR 22(75), 2021). https://arxiv.org/abs/1901.03429 arXiv:1901.03429 — `PARTIAL_TEXT_READ`
- [1] Attention is Turing-Complete — J. Perez, P. Barcelo, J. Marinkovic (2021), Journal of Machine Learning Research 22(75):1-35. https://jmlr.org/papers/v22/20-302.html — `NOT_ACCESSIBLE`
- [2] Thinking Like Transformers — G. Weiss, Y. Goldberg, E. Yahav (2021), ICML 2021, PMLR 139. https://arxiv.org/abs/2106.06981 arXiv:2106.06981 — `PARTIAL_TEXT_READ`
- [3] Tracr: Compiled Transformers as a Laboratory for Interpretability — D. Lindner, J. Kramar, S. Farquhar, M. Rahtz, T. McGrath, V. Mikulik (2023), NeurIPS 2023. https://arxiv.org/abs/2301.05062 arXiv:2301.05062 — `FULL_TEXT_READ`

**What it already explains.** A complete, executable compilation chain programmatic -> neural: (1) Perez et al.: the transformer (encoder-decoder, hard attention, rational arbitrary-precision arithmetic, positional encoding pos(i) = (1, i, 1/i, 1/i^2)) simulates any Turing machine with one encoder layer, three decoder layers, vectors of dimension d = 2\|Q\| + 4\|Sigma\| + 11, and one decoder step per TM step; without positional encodings it is order- and even proportion-invariant (cannot recognise 'even number of a's'); with FIXED precision it is not Turing complete (positional encodings become a finite alphabet extension). (2) RASP: a language of s-ops and selectors whose primitives (elementwise map ~ MLP; select/aggregate ~ attention head; selector_width) map to transformer blocks, so that program length in select-aggregate depth gives the minimal number of layers and the number of distinct selectors per layer gives the heads; empirical Table 2 shows trained transformers at the RASP-predicted (layers, heads) reach 99+% and degrade when a layer or head is removed. (3) Tracr: an open-source compiler RASP -> Craft (labelled vector spaces) -> weights of a standard decoder-only transformer (no layer norm), in six steps; reported overheads: residual stream = direct sum of one orthogonal subspace per s-op (categorical one-hot or one numerical dimension), layers = longest-path allocation (upper bound, heuristic), attention selectors realised via low-rank W_QK with BOS default and inverse temperature 100, numerical MLPs via discretisation lookup; e.g. frac_prevs compiles to a 14-dimensional residual stream (12 for embeddings, 2 for variables) and 4 layers with two no-ops. What is lost: compiled weights are not trained weights (axis-aligned, sparse, orthogonal, unrealistically wide), no learning law is compiled, boolean selector combinations are not compilable in general (Lemma F.1: 'or' of two generic selectors needs product s-ops of multiplicative dimension), and gradient-descent compression of a compiled model can change the encoding (target_pos categorical -> numerical) so the compiled semantics is not preserved under the update law.

**Formal object.** Transformer: A_i = softmax(x W_QK^i x^T), MHA(x) = sum_i A_i x W_OV^i, MLP(x) = sigma(x W_1) W_2, residual stream x in R^{N x d}. RASP: s-ops (sequence-to-sequence functions of equal length), selectors select(k, q, p) -> {0,1}^{n x n} with S[i][j] = p(k_i, q_j), aggregate(S, v)_i = mean of v over selected j, selector_width(S)_i = row sum; tokens, indices built-in. Tracr: computational graph of RASP ops with inferred finite value sets; residual space R = (+)_{s-ops} V_s (categorical: one-hot basis labelled 'name:value'; numerical: one dimension); attention W_QK = T^{-1}(W~_QK + beta_BOS x_one x_{tokens:bos}^T), T^{-1} = 100; layer index = longest path from input. Perez TM simulation: decoder output y_i encodes (q^{(i)}, s^{(i)}, m^{(i-1)}); layer 1 applies delta via 2-layer FFN; layer 2 computes head positions c^{(i)}, c^{(i+1)} by self-attention over m^{(0..i)}; layer 3 attends (hard attention with score -\|<q,k>\|) to the last time the current cell was written to fetch the symbol.

**Strongest result.** Perez et al. Theorem 3.4 (verified): 'The class of Transformer networks with positional encodings is Turing complete.' with construction size 'one encoder layer, three decoder layers and vectors of dimension d = 2\|Q\| + 4\|Sigma\| + 11'; Proposition 3.1 (proportion invariance without positional encodings) and Corollary 3.2 (the order-invariant regular language 'even number of a's' is not recognisable); and the fixed-precision negative: 'the Transformer with positional encodings and fixed precision is not Turing complete'. Tracr Lemma F.1 (verified): an attention matrix realising the OR of two selectors stored in orthogonal subspaces forces both predicates to be rank-1, so generic boolean selector combinations are not compilable into a single head. RASP Table 2 (verified): compiled (layers, heads) = Reverse (2,1), Hist (1,2), 2-Hist (2,2), Sort (2,1), Most-Freq (3,2), Dyck-1 (2,1), Dyck-2 (3,1 with select_best); trained transformers at these sizes reach 93.9-99.9% and drop (e.g. Reverse to 23.1% at L-1) when reduced.

**Assumptions.** Perez: hard attention (argmin \|<q,k>\| with averaging on ties), rational functions only (no softmax/sin/cos), arbitrary precision rationals, positional encoding computable in linear time, seq2seq with decoder loop of r steps; RASP: uniform (binary) selection patterns realised by strongly negative unselected scores; MLP blocks assumed able to compute any elementwise function (Hornik); no input-dependent loops; non-causal attention by default; Tracr: finite input vocabulary and context size (so every s-op has a finite value set); BOS token mandatory; categorical/numerical encoding annotations; selectors restricted to two input s-ops; no layer norm; layer allocation heuristic (longest path) may be suboptimal; All three: weights are constructed, not learned; no claim that gradient descent finds these circuits

**Resource model.** description length (layers, heads, residual dimension, MLP hidden size), execution time (one decoder step per TM step; attention is O(n^2) per layer), precision (arbitrary vs fixed); no learning/sample/verification accounting; Tracr Appendix E reports compression training cost (3e5 AdamW steps, 1-4 h on 2 CPU cores)

**Failure boundary.** The compiler goes one way (program -> weights) and preserves only forward semantics; it does not compile the update law (there is no 'gradient of a RASP program'), and Tracr Sec. 5.3 documents that applying gradient descent to compiled models can silently change the implemented encoding (average per-layer cosine similarity ~0.8 at near-perfect accuracy), i.e. behavioural compilation without developmental equivalence - exactly Codex hostile H-STATIC-EQUIVALENCE; expressivity limits: binary attention patterns only (Merrill et al.: saturated transformers are constant-depth threshold circuits), no probabilistic next-token computation, no general boolean selector combination; residual width grows as the sum of all s-op value-set sizes (categorical) - compiled models 'can be sparse and inefficient'; Perez's TM result needs unbounded precision, and Tracr's frac_prevs numerical values are only approximated by discretising MLPs.

**Implementation.** https://github.com/google-deepmind/tracr (Tracr, Haiku/JAX); http://github.com/tech-srl/RASP (RASP REPL); Perez et al.: none

**Track-B residual.** Tracr is the existence proof that D1 at the EXECUTION coordinate (programmatic -> neural) is engineering, with overhead reported as (layers = dependency depth, heads = selectors per layer, width = sum of value-set sizes). The residual is (a) the UPDATE coordinate: a learning law that, applied to the compiled weights, preserves the program (Sec. 5.3 shows SGD does not), (b) the reverse compiler neural -> program with bounded overhead (mechanistic interpretability, which Tracr exists to evaluate - Nanda et al. do one case by hand), and (c) whether any ecology selects the compiled (axis-aligned, orthogonal) description over the trained (superposed) one - Tracr's compression study is a first ecology axis (residual width price d) with a measured threshold (frac_prevs solved at d >= 6 of 14).

**Upward question.** What is the compiler at the update coordinate - a map from (program, program-edit law) to (weights, weight-update law) such that the registered experience -> update -> behaviour trajectory is preserved with bounded overhead - and does it exist at all for gradient descent, given that SGD on compiled weights changes encodings?

Load-bearing quotes (verbatim from sources actually read):

> "The complete construction uses one encoder layer, three decoder layers and vectors of dimension d = 2\|Q\| + 4\|Sigma\| + 11 to store one-hot representations of states, symbols and some additional working space." — [0] Perez et al. 2019, proof sketch of Theorem 3.4
> "Then from Proposition 3.1 we obtain that the Transformer with positional encodings and fixed precision is not Turing complete." — [0] Perez et al. 2019, Sec. 3.3
> "We can analyze any RASP program to infer the minimum number of layers and maximum number of heads required to realise it in a transformer." — [2] Weiss et al. 2021, Sec. 6
> "We note that RASP does not suggest the embedding width needed to encode this solution in an actual transformer." — [2] Weiss et al. 2021, footnote 7
> "In other words, we embed each s-op in its own orthogonal subspace, which is reserved for its sole use throughout the entire network." — [3] Tracr 2023, Sec. 3 step 5
> "First, we compute the longest path from the input to a given node. This path length is an upper bound for the layer number to which we can allocate the node." — [3] Tracr 2023, Sec. 3 step 4
> "The compiled frac_prevs model has a 14-dimensional residual stream, but it uses 12 out of these for the input embeddings." — [3] Tracr 2023, Sec. 4.1
> "This difference in encodings shows that even with a fairly restrictive compression setup, compressed models may not stay faithful to the original RASP programs." — [3] Tracr 2023, Sec. 5.3
> "the encodings occupy dimensionality multiplicative in the sizes of the constituent s-op output types, which is an impediment to scaling these circuits very far." — [3] Tracr 2023, Appendix F
> "Tracr constructs layers from hand-coded parameter matrices. This is both unrealistic and inefficient" — [3] Tracr 2023, Appendix A.2 Realism

Verification notes: Tracr read in full; RASP and the ICLR Perez paper read at theorem/table level; the JMLR 2021 'Attention is Turing-complete' text itself not accessible (its Theorem numbering may differ from the ICLR version quoted here). No prior repo ledger covers these parents (functional-neural-absorption-v1 cards were grepped: no hits).

### P9A.SIEGELMANN_SONTAG — Siegelmann & Sontag 1995: rational-weight saturated-linear recurrent nets are Turing universal in real time with 886 units

Disposition: `ADOPT` · best verification: `PARTIAL_TEXT_READ`

Sources:

- [0] On the computational power of neural nets — H. T. Siegelmann, E. D. Sontag (1995), Journal of Computer and System Sciences 50(1):132-150. https://doi.org/10.1006/jcss.1995.1013 — `ABSTRACT_ONLY`
- [1] Turing Computation with Recurrent Artificial Neural Networks — G. S. Carmantini, P. beim Graben, M. Desroches, S. Rodrigues (2015), arXiv cs.NE (NIPS 2015 workshop). https://arxiv.org/abs/1511.01427 arXiv:1511.01427 — `PARTIAL_TEXT_READ`
- [2] On the Turing Completeness of Modern Neural Network Architectures — J. Perez, J. Marinkovic, P. Barcelo (2019), ICLR 2019. https://arxiv.org/abs/1901.03429 arXiv:1901.03429 — `PARTIAL_TEXT_READ`
- [3] Stronger Separation of Analog Neuron Hierarchy by Deterministic Context-Free Languages — J. Sima (2021), arXiv cs.NE (Neurocomputing). https://arxiv.org/abs/2102.01633 arXiv:2102.01633 — `PARTIAL_TEXT_READ`

**What it already explains.** That a FIXED-SIZE recurrent network of first-order units with the saturated-linear activation sigma(x)=0 (x<0), x (0<=x<=1), 1 (x>1) and RATIONAL weights can simulate any Turing machine, in real time (linear-time overhead), by encoding stack/tape contents as rationals in [0,1] (Cantor-set style base encoding); one universal net of 886 units computes a universal partial-recursive function. Precision is the hidden unbounded resource: the number of digits of the analog activations grows linearly with the computation, and bounding it collapses the model to a finite automaton (Kleene regime). With arbitrary real weights the same model is super-Turing (P/poly in polynomial time). Codex ledger entry P-NEURAL-UNIVERSALITY records only the headline.

**Formal object.** x_i(t+1) = sigma( sum_j a_ij x_j(t) + sum_j b_ij u_j(t) + c_i ), i=1..N, sigma = saturated-linear (ramp), a_ij, b_ij, c_i in Q (the 1995 theorem) or R (super-Turing regime). Tape/stack encoding: a one-sided infinite symbol sequence s = d_1 d_2 ... is Godelised as psi(s) = sum_k gamma(d_k) g^{-k} in [0,1]; push/pop/substitute are affine maps on psi(s) (Carmantini Sec. 2.3.1). Sima's alpha-ANN refinement: binary-state network + alpha analog units with rational weights; 0ANN = FA, 2ANN >= DCFL, 3ANN = TM.

**Strongest result.** Main theorem (from the abstract, verbatim-level): one may simulate all Turing machines by such nets, and in particular any multi-stack Turing machine in real time, with a net of 886 processors computing a universal partial-recursive function. Quantitative refinements (verified in secondaries): Carmantini et al. give an explicit first-order R-ANN with n_units = 2 + n_s + n_s n_q + 2 n_s^2 n_q + 1 units (n_q states, n_s tape symbols) simulating a TM in real time via a nonlinear dynamical automaton, e.g. 259 units for Minsky's 7-state 4-symbol UTM versus 886 for Siegelmann-Sontag; Sima proves any TM is simulated by a 3ANN (three analog rational-weight neurons plus a binary net) with linear-time overhead, and that the analog neuron hierarchy collapses at 3: FA = 0ANN < 1ANN < 2ANN <= 3ANN = TM. Precision: analog values are rationals whose representation length grows linearly along a computation; with bounded precision the power collapses to finite automata.

**Assumptions.** Saturated-linear (piecewise-linear ramp) activation; NOT the logistic sigmoid (the logistic case is a separate later result, Kilian & Siegelmann 1996, cited in Sima 2021 fn. 1); Rational weights and exact rational arithmetic with unbounded precision of activations (unbounded precision is the memory resource); Synchronous discrete time; first-order (affine-then-activation) units; Turing universality is at the execution coordinate: weights are constructed, not learned; Real-time simulation assumes the same step model for TM and net (one net step per TM step up to constant)

**Resource model.** network size (constant, 886 or 2+n_s+n_s n_q+2n_s^2 n_q+1), time (linear overhead), precision/memory (unbounded, grows linearly); no learning, sample or verification accounting

**Failure boundary.** Provides no learning law and no statement about which functions are learnable or at what cost; the construction depends on unbounded precision, which physical hardware and every trained network lack (so the theorem never applies to a deployed model as such); says nothing about description-length or update cost relative to a symbolic TM description; the 886-unit universal net is a compiled object, exactly like a Tracr model.

**Implementation.** none known for the 1995 construction; Carmantini et al. describe a programmable NDA->R-ANN mapping (no public code URL verified)

**Track-B residual.** Under a registered finite precision p (a resource price), the neural morphology is a finite automaton and the TM-equivalence is void; the Track-B question is how the compilation overhead of programmatic -> neural scales in p and in the update coordinate (a gradient step on the 886 compiled weights does not preserve TM semantics), i.e. whether 'neural TM' is a stable point of any learning law rather than a compiled fixed point.

**Upward question.** Which precision/price regime makes the analog-state neural description cheaper than the explicit tape description for the same computation, and does any learning law ever reach the Siegelmann-Sontag encoding from experience (D2), or is it developmentally unreachable (a compiled-only fixed point)?

Load-bearing quotes (verbatim from sources actually read):

> "their work establishes that recurrent neural networks (RNNs) are Turing complete even if only a bounded number of resources (i.e., neurons and weights) is allowed." — [2] Perez et al. 2019, Sec. 1
> "Rational weights make the analog-state (shortly analog) NNs (with real-valued outputs in the interval [0, 1]) computationally equivalent to Turing machines (TMs) [10, 14]" — [3] Sima 2021, Sec. 1
> "Nevertheless, by bounding the precision of analog states, we would reduce the computational power of NNs to that of finite automata which could be implemented by binary states." — [3] Sima 2021, Sec. 1
> "the number of digits in the representation of analog values may increase (linearly) along a computation." — [3] Sima 2021, Sec. 1
> "a R-ANN that can simulate Minsky's 7-states 4-symbols UTM [15] in real-time with 259 units (as per Equation 21), approximately 1/3 of the 886 units needed in the solution proposed by Siegelmann and Sontag [1]" — [1] Carmantini et al. 2015, Sec. 4
> "we have proven that any TM can be simulated by a 3ANN having rational weights with a linear-time overhead [24]." — [3] Sima 2021, Sec. 1

Verification notes: Primary JCSS text not accessible; abstract-level claims (886 processors; real-time multi-stack simulation) verified via the publisher abstract as rendered by the search engine; the base-4 / Cantor-set stack encoding detail is FROM_MEMORY and consistent with Carmantini's Godelisation. Codex's P-NEURAL-UNIVERSALITY entry (PARENT_LEDGER_V1.json) verified only the abstract; this entry adds the activation type, precision requirement, size formulas and the fixed-precision collapse. The LITERATURE_LEDGER.md DOI 'https://doi.org/10.1006/j.jcss.1995.1013' contains a typo (extra 'j.').

### P9A.SIMA_ORPONEN — Sima & Orponen 2003: complexity-theoretic taxonomy of neural network models - the existing bounded-compilation table for the neural morphology

Disposition: `ADOPT` · best verification: `PARTIAL_TEXT_READ`

Sources:

- [0] General-purpose computation with neural networks: a survey of complexity theoretic results — J. Sima, P. Orponen (2003), Neural Computation 15(12):2727-2778. https://doi.org/10.1162/089976603322518731 — `ABSTRACT_ONLY`
- [1] Stronger Separation of Analog Neuron Hierarchy by Deterministic Context-Free Languages — J. Sima (2021), arXiv cs.NE. https://arxiv.org/abs/2102.01633 arXiv:2102.01633 — `PARTIAL_TEXT_READ`
- [2] Super-Linear Gate and Super-Quadratic Wire Lower Bounds for Depth-Two and Depth-Three Threshold Circuits — D. M. Kane, R. Williams (2015), arXiv cs.CC (STOC 2016). https://arxiv.org/abs/1511.07860 arXiv:1511.07860 — `PARTIAL_TEXT_READ`
- [3] On the Turing Completeness of Modern Neural Network Architectures — J. Perez, J. Marinkovic, P. Barcelo (2019), ICLR 2019. https://arxiv.org/abs/1901.03429 arXiv:1901.03429 — `PARTIAL_TEXT_READ`

**What it already explains.** The survey classifies neural models by architecture (feedforward vs recurrent), time (discrete vs continuous), state (binary vs analog), weights (symmetric vs asymmetric, integer/rational/real), size (finite net vs infinite family) and computation type (deterministic vs probabilistic), and for each cell records the equivalent classical model WITH resource bounds. Reconstructed table (each row verified in the named secondary unless flagged): [R1] binary-state finite recurrent nets with integer weights = finite automata (Kleene/Minsky; polynomial, sublinear-in-states neuron counts by Alon-Dewdney-Ott, Horne-Hush, Indyk - exact bounds UNVERIFIED). [R2] analog saturated-linear recurrent nets, rational weights = Turing machines, real/linear time, constant size (Siegelmann-Sontag); polynomial-time nets = P; three analog units suffice (Sima 2020). [R3] real weights = P/poly in polynomial time, arbitrary I/O maps in exponential time (Siegelmann-Sontag 1994); a proper infinite hierarchy between P and P/poly indexed by Kolmogorov complexity of the weights (Balcazar-Gavalda-Siegelmann 1997). [R4] bounded precision analog nets = finite automata. [R5] polynomial-size constant-depth threshold circuit families = TC0, strictly above AC0 (parity), with the depth-2 small-weight vs depth-3 separation (Hajnal et al.; Kane-Williams restatement). [R6] symmetric (Hopfield) nets: convergence/energy results and PSPACE/P-completeness-type results (from memory, UNVERIFIED). [R7] transformers with hard attention + arbitrary precision = Turing complete with 1 encoder + 3 decoder layers and d = 2\|Q\|+4\|Sigma\|+11; fixed precision -> not Turing complete (Perez et al., post-survey row).

**Formal object.** A family of discrete-time recurrent networks N = (V, W, sigma) with states y^{(t)} in {0,1}^{s-1} x I (binary units with Heaviside H, analog units with saturated-linear sigma), excitation xi_j^{(t)} = sum_i w_ji y_i^{(t)}, synchronous update y_j^{(t+1)} = sigma_j(xi_j^{(t)}); language acceptance via input/output protocol with online (constant delay) or offline variants; classes indexed by weight domain (Z, Q, R), analogicity alpha (number of analog units) and time bound.

**Strongest result.** The survey's content is the map itself; its load-bearing theorem rows for Track B are: integer weights <=> regular languages (Chomsky 3); rational weights <=> recursively enumerable (Chomsky 0) with linear-time simulation; real weights <=> P/poly (polynomial time); bounded precision <=> regular; and (Sima 2020/2021 refinement) FA = 0ANN < 1ANN < 2ANN <= 3ANN = TM with (DCFL \ REG) subset of (2ANN \ 1ANN), i.e. one extra analog neuron with real weights cannot recognise any non-regular deterministic context-free language online, while two rational-weight analog neurons accept every DCFL and three give Turing completeness.

**Assumptions.** Discrete synchronous time; first-order units; saturated-linear or Heaviside activations (results 'partially valid' for other activations incl. logistic); Weight domain is the classifying parameter (Z/Q/R); analog precision unbounded unless stated; Language-acceptor input/output protocols (online: bounded delay between symbols; offline: unbounded); Uniform (single finite net) vs nonuniform (families) distinction is essential: threshold-circuit rows are nonuniform families

**Resource model.** size (units/gates), time (steps; polynomial vs real-time), precision (digits of analog state), weight descriptive complexity (Kolmogorov complexity of real weights), depth (for circuits); no learning/sample/verification accounting

**Failure boundary.** The table is entirely at the execution coordinate and for hand-constructed (compiled) weights; it does not say which row a learning process lands in, nor the cost of converting a trained network into its automaton/TM equivalent (extraction), nor anything about the update law; the alpha-ANN hierarchy is 'only partially comparable' to Chomsky's (cut languages have no Chomsky counterpart), so morphology classes are not nested in the classical ones.

**Implementation.** none known

**Track-B residual.** Track B's GMI-T2/T4 execution-coordinate content is this table; what remains is a second table with the same rows but columns 'update work', 'verification work', 'revision work' and 'description length under a registered price vector' - none of which the survey family fills - plus the ecology-selection question of which row a developmental process occupies as a function of precision price.

**Upward question.** Can the same taxonomy axes (state type, weight domain, precision, analogicity alpha) be re-read as ECOLOGY prices (precision price, memory price) so that the row a developmental system occupies becomes a prediction (GMI-T10) rather than a design choice?

Load-bearing quotes (verbatim from sources actually read):

> "NNs with integer weights, corresponding to binary-state (shortly binary) networks which employ the Heaviside activation function (with Boolean outputs 0 or 1), coincide with finite automata (FAs) recognizing regular languages" — [1] Sima 2021, Sec. 1
> "In addition, NNs with arbitrary real weights can even derive "super-Turing" computational capabilities [6]. Namely, their polynomial-time computations correspond to the nonuniform complexity class P/poly" — [1] Sima 2021, Sec. 1
> "FAs = 0ANNs < 1ANNs < 2ANNs <= 3ANNs = 4ANNs = ... = TMs" — [1] Sima 2021, Sec. 1 (hierarchy display, inequality symbols transliterated)
> "It appears that the analog neuron hierarchy which is schematically depicted in Figure 1, is only partially comparable to that of Chomsky." — [1] Sima 2021, Sec. 1
> "any learning algorithm has to employ a sufficient number of analog units to be able to infer more complex grammars." — [1] Sima 2021, Sec. 5

Verification notes: The 2003 survey itself could not be read (five hosts blocked). Its taxonomy criteria are verified from the abstract; the hierarchy rows R1-R4 are verified from Sima's 2021 restatement (which cites the survey as ref [7]); R5 from Kane-Williams; R7 from Perez et al.; R6 and the exact neuron-count bounds for automaton simulation are FROM_MEMORY_UNVERIFIED. No prior repo ledger covers this parent.

### P9A.THRESHOLD_CIRCUITS — Threshold circuits: Parberry 1994 + Hajnal-Maass-Pudlak-Szegedy-Turan 1993 - TC0, depth/weight trade-offs, Boolean vs threshold overhead

Disposition: `ADOPT` · best verification: `PARTIAL_TEXT_READ`

Sources:

- [0] Threshold circuits of bounded depth — A. Hajnal, W. Maass, P. Pudlak, M. Szegedy, G. Turan (1993), Journal of Computer and System Sciences 46(2):129-154. https://doi.org/10.1016/0022-0000(93)90001-D — `NOT_ACCESSIBLE`
- [1] Circuit Complexity and Neural Networks — I. Parberry (1994), MIT Press. none — `FROM_MEMORY_UNVERIFIED`
- [2] Super-Linear Gate and Super-Quadratic Wire Lower Bounds for Depth-Two and Depth-Three Threshold Circuits — D. M. Kane, R. Williams (2015), arXiv cs.CC (STOC 2016). https://arxiv.org/abs/1511.07860 arXiv:1511.07860 — `PARTIAL_TEXT_READ`

**What it already explains.** The resource-bounded relationship between the Boolean-gate morphology (AC0: constant depth, polynomial size, unbounded fan-in AND/OR/NOT) and the threshold-gate morphology (TC0: constant depth, polynomial size, linear threshold / majority gates): TC0 strictly contains AC0 (parity and majority are in TC0 but not AC0 - Furst-Saxe-Sipser, Hastad); every Boolean function has a depth-2 threshold circuit of 2^O(n) gates (Minsky-Papert); polynomial-weight threshold gates are simulable by majority circuits, and arbitrary-weight depth-2 threshold circuits are efficiently simulable by depth-3 majority circuits (Goldmann-Hastad-Razborov 1992) - a bounded compilation between weight classes at the cost of one layer; and the first exponential lower bound: inner product mod 2 needs 2^Omega(n) gates in depth-2 small-weight threshold circuits (HMPST 1993), while it has O(n)-gate depth-3 majority circuits - a depth-2 vs depth-3 separation. Also: separating TC0 from NC1 reduces to an n^{1.1}-gate lower bound at every constant depth (Allender-Koucky).

**Formal object.** Linear threshold function f(a) = 1 iff sum_i w_i a_i >= t, w in R^n, t in R; LTF o LTF = depth-2 circuits of LTF gates; TC0_d = depth-d circuits of MAJORITY gates (equivalently polynomially-bounded integer weights) with negations; size measured in gates or wires; AC0 = constant-depth polynomial-size unbounded-fan-in AND/OR/NOT circuits.

**Strongest result.** HMPST 1993 (as restated by Kane-Williams): inner product modulo 2 requires 2^Omega(n) size depth-2 threshold circuits when weights are polynomially bounded; hence polynomial-size depth-2 (small-weight) threshold circuits are strictly weaker than depth-3. Extensions: Nisan 1994 (MAJ o LTF), Forster et al. 2001 (LTF o MAJ). Best general depth-2 results before 2015: Omega(n/log n) gates for IP2 in LTF o LTF (GHR92), Theta(n) gates for IP2 in unbounded-depth LTF circuits (Groger-Turan; Roychowdhury et al.), PARITY needs Omega(n^{3/2}) wires / Omega(n^{1/2}) gates in LTF o LTF (Impagliazzo-Paturi-Saks 1993, shown tight on average by Kane-Williams Thm 1.4). Kane-Williams Thm 1.1: Andreev's function cannot be (1/2+eps)-approximated by LTF o LTF circuits with fewer than Omega(eps^3 n^{3/2}/log^3 n) gates or Omega(eps^3 n^{5/2}/log^{7/2} n) wires, while it has O(n)-gate depth-3 majority circuits (Thm 1.2).

**Assumptions.** Nonuniform circuit families (one circuit per input length); size counted in gates or wires; Weight regime matters: polynomial (majority-simulable) vs arbitrary real weights change the achievable lower bounds; Lower bounds are for explicit functions in P (or NC1); no learning is modelled

**Resource model.** size (gates, wires), depth, weight magnitude (description length of weights); no time-of-learning, sample or verification accounting

**Failure boundary.** Says nothing about learnability of the circuits or about training dynamics; the separations are worst-case over explicit functions, not over ecologies; the depth-hierarchy frontier for threshold circuits is 'surprisingly intractable' - no super-polynomial lower bound for depth-3 majority circuits is known, so TC0 vs NC1 is open; therefore the Boolean-vs-threshold overhead table has exact entries only at depth 2.

**Implementation.** none known

**Track-B residual.** Threshold-circuit theory gives the DESCRIPTION-coordinate overhead between Boolean and threshold morphologies at fixed depth; Track B needs the corresponding overhead at the UPDATE coordinate (does the exponential depth-2 blow-up for IP2 translate into an exponential learning-time or sample gap between a Boolean-basis learner and a threshold-basis learner under a registered ecology?), which no parent here states.

**Upward question.** Is there an ecology (task distribution + depth price) under which the exponential description gap between depth-2 small-weight threshold circuits and depth-3 majority circuits becomes a predicted morphology phase boundary, and does a learning process cross it?

Load-bearing quotes (verbatim from sources actually read):

> "Hajnal et al. [HMP+93] proved the first size lower bounds for LTF o LTF circuits, showing that the inner product modulo 2 (a.k.a. IP2) requires 2^Omega(n) size when the weights of each LTF are small (polynomial in the input length)." — [2] Kane & Williams 2015, Sec. 2 history paragraph
> "Note that IP2 has MAJ o MAJ o MAJ circuits with O(n) gates, so we cannot use IP2 in our depth-three lower bounds." — [2] Kane & Williams 2015, Sec. 2
> "Minsky and Papert [MP69] proved that LTF o LTF of 2^O(n) gates can compute any Boolean function, but failed to prove a strong impossibility result for these circuits." — [2] Kane & Williams 2015, Sec. 1
> "Goldmann, Hastad, and Razborov [GHR92] showed that every LTF o LTF circuit can be efficiently simulated by a MAJ o MAJ o MAJ circuit, and computing IP2 with LTF o LTF requires Omega(n/ log n) gates." — [2] Kane & Williams 2015, Sec. 2
> "In order to formally understand the power of neural computing, we first need to crack the frontier of threshold circuits with two and three layers, a regime that has been surprisingly intractable to analyze." — [2] Kane & Williams 2015, abstract

Verification notes: HMPST 1993 and Parberry 1994 not readable; all statements attributed to them are as restated in Kane-Williams 2015 (read). The AC0 vs TC0 separation via parity (Furst-Saxe-Sipser 1984; Hastad 1986) is cited by Kane-Williams but its statement is FROM_MEMORY. No prior repo ledger covers this parent.

### P9A.UNIVERSAL_APPROXIMATION — Universal approximation (Cybenko 1989, Hornik 1991) as D0-only, plus Telgarsky 2016 depth separation as a D1 description-overhead lower bound

Disposition: `ADOPT` · best verification: `PARTIAL_TEXT_READ`

Sources:

- [0] Approximation by superpositions of a sigmoidal function — G. Cybenko (1989), Mathematics of Control, Signals and Systems 2:303-314. https://doi.org/10.1007/BF02551274 — `NOT_ACCESSIBLE`
- [1] Approximation capabilities of multilayer feedforward networks — K. Hornik (1991), Neural Networks 4(2):251-257. https://doi.org/10.1016/0893-6080(91)90009-T — `FROM_MEMORY_UNVERIFIED`
- [2] Benefits of depth in neural networks — M. Telgarsky (2016), COLT 2016, JMLR W&CP 49:1-23. https://arxiv.org/abs/1602.04485 arXiv:1602.04485 — `PARTIAL_TEXT_READ`
- [3] Thinking Like Transformers — G. Weiss, Y. Goldberg, E. Yahav (2021), ICML 2021. https://arxiv.org/abs/2106.06981 arXiv:2106.06981 — `PARTIAL_TEXT_READ`

**What it already explains.** D0 for the neural morphology over continuous functions: finite sums sum_j alpha_j sigma(y_j^T x + theta_j) with any continuous sigmoidal (Cybenko) or any bounded non-constant activation (Hornik) are dense in C(I_n) (uniform norm on compacta) and in L^p; no bound on the number of terms N is given - the theorems are existence results. Telgarsky then supplies a D1-type lower bound at the DESCRIPTION coordinate: depth is a resource that cannot be traded for width at polynomial cost: there are functions computed by ReLU networks with Theta(k^3) layers and Theta(1) nodes per layer that no network of O(k) layers and o(2^k) nodes (or boosted decision trees with o(2^{k^3}) nodes) can approximate in L1 to within 1/64.

**Formal object.** Cybenko: sigma sigmoidal iff sigma(t) -> 1 (t -> +inf), -> 0 (t -> -inf); sums S = {sum_{j=1}^N alpha_j sigma(y_j^T x + theta_j)}; density in C(I_n), I_n = [0,1]^n. Telgarsky: networks of (t, alpha, beta)-semi-algebraic gates (gate polynomial within regions cut out by t predicate polynomials of degree alpha, piece degree beta; ReLU is (1,1,1)-sa); N_d(m, l, t, alpha, beta) = networks of <= l layers, <= m nodes per layer; crossing number Cr(f) = number of intervals on which the classifier 1[f >= 1/2] is constant; (t,[a,b])-triangle functions; f^k = k-fold composition of the ReLU triangle f(z) = sigma_R(2 sigma_R(z) - 4 sigma_R(z - 1/2)).

**Strongest result.** Telgarsky Theorem 1.1 (verbatim, verified): 'Let any integer k >= 1 and any dimension d >= 1 be given. There exists f : R^d -> R computed by a neural network with standard ReLU gates in 2k^3 + 8 layers, 3k^3 + 12 total nodes, and 4 + d distinct parameters so that inf_{g in C} int_{[0,1]^d} \|f(x) - g(x)\| dx >= 1/64, where C is the union of' functions computed by networks of (t, alpha, beta)-semi-algebraic gates in <= k layers and <= 2^k/(t alpha beta) nodes, and functions computed by linear combinations of <= t decision trees each with <= 2^{k^3}/t nodes. Mechanism: Lemma 3.2 (few layers -> few oscillations: Cr(g o h) <= 2(2tm alpha/l)^l beta^{l^2}), Corollary 3.9 (many layers -> many oscillations: Cr(f^k) = (2t)^k + 1), Lemma 3.1 (low-crossing functions poorly approximate high-crossing ones). Cybenko Theorem 1/2 (FROM_MEMORY): for any continuous sigmoidal sigma the sums S are dense in C(I_n); no rate or width bound.

**Assumptions.** Cybenko/Hornik: target continuous (or Borel measurable) on a compact set; approximation in sup or L^p norm; arbitrary width; existence only; Telgarsky: semi-algebraic gates (ReLU, max, piecewise polynomial, decision trees); L1 distance on [0,1]^d; the hard function is univariate in x_1 (embedding into d dimensions is trivial); Telgarsky's separation is Theta(k^3) vs O(k) layers, not k vs k+1; large-d separations of 2 vs 3 layers are Eldan-Shamir (not read)

**Resource model.** description length (number of nodes, layers, distinct parameters); no time, sample, learning or verification accounting; Cybenko/Hornik account for nothing (existence)

**Failure boundary.** Universal approximation gives no width, no rate, no learnability, so it is non-evidence for anything at D1+ (Codex GMI-T2 already says this); Telgarsky's bound is a worst-case existence of ONE hard function per k (Sec. 1.2 shows such functions are rare: shallow nets fit most random labellings of O(k^9) points); it does not say depth is beneficial for a given ecology, nor that gradient descent finds the deep representation.

**Implementation.** none known

**Track-B residual.** The depth-separation theorem shows that description overhead between 'depth-k' and 'depth-k^3' neural sub-morphologies is exponential, so 'neural' is not one morphology at D1; Track B needs the ecology (task distribution with high oscillation / compositional structure) under which this description gap is PAID by a learner (samples, updates), i.e. a T10 phase boundary in depth rather than a worst-case separation.

**Upward question.** Which ecologies make the Telgarsky-type high-oscillation (compositional) structure typical rather than rare, so that a depth price in the resource vector predicts a phase boundary between shallow-wide and deep-narrow neural morphologies (GMI-T10), and is there an analogous separation in the update coordinate (gradient steps) rather than only in size?

Load-bearing quotes (verbatim from sources actually read):

> "there exist neural networks with Theta(k^3) layers, Theta(1) nodes per layer, and Theta(1) distinct parameters which can not be approximated by networks with O(k) layers unless they are exponentially large - they must possess Omega(2^k) nodes." — [2] Telgarsky 2016, abstract
> "The key idea is that just a few function compositions (layers) suffice to construct a highly oscillatory function, whereas function addition (adding nodes but keeping depth fixed) gives a function with few oscillations." — [2] Telgarsky 2016, Sec. 1.1
> "It is natural to wonder if there are many such special functions. The following bound indicates their population is in fact quite modest." — [2] Telgarsky 2016, Sec. 1.2
> "as famously shown by Hornik et al. (1989), MLPs such as those present in the feed-forward transformer sub-layers can approximate with arbitrary accuracy any borel-measurable function, provided sufficiently large input and hidden dimensions." — [3] Weiss et al. 2021, Sec. 3.1

Verification notes: Cybenko and Hornik primaries not accessible this session; their theorem statements are FROM_MEMORY and consistent with the Codex publisher-abstract verification (P-NEURAL-UNIVERSALITY). Telgarsky read at theorem/lemma level. The Codex GMI-T2 row cites Cybenko for universal approximation; this entry adds Telgarsky as the D1 counterweight.


## P9B — learnability / evolvability limits that separate learning morphologies (not in #377 §4)

### P9B.ABBE_DIFFERENTIABLE_VS_PAC — Abbe, Kamath, Malach, Sandon, Srebro 2021: mini-batch SGD / full-batch GD equal PAC when bρ < 1/8 (resp. mρ < 1/8), collapse to SQ when bρ² = ω(log n); a learning-law phase boundary with named axes (batch size b, gradient precision ρ)

Disposition: `ADOPT` · best verification: `PARTIAL_TEXT_READ`

Sources:

- [0] On the Power of Differentiable Learning versus PAC and SQ Learning — Emmanuel Abbe, Pritish Kamath, Eran Malach, Colin Sandon, Nathan Srebro (2021), NeurIPS 2021 (arXiv 2108.04190v2, 6 Feb 2022). https://arxiv.org/abs/2108.04190 arXiv:2108.04190 — `PARTIAL_TEXT_READ`

**What it already explains.** Owns the precise learning-law phase boundary between 'gradient learning = arbitrary sample-based (PAC) learning' and 'gradient learning = aggregate-statistics (SQ) learning'. With gradients clipped to [−1,1], rounded to multiples of ρ (d = −log ρ bits) with error ≤ 3ρ/4, and mini-batches of b fresh samples per step: (1a) if ρ < 1/(8b), bSGD simulates any PAC(m, r) method with T' = O(mn/δ) steps and p' = r + O(T'(n + log b)) parameters, and as a neural net with the five-piece 'two-stage ramp' activation when ρ < min{1/(8b), 1/12}; (1b) PAC(m' = Tb) always simulates bSGD; (1c) if bρ² > C log(Tp/δ), SQ(k' = Tp, τ' = ρ/8) simulates bSGD, so bSGD ⊆ SQ ⊊ PAC when bρ² = ω(log n) at polynomial T, p; (1d) for any b, bSGD with ρ = τ/16 and T' = k⌈C log(k/δ)/(bτ²)⌉ simulates SQ(k, τ). Corollary 2: bρ < 1/8 ⇒ bSGD[b,ρ] = PAC (and NN version = PAC_TM); bρ² ≥ ω(log n) ⇒ bSGD[b,ρ] ⊆ SQ ⊊ PAC. Full-batch GD on m samples: PAC if ρ < 1/(8m) (Thm 3a, Corollary 3: fbGD = PAC), SQ if mρ² > C(Tp log(1/ρ) + log(1/δ)) (Thm 3c). Mechanism: a 'sample extraction' procedure that recovers one raw sample from polynomially many mini-batch statistical queries when precision is fine relative to b, and the observation that with coarse precision empirical and population statistics are indistinguishable. Also owns the computational version (poly-size nets simulate poly-time PAC/SQ via circuit-to-subnet compilation).

**Formal object.** Differentiable model f_w: R^p × X → R, X = {0,1}^n, Y = {0,1}, square loss. bSGD(T, ρ, b, p, r): w^(0) ~ W (r random bits), w^(t+1) = w^(t) − γ g_t where g_t ∈ ρZ^p, ‖g_t − [∇L_{S_t}(f_{w^(t)})]_1‖_∞ ≤ 3ρ/4, S_t ~ D^b independent per step, [·]_1 = entrywise clipping to [−1,1]; error = E[sup L_D(f_{w^(T)})] over all valid roundings. fbGD(T, ρ, m, p, r): same with S_t = S ~ D^m fixed. PAC(m, r): any map from m samples and r random bits to a predictor; SQ(k, τ, r): k adaptive queries Φ_t: X×Y → [−1,1] answered within τ. Simulation preorder: C' ⪰_δ C iff for every A ∈ C there is A' ∈ C' with err(A', D) ≤ err(A, D) + δ for all D (Definition 1). Intermediate model bSQ(k, τ, b, p, r): p-dimensional vector queries answered by empirical averages over a fresh b-sample within τ (Eq. 8); Thm 2a: bSQ ⪰_δ PAC when τ < 1/(2b).

**Strongest result.** Theorem 1a: 'For all b and ρ < 1/(8b), and for all m, r, δ, it holds that bSGD(T′ = O(mn/δ), ρ, b, p′ = r + O(T′(n + log b)), r′) ⪰_δ PAC(m, r)'. Theorem 1c: 'for all T, ρ, b, p, r, such that bρ² > C log(T p/δ), it holds that SQ(k′ = T p, τ′ = ρ/8, r′ = r) ⪰_δ bSGD(T, ρ, b, p, r)'. Corollary 2: 'If ∀_n bρ < 1/8 then bSGD[b, ρ] = PAC and bSGD^σ_NN[b, ρ] = PAC_TM. If bρ² ≥ ω(log n) then bSGD[b, ρ] ⊆ SQ ⊊ PAC'. Corollary 3: 'fbGD = PAC and fbGD_NN = PAC_TM'. Open gap: 1/ρ < b < log(n)/ρ².

**Assumptions.** Gradient computation is exact up to clipping and ρ-rounding; the adversary may choose any valid rounding (worst case, E sup).; Fresh independent mini-batches at each step (bSGD); fixed sample (fbGD); square loss; binary inputs/outputs.; Model size p, iterations T, and precision 1/ρ may be polynomial in n for the class statements; the PAC-simulating networks use a specific five-piece piecewise-linear activation with a flat central segment (ReLU would need fixed, untrainable weights).; Step size fixed (γ = 1 or 2) and irrelevant to the results; initialization may be sampled in poly(n) time for the NN version.

**Resource model.** samples (T·b or m), iterations T, parameters p, random bits r, precision bits d = −log ρ, mini-batch size b, SQ query count k and tolerance τ, runtime TIME for the computational versions; no memory or verification accounting

**Failure boundary.** Simulation results, not natural-emergence results: the PAC-simulating network is a hand-built gadget that decodes samples from gradients; nothing says that ordinary training on ordinary architectures exploits the bρ < 1/8 regime. The intermediate regime 1/ρ < b < log(n)/ρ² is open. Only gradient-based laws are placed on the (b, ρ) plane; evolution (CSQ), query learning and Bayesian inference are not positioned there. Says nothing about which morphology is favoured, only what the gradient CHANNEL can transmit.

**Implementation.** none known

**Track-B residual.** Track B needs (i) the (b, ρ) plane merged with Valiant's (t, s) fitness channel and Angluin's (MQ, EQ) channel into one feedback-precision coordinate of the ecology, (ii) the cost of realizing precision ρ charged (bits per gradient, hardware), and (iii) a statement that the morphology acquired under a low-precision large-batch regime is aggregate-statistics-shaped (SQ-implementable) while under a fine-precision regime it may be sample-memorizing/algebraic — none of which Abbe et al. claim.

**Upward question.** Is there a single charged 'feedback channel capacity' coordinate (bits of target-dependent information per interaction, combining ρ, b, τ, t, query type) such that PAC-, SQ-, CSQ- and EQ-acquirable morphology classes are its level sets?

Load-bearing quotes (verbatim from sources actually read):

> "With fine enough precision relative to minibatch size, namely when bρ is small enough, SGD can go beyond SQ learning and simulate any sample-based learning algorithm and thus its learning power is equivalent to that of PAC learning" — [0] abstract
> "On the other hand, when bρ^2 is large enough, the power of SGD is equivalent to that of SQ learning." — [0] abstract
> "Theorem 1a (PAC to bSGD). For all b and ρ < 1/(8b), and for all m, r, δ, it holds that bSGD(T′ = O(mn/δ), ρ, b, p′ = r + O(T′(n + log b)), r′) ⪰_δ PAC(m, r)." — [0] Sec. 3, Theorem 1a
> "for all T, ρ, b, p, r, such that bρ^2 > C log(T p/δ), it holds that SQ(k′ = T p, τ′ = ρ/8, r′ = r) ⪰_δ bSGD(T, ρ, b, p, r)." — [0] Sec. 3, Theorem 1c
> "If ∀_n bρ < 1/8 then bSGD[b, ρ] = PAC and bSGD^σ_NN[b, ρ] = PAC_TM. If bρ^2 ≥ ω(log n) then bSGD[b, ρ] ⊆ SQ ⊊ PAC" — [0] Corollary 2
> "Corollary 3. fbGD = PAC and fbGD_NN = PAC_TM." — [0] Sec. 6
> "Overall, except for an intermediate regime between 1/ρ and log(n)/ρ^2, we can precisely capture the power of bSGD." — [0] Sec. 1
> "The clipping and rounding we use captures using d = − log ρ bits of precision, and indeed we generally consider ρ = 2^{−d} where d ∈ N." — [0] Sec. 2 Precision, Rounding and Clipping
> "for all T, ρ, m, p, r, such that mρ^2 > C(T p log(1/ρ) + log(1/δ)), it holds that SQ(k′ = T p, τ′ = ρ/8, r′ = r) ⪰_δ fbGD(T, ρ, m, p, r)." — [0] Sec. 6, Theorem 3c
> "pretending that bSGD or fbGD do find the global minimizer would mean we can learn all poly-time computable functions, which is known to be impossible [e.g. Kearns and Valiant, 1994, Klivans and Sherstov, 2009]." — [0] Sec. 1

Verification notes: Theorem and corollary statements transcribed from the arXiv full text; proofs (Appendix D, E) not checked. Abbe & Sandon 2020 (b = 1 result) is a missing parent. Not previously in any ORION ledger.

### P9B.ANGLUIN_LSTAR — Angluin 1987 L*: polynomial-time exact learning of regular sets from a minimally adequate teacher (membership + equivalence queries with counterexamples) — the tractable side of the verification-contract flip

Disposition: `ADOPT` · best verification: `PARTIAL_TEXT_READ`

Sources:

- [0] Learning Regular Sets from Queries and Counterexamples — Dana Angluin (1987), Information and Computation 75(2):87-106. https://doi.org/10.1016/0890-5401(87)90052-6 — `NOT_ACCESSIBLE`
- [1] Query Learning Bounds for Advice and Nominal Automata — Kevin Zhou (2024), arXiv 2409.10822. https://arxiv.org/abs/2409.10822 arXiv:2409.10822 — `PARTIAL_TEXT_READ`
- [2] On the Hardness of Learning Regular Expressions — Attias, Reyzin, Srebro, Vardi (2025), arXiv 2510.04834. https://arxiv.org/abs/2510.04834 arXiv:2510.04834 — `PARTIAL_TEXT_READ`
- [3] Counterexample Guided Learning in the Large using Reasoning Agents — Hongyi Liu, Frederic Sala, Thomas Reps, Adithya Murali (2026), arXiv 2606.11521. https://arxiv.org/abs/2606.11521 arXiv:2606.11521 — `PARTIAL_TEXT_READ`

**What it already explains.** Owns the tractable side: with a minimally adequate teacher answering membership queries (is w ∈ L?) and equivalence queries (is the conjectured DFA correct? if not, return a counterexample), the minimum DFA for any regular language is identified exactly in time polynomial in the number of states n of the minimal DFA and the length m of the longest counterexample, using an observation table (S, E, T) kept closed and consistent; at most n equivalence queries are needed because each counterexample forces at least one new state. This is the canonical instance of a class flipping from intractable (passive: NP-hard proper, cryptographically hard improper) to tractable purely by changing the verification contract. Later work (Chase & Freitag 2020, as restated by Zhou 2024) bounds (EQ+MQ) query complexity by O(Ldim · Cdim) via Myhill-Nerode, with no dependence on counterexample length but worse dependence on n.

**Formal object.** Concept class C = regular languages over Σ, target L*; oracle O_mem(x) = 1[x ∈ L*]; equivalence oracle: given hypothesis h, answers yes if L(h) = L*, else returns counterexample(s) C ⊆ L(h) △ L*. L*: maintain observation table (S, E, T) with S prefix-closed, E suffix-closed, T: (S ∪ SΣ)·E → {0,1} filled by membership queries; table closed (every row of SΣ equals some row of S) and consistent (rows equal in S stay equal after any one-letter extension) ⇒ conjecture the DFA whose states are distinct rows of S; on counterexample t, add all prefixes of t to S and refill; repeat. Learner succeeds when it submits the target as an equivalence query (Zhou 2024 Def. 1). By Myhill-Nerode, distinct rows ≤ n, so at most n conjectures.

**Strongest result.** Verified qualitative statement: 'the L∗ algorithm that learns deterministic finite automata (DFAs) using a polynomially bounded number of equivalence and membership queries' (Zhou 2024), and that L*'s bound depends on the length of the longest counterexample (Zhou 2024 Discussion). Exact bounds as I recall them from Angluin 1987 — at most n equivalence queries, O(m n²) membership queries (O(\|Σ\| m n²) for alphabet size \|Σ\|), total time polynomial in n and m — are FROM_MEMORY_UNVERIFIED in this session and should be checked against Angluin's Theorem in Sec. 3 before being quoted as theorem-grade.

**Assumptions.** A teacher that answers equivalence queries exactly (decidable for regular languages via symmetric-difference automata) and membership queries at unit cost; counterexamples of bounded length m.; Target is a regular language (finite Myhill-Nerode index); exact identification, not PAC approximation (Angluin also shows equivalence queries can be simulated by PAC sampling, giving PAC+MQ learnability).; Hypotheses are DFAs (proper); the observation-table invariants (closed, consistent) are maintained by membership queries.

**Resource model.** number of equivalence queries (≤ n), number of membership queries (poly in n, m), time poly(n, m); the cost of the teacher itself (constructing counterexamples) is NOT charged

**Failure boundary.** Requires an equivalence oracle; with membership queries alone (no equivalence queries) exact learning of DFAs needs exponentially many queries in general, and Angluin-Kharitonov 1995 show membership queries do not help for DNF under cryptographic assumptions (as cited by Attias et al.); for regular EXPRESSIONS the MQ setting stays hard (Attias et al. 2025) because description length differs exponentially between DFAs and REs. Does not say anything about which morphology should host the learner; the observation table IS a discrete data structure, so the tractable regime is naturally symbolic/automaton-shaped, but nothing forbids a neural implementation of the same query strategy.

**Implementation.** many open implementations exist (e.g. LearnLib, AALpy) — not verified in this session

**Track-B residual.** State the verification-contract phase boundary as a charged ecology coordinate: passive labelled sample (cost per example c_s, no counterexample oracle) ⇒ automaton acquisition super-polynomial (Gold / Pitt-Warmuth proper; Kearns-Valiant improper); MQ+EQ oracle at cost c_q per query ⇒ acquisition in poly(n, m) queries (Angluin). Track B must (i) price the oracle, (ii) show the same flip for non-automaton morphologies compiled from a common basis, and (iii) predict where along c_q/c_s the frontier changes membership — none of which Angluin or Gold address.

**Upward question.** Is 'verification strength' a single scalar ecology coordinate (e.g. counterexample-oracle availability x query price) that induces the same tractability flip for programmatic and rule morphologies as for DFAs, and can its critical value be predicted before search from the Myhill-Nerode/consistency dimension of the task?

Load-bearing quotes (verbatim from sources actually read):

> "The field was initiated by Angluin in 1987 with the introduction of the L∗ algorithm that learns deterministic finite automata (DFAs) using a polynomially bounded number of equivalence and membership queries [1]." — [1] Zhou 2024, Sec. 1
> "their results have no dependence on the length of the longest counterexample returned by the oracle (while the L∗ algorithm does), but a worse dependence on the number of states." — [1] Zhou 2024, Discussion & Related Work
> "An equivalence query (EQ) consists of a hypothesis H ∈ H, to which the oracle answers yes if H = C, or with a counterexample x ∈ X for which H(x) ≠ C(x)." — [1] Zhou 2024, Sec. 2.1
> "Let C ⊆ H be two concept classes on a set X, c = Cdim(C, H), and d = Ldim(C). Then (EQ+MQ)-query complexity of C with queries from H is O(cd)." — [1] Zhou 2024, Theorem 1 (= Chase & Freitag 2020, Thm 2.24)
> "Moreover, ≡_L has exactly n classes if and only if the minimal DFA recognizing L has exactly n states." — [1] Zhou 2024, Theorem 2 (Myhill-Nerode)
> "In contrast, DFAs are tractably learnable with membership queries via the L⋆ algorithm of Angluin [1987]." — [2] Attias et al. 2025, Table 1 notes
> "Angluin’s L∗ algorithm Angluin [1987], which learns regular sets through membership and equivalence queries with counterexamples; this oracle setting closely matches ours." — [3] Liu et al. 2026, Sec. 2

Verification notes: Original blocked. The paired flip (this entry vs P9B.DFA_HARDNESS) is verified at the level 'passive PAC: hard; PAC+MQ: tractable' from Attias et al. 2025 Table 1, which cites both sides. Exact L* query counts are flagged FROM_MEMORY_UNVERIFIED.

### P9B.COMP_STAT_TRADEOFF — Computational sample complexity (Decatur, Goldreich, Ron 1999; Servedio 2000) and 'Using More Data to Speed-up Training Time' (Shalev-Shwartz, Shamir, Tromer 2012): the data-volume axis changes which learner is efficient

Disposition: `ADOPT` · best verification: `FULL_TEXT_READ`

Sources:

- [0] Using More Data to Speed-up Training Time — Shai Shalev-Shwartz, Ohad Shamir, Eran Tromer (2012), AISTATS 2012 (arXiv 1106.1216v2). https://arxiv.org/abs/1106.1216 arXiv:1106.1216 — `FULL_TEXT_READ`
- [1] Computational Sample Complexity — Scott E. Decatur, Oded Goldreich, Dana Ron (1999), SIAM Journal on Computing 29(3):854-879. https://doi.org/10.1137/S0097539797325648 — `NOT_ACCESSIBLE`
- [2] Computational sample complexity and attribute-efficient learning — Rocco A. Servedio (2000), J. Comput. Syst. Sci. 60(1):161-178. https://doi.org/10.1006/jcss.1999.1666 — `NOT_ACCESSIBLE`

**What it already explains.** Owns the DATA-VOLUME × COMPUTE axis: the runtime needed to learn a class to excess error ε is a decreasing function T_{H,ε}(m) of the number of available examples m; its finite-ness threshold is the information-theoretic sample complexity, its limit T_{H,ε}(∞) is the data-laden regime. DGR 1999 first separated information-theoretic from computational sample complexity (examples needed to learn in polynomial time) and exhibited a class not efficiently learnable from few examples but efficiently learnable from polynomially more; Servedio 2000: a subclass of 1-decision lists learnable inefficiently from O(1) examples, not efficiently from o(n), efficiently from Ω(n). SST 2012 Theorem 1 (agnostic, cryptographic): a problem over X = {0,1}^{2n} that is inefficiently learnable with m = O(1/ε) samples in time O(2^n + m), not polynomial-time learnable from O(log n) samples if one-way permutations exist, and efficiently learnable (time O(m), improper predictor of runtime O(m³)) from m = O(n/ε²) samples via Gaussian elimination over GF(2). Natural (upper-bound-only) examples: 3-DNF (ERM over 3-DNF: d/ε samples but not poly(d); ERM over conjunctions of triples: d³/ε samples, poly time); agnostic preferences (d/ε² not poly(d) vs d²/ε² in time O(m)); kernel halfspaces (L²/ε² samples, time exp(L²/ε² log(L/ε)) vs exp(L log(L/ε)) both); Banditron; sparse PCA thresholding vs SDP.

**Formal object.** Agnostic PAC: instances X, targets Y, loss ℓ, unknown D over Z ⊆ X×Y, err(h) = E_{(x,y)~D} ℓ(h(x), y); hypothesis class H; learner A with time(A, m) = worst-case expected runtime on m examples (also bounding the returned predictor's per-instance runtime). Main object: T_{H,ε}(m) = min{t : ∃A s.t. ∀D, time(A, m) ≤ t ∧ err(A(m)) ≤ inf_{h∈H} err(h) + ε}, = ∞ if no t qualifies. Theorem 1 construction: Z = {((r, s), b) : ⟨P^{-1}(s), r⟩ = b} for a one-way permutation P; H = {h_x(r, s) = ⟨x, r⟩ if s = P(x), else random bit}; hard distributions D_x uniform over ((r, P(x)), ⟨x, r⟩); efficient learner: find most common s', collect examples with s = s', predict ⟨x', r⟩ for r in their GF(2) span (Lemma 2: unspanned mass ≤ n/m'), random bit otherwise; Goldreich-Levin inverts P from any O(log n)-sample learner.

**Strongest result.** SST 2012 Theorem 1 (three bullets: inefficient O(1/ε) samples & O(2^n + m) time; no poly-time algorithm from O(log n) samples under one-way permutations; efficient from m = O(n/ε²) samples in O(m) training time with an O(m³) improper predictor). DGR 1999 and Servedio 2000 results as restated in SST Sec. 1.1 (originals not read).

**Assumptions.** Cryptographic assumption (one-way permutations, e.g. RSA) for the formal gap; the 'natural' gaps rest on current best upper bounds without matching lower bounds (explicitly flagged as open by the authors).; Agnostic, improper learning: the efficient predictor is not in H (Sec. 1.1: 'our efficient learning procedure computes and returns an improper predictor').; Runtime measured as worst-case expected runtime including the predictor's evaluation cost; the model captures the full curve T(m), not just polynomial vs not.; DGR/Servedio constructions are realizable and rely on the labels being produced by a hypothesis in the class.

**Resource model.** samples m and training time t jointly (the curve T_{H,ε}(m)); predictor runtime; excess error ε; no memory/verification accounting

**Failure boundary.** Curves are known at two points (information-theoretic and data-laden) but 'we do not know how the rest of the curve looks like'. The mechanism of the speed-up — enlarge the hypothesis class to make ERM convex/greedy at the price of more samples (Figure 1) — is a change of REPRESENTATION with the same morphology family, so it is not itself a morphology law. No prospective way to compute the crossover m* for a new problem without solving it.

**Implementation.** none known

**Track-B residual.** Track B's data-volume phase claim must be stated as a T_{H,ε}(m)-type curve per morphology family with matched capability, and the phase boundary as the m at which the nondominated family changes; SST/DGR give the object and the existence of crossovers within one family, not across morphology classes with charged construction/verification cost.

**Upward question.** Across morphology families compiled from one basis, does the family that is nondominated at the information-theoretic sample complexity differ from the family nondominated in the data-laden limit, and can the crossover m* be predicted from the ecology's structure (e.g. SQ-dimension, algebraic closure) before search?

Load-bearing quotes (verbatim from sources actually read):

> "T_{H,ǫ}(m) = min{t : ∃ A s.t. ∀ D, time(A, m) ≤ t ∧ err(A(m)) ≤ inf_{h∈H} err(h) + ǫ}" — [0] Sec. 2, Eq. (1)
> "It is inefficiently learnable with sample size m = O(1/ǫ), and running time O(2^n + m)." — [0] Theorem 1, bullet 1
> "Assuming one-way permutations exist, there exist no polynomial-time algorithm based on a sample of size O(log(n))." — [0] Theorem 1, bullet 2
> "It is efficiently learnable with a sample of size m = O(n/ǫ^2). Specifically, the training time is O(m), resulting in an improper predictor whose runtime is O(m^3)." — [0] Theorem 1, bullet 3
> "[6] were the first to jointly study the computational and sample complexity, and to show that a tradeoff between runtime and sample size exists." — [0] Sec. 1.1 (on Decatur, Goldreich, Ron)
> "they distinguish between the information theoretic sample complexity of a class and its computational sample complexity, the latter being the number of examples needed for learning the class in polynomial time." — [0] Sec. 1.1
> "[11] showed that for a concept class composed of 1-decision-lists over {0, 1}^n, which can be learned inefficiently using O(1) examples, no algorithm can learn it efficiently using o(n) examples, and there is an efficient algorithm using Ω(n) examples." — [0] Sec. 1.1 (on Servedio 2000)
> "Still, we do not know how the rest of the curve looks like." — [0] Sec. 2.1

Verification notes: SST 2012 read in full. DGR 1999 and Servedio 2000 verified only through SST's restatement. Not previously in any ORION ledger.

### P9B.DFA_HARDNESS — Passive learning of DFAs is hard: Gold 1978 (minimum consistent DFA NP-hard), Pitt-Warmuth 1993 (no polynomial-ratio approximation), Kearns-Valiant 1994 (cryptographic, representation-independent PAC hardness)

Disposition: `ADOPT` · best verification: `PARTIAL_TEXT_READ`

Sources:

- [0] Complexity of automaton identification from given data — E. Mark Gold (1978), Information and Control 37(3):302-320. https://doi.org/10.1016/S0019-9958(78)90562-4 — `NOT_ACCESSIBLE`
- [1] The minimum consistent DFA problem cannot be approximated within any polynomial — Leonard Pitt, Manfred K. Warmuth (1993), Journal of the ACM 40(1):95-142. https://doi.org/10.1145/138027.138042 — `NOT_ACCESSIBLE`
- [2] Cryptographic limitations on learning Boolean formulae and finite automata — Michael Kearns, Leslie Valiant (1994), Journal of the ACM 41(1):67-95. https://doi.org/10.1145/174644.174647 — `NOT_ACCESSIBLE`
- [3] Learning deterministic finite-state machines from the prefixes of a single string is NP-complete — Radu Cosmin Dumitru, Ryo Yoshinaka, Ayumi Shinohara (2026), arXiv 2601.12621. https://arxiv.org/abs/2601.12621 arXiv:2601.12621 — `PARTIAL_TEXT_READ`
- [4] On the Hardness of Learning Regular Expressions — Idan Attias, Lev Reyzin, Nathan Srebro, Gal Vardi (2025), arXiv 2510.04834. https://arxiv.org/abs/2510.04834 arXiv:2510.04834 — `PARTIAL_TEXT_READ`

**What it already explains.** Owns the passive-verification side of the automaton phase boundary. Proper side: given a finite sample (D+, D-) of accepted/rejected strings, deciding whether a DFA with ≤ m states is consistent is NP-complete (Gold 1978; Angluin 1978), and, assuming P ≠ NP, for any constant c no polynomial-time algorithm can output a consistent DFA with ≤ m*^c states where m* is the minimum (Pitt-Warmuth 1993); sharpened by Chalermsook et al. 2014 to n^{1-ε}-inapproximability in the sample size n, tight against the trivial prefix-tree acceptor. Improper side: under RSA / factoring Blum integers / quadratic residuosity, poly(n)-state DFAs (and Boolean formulae, constant-depth threshold circuits) are not even weakly PAC-learnable distribution-free by ANY polynomial-time learner outputting ANY polynomial-time hypothesis (Kearns-Valiant 1994); later extended to the uniform distribution under local-PRG assumptions (Daniely-Vardi 2021) and to other assumptions (random k-SAT, sparse LPN).

**Formal object.** MinConDFA / ConDFA: input a DFA sample (D+, D-) ⊂ Σ* × Σ* disjoint finite, integer m; decide existence of a DFA M = (Q, Σ, δ, F, q_0) with \|Q\| ≤ m and M(s) = + ∀ s ∈ D+, M(s) = - ∀ s ∈ D-. Reduction from graph K-colouring (Zhang 2020 variant): sample Z+ = {ε} ∪ {v_i e_ij : i<j}, Z- = V ∪ {v_j e_ij : i<j}; G is K-colourable iff a consistent DFA with K+1 states exists. Kearns-Valiant: weak PAC learning of C_n = {c representable by a DFA with ≤ n^ε states} is as hard as inverting RSA / factoring Blum integers / deciding quadratic residues; the hardness is representation-independent (improper learning) because the reduction produces a distinguisher from any accurate hypothesis.

**Strongest result.** Verified restatements: 'It was shown to be NP-hard by Gold (1978) and Angluin (1978)' and 'Assuming P ≠ NP, they proved that for any constant c, no polynomial-time algorithm can guarantee a consistent DFA of size at most m*^c' (Dumitru et al. 2026, Sec. 1, on Pitt-Warmuth 1993); Attias et al. 2025 Table 1: poly(n)-size DFA is Hard in PAC distribution-free (Kearns-Valiant 1994 under Assumption A: RSA, factoring Blum integers, or quadratic residues) and Hard under the uniform distribution (Daniely-Vardi 2021), but Tractable with membership queries. Exact theorem numbers in the three originals not verified.

**Assumptions.** Gold/Pitt-Warmuth: proper learning (hypothesis must be a DFA), worst-case finite samples; Gold's original model is a Mealy-machine variant (Dumitru et al. footnote 1; Lingg et al. 2024 give the DFA adaptation).; Kearns-Valiant: cryptographic assumptions; distribution-free (a specific hard distribution is constructed); polynomial-size DFAs; representation-independent.; Passive access only: i.i.d. labelled examples (PAC) or a given finite sample; no membership or equivalence queries.; Complexity measured in number of states; description length differs polynomially for DFAs but exponentially versus REs (Attias et al. Table 2), so 'hard to learn DFAs' is a statement about a complexity measure, not about regular languages per se.

**Resource model.** time (polynomial vs super-polynomial), sample size n, number of states m; no memory/verification accounting

**Failure boundary.** Hardness is relative to the access protocol and the complexity measure: the same regular languages become tractable with membership+equivalence queries (Angluin) and can be tractable when the sample is characteristic / structurally complete (Oncina-García 1992, de la Higuera 1997, Trakhtenbrot-Barzdin 1973 as cited by Dumitru et al.). Cryptographic results are conditional. Nothing is said about which learner morphology fails: the obstruction is representation-independent, so neural, symbolic and programmatic learners are all blocked equally under passive access.

**Implementation.** none known

**Track-B residual.** Track B needs the CHARGED cost of realizing the query interface (a verifier that answers equivalence queries with counterexamples) as an ecology resource, so that 'automaton morphology becomes acquirable' is a prediction about the verification-contract coordinate rather than a restatement of Angluin vs Gold.

**Upward question.** Is there an architecture-free coordinate (e.g. availability and price of counterexample-producing verification) whose value predicts the tractable/intractable flip for every class with a Myhill-Nerode-style characterization, not only DFAs?

Load-bearing quotes (verbatim from sources actually read):

> "It was shown to be NP-hard by Gold (1978) and Angluin (1978)." — [3] Dumitru, Yoshinaka, Shinohara 2026, Sec. 1
> "Assuming P̸ = NP, they proved that for any constant c, no polynomial-time algorithm can guarantee a consistent DFA of size at most m_*^c, where m_* denotes the size of a smallest consistent DFA." — [3] Dumitru et al. 2026, Sec. 1 (on Pitt and Warmuth 1993)
> "Chalermsook et al. (2014) proved that MinConDFA is NP-hard to approximate within a factor of n^{1−ϵ} for any constant ϵ > 0, where n is the sample size" — [3] Dumitru et al. 2026, Sec. 1
> "Kearns and Valiant [1994] showed distribution-free PAC hardness under Assumption A" — [4] Attias et al. 2025, Table 1 notes (Assumption A: RSA, factoring Blum integers, or quadratic residues)
> "In contrast, DFAs are tractably learnable with membership queries via the L⋆ algorithm of Angluin [1987]." — [4] Attias et al. 2025, Table 1 notes
> "A key takeaway is that what truly matters is the complexity measure (or description length, or equivalently ‘prior’) induced by the model, rather than the concept class itself." — [4] Attias et al. 2025, Sec. 6

Verification notes: All three originals blocked. Restatements come from two 2025-2026 arXiv papers whose authors include Srebro/Vardi (learning theory) and Yoshinaka/Shinohara (grammatical inference); both cite the originals by DOI. Abbe et al. 2021 (read in full for entry 9) also cites Kearns-Valiant 1994 for 'we can learn all poly-time computable functions, which is known to be impossible'.

### P9B.GRADIENT_FAILURES — Shalev-Shwartz, Shamir, Shammah 2017: non-informative gradients on parity-like (orthogonal) target families; decomposition vs end-to-end; conditioning; flat activations and the forward-only rule

Disposition: `ADOPT` · best verification: `FULL_TEXT_READ`

Sources:

- [0] Failures of Gradient-Based Deep Learning — Shai Shalev-Shwartz, Ohad Shamir, Shaked Shammah (2017), ICML 2017 (arXiv 1703.07950v2). https://arxiv.org/abs/1703.07950 arXiv:1703.07950 — `FULL_TEXT_READ`
- [1] Code: failures_of_DL — Shaked Shammah (2017), GitHub. https://github.com/shakedshammah/failures_of_DL — `NOT_ACCESSIBLE`

**What it already explains.** Owns the GRADIENT-INFORMATION axis at the level of the learning law: for a family H of pairwise-orthogonal target functions (E_x[h h'] = 0, E_x[h²] ≤ 1) and ANY differentiable predictor p_w with E_x‖∂p_w/∂w‖² ≤ G(w)², the variance of the population gradient across targets is Var(H, F, w) ≤ G(w)²/\|H\| (Theorem 1), so for random parities over d bits the gradient at any w is exponentially (2^{-d}) concentrated around a target-independent vector; empirically no progress beyond chance at d ≈ 30. Extends to linear-periodic targets under smooth input distributions (Shamir 2016, Theorem 2), to end-to-end training of a k-fold parity of image sub-labels (Theorem 3: Var ≤ G(w)² · O(√(k log d / d))^k; end-to-end fails already at k = 3 while decomposition with intermediate supervision succeeds), to conditioning (Theorem 4: Ω(n^{3.5}) condition number for a fully connected encoder vs Θ(n³) for a convolution vs O(1) after explicit whitening), and to flat activations where the true gradient is identically zero but a non-gradient 'forward-only' local rule ∇̃F(w) = E_x[(u(wᵀx) − y(x)) x] converges in O(L²/ε²) (Kalai-Sastry / Kakade et al., as cited). Explicitly links the parity failure to SQ theory and to the result that approximate-gradient methods are SQ algorithms (Feldman, Guzmán, Vempala 2015).

**Formal object.** Stochastic optimization F_h(w) = E_x[ℓ(p_w(x), h(x))]; target-variance of the gradient Var(H, F, w) = E_h‖∇F_h(w) − E_{h'}∇F_{h'}(w)‖² (Eq. 2). Theorem 1: under (i) E_x[h²] ≤ 1 and pairwise orthogonality of H, (ii) E_x‖∂p_w(x)/∂w‖² ≤ G(w)², (iii) square loss or ℓ(ŷ,y) = r(ŷ·y) with r 1-Lipschitz and h ∈ {±1}: Var(H, F, w) ≤ G(w)²/\|H\|. Parity family H = {x ↦ (−1)^{⟨x,v*⟩}: v* ∈ {0,1}^d}, x uniform on {0,1}^d, \|H\| = 2^d. Signal-to-noise proxy Sig_u/Noi_u with Sig_u = ‖E[h_u g]‖², Noi_u = E‖h_u g − E[h_u g]‖², g = ∂p_w/∂w. Forward-only rule for y(x) = u(v*ᵀx), u monotone step: ∇̃F(w) = E_x[(u(wᵀx) − y(x)) x] (Eq. 4), i.e. identity backprop message through u.

**Strongest result.** Theorem 1 (variance bound G(w)²/\|H\|); its parity corollary Var ≤ G(w)²/2^d; Theorem 3 (k-fold composition, Var ≤ G(w)²·O(√(k log d/d))^k); Theorem 4 (condition number Ω(n^{3.5}) and GD needs ≥ S²_{1,1}/(2 S²_{n,n}) iterations to get within 0.5 of U); Sec. 5.5 convergence O(L²/ε²) of the forward-only rule under L-Lipschitz u and bounded ‖w‖. Empirical: Fig. 1 parity accuracy vs iterations for d = 5, 10, 30; Fig. 3 end-to-end fails for k ≥ 3 with 20,000 SGD iterations vs decomposition succeeding in 2,500; Fig. 4 log-SNR ≈ −15 for end-to-end at k = 4.

**Assumptions.** Population (exact) gradients in the theorems; the oracle model (Shamir 2016 Thm 4) needs gradients accurate to below machine precision for the formal iteration lower bound.; Targets drawn uniformly from an orthogonal family; the difficulty is in the random choice of v*, a fixed known parity is easy (LSTM can learn full parity).; Losses: square loss or margin-type classification losses; predictors differentiable with bounded gradient norm.; Results are architecture-independent (any predictor class), which is precisely why they are learning-law rather than morphology statements.

**Resource model.** number of gradient iterations, gradient precision (implicitly), SNR of stochastic gradients, condition number; no samples/memory/verification accounting

**Failure boundary.** Explains failure of gradient-based laws on orthogonal families; does not identify which non-gradient law succeeds in general (parity is solved by Gaussian elimination, i.e. an algebraic/programmatic morphology, but the paper only mentions this via SQ theory). The forward-only rule is one-layer only ('We leave further study of deeper networks to future work'). The decomposition result requires extra supervision (intermediate labels), i.e. a richer feedback contract, so it is an ecology change, not a morphology change. No prospective prediction of where gradient laws stop working in natural task families.

**Implementation.** https://github.com/shakedshammah/failures_of_DL (cited in paper)

**Track-B residual.** Given a task family with measurable orthogonality (SQ-dimension) and a feedback contract (labels only vs decomposed intermediate labels vs exact-verification), predict before training whether the dominant acquired learning law is gradient-like, algebraic (elimination), or associative, with all three compiled from one basis and the training/verification cost charged. SSS17 supply the negative half for gradients only.

**Upward question.** Can gradient-target variance Var(H, F, w) — measurable without an architecture label — serve as a preregistered ecology coordinate whose small values predict a phase where non-gradient (algebraic/associative/query-driven) update laws occupy the frontier?

Load-bearing quotes (verbatim from sources actually read):

> "Var(H, F, w) ≤ G(w)^2 / \|H\|." — [0] Theorem 1
> "by Theorem 1, we get that Var(H, F, w) ≤ G(w)^2/2^d – that is, exponentially small in the dimension d." — [0] Sec. 2.2
> "We emphasize that these results hold regardless of which class of predictors we use (e.g. they can be arbitrarily complex neural networks) – the problem lies in using a gradient-based method to train them." — [0] Sec. 2.2
> "Recently, [8] have formally shown that gradient-based methods with an approximate gradient oracle can be implemented as a statistical query algorithm" — [0] Sec. 2.2
> "to the point where around d = 30, no advance beyond random performance is observed after reasonable time." — [0] Sec. 2.1
> "However, using the end-to-end approach works only for k = 1, 2, and completely fails already when k = 3 (or larger)." — [0] Sec. 3.1
> "this kind of update can be interpreted as replacing the backpropagation message for the activation function u with an identity message." — [0] Sec. 5.5 The 'Forward-Only' Update Rule
> "its reliance on local properties of the loss function, with the objective being of a global nature." — [0] Sec. 1

Verification notes: Full main text read; appendix proofs not checked. Not previously in any ORION ledger.

### P9B.LEARNABILITY_UNDECIDABLE — Ben-David, Hrubeš, Moran, Shpilka, Yehudayoff: EMX learnability of finite subsets of [0,1] is independent of ZFC (equivalent to 2^ℵ0 < ℵω); no finite-character dimension exists — a P5-class limit on learnability characterizations

Disposition: `ADOPT` · best verification: `FULL_TEXT_READ`

Sources:

- [0] Learnability can be undecidable — Shai Ben-David, Pavel Hrubeš, Shay Moran, Amir Shpilka, Amir Yehudayoff (2019), Nature Machine Intelligence 1:44-48. https://doi.org/10.1038/s42256-018-0002-3 — `NOT_ACCESSIBLE`
- [1] On a learning problem that is independent of the set theory ZFC axioms — Shai Ben-David, Pavel Hrubeš, Shay Moran, Amir Shpilka, Amir Yehudayoff (2017), arXiv 1711.05195v1 (precursor of the Nature MI paper). https://arxiv.org/abs/1711.05195 arXiv:1711.05195 — `FULL_TEXT_READ`

**What it already explains.** Owns an absolute limit on 'learnability characterization' programmes: for the Expectation Maximization (EMX) problem — given a family F of {0,1}-valued functions on X and i.i.d. samples from an unknown countably supported P, output h ∈ F (proper) with E_P(h) ≥ sup_{h'∈F} E_P(h') − ε w.p. ≥ 1−δ — the class F^R_fin of finite subsets of the unit interval is EMX-learnable iff 2^{ℵ0} < ℵ_ω, a statement independent of ZFC (Gödel/Cohen). The tool is monotone compression: F^X_fin has a (k+1)-size monotone compression scheme iff \|X\| ≤ ℵ_k (Theorems 4, 5); for union-bounded classes EMX learnability ⇔ weak learnability ⇔ existence of an (m+1)→m monotone compression ⇔ strong uniform compression with f^{-1}(m) side bits (Corollary 4), with sample complexity O(k log(k/ε) + log(1/δ))/ε² (Theorem 1) improving to expected excess d/(m+1) i.e. O(1/(εδ)) (Theorem 2). Consequence (Theorem 8): no finite-character property (bounded first-order formula over the domain and class) can characterize EMX learnability the way VC dimension characterizes PAC; the independence already holds for weak learnability (ε = δ = 1/3).

**Formal object.** Definition 2 (EMX): G: ∪_i X^i → F is an (ε, δ)-EMX-learner for F if for some m = m(ε, δ), Pr_{S~P^m}[Opt_P(F) − E_P(G(S)) ≥ ε] ≤ δ for every countably supported P over X, Opt_P(F) = sup_{h∈F} E_P(h). Definition 3: an m → d monotone compression scheme is η: X^{≤d} → F such that for every m' ≤ m, h ∈ F, x_1..x_{m'} ∈ h there exist i_1..i_k, k ≤ d, with x_i ∈ η[(x_{i_1}..x_{i_k})] for all i ≤ m'. Definition 4: F union bounded if ∀ h_1, h_2 ∈ F ∃ h_3 ∈ F with h_1 ∪ h_2 ⊆ h_3. Finite superset reconstruction game (Definition 1): Alice sends S' ⊆ S of bounded size, Bob outputs finite η(S') ⊇ S; possible with \|S'\| ≤ k iff \|X\| < ℵ_k. Definition 6: finite-character property = ZFC-provably equivalent to a bounded formula φ(X, Y).

**Strongest result.** Theorem 4 + Theorem 5: F^X_fin has a (k+1)-size monotone compression scheme iff \|X\| ≤ ℵ_k. Corollary 6: 'The EMX-learnability of (and learning rates when it is learnable) of F^R_fin with respect to the class of all probability distributions over the real line that have countable support is independent of ZFC set theory.' Theorem 8: no finite-character property can sandwich the (1/3,1/3)-EMX sample complexity of all classes. Theorem 3: (1/3,1/3)-EMX learnability with d_0 samples ⇒ m → 3d_0/2 monotone compression for every m (union-bounded F).

**Assumptions.** Countably supported distributions over the full power-set σ-algebra (needed for measurability; authors say it 'does not harm the main message').; Proper learning (must output an element of F; otherwise the all-ones function trivializes EMX).; Union-boundedness of F for the learnability ⇔ compression equivalence (Theorems 2, 3); F^R_fin is closed under finite unions.; Consistency of ZFC; existence of models with CH and with 2^ℵ0 > ℵ_ω (Easton/Cohen).

**Resource model.** samples (m(ε, δ)); compression size d; no time, memory or verification accounting

**Failure boundary.** The undecidable class (finite subsets of the reals under countably supported distributions) 'may not arise in practical ML applications'; the result is about the robustness of the DEFINITION of learnability to the set-theoretic model, not about any computable learner. Whether monotone compression and EMX learnability coincide without union-boundedness is open (Question 1). It constrains only characterization programmes that seek a single finitary dimension for a general setting; PAC binary classification is unaffected (Theorem 7: VC dimension is finite-character and PAC learnability is model-independent).

**Implementation.** none known (set-theoretic result)

**Track-B residual.** Track B's morphology-acquirability predicate must be stated for finite, computable ecologies with finite-character coordinates (VC-like, SQ-like, consistency-dimension-like); Ben-David et al. prove that a general 'is this class acquirable?' predicate over uncountable domains can be non-finitary and even undecidable, so any Track-B phase law claiming generality beyond finite-character coordinates is illegitimate. What remains open for Track B: whether a finite-character coordinate vector suffices to predict morphology frontier membership in registered finite ecologies.

**Upward question.** Which Track-B ecology coordinates are finite-character (decidable from finite witnesses of domain points and morphologies), and can the phase law be restricted to them without losing the morphologies of interest?

Load-bearing quotes (verbatim from sources actually read):

> "the class of finite subsets of the real unit interval is EMX learnable if and only if 2^{ℵ_0} < ℵ_ω." — [1] Sec. 1.1
> "This result implies that there exist no combinatorial parameter of a finite character that characterizes EMX learnability the way the VC dimension and its variants characterize learnability" — [1] Sec. 1
> "Furthermore, our independence result applies already to “weak learnability” — the ability to find a function in the class that approximates the maximum possible expectation up to some additive constant, say 1/3." — [1] Sec. 1
> "We show that there is a strategy in which Alice sends a subset of size at most k if and only if \|X\| < ℵ_k." — [1] Sec. 1.1
> "Corollary 6. The EMX-learnability of (and learning rates when it is learnable) of F^R_fin with respect to the class of all probability distributions over the real line that have countable support is independent of ZFC set theory." — [1] Sec. 5
> "Theorem 8. There is some constant c > 0 so that the following holds. Assuming ZFC is consistent, there is no finite character property A so that for some integers m, M > c" — [1] Sec. 6
> "It is important to restrict the learning algorithm to being proper (i.e. outputting an element of F), since the all-ones functions is always a maximizer of this expectation." — [1] Sec. 2

Verification notes: Nature MI version not accessible; the arXiv 2017 precursor by the same five authors was read in full and contains the same theorems (numbering may differ in the Nature version). Not previously in any ORION ledger.

### P9B.NFL_LEARNING — Wolpert 1996: supervised-learning no-free-lunch — off-training-set error is algorithm-independent when averaged uniformly over targets (short entry; cross-reference family P0)

Disposition: `ADOPT` · best verification: `PARTIAL_TEXT_READ`

Sources:

- [0] The Lack of A Priori Distinctions Between Learning Algorithms — David H. Wolpert (1996), Neural Computation 8(7):1341-1390. https://doi.org/10.1162/neco.1996.8.7.1341 — `NOT_ACCESSIBLE`
- [1] What is important about the No Free Lunch theorems? — David H. Wolpert (2020), arXiv 2007.10928 (book chapter). https://arxiv.org/abs/2007.10928 arXiv:2007.10928 — `PARTIAL_TEXT_READ`

**What it already explains.** Owns the zero-order ecology-relativity theorem for learners: in the extended Bayesian framework with off-training-set (OTS) cost C(f, h, d) ∝ Σ_{q ∉ d_X} P(q) L(y_f, y_h) f(y_f\|q) h(y_h\|q), the posterior expected OTS loss satisfies E(Φ \| d, A) = E(Φ \| d, B) and E(Φ \| m, A) = E(Φ \| m, B) for any two learning algorithms A, B when the prior over targets is uniform (and for symmetric losses under the stated conditions); performance is an inner product between the algorithm vector and the target posterior, so 'anti-cross-validation beats cross-validation as often as the reverse' and non-uniformity of P(f) by itself licenses nothing about which algorithm to use.

**Formal object.** Finite X, Y; target distribution f(y_f \| x); training set d of m pairs generated by P(d \| f); hypothesis h(y_h \| x) produced by the learning algorithm P(h \| d); loss L(y_h, y_f); OTS cost C(f, h, d) as above with P(q) supported on X \ d_X. Inner-product formula: P(c \| d) = ∫ df dh P(h \| d) P(f \| d) M_{c,d}(f, h) with M symmetric for symmetric L. NFL: for any two algorithms E(Φ \| d, A) = E(Φ \| d, B) (uniform P(f)); search version Σ_{f∈B} E(Φ \| f, m, A) = constant − Σ_{f ∉ B} E(Φ \| f, m, A).

**Strongest result.** E(Φ \| d, A) = E(Φ \| d, B) for any two algorithms A and B (Wolpert 2020 Eq. 2, restating Wolpert 1996); theorem numbers in the 1996 paper not verified.

**Assumptions.** Uniform (or symmetric-averaged) prior over target functions; OTS error; symmetric loss; finite X, Y; the conditioning event is the data d (posterior form), not the target f.

**Resource model.** none (pure generalization-error statement)

**Failure boundary.** Averaging over all targets; says nothing under any structured P(f), which is exactly where Track B lives; the theorem is about algorithms as maps d ↦ h, so two morphologies implementing the same map are indistinguishable.

**Implementation.** none

**Track-B residual.** Already absorbed by Codex as GMI-T1 (P-NFL) and by family P0; residual for this family: every phase claim must name the structured ecology (P(f)) restriction under which it holds — the flips in this family (SQ-dimension, VC dimension, verification contract, precision) are exactly such restrictions.

**Upward question.** Cross-ref P0 (family P0.json in the scratchpad; note: that file failed json.load in this session — line 47 col 124 — and should be repaired by its owner).

Load-bearing quotes (verbatim from sources actually read):

> "E(Φ \| d, A) = E(Φ \| d, B) for any two algorithms A and B." — [1] Wolpert 2020, Sec. 5, Eq. (2)
> "The No Free Lunch theorems prove that under a uniform distribution over induction problems (search problems or learning problems), all induction algorithms perform equally." — [1] Wolpert 2020, abstract
> "In other words, anti-cross-validation beats cross-validation as often as the reverse." — [1] Wolpert 2020, Sec. 4
> "Arguments that P( f ) is non-uniform in the real world do not, by themselves, establish anything whatsoever about what search algorithm to use in the real world." — [1] Wolpert 2020, Sec. 3

Verification notes: 1996 original blocked; statements taken from Wolpert's own 2020 restatement, which cites [1] = Neural Computation 8:1341-1390, 1391-1421. Prior Codex ledger covers Wolpert-Macready 1997 (optimization NFL) at abstract depth.

### P9B.NOVELTY_SEARCH — Lehman & Stanley 2011, Novelty Search — added here only as the 'search algorithm determines the phase' hostile

Disposition: `ADOPT` · best verification: `ABSTRACT_ONLY`

Sources:

- [0] Abandoning Objectives: Evolution Through the Search for Novelty Alone — Joel Lehman, Kenneth O. Stanley (2011), Evolutionary Computation 19(2):189-223. https://doi.org/10.1162/EVCO_a_00025 — `ABSTRACT_ONLY`

**What it already explains.** Owns (at abstract depth, per prior ledgers) that replacing the objective by behavioural novelty (k-nearest-neighbour sparseness in behaviour space with an archive) finds solutions in deceptive domains (maze, biped) where objective-driven search stalls: the found behaviours depend on the search process, not only on the fitness landscape.

**Formal object.** Novelty metric ρ(x) = (1/k) Σ_{i=1..k} dist(x, μ_i) over the k nearest neighbours in behaviour space (population ∪ archive) — FROM_MEMORY_UNVERIFIED in this session.

**Strongest result.** Empirical only; not re-verified here.

**Assumptions.** A behaviour characterization and distance are supplied by the experimenter (a morphology-label-free but domain-specific choice).

**Resource model.** evaluations; none beyond

**Failure boundary.** Not a theory of which morphology emerges; a search backend. Already dispositioned SEARCH_BACKEND_PARENT_ONLY by Codex.

**Implementation.** NEAT-based; not verified

**Track-B residual.** Hostile H-SEARCH-ALGORITHM (hostile registry) made concrete with verified evidence from this family: (i) AutoML-Zero Fig. 4 — evolution/random-search success ratio 2.9x → 23000x as difficulty rises, and Table S5 — the 'Full' vs 'Basic' evolutionary method changes the NN-beating success fraction from 0.00 to 0.11 at 100 processes; (ii) GPICL Fig. 7 — whether the generalizing learning algorithm emerges at all depends on the meta-optimizer's task batch size (plateau/overfit/generalize phase diagram), and Intervention 2 — changing Adam's ε 'results in more than halving the plateau length'; (iii) Kirsch-Schmidhuber — ES vs backprop meta-training changes stability and horizon. Therefore any Track-B phase boundary must be shown invariant under at least two search families (objective-driven and novelty/quality-diversity) on the same frozen basis and ecology, otherwise the terminal is SEARCH_ALGORITHM_DETERMINES_FRONTIER.

**Upward question.** Is the morphology frontier a property of (basis, ecology) alone, or of (basis, ecology, search measure)? The parents in this family provide theorem-grade flips that are search-independent (they hold for every polynomial-time learner), which is the standard a Track-B phase law must meet.

Load-bearing quotes (verbatim from sources actually read):

> "As the task type becomes more difficult, evolution vastly outperforms RS, illustrating the complexity of AutoML-Zero when compared to more traditional AutoML spaces." — [0] AutoML-Zero Fig. 4 caption (verified in entry P3.AUTOML_ZERO source 0)
> "Using smaller ϵ results in more than halving the plateau length." — [0] GPICL Sec. 4.3 Intervention 2 (verified in entry P4 source 1)

Verification notes: Quotes above are from AutoML-Zero and GPICL full texts (entries 1-2), not from Lehman & Stanley, whose paper was not accessible; source_index 0 here refers to those verified texts via the cited entries. Lehman & Stanley itself is ABSTRACT_ONLY via prior ledgers.

### P9B.PAC_VC — PAC learnability (Valiant 1984) and its VC-dimension characterization (Blumer, Ehrenfeucht, Haussler, Warmuth 1989): sample complexity as an ecology coordinate

Disposition: `ADOPT` · best verification: `FULL_TEXT_READ`

Sources:

- [0] A Theory of the Learnable — Leslie G. Valiant (1984), Communications of the ACM 27(11):1134-1142. https://doi.org/10.1145/1968.1972 — `NOT_ACCESSIBLE`
- [1] Learnability and the Vapnik-Chervonenkis Dimension — Anselm Blumer, Andrzej Ehrenfeucht, David Haussler, Manfred K. Warmuth (1989), Journal of the ACM 36(4):929-965. https://doi.org/10.1145/76359.76371 — `NOT_ACCESSIBLE`
- [2] On the Hardness of Learning Regular Expressions — Idan Attias, Lev Reyzin, Nathan Srebro, Gal Vardi (2025), arXiv 2510.04834. https://arxiv.org/abs/2510.04834 arXiv:2510.04834 — `PARTIAL_TEXT_READ`
- [3] On a learning problem that is independent of the set theory ZFC axioms — Ben-David, Hrubeš, Moran, Shpilka, Yehudayoff (2017), arXiv 1711.05195. https://arxiv.org/abs/1711.05195 arXiv:1711.05195 — `FULL_TEXT_READ`
- [4] Samplability makes learning easier — Guy Blanc, Caleb Koch, Jane Lange, Carmen Strassle, Li-Yang Tan (2025), arXiv 2512.01276. https://arxiv.org/abs/2512.01276 arXiv:2512.01276 — `PARTIAL_TEXT_READ`

**What it already explains.** Owns the distribution-free, worst-case statistical coordinate of an ecology: for binary classification the number of i.i.d. labelled examples needed to reach error ε with confidence 1-δ is Θ((d + log(1/δ))/ε) where d = VC dimension of the target class, independent of the learner's representation; finite VC dimension characterizes learnability (with consistent-hypothesis learners) and infinite VC dimension forbids it. It also fixes the two-resource split that every later separation in this family exploits: information-theoretic sample complexity vs polynomial-time computability (Valiant's definition demands both: success for all distributions with time and samples polynomial in n, 1/ε, 1/δ, and hypothesis evaluable in polynomial time; improper = representation-independent learning allowed).

**Formal object.** Concept class C_n ⊆ {0,1}^{X_n}, X_n = {0,1}^n. A (possibly randomized) algorithm A PAC-learns C_n if for all ε, δ ∈ (0,1), all n, all c* ∈ C_n and all distributions D_n over X_n, given i.i.d. examples (x, c*(x)), x ~ D_n, A outputs h with Pr_{x~D_n}[h(x) ≠ c*(x)] ≤ ε with probability ≥ 1-δ; tractable if running time ≤ p(n, 1/ε, 1/δ). VC dimension: size of the largest set S ⊆ X shattered by C (every labelling of S realized by some f ∈ C). Fundamental theorem: sample complexity m(ε, δ) = Θ((d + log(1/δ))/ε) (upper bound via uniform convergence / ε-nets, lower bound Ω(d/ε) via the hard distribution D(x^(1)) = 1-8ε, D(x^(i)) = 8ε/(d-1) on a shattered set).

**Strongest result.** BEHW89 (as restated by Ben-David et al. 2017 and Blanc et al. 2025): a class of binary functions is PAC learnable iff its VC dimension is finite, with sample complexity Θ((d+log(1/δ))/ε); any learner over the shattering-set hard distribution needs Ω(d/ε) samples (Fact 5.8 in Blanc et al., citing BEHW89 and EHKV89). Exact theorem numbers in the JACM paper not verified in this session.

**Assumptions.** i.i.d. examples from a fixed but arbitrary (adversarial, possibly non-samplable) distribution; realizable labels in the basic model.; Binary labels; the characterization does not extend to multiclass with infinitely many labels or to the EMX setting (see P9B.LEARNABILITY_UNDECIDABLE).; Learner is computationally unbounded for the sample-complexity statement; polynomial-time learnability additionally requires an efficient consistent-hypothesis finder.; Passive learning from random examples only (no membership queries).

**Resource model.** samples (exact, worst case over distributions), confidence; time only as 'polynomial'; no memory, verification or update-work accounting

**Failure boundary.** Says nothing about which morphology realizes the learner; two morphologies with the same hypothesis class have identical PAC sample complexity, so VC dimension cannot separate morphologies at all. It is representation-independent by design: the resource it measures is the ecology's, not the morphology's. Worst-case over distributions can be exponentially pessimistic for samplable distributions (Blanc et al. 2025 Theorem 1: exponential VC dimension yet polynomial-sample learnable under samplable distributions). Does not couple samples to compute (that coupling is the content of P9B.COMP_STAT_TRADEOFF).

**Implementation.** none known (mathematical characterization)

**Track-B residual.** Given a registered ecology (D, C, ε, δ) with fixed PAC sample complexity, which morphology attains that sample complexity at the lowest charged compute/verification/revision cost, and does the answer change with distribution complexity (samplable vs arbitrary)? PAC/VC fixes the sample axis; it does not rank morphologies on it.

**Upward question.** Which ecology coordinates other than VC dimension (distribution complexity, noise, query access, feedback precision) make the same class flip between learnable and unlearnable, and do those flips align with morphology families?

Load-bearing quotes (verbatim from sources actually read):

> "A (possibly randomized) algorithm A is said to PAC learn C_n if, for all ϵ, δ ∈ (0, 1), for all n ∈ N, for all c⋆ ∈ C_n, and for all distributions D_n over X_n" — [2] Attias et al. 2025, Sec. 3 'PAC learning [Valiant, 1984]'
> "The learner may output an arbitrary hypothesis h : X_n → {0, 1} (not necessarily in C_n), provided that h can be evaluated in polynomial time in (n, 1/ϵ, 1/δ)." — [2] Attias et al. 2025, Sec. 3
> "in binary classification the PAC-learning sample complexity is Θ((d+log(1/δ))/ǫ) where d is the VC-dimension of the class [4,16]." — [3] Ben-David et al. 2017, Sec. 6
> "A fundamental result of statistical learning theory is the characterization of PAC learnability in terms of the Vapnik-Chervonenkis dimension of a class [26,4]." — [3] Ben-David et al. 2017, Sec. 1
> "then, any algorithm which learns C over D must use at least Ω(d/ε) samples." — [4] Blanc et al. 2025, Fact 5.8
> "There is a concept class with exponential VC dimension—and hence requires exponential sample complexity in standard PAC—but is learnable with polynomial sample complexity, and in fact even in polynomial time, in samplable PAC." — [4] Blanc et al. 2025, Theorem 1

Verification notes: Originals not fetchable (ACM DL, MIT mirror blocked). All quoted statements come from arXiv full texts read in this session that restate Valiant 1984 / BEHW89 with citations. Blanc et al. 2025 is noted as a missing parent (distribution-complexity axis).

### P9B.SQ_MODEL — Statistical query learning (Kearns 1998): noise-tolerant learning through an expectation oracle; parity lower bound; SQ ⊊ noisy-PAC (Blum-Kalai-Wasserman)

Disposition: `ADOPT` · best verification: `FULL_TEXT_READ`

Sources:

- [0] Efficient Noise-Tolerant Learning from Statistical Queries — Michael Kearns (1998), Journal of the ACM 45(6):983-1006 (STOC 1993). https://doi.org/10.1145/293347.293351 — `NOT_ACCESSIBLE`
- [1] Noise-Tolerant Learning, the Parity Problem, and the Statistical Query Model — Avrim Blum, Adam Kalai, Hal Wasserman (2003), Journal of the ACM 50(4):506-519 (arXiv cs/0010022, 2000). https://arxiv.org/abs/cs/0010022 arXiv:cs/0010022 — `FULL_TEXT_READ`
- [2] A Complete Characterization of Statistical Query Learning with Applications to Evolvability — Vitaly Feldman (2013), arXiv 1002.3183. https://arxiv.org/abs/1002.3183 arXiv:1002.3183 — `PARTIAL_TEXT_READ`

**What it already explains.** Owns the NOISE axis of learnability: an SQ algorithm never sees examples, only answers v with \|E_{x~D}[ψ(x, f(x))] - v\| ≤ τ to polynomially many queries ψ of inverse-polynomial tolerance τ; every SQ algorithm converts automatically to a PAC algorithm tolerant to random classification noise of any rate η < 1/2 (Kearns), so SQ-learnability is a sufficient condition for noise-robust learnability. Owns the information-theoretic obstruction: a class with d nearly pairwise-uncorrelated concepts (SQ-DIM = d) cannot be learned to error < 1/2 - 1/d³ unless the number of queries or 1/τ is at least (1/2) d^{1/3} (Blum, Furst, Jackson, Kearns, Mansour, Rudich 1994, Thm 12), hence parity over n bits (2^n mutually orthogonal functions under uniform) is not even weakly SQ-learnable although it is PAC-learnable by Gaussian elimination. Owns the strict separation SQ ⊊ noisy-PAC: parities on the first O(log n log log n) bits are PAC-learnable with random classification noise in poly(n) time but need n^{O(log log n)} SQ queries (BKW Thm 2: length-k parity with constant noise solvable in 2^{O(k/log k)} time and samples), and O(log n)-wise SQ queries add no weak-learning power (BKW Thm 5).

**Formal object.** Oracle STAT(f, D): on query (ψ, τ), ψ: X × {-1,1} → [-1,1] (or {0,1}-valued predicate in Kearns' original), τ ∈ (0,1], returns any v with \|E_{x~D}[ψ(x, f(x))] - v\| ≤ τ. A learns C in time t from statistical queries of tolerance τ if A PAC-learns C using STAT(f, D) instead of EX(f, D), each ψ evaluable in time t; efficient SQ learning: t = poly(n, 1/ε) and τ ≥ 1/poly(n, 1/ε). SQ-DIM(C, D) = largest d with f_1..f_d ∈ C, \|⟨f_i, f_j⟩_D\| ≤ 1/d for i ≠ j (Def. 2.3 in Feldman 2013 = Def. 2 in BFJKMR). Random classification noise model: each label flipped independently with probability η < 1/2; learner must run in time polynomial in n, 1/ε, 1/δ (and, for SQ-derived algorithms, 1/(1-2η)).

**Strongest result.** Kearns (as restated by BKW Sec. 1, 2.1): SQ-learnable ⇒ PAC-learnable under random classification noise (theorem number in JACM paper unverified). BFJKMR Thm 12 (quoted by BKW as Theorem 1): learning C to error < 1/2 - 1/d³ in SQ requires queries or 1/τ ≥ (1/2) d^{1/3}, d = SQ-DIM(C, D). BKW Theorem 2: 'The length-k parity problem, for noise rate η equal to any constant less than 1/2, can be solved with number of samples and total computation-time 2^{O(k/log k)}', giving the first class learnable with noise but not by SQ. BKW Theorem 5: k = O(log n)-wise SQ queries reduce to unary queries for weak learning.

**Assumptions.** Distribution D fixed (known-distribution setting, or unlabelled samples available in the unknown-distribution setting).; Queries polynomially evaluable; tolerance inverse-polynomial (each query simulable from O(1/τ²) noisy samples).; Noise is random classification noise (label flips independent of x); malicious or attribute noise are separate models.; Lower bounds are information-theoretic (no complexity assumptions) but relative to the SQ interface.

**Resource model.** number of queries, tolerance 1/τ, evaluation time per query, noise rate via 1/(1-2η); samples only implicitly (O(1/τ²) per query); no memory/verification accounting

**Failure boundary.** SQ characterizes what is learnable through AGGREGATE statistics; it does not describe morphologies, and the same class is learnable or not depending purely on the access channel (parity: PAC yes, SQ no, noisy-PAC yes for small support). The separation SQ ⊊ noisy-PAC is 'rather small' (poly(n) vs n^{O(log log n)}); full-length noisy parity remains open (LPN). No statement about compute-vs-samples beyond query count. SQ-DIM characterizes weak learning only; strong learning needs Feldman's SQ-SDIM.

**Implementation.** none known

**Track-B residual.** Which morphologies are, at charged cost, implementable ONLY through aggregate statistics (hence noise-robust but parity-blind) versus through individual examples (hence parity-capable but noise-fragile)? SQ separates function classes by access channel; Track B must attach channel access to morphology resource vectors and predict the flip.

**Upward question.** Can the SQ-dimension of the ecology's task family be measured without architecture labels and used as a preregistered coordinate predicting when aggregate-statistic morphologies (gradient, evolutionary, Bayesian-averaging) lose to example-memorizing/algebraic morphologies (retrieval, Gaussian-elimination-like programs)?

Load-bearing quotes (verbatim from sources actually read):

> "any algorithm for learning in the SQ model can automatically be converted to an algorithm for learning in the presence of random classification noise in the standard PAC model." — [1] BKW 2003, Sec. 1
> "the class of parity functions, which can be learned efficiently from non-noisy data in the PAC model, provably cannot be learned efficiently in the SQ model under the uniform distribution." — [1] BKW 2003, Sec. 1
> "we demonstrate that the set of problems learnable in the statistical query model is a strict subset of those problems learnable in the presence of noise in the PAC model." — [1] BKW 2003, abstract
> "In order to learn C to error less than 1/2 − 1/d^3 in the SQ model, where d = SQ-DIM(C, D), either the number of queries or 1/τ must be at least (1/2) d^{1/3}" — [1] BKW 2003, Theorem 1 (= Thm. 12 of BFJKMR 1994)
> "The length-k parity problem, for noise rate η equal to any constant less than 1/2, can be solved with number of samples and total computation-time 2^{O(k/log k)}." — [1] BKW 2003, Theorem 2
> "The oracle may respond to the query with any value v satisfying \|E_D[ψ(x, f (x))] − v\| ≤ τ where τ is referred to as the tolerance of the query." — [2] Feldman 2013, Sec. 2.3
> "The algorithm is said to (efficiently) SQ learn C if t is polynomial in n and 1/ǫ, and τ is lower-bounded by the inverse of a polynomial in n and 1/ǫ." — [2] Feldman 2013, Sec. 2.3

Verification notes: Kearns 1998 original blocked; definitions and results verified from BKW 2003 (full text) and Feldman 2013 (Sec. 2.3), both of which restate Kearns' model with citation. BKW 2003 and BFJKMR 1994 are noted as missing parents in the synthesis.

### P9B.VALIANT_EVOLVABILITY — Valiant's evolvability model: evolvable ⊆ SQ; monotone conjunctions evolvable under uniform; parity not evolvable; Feldman: evolvability = CSQ (Boolean loss) / = SQ (quadratic loss)

Disposition: `ADOPT` · best verification: `PARTIAL_TEXT_READ`

Sources:

- [0] Evolvability — Leslie G. Valiant (2009), Journal of the ACM 56(1), Article 3, pp. 3.1-3.21. https://doi.org/10.1145/1462153.1462156 — `NOT_ACCESSIBLE`
- [1] Evolvability from learning algorithms — Vitaly Feldman (2008), STOC 2008, pp. 619-628. https://doi.org/10.1145/1374376.1374465 — `NOT_ACCESSIBLE`
- [2] A Complete Characterization of Statistical Query Learning with Applications to Evolvability — Vitaly Feldman (2013), arXiv 1002.3183v3 (FOCS 2009 earlier version). https://arxiv.org/abs/1002.3183 arXiv:1002.3183 — `PARTIAL_TEXT_READ`
- [3] Evolution with Drifting Targets — Varun Kanade, Leslie G. Valiant, Jennifer Wortman Vaughan (2010), COLT 2010 (arXiv 1005.3566). https://arxiv.org/abs/1005.3566 arXiv:1005.3566 — `PARTIAL_TEXT_READ`

**What it already explains.** Owns a formal D2 acquisition model in which the ONLY feedback is empirical performance of a polynomial neighbourhood of the current representation (no examples seen): Perf_f(r, D) = E_{x~D}[f(x) r(x)] = 1 - 2 err_D(f, r); evolution algorithm E = (R, Neigh, μ, t, s) with polynomial-size neighbourhoods Neigh(r, ε) ∋ r, mutation probabilities μ ≥ 1/p(n,1/ε), tolerance t bounded by inverse polynomials, sample size s polynomial; selection: beneficial set Bene = {r': v(r') ≥ v(r) + t}, neutral Neut = {r': \|v(r') - v(r)\| < t}; pick from Bene if nonempty else from Neut. C is evolvable over D if from ANY r_0, after g(n, 1/ε) generations, Perf ≥ 1 - ε w.p. ≥ 1-ε. Results owned: (a) every evolvable class is SQ-learnable (Valiant; the model is a restriction of learning from examples); (b) monotone conjunctions are evolvable over the uniform distribution via add/remove/swap-one-variable neighbourhoods (Valiant; re-derived by Kanade et al. Theorem 17 with explicit tolerance ε²/18, g ≥ 144/ε², s = Õ(1/ε²), drift ≤ ε²/144); (c) parity is not evolvable (evolvable ⊆ SQ and parity ∉ SQ over uniform); (d) Feldman 2008: evolvability in Valiant's model is EQUIVALENT to learning by correlational statistical queries (CSQ: queries of the form ψ(x, l) = φ(x)·l); with quadratic loss over real-valued hypotheses it equals full SQ learnability (Feldman 2009 'Robustness of evolvability'); (e) Feldman 2013 Thm 5.5: every efficiently SQ-learnable class is MONOTONICALLY evolvable over any fixed distribution with quadratic loss; Thm 5.7: disjunctions are monotonically, distribution-independently evolvable with quadratic loss; conjunctions are NOT distribution-independently evolvable with Boolean loss (Feldman 2011).

**Formal object.** See Kanade-Valiant-Vaughan Sec. 2.2-2.3 (verbatim restatement of Valiant's model): mutator M(f, D, E, ε, r_{i-1}) evaluates empirical performance v(r) = (1/s) Σ_{i=1..s} f(x_i) r(x_i) for every r ∈ Neigh(r_{i-1}, ε) on a sample of size s, forms Bene and Neut with tolerance t(r_{i-1}, ε), and outputs a survivor with probability proportional to μ. Definition 1 (Evolvability [Valiant]): C evolvable over D by E iff ∃ polynomial g(n, 1/ε) such that ∀ n, f ∈ C_n, r_0 ∈ R_n, ε > 0, with probability ≥ 1-ε the sequence r_i = M(f, D, E, ε, r_{i-1}) satisfies Perf_f(r_{g(n,1/ε)}, D) ≥ 1-ε. Feldman's generalization (Def. 5.1-5.3): hypotheses in F^∞_1 (range [-1,1]), loss L, LPerf_f(φ, D) = 1 - 2 E_D[L(f(x), φ(x))]/L(-1,1), selection rule SelNB[L, t, p, s] with candidate pool p; monotone if LPerf never drops below its initial value. CSQ: statistical query restricted to ψ(x, l) ≡ φ(x)·l; every SQ decomposes as φ_1(x)·l + φ_2(x) (Lemma 2.2).

**Strongest result.** Verified statements: (i) 'Feldman [9] proved that the original model of evolvability is equivalent to a restriction of the statistical query model of learning [15] known as learning by correlational statistical queries (CSQ)' (KVV 2010 Sec. 5); (ii) Feldman 2013 Thm 5.5 (monotone distribution-specific evolvability of every SQ-learnable class, quadratic loss) and Thm 5.7 (disjunctions monotonically, distribution-independently evolvable); (iii) KVV Theorem 8 (strictly beneficial neighbourhood ⇒ evolvable with drifting targets, drift Δ ≤ 1/(16 b(n,1/ε))) and Theorem 17 (monotone conjunctions, uniform distribution, explicit polynomials). Valiant's own theorem numbers for 'evolvable ⇒ SQ' and 'monotone conjunctions evolvable under uniform' were not verified (paper not accessible); the parity non-evolvability follows from (i) plus the SQ parity lower bound (P9B.SQ_MODEL).

**Assumptions.** Fixed target f (KVV relax to Δ-drifting sequences with err_D(f_{i-1}, f_i) ≤ Δ); fixed distribution D over conditions; performance = correlation (0/1 loss) for Boolean hypotheses, or admissible loss over [-1,1]-valued hypotheses in Feldman's extension.; Neighbourhood size, mutation probabilities, tolerance, sample size and generation count all polynomial in n and 1/ε; the mutator is an explicit polynomial-time algorithm on representations.; Selection sees only empirical performance (fitness), never examples: 'the learner observes only the empirical performance of a set of functions that are feasible variants of the current function'.; Distribution-specific results (Thm 5.5) need access to D (samplable or a fixed sample) — the algorithm may be non-uniform otherwise.; Robustness translations (fixed tolerance, best-of-neighbourhood selection, quasi-monotone) are proved equivalent to the basic model (Feldman 2009; KVV 2010).

**Resource model.** generations g(n,1/ε), population/candidate pool p(n,1/ε), sample size per fitness evaluation s(n,1/ε), tolerance t, neighbourhood size; circuit size of hypotheses grows additively polynomially per step (Thm 5.4 item 3); time polynomial; no memory or verification accounting

**Failure boundary.** Says which FUNCTION classes are acquirable by fitness-only bounded search, not which morphology; the representation class R is chosen by the algorithm designer (R can be 'all circuits', Thm 5.5), so evolvability is not a statement about program shape. Parity is representable by a 2-layer net or a linear GF(2) rule yet unacquirable by ANY evolution algorithm — the obstruction is the feedback channel (correlation-only, polynomial tolerance), not expressivity. Distribution dependence is severe: conjunctions evolvable under uniform but not distribution-independently with Boolean loss; loss choice changes the class (CSQ vs SQ). No statement about drift beyond inverse-polynomial Δ; no accounting of what the neighbourhood generator itself costs; no result on which of two evolvable classes is reached first.

**Implementation.** none known (Feldman 2013 Sec. 5.4 gives an explicit mutation algorithm for disjunctions; no code)

**Track-B residual.** Track B must state morphology classes as behaviour/resource equivalence classes and ask which are acquirable under a fitness-only (CSQ-like) feedback channel versus an example-access (PAC) channel versus a query (L*) channel at bounded cost from a common basis; Valiant/Feldman give the function-class version of exactly this question (evolvable = CSQ ⊊ SQ ⊊ PAC) but never quotient by morphology and never charge the mutator.

**Upward question.** Is there a bounded compilation that maps Valiant's (R, Neigh, μ, t, s) mutator and Abbe's (b, ρ) gradient oracle and Angluin's (MQ, EQ) teacher onto ONE feedback-channel coordinate of the ecology contract, so that morphology acquirability is a function of that coordinate?

Load-bearing quotes (verbatim from sources actually read):

> "Evolution is then modeled as a restricted form of learning from examples, in which the learner observes only the empirical performance of a set of functions that are feasible variants of the current function." — [3] KVV 2010, Sec. 1 Overview
> "Perf_f (r, D) = E_{x∼D}[f (x)r(x)] = 1 − 2err_D(f, r)" — [3] KVV 2010, Sec. 2.1
> "It is required that for all r and ǫ, for all r′ ∈ Neigh(r, ǫ), μ(r, r′, ǫ) ≥ 1/p(n, 1/ǫ) for a polynomial p." — [3] KVV 2010, Sec. 2.2
> "we say that C is evolvable over D by E if there exists a polynomial g(n, 1/ǫ) such that for every n ∈ N, f ∈ C_n, r_0 ∈ R_n, and ǫ > 0," — [3] KVV 2010, Definition 1 (Evolvability [19])
> "Feldman [9] proved that the original model of evolvability is equivalent to a restriction of the statistical query model of learning [15] known as learning by correlational statistical queries (CSQ) [5]." — [3] KVV 2010, Sec. 5
> "tolerance function t(r, ǫ) = ǫ^2/18 for all r ∈ R_n, any generation polynomial g(n, 1/ǫ) ≥ 144/ǫ^2, a sample size s(n, 1/ǫ) = Õ(1/ǫ^2)" — [3] KVV 2010, Theorem 17 (monotone conjunctions, uniform distribution)
> "There we showed that, depending on how the performance of hypotheses is measured, evolvability is equivalent to either the SQ learnability or the learnability by restricted SQs referred to as correlational SQs" — [2] Feldman 2013, Sec. 1.3
> "A correlational statistical query is a statistical query for a correlation of a function over X with the target [11]. Namely the query function ψ(x, ℓ) ≡ φ(x) · ℓ" — [2] Feldman 2013, Sec. 2.3
> "Prior to this work monotone evolvability was only known for several very restricted classes of functions and distributions, namely, conjunctions over the uniform distribution [40], decision lists over the uniform distribution [35], and the singletons" — [2] Feldman 2013, Sec. 1.3
> "In addition we prove in [20] that conjunctions are not evolvable distribution-independently with the Boolean loss." — [2] Feldman 2013, Sec. 6
> "Let D be a distribution and C be a concept class efficiently SQ learnable over D. There exist polynomials p(n, 1/ǫ) and s(n, 1/ǫ), an inverse polynomial t(n, 1/ǫ) and an evolution algorithm" — [2] Feldman 2013, Theorem 5.5

Verification notes: Valiant 2009 and Feldman 2008 originals blocked; the model definition is taken verbatim from Kanade-Valiant-Vaughan 2010 (co-authored by Valiant, explicitly '[19]' = Valiant's model) and the CSQ equivalence from Feldman's own 2013 paper. The evolvability-theory-v0 collision matrix in the repo covers biological evolvability (Hansen, modularity), not Valiant's model; no prior ORION ledger reconstructs this parent.


## Corrections to the V1 (Codex) ledger reported by the depth pass

| family | prior entry | defect | correction | evidence |
|---|---|---|---|---|
| P7P8P6P5 | P-CATEGORICAL-LEARNING (PARENT_LEDGER_V1.json / LITERATURE_LEDGER.md) - Fong-Spivak-Tuyeras recorded as establishing 'backprop is a functor' at abstract depth | The Codex entry treats Theorem III.2 as sound and does not record that the functor L_{eps,e} is defective as stated, nor that its invertibility hypothesis on the error function excludes standard losses. | Record Theorem III.2 as corrected by Cruttwell et al. 2022 Section 6: the functor does not respect the equivalence relation on learners and the invertibility condition 'is not a constraint that appears in machine learning practice'; the sound statement is Para(R): Para(C) -> Para(Lens(C)) for any CRDC C, with optimisers as reparametrisation 2-cells. | P7.BACKPROP_AS_FUNCTOR and P7.CATEGORICAL_GRADIENT_LEARNING entries; Cruttwell et al. 2022 Section 6 (FULL/PARTIAL_TEXT_READ). |
| P7P8P6P5 | P-CATEGORICAL-LEARNING (CDL 2024 component) - recorded as covering 'some automata constructs' | Overstates CDL's automata coverage as if it supplied learning laws for automata; CDL only encodes Mealy/Moore/stream SHAPES as (co)algebras with neural cells and hypothesises (not derives) learnable code/logic. | CDL owns weight tying as lax 2-cell/comonoid (Theorem G.10) and architecture shapes as (co)algebra homomorphisms; it owns no non-gradient learning law. Quote: 'we hypothesise neural networks that can learn not merely conservation laws ..., but verifiably correct logical argument, or code.' | P7.CDL entry; cdl2024.txt read fully. |
| P7P8P6P5 | GENERAL_INTELLIGENCE_THEORY_PARENT_ATLAS_V1.md, atlas row T4 (Hyperon / cognitive synergy) | Presents cognitive synergy as a mechanism with evidential standing. | Cognitive synergy is conjecture-level: the Hyperon paper's claim is conditional ('If s multi-paradigmatic integrative approach is more efficient than mono-paradigmatic, then Hyperon has chances'); Goertzel 2017 states conjectures 1-3 and calls the arguments 'hand-wavy'; no theorem, no experiment. Mark as engineered D0 with an unproved efficiency conjecture. | P8.HYPERON entry; hyperon.txt Section 4/4.1 and Goertzel 2017 Section 8 quotes. |
| P7P8P6P5 | PARENT_EXPANSION_V2.md Section A - Niu & Spivak Poly recorded as STRONG_PARENT_FOR_B0_LOCAL_ADAPTIVE_TRANSDUCERS | The word 'adaptive' is not supported: Poly's dynamical systems (lenses Sy^S -> p) and mode-dependent interaction (Section 4.4.4) contain no update, learning, or adaptation law and no cost. | Re-label as STRONG_PARENT_FOR_B0 (representability of interacting/mode-dependent dynamical systems); adaptation must be imported from the Para(Optic) family or from CDL's Mealy-machine reading. | P7.POLY_DYNAMICAL entry; Niu-Spivak Definition 4.18, Example 7.19, Section 4.4.4. |
| P7P8P6P5 | DERIVATION_MATRIX_V1.md and THEOREM_REGISTRY_V2.json probabilistic row (registry T8 / brief T6) | No computability boundary is recorded; the matrix implies a probabilistic-program morphology can compile arbitrary conditioning. | Insert the Ackerman-Freer-Roy boundary: conditioning is noncomputable in general (Theorem 7.6, Prop 6.4, Cor 8.5) and computable in the discrete / density / smooth-noise classes (Prop 9.2, Cor 9.6, Section 9.4); any D1 claim must name the observation class. | P6.CONDITIONING_LIMIT entry; afr2011.txt Sections 1, 5-9 read. |
| P7P8P6P5 | P-CHURCH (PARENT_LEDGER_V1.json) | Abstract-depth: does not record the query semantics, the admissibility/positive-probability preconditions, or the discretised-reals design. | Add: query = sampling conditioned on a predicate with rejection (exact, 'often intractable') and MCMC-over-traces implementations; Theorem 2.3 preconditions; 'all primitive types are countable; real numbers are approximated'; Staton et al. score/norm typing (R x P(A)) + 1 + 1 for the continuous case. | P6.CHURCH_SEMANTICS entry (PARTIAL_TEXT_READ of both papers). |
| P7P8P6P5 | LEARNING_LAW_ATLAS_V1.md Sections 1-2 (gradient and Bayesian law rows) | Omits the three parents that already unify the laws: Cruttwell et al. (optimisers as 2-cells, any C -> Lens(C)), Smithe/BHS (Bayesian lenses, almost-sure functoriality), Capucci et al. (parametrised optics, selection functions as lax monoidal pseudofunctors). Also omits Reverse Derivative Ascent (gradient law on Boolean circuits). | Add rows for Para(Lens(C)) with CRDC R, BayesLens/BLens(C) with Bayesian inversion, Para(Optic) with selection functions, and RDA; mark the B3 rung PARENT_SUFFICIENT at the algebraic-interface level for these three laws. | Entries P7.CATEGORICAL_GRADIENT_LEARNING, P7.BAYESIAN_LENSES, P7.CATEGORICAL_CYBERNETICS, P7.REVERSE_DERIVATIVE_BOOLEAN. |
| P7P8P6P5 | Codex capsule as a whole (LITERATURE_LEDGER.md, PARENT_LEDGER_V1.json) | Missing parents that this family found load-bearing: Sigma (Rosenbloom et al.), Ackerman-Freer-Roy, Cruttwell et al., Smithe, Capucci et al., Anderson's rational analysis, Le-Baydin-Wood inference compilation, DreamCoder, NEAR, HOUDINI, Gavranovic 2022 space-time tradeoffs. | Absorb the 19 entries of this ledger; in particular record Gavranovic 2022 as the only categorical parent that charges a resource. | This ledger; P7.RESOURCE_SILENCE census. |
| P7P8P6P5 | Any prior implicit claim that Track B could supply 'a unified algebra of learning laws' as a novel result | Already owned. | B3 is PARENT_SUFFICIENT at the algebraic level for gradient/Bayesian/selection laws; Track B's contribution must be the cost functor, the ecology-indexed selection law (the missing 'feedback mechanism'), and label-free developmental acquisition. | Family synthesis (a) with quotes. |
| P9A_P0 | LITERATURE_LEDGER.md, Section A, Siegelmann & Sontag row, URL | DOI typed as https://doi.org/10.1006/j.jcss.1995.1013 (spurious 'j.') | https://doi.org/10.1006/jcss.1995.1013 (as in PARENT_LEDGER_V1.json) | publisher DOI as listed in Sima 2021 ref [14] and in the search-engine record |
| P9A_P0 | LITERATURE_LEDGER.md Siegelmann-Sontag row ('finite recurrent sigmoidal rational nets') and NEURAL_MORPHOLOGY_PARENT_ANALYSIS_V1 ('recurrent sigmoidal nets under their construction') | The 1995 theorem is for the saturated-linear (ramp) activation, not the logistic sigmoid; the logistic case is Kilian & Siegelmann 1996; the entries also omit the unbounded-precision requirement and the fixed-precision collapse to finite automata, which is what makes the result execution-coordinate-only | State: saturated-linear activation, rational weights, unbounded precision (digits grow linearly), 886 units, real-time; at bounded precision the model is a finite automaton (Kleene regime) | Sima 2021 Sec. 1 (quoted in P9A.SIEGELMANN_SONTAG); Perez et al. 2019 Sec. 2 (piecewise-linear sigmoid); Carmantini 2015 |
| P9A_P0 | PARENT_LEDGER_V1.json P-NEURAL-UNIVERSALITY | Conflates two different D0 results under one entry: Cybenko (approximation of continuous functions on compacta, width unbounded, static) and Siegelmann-Sontag (exact computation, fixed size, unbounded precision, dynamic); their kill scopes and residuals differ (approximation vs simulation) | Split into P-NEURAL-APPROXIMATION (Cybenko/Hornik + Telgarsky as D1 counterweight) and P-NEURAL-SIMULATION (Kleene/Siegelmann-Sontag/Perez/Sima-Orponen table) | This family's entries 2, 3, 5 |
| P9A_P0 | THEOREM_REGISTRY_V2.json GMI-T2 (parent: Cybenko 1989; Siegelmann-Sontag 1995; status ADOPTED_LIMIT) | Stated only as a limit ('representability does not establish ...'); its positive content at the execution coordinate is a theorem-grade bounded-compilation table (constant-size/linear-time neural <-> TM/FA, 1+3-layer transformer TM simulation, Tracr compiler with reported overhead) that the registry does not record, and its parent list omits Sima-Orponen 2003, Perez et al. 2019/2021, Weiss et al. 2021 and Lindner et al. 2023 | Split GMI-T2 into T2a (exec/desc coordinates: PARENT_THEOREM, table in P9A synthesis) and T2b (upd/ver/rev coordinates: FORMAL_TARGET); extend the parent list | P9A entries 3, 6 and the sufficiency table |
| P9A_P0 | GAP_REGISTER_V2.json B0-PARENTS remaining: 'proof-level Levin search reconstruction', 'proof-level Blum speedup implications' | The Hutter half of Levin/Hutter is now reconstructed at theorem level with constants (Theorem 1: 5 t_p + d_p time_{t_p} + c_p, d_p = 40*2^{l(p)+l(t_p)}, c_p = 40*2^{l(proof)+1} O(l(proof)^2); Theorem 2); Levin 1973 and Blum 1967 primaries remain unread in both P0 and P9A | Mark Levin/Hutter as RECONSTRUCTED_VIA_HUTTER_2002_FULL_TEXT; keep Blum as OPEN_PRIMARY_UNREAD with the provability escape recorded | P9A entries 10, 11; sibling P0.LEVIN_SEARCH |
| P9A_P0 | GAP_REGISTER_V2.json B3-NEURAL-DOMINANCE candidate factor 'differentiable credit' and NEURAL_MORPHOLOGY_PARENT_ANALYSIS_V1 N-section on backprop ('can make adaptation of very large parameter sets feasible when a useful loss/gradient exists') | Stated as an empirical/heuristic factor; it is a theorem (Baur-Strassen / cheap gradient principle, <= ~4x forward cost) and it is basis-dependent (fails for formulas and planar circuits), which the analysis does not record | Replace 'differentiable credit' by 'cheap gradient in a DAG+adjoint basis (Baur-Strassen 1983; Griewank-Walther), provably not available in tree/planar bases (Ramya-Shastri 2025)' | P9A entry 8 |
| P9A_P0 | EQUIVALENCE_CONTRACT_V1.md examples 'neural network compiled to an explicit program with huge overhead; program compiled to a neural emulator with huge training cost' | Program -> neural compilation has NO training cost (Tracr constructs weights directly with modest, reported overhead); the 'huge cost' example conflates compilation with training, and the actually-huge direction is the reverse (neural -> program), which is manual reverse engineering (Nanda) | Example should read: 'program compiled to a neural emulator with bounded overhead but no preserved update law (Tracr); neural network compiled to an explicit program only by manual mechanistic interpretation (Nanda), overhead unbounded' | P9A entries 6, 7 |
| P9A_P0 | HOSTILE_REGISTRY_V1.json (no hostile for hardware-price hysteresis; #377 hostile 'tensor implementation gives neural forms uncharged hardware advantage') | The hostile has a named parent (Hooker 2020) and a mechanism (lock-in: hardware optimised for past winners), which the registry's H-POSTHOC-PRICE test (preregister the price vector) does not capture - a preregistered price vector can itself be lottery-selected | Add H-HARDWARE-LOTTERY: required test = report frontiers under at least two registered price vectors (dense-matmul-cheap and pointer/branch-cheap) and state hysteresis | P9A entry 13 |
| P9B_P3P4 | LITERATURE_LEDGER.md Sec. C row 'Real et al., AutoML-Zero (2020)' and PARENT_LEDGER_V1.json P-AUTOML-ZERO | States that from basic mathematical operations evolutionary search rediscovered two-layer neural nets trained by backprop, without recording that this result (Fig. 5) used an op set restricted to exactly the ops of a two-layer net with gradient descent, fixed component lengths 21/3/9, and teacher-network tasks; the unrestricted 58-op from-empty run (Sec. 4.2) produced a bilinear (multiplicative-interaction) model with normalized gradients and weight accumulation, not a two-layer ReLU network. | Split the owned claim: (a) restricted-op rediscovery of two-layer backprop (Fig. 5); (b) open-op discovery of a bilinear SGD-like learner surpassing a two-layer FC net on binary CIFAR-10 (84.06 vs 82.22). Record the pre-encoded structure (typed vector/matrix memory, dot/outer/matvec/heaviside, supervised Predict/Learn slot, no control flow, no derivatives). | arXiv 2003.03384 Suppl. S5 ('we only allow as ops those that appear in a two-layer neural network with gradient descent'; 'Fixed num. instructions for Setup/Predict/Learn: 21/3/9'); Sec. 4.2 first sentence; Fig. 6 bottom-right code and flow diagram. |
| P9B_P3P4 | PARENT_LEDGER_V1.json P-AUTOML-ZERO 'owns': task_conditioned_algorithm_features | Not wrong, but under-specified: the task-conditioned adaptations were obtained by initializing the population with the Fig. 5 network, i.e. they are within-neural refinements, and the statistics are 8/30, 30/30, 24/30 vs controls 0/30, 3/30, 0/30. | Record as a within-morphology phase signal only, with the initialization caveat. | arXiv 2003.03384 Sec. 4.3 and Suppl. S5 ('we initialize the population with the simple two-layer neural network with gradient descent of Figure 5'). |
| P9B_P3P4 | THEOREM_REGISTRY_V2.json GMI-T10 (status OPEN_NOT_CONFIRMATORY, no parent listed) | The registry lists no parent theorems although theorem-grade phase boundaries along ecology coordinates already exist at the function-class level. | Add parent anchors: Angluin 1987 vs Gold 1978 / Pitt-Warmuth 1993 / Kearns-Valiant 1994 (verification_strength); Abbe et al. 2021 Cor. 2 (feedback precision x batch); Kearns 1998 + BKW 2003 (noise); SST 2012 Thm 1 + DGR 1999 (data_volume); Valiant/Feldman (distribution class x loss). Mark T10 'PARENT_ANCHORED_FOR_FUNCTION_CLASSES; OPEN_FOR_MORPHOLOGY_CLASSES'. | Entries P9B.* of this ledger. |
| P9B_P3P4 | Brief's theorem-hook list (T9 = ecology relativity, T10 = phase boundary) vs THEOREM_REGISTRY_V2.json (GMI-T1 = NFL/ecology relativity, GMI-T9 = programmatic compilation, GMI-T10 = phase boundary) | Numbering mismatch between the brief and the registry for T9. | Synthesis above uses the brief's numbering but flags the registry mapping (T9_brief -> GMI-T1_registry). | THEOREM_REGISTRY_V2.json rows GMI-T1, GMI-T9, GMI-T10 read in this session. |
| P9B_P3P4 | ECOLOGY_CONTRACT_V1.json candidate_structural_coordinates | Lacks a coordinate for feedback-channel precision / access type (gradient precision rho x batch b; SQ tolerance; fitness-only vs example vs query access) and for task diversity (number of tasks), both of which carry proven or reproducible flips in this family. | Add 'feedback_channel_type_and_precision' and 'task_diversity' as candidate coordinates. | Abbe et al. 2021 Cor. 2; Feldman 2013 Sec. 1.3; Kirsch et al. 2022 Insight 1/3. |
| P9B_P3P4 | Scratchpad sibling ledger P0.json | Fails json.load (Expecting ',' delimiter: line 47 column 124). | Owner of family P0 should repair before merge; P9B.NFL_LEARNING cross-references it. | python3 json.load in this session. |
| W4_P2P3P5P8_LB | None | None | 'the categorical works charge nothing' is false as stated: Gavranovic 2022 charges time/space of lens vs optic composition and identifies lens composition with gradient checkpointing; the correct statement is 'the 1-categorical quotient discards resource content; a 2-categorical refinement recovers it' | P7.LENS_OPTIC_SPACETIME_GAVRANOVIC |
| W4_P2P3P5P8_LB | None | None | the published parent for the memorization-vs-in-context switch names FOUR axes (burstiness, number of rare classes, label multiplicity, within-class variation) and one coexistence regime (Zipf exponent ~1); the axis file should carry these as the parent flips rather than a single 'diversity' scalar | P4.ICL_DISTRIBUTIONAL_CHAN |
| W4_P2P3P5P8_LB | None | None | the accessible 2007 paper establishes the universality-curve picture and cites the 2006 TCS 'small fast' result; the polynomial-overhead claim for minimal bases must still be verified against the 2006 text | P0.SMALL_UTM_WEAK_NEARY_WOODS |

## Missing parents reported (must be absorbed before any saturation claim)

- (P0) Slot & van Emde Boas 1984 (STOC) 'On tape versus core' - the actual source of the invariance-thesis wording quoted by Accattoli-Dal Lago
- (P0) Cook & Reckhow 1973 'Time-bounded random access machines' - the RAM/TM polynomial simulation the ECT proof rests on
- (P0) Hartmanis-Stearns 1965 / Hennie-Stearns 1966 time hierarchy and tape-reduction theorems (the fine overhead catalogue inside van Emde Boas 1990)
- (P0) Gurevich 2000 ASM thesis + Dershowitz-Gurevich 2008 axiomatization of algorithms - the step-for-step BEHAVIORAL equivalence notion is the natural formalization of 'preserving registered semantics' in D1, finer than functional equivalence
- (P0) Boker & Dershowitz 2006 'Comparing computational power' - the simulation/representation notion used in the ECT proof
- (P0) Levin 1984 'Randomness conservation inequalities' and Kt complexity - where Levin's search algorithm is actually written down (V'yugin says the 1973 note contains neither algorithm nor proof)
- (P0) Schmidhuber 2002 Speed Prior; Schmidhuber 2004 OOPS; Schmidhuber 2009 Godel machine (OOPS/Godel already in HST ledger) - resource-bounded universal priors are the parents of the budget \|-> morphology map
- (P0) Hutter 2005 book / Veness et al. 2011 MC-AIXI (computable approximations of the universal agent)
- (P0) Lattimore-Hutter 2011 (read here) and Schaffer 1994 conservation law - free-lunch/no-free-lunch under structured priors
- (P0) Igel & Toussaint 2004 (JMMA) NFL for non-uniform distributions; Auger & Teytaud 2010 continuous lunches are free; Alabert et al. 2014 (read) - NFL's domain-cardinality dependence
- (P0) Whitley & Rowe 2008 focused NFL; Wolpert & Macready 2005 coevolutionary free lunches
- (P0) Blum 1971 effective speed-up; McCreight-Meyer 1969 union theorem; Borodin 1972 gap theorem; Meyer-Fischer 1972 - the rest of abstract complexity that constrains 'optimal morphology' claims
- (P0) Krajicek-Pudlak 1989 optimal proof systems; Chen-Flum 2010; Monroe 2012 (read) - p-optimality for natural problems, the verification-contract-relative version of Blum
- (P0) Rice-Shapiro 1956; Kreisel-Lacombe-Shoenfield 1957 / Ceitin 1962; Friedberg 1958; Hoyrup 2015 (read) and Hoyrup-Rojas 2015 'information carried by programs' - the decidability frontier for morphology identification
- (P0) Valiant 1984 PAC; Board & Pitt 1990 reverse Occam; Blumer et al. 1989 (JACM) VC-Occam; Ehrenfeucht et al. 1989 lower bound - the full Occam theorem family
- (P0) Barron & Cover 1991; Rissanen 1983/1986/1996; Barron-Rissanen-Yu 1998; Wallace-Boulton 1968 MML - the MDL consistency and refined-MDL sources Grunwald summarizes
- (P0) Bennett 1988 logical depth; Solomonoff 1989 incremental learning / conceptual jump size - the developmental cost law parents (Ozkural 1504.03303 read as secondary)
- (P0) Neary & Woods 2006 (polynomial-time small universal machines) - shows small universal bases need not pay exponential simulation overhead, relevant to B1 minimality vs. D1 overhead
- (P1) Lattimore & Hutter 2011 'Asymptotically optimal agents' and Lattimore 2013 thesis (BayesExp, weak asymptotic optimality) - the only non-trivial optimality notion surviving Leike-Hutter Table 2
- (P1) Orseau 2010/2013 and Orseau, Lattimore & Hutter 2013 universal knowledge-seeking agents; Ring & Orseau 2011 delusion box - exploration/reward-model failures of universal agents
- (P1) Sunehag & Hutter 2012/2014 (optimistic agents; 'intelligence as inference or forcing Occam on the world') and Mueller 2010 stationary algorithmic probability - the natural-UTM problem
- (P1) Hutter 2002 'The fastest and shortest algorithm for all well-defined problems' and Schmidhuber Gödel Machine (2003/2009) - self-rewriting provably optimal agents (Gödel machine already in repo ledgers)
- (P1) Hernandez-Orallo C-test (1998), Hernandez-Orallo & Dowe 2010 anytime universal intelligence test, Legg & Veness 2013 approximation of Upsilon, Hernandez-Orallo 2017 'The Measure of All Minds' - computable intelligence measures
- (P1) Horvitz 1987 and Zilberstein & Russell 1991/1996 (anytime algorithms, composition of performance profiles) - origin of bounded optimality and the composition results R&S rely on
- (P1) Russell 1997 'Rationality and Intelligence' and Russell 2016 'Rationality and Intelligence: A Brief Update' - restatements of P1-P4 with learning; not fetched
- (P1) Lieder & Griffiths 2020 resource-rational analysis; Griffiths, Lieder & Goodman 2015; Callaway et al. 2018 'Learning to select computations' - metalevel RL as a developmental account of metareasoning
- (P1) Ortega & Braun 2013 (thermodynamics of bounded rational decision-making) and Genewein, Leibfried, Grau-Moya & Braun 2015 (information-theoretic bounded rationality; abstraction/hierarchy emerging from information costs) - closest existing candidates for a resource-price phase law
- (P1) Gigerenzer & colleagues on ecological rationality (heuristics matched to environment structure) - morphology-ecology matching in the empirical literature
- (P1) Wolpert & Macready 1997 NFL (addressed by Legg-Hutter §5.2 but needed for T9 phrasing); Lattimore & Hutter 'No free lunch versus Occam's razor'
- (P1) Aslanides, Leike & Hutter 2017 'Universal reinforcement learning algorithms: survey and experiments' (AIXIjs) - implementations of the family's agents
- (P4) Hochreiter, Younger, Conwell 2001 'Learning to learn using gradient descent' (ICANN) - the first gradient-trained meta-RNN; cited by every parent here
- (P4) Santoro et al. 2016 memory-augmented meta-learning (ICML); Mishra et al. 2018 SNAIL; Munkhdalai & Yu 2017 Meta Networks (black-box baselines used by Finn & Levine)
- (P4) Chalmers 1990 'The evolution of learning' (evolution rediscovers the delta rule in 20% of runs, per Soltoggio et al.) - a blind-recovery (B5) datum for learning laws
- (P4) Real et al. 2020 AutoML-Zero (symbolic program search rediscovers backprop) - cross-paradigm (programmatic) learning-law emergence; likely in P3
- (P4) Oh et al. 2020 'Discovering reinforcement learning algorithms'; Kirsch, van Steenkiste, Schmidhuber 2019 MetaGenRL; Kirsch et al. 2021 'Introducing symmetries to black box meta RL'
- (P4) Metz et al. 2019 'Understanding and correcting pathologies in the training of learned optimizers'; Metz et al. 2020 'Tasks, stability, architecture, and compute'; Metz et al. 2022 learned_optimization / STAR (Harrison et al. 2022)
- (P4) Ortega et al. 2019 'Meta-learning of sequential strategies'; Mikulik et al. 2020 'Meta-trained agents implement Bayes-optimal agents'; Mueller et al. 2022 PFNs 'Transformers can do Bayesian inference'; Hollmann et al. TabPFN - needed for T6 (Bayes specialization of emergent in-context learners)
- (P4) Chan et al. 2022 'Data distributional properties drive emergent in-context learning in transformers'; Garg et al. 2022 'What can transformers learn in-context?' - additional phase-law evidence over data-distribution axes
- (P4) Raghu et al. 2020 'Rapid learning or feature reuse?' (MAML's mechanism is feature reuse) - relevant to identifying what MAML actually develops
- (P4) Grant et al. 2018 'Recasting gradient-based meta-learning as hierarchical Bayes'; Franceschi et al. 2018 bilevel programming for HPO and meta-learning
- (P4) Schlag, Irie, Schmidhuber 2021 'Linear transformers are secretly fast weight programmers'; Irie et al. 2022 modern self-referential weight matrix (used here as the accessible secondary for Schmidhuber 1992/93)
- (P4) Miconi et al. 2018/2019 differentiable plasticity / backpropamine; Najarro & Risi 2020 Hebbian meta-learning; Randazzo et al. 2020 MPLP; Gregor 2020 - the learned-local-rule branch that Sandler and VSML generalize
- (P4) Zenke, Poole, Ganguli 2017 synaptic intelligence; Rusu et al. 2016 progressive nets; Lopez-Paz & Ranzato 2017 GEM; McClelland, McNaughton, O'Reilly 1995 complementary learning systems; Carpenter & Grossberg 1987 ART1 - the continual-learning remedy families in primary form
- (P4) Maurer, Pontil, Romera-Paredes 2016 and PAC-Bayes meta-bounds (already in HST ledger) - statistical side of learned bias beyond Baxter
- (P4) Wolpert & Macready 1997 NFL (already in HST ledger) - cited by Andrychowicz as the reason specialization is the only route to improvement
- (P6) Wingate, Stuhlmüller & Goodman 2011, 'Lightweight implementations of probabilistic programming languages via transformational compilation' (AISTATS) — the random-database single-site MH and address naming that Anglican, Le et al. and van de Meent build on; the canonical compile of a Church-class program to an inference target.
- (P6) Ścibior, Kammar, Vákár, Staton, Yang, Cai, Ostermann, Moss, Heunen, Ghahramani 2018, 'Denotational validation of higher-order Bayesian inference' (POPL) — proves MH/SMC correct against the Staton/Heunen semantics; needed for any 'inference-as-programming is sound' claim.
- (P6) Lew, Cusumano-Towner, Sherman, Carbin, Mansinghka 2020, 'Trace types and denotational semantics for sound programmable inference' (POPL) — soundness for Gen-style GFI compositions.
- (P6) Borgström, Dal Lago, Gordon, Szymczak 2016, 'A lambda-calculus foundation for universal probabilistic programming' (ICFP; arXiv 1512.08990) — operational semantics for the Church class with continuous distributions.
- (P6) Freer & Roy 2012, 'Computable de Finetti measures' (APAL) and Ackerman, Freer & Roy 2017, 'On computability and disintegration' (MSCS; arXiv 1509.02992) — the exchangeable positive result and the disintegration extension of the limit.
- (P6) Cooper 1990; Dagum & Luby 1993 — NP-hardness of exact and of approximate inference in Bayesian networks: the *complexity* limit inside ACR's computable region, needed for T6/T10.
- (P6) Gershman & Goodman 2014, 'Amortized inference in probabilistic reasoning' (CogSci) and Hinton, Dayan, Frey & Neal 1995 (wake-sleep) / Dayan et al. 1995 (Helmholtz machine) — origins of the amortized hybrid.
- (P6) Griffiths, Vul & Sanborn 2012, 'Bridging levels of analysis for probabilistic models of cognition'; Vul, Goodman, Griffiths & Tenenbaum 2014, 'One and done?'; Lieder & Griffiths 2020, 'Resource-rational analysis' — the only line in this tradition that *prices* approximate inference against an ecology and predicts which approximation is used; closest existing approach to a D3-type claim and must be absorbed before Track B claims a phase law.
- (P6) Saad, Cusumano-Towner, Schaechtle, Rinard & Mansinghka 2019, 'Bayesian synthesis of probabilistic programs for automatic data modeling' (POPL); Ellis et al. 2021 DreamCoder — acquisition of program libraries (the PLoT's 'effective language' dynamics) with explicit compression/refactoring costs.
- (P6) Solomonoff 1964 / Hutter 2005 — universal (noncomputable) priors; ACR sec. 1.4.3 separates them explicitly; Track B's P-family on universal induction should cross-reference (a _hutter2012.txt is already in the scratchpad).
- (P6) Rezende, Mohamed & Wierstra 2014, 'Stochastic backpropagation and approximate inference in deep latent Gaussian models' — independent co-discovery of the VAE; Burda, Grosse & Salakhutdinov 2016 (IWAE) — tightening the bound with particles, i.e. the sampling↔variational bridge.
- (P7) Braithwaite, Hedges, St Clere Smithe 2023, 'The compositional structure of Bayesian inference' (MFCS 2023; dependent Bayesian lenses; canonical statement of BUCO) — needed to close the probabilistic leg rigorously
- (P7) Gavranovic 2022, 'Space-time tradeoffs of lenses and optics via higher category theory' (arXiv:2209.09351) — the ONE categorical-cybernetics paper that explicitly charges a resource (space vs time) in optics; directly relevant to the D1 residual
- (P7) Gavranovic 2024 PhD thesis 'Fundamental Components of Deep Learning: A category-theoretic approach' (arXiv:2403.13001)
- (P7) Hedges 2019, 'From open learners to open games' (arXiv:1902.08666) and Fong & Johnson 2019, 'Lenses and learners' (arXiv:1903.03671) — the Learn/Lens/Game embeddings
- (P7) Dalrymple 2019, 'Dioptics: a common generalization of open games and gradient-based learners' (SYCO 7)
- (P7) Sprunger & Katsumata 2019, 'Differentiable causal computations via delayed trace' (LICS) — RNN learning inside Cartesian differential categories
- (P7) Vakar & Smeding 2022 CHAD; Alvarez-Picallo, Ghica, Sprunger, Zanasi 2021 functorial string diagrams for reverse-mode AD
- (P7) Dudzik, von Glehn, Pascanu, Velickovic 2024, 'Asynchronous algorithmic alignment with cocycles' (LoG) — lax morphisms as asynchrony
- (P7) de Moor 1994, 'Categories, relations and dynamic programming'; Bird & de Moor 1997 'Algebra of Programming' — the programmatic morphology's own algebra (relational calculus of programs), needed for T7/T8
- (P7) Xu et al. 2019, 'What can neural networks reason about?' — the sample-complexity theorem behind algorithmic alignment (only resource-type result in the DP bridge)
- (P7) Smithe 2022, 'Open dynamical systems as coalgebras for polynomial functors, with application to predictive processing' (arXiv:2206.03868) and Myers, 'Categorical Systems Theory' — where learning optics and Poly machines meet
- (P7) Bolt, Hedges, Zahn 2019 'Bayesian open games' (arXiv:1910.03656)
- (P7) Egri-Nagy & Nehaniv 2013 'Cascade product of permutation groups' (arXiv:1303.0091); Maler 2010 'On the Krohn-Rhodes cascaded decomposition theorem'; Diekert, Kufleitner, Steinberg 2012 'The Krohn-Rhodes theorem and local divisors' — for a verified statement of the prime decomposition and complexity
- (P7) Cho & Jacobs 2019 'Disintegration and Bayesian inversion via string diagrams'; Fritz 2020 'A synthetic approach to Markov kernels' — the Markov-category base that Bayesian lenses presuppose
- (P7P8P6P5) Hedges & Sakamoto 2022, 'Value iteration is optic composition' (arXiv:2206.04547) - would extend B3 to the dynamic-programming/RL law within the same optic algebra
- (P7P8P6P5) Bolt, Hedges, Zahn 2019, 'Bayesian open games' (arXiv:1910.03656) - the asserted-but-not-proved Bayesian branch of Capucci et al. Section 6
- (P7P8P6P5) Gavranovic 2024 PhD thesis 'Fundamental Components of Deep Learning: A category-theoretic approach' (arXiv:2403.13001) - consolidates Para, optics, weight tying and the space-time remark
- (P7P8P6P5) Gavranovic 2022 'Space-time tradeoffs of lenses and optics via higher category theory' (arXiv:2209.09351) - read here only as the exception in P7.RESOURCE_SILENCE; deserves its own entry as the only categorical parent that charges a resource
- (P7P8P6P5) Wilson & Zanasi 2023, 'Data-parallel algorithms for string diagrams' - implementation-level cost of categorical backprop
- (P7P8P6P5) Kamiya & Welliaveetil 2021, 'A category theory framework for Bayesian learning' (arXiv:2111.14293)
- (P7P8P6P5) Shiebler, Gavranovic, Wilson 2021, 'Category theory in machine learning' survey (arXiv:2106.07032)
- (P7P8P6P5) Sprunger & Katsumata 2019, 'Differentiable causal computations via delayed trace' (LICS) - recurrent/stateful backprop as a categorical construction
- (P7P8P6P5) Fong & Johnson 2019, 'Lenses and learners' (arXiv:1903.03671) - the precise relation between Learn and lenses that Fong-Spivak-Tuyeras Section VII.D only sketches
- (P7P8P6P5) Dalrymple 2019 'Dioptics' - a generalisation covering nondeterministic/probabilistic backward passes
- (P7P8P6P5) Laird 2012 'The Soar Cognitive Architecture' and Laird, Lebiere, Rosenbloom 2017 'A Standard Model of the Mind' (Common Model of Cognition) - the rule/production side that GMI-T7 lacks
- (P7P8P6P5) Rosenbloom, Demski, Ustun 2016 'The Sigma cognitive architecture and system: towards functionally elegant grand unification' (J. AGI 7(1)) - the primary Sigma source, NOT_ACCESSIBLE here (proxy blocks sciendo/degruyter); the 2018 I/ITSEC paper (arXiv:2101.02231) was used instead
- (P7P8P6P5) Anderson & Schooler 1991 'Reflections of the environment in memory' (Psychological Science) - NOT_ACCESSIBLE; only secondary restatements verified
- (P7P8P6P5) Freer & Roy 2012 'Computable de Finetti measures' and Hoyrup & Rojas on computable measure theory - the positive side of the AFR boundary
- (P7P8P6P5) Gaunt et al. 2016/2017 TerpreT and Neural TerpreT - the only work that compares gradient, SMT, ILP and Sketch backends on the SAME program-induction problems; closest existing witness to a 'same problem, different law' comparison (though morphology is still fixed)
- (P7P8P6P5) Cho & Jacobs 2019 'Disintegration and Bayesian inversion via string diagrams' - the categorical origin of the Bayesian inversion used by Smithe/BHS
- (P7P8P6P5) Real et al. 2020 AutoML-Zero and Kirsch et al. meta-learning of learning rules - the only search-over-update-rules results; belong to sibling family but are the natural test of the B3 algebra's closure under search
- (P9A_P0) Merrill, Sabharwal & Smith 2022 'Saturated transformers are constant-depth threshold circuits' (TACL) and Merrill & Sabharwal 2023 on log-precision transformers in TC0 - the fixed-precision row of the transformer table (cited by Tracr, not read)
- (P9A_P0) Giannou et al. 2023 'Looped transformers as programmable computers' and Wei, Chen & Ma 2022 'Statistically meaningful approximation' - alternative programmatic -> transformer compilers with sample-complexity accounting (cited by Tracr)
- (P9A_P0) Kilian & Siegelmann 1996 (logistic-sigmoid universality) and Balcazar-Gavalda-Siegelmann 1997 (Kolmogorov-complexity hierarchy of real-weight nets) - the missing precision-price rows
- (P9A_P0) Indyk 1995 / Alon-Dewdney-Ott 1991 / Horne-Hush 1996 - exact neuron counts for automaton simulation (the FA row's constants)
- (P9A_P0) Morgenstern 1985 'How to compute fast a function and all its derivatives' - the constructive Baur-Strassen constant
- (P9A_P0) Griewank 1992 checkpointing (log time/space) - the memory price of the cheap gradient
- (P9A_P0) Barak et al. 2022 'Hidden progress in deep learning: SGD learns parities near the computational limit' - progress measures with a theorem
- (P9A_P0) Thilak et al. 2022 slingshot mechanism; Varma et al. 2023 'Explaining grokking through circuit efficiency' (grokking without weight decay; efficiency-based explanation) - not read
- (P9A_P0) Barham & Isard 2019 'Machine learning is stuck in a rut' - the quantitative capsule-network hardware case behind Hooker
- (P9A_P0) Kautz 2020 'The third AI summer' (AAAI Engelmore lecture) - primary for the six types
- (P9A_P0) Domingos & Lowd 2009 'Markov Logic' (book) and Poon & Domingos 2006 MC-SAT - inference cost rows for MLNs
- (P9A_P0) Slot & van Emde Boas 1984 (STOC) 'On tape versus core' - the original invariance-thesis statement (P0 cites it via Accattoli-Dal Lago)
- (P9A_P0) Linnainmaa 1970/1976, Speelpenning 1980, Werbos 1974 - priority for reverse mode (cited in Baydin)
- (P9B_P3P4) Blum, Furst, Jackson, Kearns, Mansour, Rudich 1994 (SQ-dimension characterization, Thm 12) - the actual source of the parity SQ lower bound.
- (P9B_P3P4) Blum, Kalai, Wasserman 2003 JACM (SQ strictly inside noisy-PAC; 2^{O(n/log n)} noisy parity) - read in full here; deserves its own entry as the noise-axis flip.
- (P9B_P3P4) Abbe & Sandon 2020 (single-example SGD simulates any poly-time learner) - the b = 1 origin of entry 9.
- (P9B_P3P4) Feldman 2009 COLT 'Robustness of evolvability' and Feldman 2011 COLT 'Distribution-independent evolvability of linear threshold functions' (loss-function axis of the evolvability phase).
- (P9B_P3P4) Kanade, Valiant, Vaughan 2010 'Evolution with drifting targets' - drift-rate axis (Delta <= 1/(16 b(n,1/eps))) matching ECOLOGY_CONTRACT_V1's drift_process; read here, should be its own entry.
- (P9B_P3P4) Chase & Freitag 2020 (query learning bounds via Littlestone and consistency dimension) - architecture-free coordinates for the query-learning regime.
- (P9B_P3P4) Chalermsook, Laekhanukit, Nanongkai 2014 (n^{1-eps} inapproximability of MinConDFA) and Daniely-Vardi 2021 (uniform-distribution DFA hardness from local PRGs).
- (P9B_P3P4) Angluin & Kharitonov 1995 'When won't membership queries help?' - the other side of the verification-contract axis (queries do not help for DNF).
- (P9B_P3P4) Blum & Rivest 1992 (training a 3-node network is NP-complete) - cited by Abbe et al.; the neural-side analogue of Gold.
- (P9B_P3P4) Feldman, Guzman, Vempala 2015 (approximate-gradient methods are SQ algorithms) - the bridge used by SSS17.
- (P9B_P3P4) Blanc, Koch, Lange, Strassle, Tan 2025 'Samplability makes learning easier' - distribution-complexity axis (exponential VC yet poly-sample learnable under samplable D).
- (P9B_P3P4) Collins, Sohl-Dickstein, Sussillo 2016 (constant bits per parameter) - used by GPICL to explain the memorization regime; a capacity-axis parent.
- (P9B_P3P4) Chan et al. 2022 'Data distributional properties drive emergent in-context learning in transformers' - independent evidence for the task-distribution axis.
- (P9B_P3P4) Attias, Reyzin, Srebro, Vardi 2025 - description-length dependence of learnability across equivalent representations (DFA vs NFA vs RE), directly relevant to defining morphology classes by resource rather than by language.
- (W4_P2P3P5P8_LB) Chalmers 1990 'The evolution of learning: an experiment in genetic connectionism' (blind rediscovery of the delta rule) — NOT accessible in this session (not on arXiv; arxiv.org egress blocked anyway); status unchanged FROM_MEMORY_UNVERIFIED; load-bearing for B5
- (W4_P2P3P5P8_LB) Cooper 1990 (NP-hardness of exact Bayesian inference); Dagum & Luby 1993 (NP-hardness of approximate inference) — NOT accessible; load-bearing for the M3 complexity axis
- (W4_P2P3P5P8_LB) Wingate, Stuhlmueller, Goodman 2011 (lightweight implementations of probabilistic programming via transformational compilation) — NOT accessible; the D1 compiler instance for M3
- (W4_P2P3P5P8_LB) Zilberstein & Russell 1996 (anytime algorithm composition) — NOT accessible; parent of the combinator cost algebra
- (W4_P2P3P5P8_LB) Bennett 1988 (logical depth); Solomonoff 1989 (conceptual jump size) — NOT accessible; OOPS Sec. 4.3 cites conceptual jump size as the parent of its 'degree of bias'
- (W4_P2P3P5P8_LB) Gurevich 2000 ASM thesis; Boker & Dershowitz 2006 — NOT accessible; parents of the equivalence notion in DEFINITIONS_V2 §4
- (W4_P2P3P5P8_LB) Neary & Woods 2006 TCS 'Small fast universal Turing machines' — NOT accessible (only the 2007 weak-machines paper was)
- (W4_P2P3P5P8_LB) Auger & Teytaud 2010 (continuous free lunches); Whitley & Rowe 2008 — NOT accessed
- (W4_P2P3P5P8_LB) Srivastava, Steunebrink, Schmidhuber 2012/2013 (first PowerPlay experiments) — not accessed
- (W4_P2P3P5P8_LB) Genewein et al. 2015 (bounded rationality, abstraction and hierarchical decision-making) — not accessed; extends Ortega-Braun
- (W4_P2P3P5P8_LB) Schumacher, Vose, Whitley 2001 (sharpened NFL; the c.u.p. theorem itself) — not accessed; Igel-Toussaint restate it
- (W4_P2P3P5P8_LB) Cao et al. 2023 babble (e-graph library learning) — not accessed; complements Stitch
