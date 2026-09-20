import LTSPathsV27
import CoalgebraControlsV27
import TaskControlsV27
namespace ParentBindingsV27
open TypedPathsV11 StochasticV14
universe u v w
theorem rel_hom (A B : Type u) : RelParentV27.category.Hom A B=(A→B→Prop) := rfl
theorem rel_id (A : Type u) (a b : A) : RelParentV27.category.id A a b ↔ b=a := Iff.rfl
theorem rel_comp {A B C : Type u} (r : A→B→Prop) (s : B→C→Prop) (a : A) (c : C) :
    RelParentV27.category.comp r s a c ↔ ∃ b,r a b ∧ s b c := Iff.rfl
theorem total_hom (A B : Type u) : RelParentV27.totalCategory.Hom A B=TotalRel A B := rfl
theorem inclusion_rel {A B : Type u} (r : TotalRel A B) :
    RelParentV27.inclusion.hom r=r.relates := rfl
theorem successors {S : Type u} {A : Type v} (r : LTSCoalgebraV27.LTS S A) (s : S) (a : A) (t : S) :
    LTSCoalgebraV27.successors r s (a,t) ↔ r s a t := Iff.rfl
theorem power_map {S : Type u} {T : Type w} {A : Type v} (f : S→T) (p : (A×S)→Prop) (a : A) (t : T) :
    LTSCoalgebraV27.powerMap f p (a,t) ↔ ∃ s,p (a,s) ∧ f s=t := Iff.rfl
theorem graph_type {S : Type u} {A : Type v} (r : LTSCoalgebraV27.LTS S A) (s t : S) :
    LTSPathsV27.Graph r s t={a:A // r s a t} := rfl
theorem graph_edge {S : Type u} {T : Type w} {A : Type v}
    {r : LTSCoalgebraV27.LTS S A} {q : LTSCoalgebraV27.LTS T A} {f : S→T}
    (hf : LTSCoalgebraV27.Forward r q f) {s t : S} (e : LTSPathsV27.Graph r s t) :
    (LTSPathsV27.edge hf e).val=e.val := rfl
theorem labels_nil {S : Type u} {A : Type v} {r : LTSCoalgebraV27.LTS S A} (s : S) :
    LTSPathsV27.labels (r:=r) (.nil s)=[] := rfl
theorem labels_cons {S : Type u} {A : Type v} {r : LTSCoalgebraV27.LTS S A}
    {s t z : S} (e : LTSPathsV27.Graph r s t) (p : Path (LTSPathsV27.Graph r) t z) :
    LTSPathsV27.labels (.cons e p)=e.val::LTSPathsV27.labels p := rfl
theorem labels_append {S : Type u} {A : Type v} {r : LTSCoalgebraV27.LTS S A}
    {s t z : S} (p : Path (LTSPathsV27.Graph r) s t) (q : Path (LTSPathsV27.Graph r) t z) :
    LTSPathsV27.labels (p.append q)=LTSPathsV27.labels p ++ LTSPathsV27.labels q := by
  induction p with
  | nil => rfl
  | cons e p ih => exact congrArg (List.cons e.val) (ih q)
theorem system_hom (F : SetCoalgebraV27.SetEndo.{u}) (S T : SetCoalgebraV27.System F) :
    (SetCoalgebraV27.category F).Hom S T=
      {f:S.carrier→T.carrier // ∀s,F.map f (S.step s)=T.step (f s)} := rfl
theorem system_id (F : SetCoalgebraV27.SetEndo.{u}) (S : SetCoalgebraV27.System F) :
    ((SetCoalgebraV27.category F).id S).val=id := rfl
theorem system_comp {F : SetCoalgebraV27.SetEndo.{u}} {S T U : SetCoalgebraV27.System F}
    (f : SetCoalgebraV27.Hom F S T) (g : SetCoalgebraV27.Hom F T U) :
    ((SetCoalgebraV27.category F).comp f g).val=g.val ∘ f.val := rfl
theorem forget_obj (F : SetCoalgebraV27.SetEndo.{u}) (S : SetCoalgebraV27.System F) :
    (SetCoalgebraV27.forget F).obj S=S.carrier := rfl
theorem forget_hom {F : SetCoalgebraV27.SetEndo.{u}} {S T : SetCoalgebraV27.System F}
    (f : SetCoalgebraV27.Hom F S T) : (SetCoalgebraV27.forget F).hom f=f.val := rfl
theorem tagged_hom (F : SetCoalgebraV27.SetEndo.{u}) (S T : SetCoalgebraV27.System F) :
    (SetCoalgebraV27.tagged F).Hom S T=(S.carrier→T.carrier) := rfl
theorem tagged_obj (F : SetCoalgebraV27.SetEndo.{u}) (S : SetCoalgebraV27.System F) :
    (SetCoalgebraV27.taggedForget F).obj S=S := rfl
theorem output_step (b : Bool) :
    (CoalgebraControlsV27.singleton b).step ()=(b,()) := rfl
end ParentBindingsV27
