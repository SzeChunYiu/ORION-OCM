import SimulationV20
import PartialPostcontextV20
namespace SimulationPruningV20
open PartialContextV15 FrontierOrderV20 GuardedMapsV20
open SimulationV20 PartialPostcontextV20
universe u v w
theorem image_compose {X : Type u} {Y : Type v} {Z : Type w}
    (F : X → Option Y) (G : Y → Option Z) (S : X → Prop) (z : Z) :
    Image (compose G F) S z ↔ Image G (Image F S) z := by
  constructor
  · rintro ⟨x,hx,hz⟩
    cases hf : F x with
    | none => simp [compose,hf] at hz
    | some y => exact ⟨y,⟨x,hx,hf⟩,by simpa [compose,hf] using hz⟩
  · rintro ⟨y,⟨x,hx,hf⟩,hg⟩
    exact ⟨x,hx,by simp [compose,hf,hg]⟩
theorem word_pruning {X : Type u} {A : Type v}
    (b : PreorderSpec X) (d : X → A → Option X)
    (C S : X → Prop) (hc : Cofinal (simulationOrder b d) C S) (w : List A) :
    ∀ x, Down (simulationOrder b d) (Image (fun z => run d z w) C) x ↔
      Down (simulationOrder b d) (Image (fun z => run d z w) S) x :=
  image_down _ _ _ (word_guarded b d w) C S hc
theorem frontier_word_pruning {X : Type u} {A : Type v}
    (b : PreorderSpec X) (d : X → A → Option X)
    [DecidableRel (simulationOrder b d).le] (xs : List X) (w : List A) :
    ∀ x, Down (simulationOrder b d)
      (Image (fun z => run d z w) (fun z => z ∈ frontier (simulationOrder b d) xs)) x ↔
      Down (simulationOrder b d) (Image (fun z => run d z w) (fun z => z ∈ xs)) x :=
  word_pruning b d _ _ (frontier_cofinal (simulationOrder b d) xs) w
theorem endpoint_guarded {X : Type u} {A : Type v} {W : Type w}
    (b : PreorderSpec X) (d : X → A → Option X)
    (P : X → Prop) (k : Context X W) (hf : Guarded b k.order (valueMap P k)) :
    Guarded (simulationOrder b d) k.order (valueMap P k) := by
  intro x y hxy z hz
  exact hf x y (simulation_base b d x y hxy) z hz
def WordAttained {X : Type u} {A : Type v} {W : Type w}
    (d : X → A → Option X) (P : X → Prop) (k : Context X W)
    (word : List A) (S : X → Prop) :=
  Attained P k (Image (fun x => run d x word) S)
theorem word_attained_image {X : Type u} {A : Type v} {W : Type w}
    (d : X → A → Option X) (P : X → Prop) (k : Context X W)
    (word : List A) (S : X → Prop) (z : W) :
    WordAttained d P k word S z ↔
      Image (compose (valueMap P k) (fun x => run d x word)) S z := by
  rw [image_compose]
  exact attained_valueMap P k _ z
theorem endpoint_image_cofinal {X : Type u} {A : Type v} {W : Type w}
    (b : PreorderSpec X) (d : X → A → Option X)
    (P : X → Prop) (k : Context X W) (hf : Guarded b k.order (valueMap P k))
    (C S : X → Prop) (hc : Cofinal (simulationOrder b d) C S) (word : List A) :
    Cofinal k.order (WordAttained d P k word C) (WordAttained d P k word S) := by
  have hg := guarded_compose (simulationOrder b d) (simulationOrder b d) k.order
    (fun x => run d x word) (valueMap P k)
    (word_guarded b d word) (endpoint_guarded b d P k hf)
  have hi := image_cofinal _ _ _ hg C S hc
  simpa only [Cofinal,← word_attained_image] using hi
theorem endpoint_value_pruning {X : Type u} {A : Type v} {W : Type w}
    (b : PreorderSpec X) (d : X → A → Option X)
    (P : X → Prop) (k : Context X W) (hf : Guarded b k.order (valueMap P k))
    (C S : X → Prop) (hc : Cofinal (simulationOrder b d) C S) (word : List A) :
    ∀ z, Down k.order (WordAttained d P k word C) z ↔
      Down k.order (WordAttained d P k word S) z :=
  cofinal_down k.order _ _ (endpoint_image_cofinal b d P k hf C S hc word)
theorem endpoint_goal_pruning {X : Type u} {A : Type v} {W : Type w}
    (b : PreorderSpec X) (d : X → A → Option X)
    (P : X → Prop) (k : Context X W) (hf : Guarded b k.order (valueMap P k))
    (C S : X → Prop) (hc : Cofinal (simulationOrder b d) C S) (word : List A)
    (G : W → Prop) (hg : Upward k.order G) :
    (∃ z, WordAttained d P k word C z ∧ G z) ↔
      (∃ z, WordAttained d P k word S z ∧ G z) :=
  cofinal_goals k.order _ _ (endpoint_image_cofinal b d P k hf C S hc word) G hg
end SimulationPruningV20
