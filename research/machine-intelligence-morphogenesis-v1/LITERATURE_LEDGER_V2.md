# Track-B Literature Ledger V2 — primary-source depth pass (issue #377 GMI-D0)

Coverage terminal (computed by `build_parent_ledger_v2.py`, never asserted): `PARENT_COVERAGE_PARTIAL__NO_FULL_TEXT_FOR_P2_P3_P5_P8`

Depth histogram over entries (best source per entry): {"FULL_TEXT_READ": 26, "NOT_ACCESSIBLE": 1, "PARTIAL_TEXT_READ": 19}

Rule: `FULL_TEXT_READ` means the worker read the full text and every quote is verbatim from it; `PARTIAL_TEXT_READ` means sections were read; `ABSTRACT_ONLY`/`NOT_ACCESSIBLE`/`FROM_MEMORY_UNVERIFIED` entries carry no load-bearing claim in Track B until upgraded. V1 (Codex) abstract-depth records are preserved in `PARENT_LEDGER_V2.json:v1_records` and are not re-rendered here.

| #377 family | entries | full-text entries |
|---|---|---|
| P0 | 8 | 7 |
| P1 | 9 | 3 |
| P2 | 0 | 0 |
| P3 | 0 | 0 |
| P4 | 9 | 4 |
| P5 | 0 | 0 |
| P6 | 9 | 5 |
| P7 | 11 | 7 |
| P8 | 0 | 0 |


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
