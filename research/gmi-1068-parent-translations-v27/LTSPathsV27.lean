import LTSCoalgebraV27
import ProcessMapsV26
namespace LTSPathsV27
open TypedPathsV11 LTSCoalgebraV27 ProcessMapsV26
universe u v w
variable {S : Type u} {T : Type w} {A : Type v}
def Graph (r : LTS S A) (s t : S) := {a : A // r s a t}
theorem generator_iff (r : LTS S A) (s t : S) (a : A) :
    (∃ e : Graph r s t, e.val=a) ↔ r s a t := by
  constructor
  · rintro ⟨e,rfl⟩; exact e.property
  · intro h; exact ⟨⟨a,h⟩,rfl⟩
def labels {r : LTS S A} : {s t : S} → Path (Graph r) s t → List A
  | _,_,.nil _ => []
  | _,_,.cons e p => e.val :: labels p
variable {r : LTS S A} {q : LTS T A} {f : S → T}
def edge (hf : Forward r q f) {s t : S} (e : Graph r s t) : Graph q (f s) (f t) :=
  ⟨e.val,hf s e.val t e.property⟩
def mapPath (hf : Forward r q f) : {s t : S} → Path (Graph r) s t → Path (Graph q) (f s) (f t)
  | _,_,.nil s => .nil (f s)
  | _,_,.cons e p => .cons (edge hf e) (mapPath hf p)
theorem map_nil (hf : Forward r q f) (s : S) :
    mapPath hf (.nil s)=.nil (f s) := rfl
theorem map_cons (hf : Forward r q f) {s t u : S} (e : Graph r s t) (p : Path (Graph r) t u) :
    mapPath hf (.cons e p)=.cons (edge hf e) (mapPath hf p) := rfl
theorem map_append (hf : Forward r q f) {s t u : S} (p : Path (Graph r) s t) (z : Path (Graph r) t u) :
    mapPath hf (p.append z)=(mapPath hf p).append (mapPath hf z) := by
  induction p with
  | nil => rfl
  | cons e p ih => exact congrArg (Path.cons (edge hf e)) (ih z)
def pathMap (hf : Forward r q f) : ProcessMap (Path.category (Graph r)) (Path.category (Graph q)) where
  obj := f
  hom := mapPath hf
  id_law := map_nil hf
  comp_law := map_append hf
theorem map_labels (hf : Forward r q f) {s t : S} (p : Path (Graph r) s t) :
    labels (mapPath hf p)=labels p := by
  induction p with
  | nil => rfl
  | cons e p ih => exact congrArg (List.cons e.val) ih
theorem map_eval (hf : Forward r q f) {s t : S} (p : Path (Graph r) s t) :
    eval (Path.category (Graph q)) f (fun e => Path.single (edge hf e)) p=mapPath hf p := by
  induction p with
  | nil => rfl
  | cons e p ih => exact congrArg (Path.cons (edge hf e)) ih
theorem lift_aux (hf : Forward r q f) (hb : Back r q f) {v u : T}
    (p : Path (Graph q) v u) (s : S) (hv : f s=v) :
    ∃ t : S, ∃ z : Path (Graph r) s t, f t=u ∧ HEq (mapPath hf z) p := by
  induction p generalizing s with
  | nil v =>
    subst v
    exact ⟨s,.nil s,rfl,HEq.rfl⟩
  | @cons v v' u e p ih =>
    subst v
    obtain ⟨t,ht,he⟩ := hb s e.val v' e.property
    subst v'
    obtain ⟨z,pz,hend,hz⟩ := ih t rfl
    subst u
    have hp : mapPath hf pz=p := eq_of_heq hz
    refine ⟨z,.cons ⟨e.val,ht⟩ pz,rfl,?_⟩
    have heq : edge hf (⟨e.val,ht⟩ : Graph r s t)=e := Subtype.ext rfl
    simp only [mapPath,heq,hp]
    exact HEq.rfl
theorem lift_path (hf : Forward r q f) (hb : Back r q f) {s : S} {u : T}
    (p : Path (Graph q) (f s) u) :
    ∃ t : S, ∃ z : Path (Graph r) s t,
      (⟨f t,mapPath hf z⟩ : Sigma (fun v => Path (Graph q) (f s) v))=⟨u,p⟩ := by
  obtain ⟨t,z,he,hp⟩ := lift_aux hf hb p s rfl
  subst u
  exact ⟨t,z,congrArg (Sigma.mk (f t)) (eq_of_heq hp)⟩
end LTSPathsV27
