/-
  S1 — state-class choice law at the registered finite scope.

  Target for: HELDOUT_TRANSITION_FORMALIZATION_V1.md §3 ("frozen transition law",
  `lambda* = eta*p/2`) with the exact semantics of `full_enumeration_v1.py`
  (`_stateless_errors`, `_stateful_errors`, `build_universe`, `objective`, `search`).

  Lean 4 core only.  No `import` line: this file is self-contained.
  This is a TARGET stub: the load-bearing proofs are left as `sorry`.  The finite facts
  that a proof would rest on (the 16-table stateless facts, the explicit one-bit (0,0)
  witness, the threshold bridge) are already discharged here by `decide` / `omega`, so the
  remaining obligations are exactly the argmin argument, the two block lower bounds, and
  the structural census.

  ---------------------------------------------------------------------------
  Modelling note 1 (integerisation).  `objective` in the Python is
      J(x) = eta*((1-p)*e0/16 + p*e1/16) + lambda*state_bits          (Fraction)
  and `search` compares candidates through `_integer_coefficients`, i.e. through
      value_int(x) = a*e0 + b*e1 + c*s
  with (a,b,c) = scale*(eta(1-p)/16, eta*p/16, lambda) for a positive `scale`.
  Multiplying the objective by any fixed positive scale preserves the argmin set,
  so the argmin law can be stated over natural-number coefficients with no loss.
  The `scale` chosen in `threshold_bridge` below (16*pd*ed*ld) is NOT the lcm-derived
  `scale` of `_integer_coefficients`; it is a (possibly larger) common denominator.
  Any positive common denominator induces the same ordering, hence the same argmin.

  Modelling note 2 (what "persistent-state class" means here).  `build_universe`
  assigns `state_bits = 1` to ALL 65,536 stateful transducers, including the ones
  whose next-state table never changes the state.  So PERSISTENT_STATE is a
  syntactic tag on the second enumeration block and a cost tag in the objective;
  it is NOT the property "the candidate's behaviour uses persistent state".
  The theorems below are therefore about a cost-tagged partition of the enumeration.
  ---------------------------------------------------------------------------
-/

namespace S1E

/-- bit `i` of the truth table `t` (Python `_bit`). -/
def bit (t i : Nat) : Nat := (t >>> i) % 2

/-- the 8 binary sequences of length 3 (Python `SEQUENCES`), in some order. -/
def seqs : List (Nat × Nat × Nat) :=
  (List.range 8).map (fun n => (bit n 0, bit n 1, bit n 2))

/-- the post-search summary of a candidate: `(state_bits, error_now, error_delay)`. -/
structure Summary where
  stateBits : Nat
  errNow    : Nat
  errDelay  : Nat
deriving DecidableEq, Repr

/-- Python `_stateless_errors`: output = bit(out, 2*mode + current); scored at t = 1,2;
    target = current for mode 0, previous bit for mode 1. -/
def statelessErrors (out : Nat) : Nat × Nat :=
  seqs.foldl
    (fun acc s =>
      let s0 := s.1; let s1 := s.2.1; let s2 := s.2.2
      let e0 := (if bit out (2 * 0 + s1) = s1 then 0 else 1)
              + (if bit out (2 * 0 + s2) = s2 then 0 else 1)
      let e1 := (if bit out (2 * 1 + s1) = s0 then 0 else 1)
              + (if bit out (2 * 1 + s2) = s1 then 0 else 1)
      (acc.1 + e0, acc.2 + e1))
    (0, 0)

/-- Python `_stateful_errors`, one mode: state starts at 0, index = 4*state + 2*mode + current,
    t = 0 is unscored, t = 1,2 are scored. -/
def statefulErrorsMode (nxt out mode : Nat) : Nat :=
  seqs.foldl
    (fun acc s =>
      let s0 := s.1; let s1 := s.2.1; let s2 := s.2.2
      let i0 := 4 * 0 + 2 * mode + s0
      let st1 := bit nxt i0
      let i1 := 4 * st1 + 2 * mode + s1
      let t1 := if mode = 0 then s1 else s0
      let e1 := if bit out i1 = t1 then 0 else 1
      let st2 := bit nxt i1
      let i2 := 4 * st2 + 2 * mode + s2
      let t2 := if mode = 0 then s2 else s1
      let e2 := if bit out i2 = t2 then 0 else 1
      acc + e1 + e2)
    0

def statefulErrors (nxt out : Nat) : Nat × Nat :=
  (statefulErrorsMode nxt out 0, statefulErrorsMode nxt out 1)

/-- the 16 stateless output tables on visible `(M,X)`. -/
def statelessBlock : List Summary :=
  (List.range 16).map (fun o =>
    let e := statelessErrors o
    { stateBits := 0, errNow := e.1, errDelay := e.2 })

/-- the 256*256 one-bit stateful transducers. -/
def statefulBlock : List Summary :=
  (List.range 256).flatMap (fun n =>
    (List.range 256).map (fun o =>
      let e := statefulErrors n o
      { stateBits := 1, errNow := e.1, errDelay := e.2 }))

/-- Python `build_universe` (candidate IDs are irrelevant to the argmin law). -/
def candidateUniverse : List Summary := statelessBlock ++ statefulBlock

/-- the integerised exact objective of `search`. -/
def J (a b c : Nat) (x : Summary) : Nat :=
  a * x.errNow + b * x.errDelay + c * x.stateBits

/-- `x` is an exhaustive argmin of the registered universe. -/
def IsArgmin (a b c : Nat) (x : Summary) : Prop :=
  x ∈ candidateUniverse ∧ ∀ y ∈ candidateUniverse, J a b c x ≤ J a b c y

/- ------------------------------------------------------------------ -/
/- Supporting finite facts (route: 16-table `decide` + two witnesses). -/
/- ------------------------------------------------------------------ -/

/-- census: 16 + 256*256 = 65552.  Provable structurally from
    `List.length_append`, `List.length_map`, `List.length_flatMap`, `List.length_range`
    — it must NOT be discharged by evaluating the 65,536 error computations. -/
theorem census : candidateUniverse.length = 65552 := by
  sorry

/-- every stateless table has delayed error exactly 8/16 = 1/2: the output depends only on
    the current bit, and for each fixed current bit the previous bit is 0 in exactly as many
    scored events as it is 1.  (Stronger than "the minimum is 8"; 16-table `decide`.) -/
theorem stateless_errDelay_const : ∀ x ∈ statelessBlock, x.errDelay = 8 := by
  decide

/-- the `(error_now, error_delay) = (0, 1/2)` stateless witness of the control list. -/
theorem stateless_witness :
    ({ stateBits := 0, errNow := 0, errDelay := 8 } : Summary) ∈ statelessBlock := by
  decide

/-- the explicit one-bit `(0,0)` witness, shipped rather than postulated:
    next-state table 170 (= 0b10101010, "copy the current bit into the state") together with
    output table 226 (= 0b11100010, "emit the current bit in immediate mode, the state in
    delayed mode") scores zero error in both modes.  Kernel-checked. -/
theorem statefulErrors_170_226 : statefulErrors 170 226 = (0, 0) := by
  decide

/-- the one-bit `(0,0)` risk witness of the control list (follows from the table above
    together with `170 ∈ List.range 256`, `226 ∈ List.range 256` and `List.mem_flatMap`). -/
theorem stateful_witness :
    ({ stateBits := 1, errNow := 0, errDelay := 0 } : Summary) ∈ statefulBlock := by
  sorry

theorem stateless_stateBits : ∀ x ∈ statelessBlock, x.stateBits = 0 := by
  decide

theorem stateful_stateBits : ∀ x ∈ statefulBlock, x.stateBits = 1 := by
  sorry

/-- best achievable value inside the stateless block is exactly `8*b`. -/
theorem stateless_lower_bound (a b c : Nat) :
    ∀ x ∈ statelessBlock, 8 * b ≤ J a b c x := by
  sorry

/-- best achievable value inside the stateful block is exactly `c`. -/
theorem stateful_lower_bound (a b c : Nat) :
    ∀ x ∈ statefulBlock, c ≤ J a b c x := by
  sorry

/- ------------------------------------------------------------------ -/
/- The choice law.                                                     -/
/- ------------------------------------------------------------------ -/

/-- S1(a): every exhaustive argmin carries the persistent-state tag iff `lambda < eta*p/2`
    (integerised: `c < 8*b`).  `0 < c` is the registered-world hypothesis `state_price > 0`
    of `objective`; the statement in fact holds without it. -/
theorem argmin_persistent_iff (a b c : Nat) (hc : 0 < c) :
    (∀ x, IsArgmin a b c x → x.stateBits = 1) ↔ c < 8 * b := by
  sorry

/-- S1(b): every exhaustive argmin is stateless iff `lambda > eta*p/2`. -/
theorem argmin_stateless_iff (a b c : Nat) (hc : 0 < c) :
    (∀ x, IsArgmin a b c x → x.stateBits = 0) ↔ 8 * b < c := by
  sorry

/-- S1(c): at `lambda = eta*p/2` both property classes are represented among the argmins
    (the registered "exact boundary tie"). -/
theorem argmin_tie_at_threshold (a b c : Nat) (hc : 0 < c) (h : c = 8 * b) :
    (∃ x, IsArgmin a b c x ∧ x.stateBits = 0) ∧ (∃ x, IsArgmin a b c x ∧ x.stateBits = 1) := by
  sorry

/- ------------------------------------------------------------------ -/
/- Bridge from the rational registered world to the integer coefficients. -/
/- ------------------------------------------------------------------ -/

/-- With `p = pn/pd`, `eta = en/ed`, `lambda = ln/ld` (positive denominators, `pn ≤ pd`),
    a common-denominator integerisation of the objective is
        a = en*(pd-pn)*ld,  b = en*pn*ld,  c = 16*ln*pd*ed
    (scale = 16*pd*ed*ld).  Under it, the integer threshold `c < 8*b` is EXACTLY the
    registered analytic law `lambda < eta*p/2`, cross-multiplied.  The positivity
    hypotheses are the side conditions of that cross-multiplication step (`lambda < eta*p/2`
    ⟺ `2*ln*pd*ed < en*pn*ld` requires `pd, ed, ld > 0`); the step itself is not formalised
    here, because Lean 4 core carries no rational field. -/
theorem threshold_bridge (pn pd en ed ln ld : Nat)
    (_hpd : 0 < pd) (_hed : 0 < ed) (_hld : 0 < ld) (_hp : pn ≤ pd)
    (_hen : 0 < en) (_hln : 0 < ln) :
    (16 * (ln * pd * ed) < 8 * (en * pn * ld)) ↔ (2 * (ln * pd * ed) < en * pn * ld) := by
  omega

/- === evaluation self-check of the encoding (scratch; NOT part of the target) === -/
#eval candidateUniverse.length                                -- 65552 (registered census)
#eval statelessBlock.length                                   -- 16
#eval statefulBlock.length                                    -- 65536
#eval statelessBlock.all (fun x => x.errDelay == 8)           -- true (delayed error ≡ 8/16)
#eval statelessBlock.contains { stateBits := 0, errNow := 0, errDelay := 8 }  -- true
#eval statefulBlock.contains { stateBits := 1, errNow := 0, errDelay := 0 }   -- true
#eval (candidateUniverse.map (fun x => (x.stateBits, x.errNow, x.errDelay))).eraseDups.length
                                                              -- 146 (registered control)
def bestBits (a b c : Nat) : List Nat :=
  let vals := candidateUniverse.map (fun x => (J a b c x, x.stateBits))
  let m := vals.foldl (fun acc v => min acc v.1) 1000000
  ((vals.filter (fun v => v.1 == m)).map (fun v => v.2)).eraseDups
#eval bestBits 3 8 63   -- c < 8b : [1]
#eval bestBits 3 8 64   -- c = 8b : [0, 1]
#eval bestBits 3 8 65   -- c > 8b : [0]
end S1E
