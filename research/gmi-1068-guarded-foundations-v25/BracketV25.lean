import ResponsesV19
namespace BracketV25
universe u v w x
inductive Tree (O : Type u) (A : Type v) where
  | arrow : A → Tree O A
  | empty : O → Tree O A
  | seq : Tree O A → Tree O A → Tree O A
def Tree.map {O : Type u} {A : Type v} {P : Type w} {B : Type x}
    (fo : O → P) (fa : A → B) : Tree O A → Tree P B
  | .arrow a => .arrow (fa a)
  | .empty o => .empty (fo o)
  | .seq l r => .seq (l.map fo fa) (r.map fo fa)
abbrev Word (A : Type u) := A × List A
def append (x y : Word A) : Word A := (x.1,x.2 ++ y.1::y.2)
def flatten {O : Type u} {A : Type v} (unit : O → A) : Tree O A → Word A
  | .arrow a => (a,[])
  | .empty o => (unit o,[])
  | .seq l r => append (flatten unit l) (flatten unit r)
def fold (m : A → A → Option A) (w : Word A) := ResponsesV19.run m w.1 w.2
def eval {O : Type u} {A : Type v} {B : Type w}
    (m : B → B → Option B) (a : A → Option B) (e : O → Option B) :
    Tree O A → Option B
  | .arrow x => a x
  | .empty o => e o
  | .seq l r => (eval m a e l).bind (fun x => (eval m a e r).bind (m x))
def Valid {O : Type u} {A : Type v} (a : A → Prop) (e : O → Prop) : Tree O A → Prop
  | .arrow x => a x
  | .empty o => e o
  | .seq l r => Valid a e l ∧ Valid a e r
theorem flatten_arrow {O : Type u} {A : Type v} (unit : O → A) (a : A) :
    flatten unit (.arrow a)=(a,[]) := rfl
theorem flatten_empty {O : Type u} {A : Type v} (unit : O → A) (o : O) :
    flatten unit (.empty o)=(unit o,[]) := rfl
theorem flatten_seq {O : Type u} {A : Type v} (unit : O → A) (l r : Tree O A) :
    flatten unit (.seq l r)=append (flatten unit l) (flatten unit r) := rfl
theorem eval_seq {O : Type u} {A : Type v} {B : Type w}
    (m : B → B → Option B) (a : A → Option B) (e : O → Option B) (l r : Tree O A) :
    eval m a e (.seq l r)=(eval m a e l).bind (fun x => (eval m a e r).bind (m x)) := rfl
theorem map_map {O : Type u} {A : Type v} {P : Type w} {B : Type x}
    (fo : O → P) (fa : A → B) (go : P → O) (ga : B → A)
    (ho : ∀ o, go (fo o)=o) (ha : ∀ a, ga (fa a)=a) (t : Tree O A) :
    (t.map fo fa).map go ga=t := by
  induction t with
  | arrow a => simp [Tree.map,ha]
  | empty o => simp [Tree.map,ho]
  | seq l r hl hr => simp [Tree.map,hl,hr]
end BracketV25
