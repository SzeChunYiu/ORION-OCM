import PartialPostcontextV20
namespace AttainedFrontierV20
open PartialContextV15 FrontierOrderV20 GuardedMapsV20 PartialPostcontextV20
universe u v
noncomputable def values {H : Type u} {W : Type v}
    (P : H → Prop) (k : Context H W) (hs : List H) : List W :=
  hs.filterMap (valueMap P k)
theorem values_mem {H : Type u} {W : Type v}
    (P : H → Prop) (k : Context H W) (hs : List H) (w : W) :
    w ∈ values P k hs ↔ Attained P k (fun h => h ∈ hs) w := by
  simp only [values,List.mem_filterMap,valueMap_iff,Attained]
noncomputable def attainedFrontier {H : Type u} {W : Type v}
    (P : H → Prop) (k : Context H W) [DecidableRel k.order.le]
    (hs : List H) : List W := frontier k.order (values P k hs)
theorem attained_frontier_mem {H : Type u} {W : Type v}
    (P : H → Prop) (k : Context H W) [DecidableRel k.order.le]
    (hs : List H) (w : W) :
    w ∈ attainedFrontier P k hs ↔
      Maximal k.order (Attained P k (fun h => h ∈ hs)) w := by
  simp only [attainedFrontier,frontier_mem,Maximal,values_mem]
theorem attained_frontier_cofinal {H : Type u} {W : Type v}
    (P : H → Prop) (k : Context H W) [DecidableRel k.order.le]
    (hs : List H) :
    Cofinal k.order (fun w => w ∈ attainedFrontier P k hs)
      (Attained P k (fun h => h ∈ hs)) := by
  have hc := frontier_cofinal k.order (values P k hs)
  simpa only [values_mem,attainedFrontier] using hc
theorem attained_frontier_down {H : Type u} {W : Type v}
    (P : H → Prop) (k : Context H W) [DecidableRel k.order.le]
    (hs : List H) :
    ∀ w, Down k.order (fun z => z ∈ attainedFrontier P k hs) w ↔
      Down k.order (Attained P k (fun h => h ∈ hs)) w :=
  cofinal_down k.order _ _ (attained_frontier_cofinal P k hs)
theorem attained_frontier_goals {H : Type u} {W : Type v}
    (P : H → Prop) (k : Context H W) [DecidableRel k.order.le]
    (hs : List H) (G : W → Prop) (hg : Upward k.order G) :
    (∃ w, w ∈ attainedFrontier P k hs ∧ G w) ↔
      (∃ w, Attained P k (fun h => h ∈ hs) w ∧ G w) :=
  cofinal_goals k.order _ _ (attained_frontier_cofinal P k hs) G hg
end AttainedFrontierV20
