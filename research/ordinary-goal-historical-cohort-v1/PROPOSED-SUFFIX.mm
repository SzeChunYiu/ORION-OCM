${
cut-boundary-27 $e |- ( B C_ C -> ( B i^i A ) C_ C ) $.
cut-lemma-00 $p |- ( B C_ C -> ( A i^i B ) C_ C ) $= cB cC wss cA cB cin cB cA cin cC cA cB incom cut-boundary-27 eqsstrid $.
$}
${
cut-boundary-23 $e |- ( A i^i B ) = ( B i^i A ) $.
cut-lemma-01 $p |- ( B C_ C -> ( A i^i B ) C_ C ) $= cB cC wss cA cB cin cB cA cin cC cut-boundary-23 cB cA cC ssinss1 eqsstrid $.
$}
${
cut-boundary-35 $e |- ( A = B -> ( C \ A ) = ( C \ B ) ) $.
cut-lemma-02 $p |- ( A = B -> ( ( A \ C ) u. ( C \ A ) ) = ( ( B \ C ) u. ( C \ B ) ) ) $= cA cB wceq cA cC cdif cB cC cdif cC cA cdif cC cB cdif cA cB cC difeq1 cut-boundary-35 uneq12d $.
$}
${
cut-boundary-31 $e |- ( A = B -> ( A \ C ) = ( B \ C ) ) $.
cut-lemma-03 $p |- ( A = B -> ( ( A \ C ) u. ( C \ A ) ) = ( ( B \ C ) u. ( C \ B ) ) ) $= cA cB wceq cA cC cdif cB cC cdif cC cA cdif cC cB cdif cut-boundary-31 cA cB cC difeq2 uneq12d $.
$}
${
cut-boundary-55 $e |- ( A e. ( C \ B ) <-> ( A e. C /\ -. A e. B ) ) $.
cut-lemma-04 $p |- ( ( A e. ( B \ C ) \/ A e. ( C \ B ) ) <-> ( ( A e. B /\ -. A e. C ) \/ ( A e. C /\ -. A e. B ) ) ) $= cA cB cC cdif wcel cA cB wcel cA cC wcel wn wa cA cC cB cdif wcel cA cC wcel cA cB wcel wn wa cA cB cC eldif cut-boundary-55 orbi12i $.
$}
${
cut-boundary-51 $e |- ( A e. ( B \ C ) <-> ( A e. B /\ -. A e. C ) ) $.
cut-lemma-05 $p |- ( ( A e. ( B \ C ) \/ A e. ( C \ B ) ) <-> ( ( A e. B /\ -. A e. C ) \/ ( A e. C /\ -. A e. B ) ) ) $= cA cB cC cdif wcel cA cB wcel cA cC wcel wn wa cA cC cB cdif wcel cA cC wcel cA cB wcel wn wa cut-boundary-51 cA cC cB eldif orbi12i $.
$}
${
cut-boundary-56 $e |- ( ( A e. ( B \ C ) \/ A e. ( C \ B ) ) <-> ( ( A e. B /\ -. A e. C ) \/ ( A e. C /\ -. A e. B ) ) ) $.
cut-lemma-06 $p |- ( A e. ( ( B \ C ) u. ( C \ B ) ) <-> ( ( A e. B /\ -. A e. C ) \/ ( A e. C /\ -. A e. B ) ) ) $= cA cB cC cdif cC cB cdif cun wcel cA cB cC cdif wcel cA cC cB cdif wcel wo cA cB wcel cA cC wcel wn wa cA cC wcel cA cB wcel wn wa wo cA cB cC cdif cC cB cdif elun cut-boundary-56 bitri $.
$}
${
cut-boundary-43 $e |- ( A e. ( ( B \ C ) u. ( C \ B ) ) <-> ( A e. ( B \ C ) \/ A e. ( C \ B ) ) ) $.
cut-boundary-51 $e |- ( A e. ( B \ C ) <-> ( A e. B /\ -. A e. C ) ) $.
cut-boundary-55 $e |- ( A e. ( C \ B ) <-> ( A e. C /\ -. A e. B ) ) $.
cut-lemma-07 $p |- ( A e. ( ( B \ C ) u. ( C \ B ) ) <-> ( ( A e. B /\ -. A e. C ) \/ ( A e. C /\ -. A e. B ) ) ) $= cA cB cC cdif cC cB cdif cun wcel cA cB cC cdif wcel cA cC cB cdif wcel wo cA cB wcel cA cC wcel wn wa cA cC wcel cA cB wcel wn wa wo cut-boundary-43 cA cB cC cdif wcel cA cB wcel cA cC wcel wn wa cA cC cB cdif wcel cA cC wcel cA cB wcel wn wa cut-boundary-51 cut-boundary-55 orbi12i bitri $.
$}
${
cut-lemma-08 $p |- ( A e. ( B /_\ C ) <-> A e. ( ( B \ C ) u. ( C \ B ) ) ) $= cB cC csymdif cB cC cdif cC cB cdif cun cA cB cC df-symdif eleq2i $.
$}
${
cut-lemma-09 $p |- ( B = ( V \ A ) -> ( V \ ( V \ A ) ) = ( V \ B ) ) $= cB cV cA cdif wceq cV cB cdif cV cV cA cdif cdif cB cV cA cdif cV difeq2 eqcomd $.
$}
${
cut-lemma-10 $p |- ( A C_ V -> ( B = ( V \ A ) -> A = ( V \ B ) ) ) $= cA cV wss cB cV cA cdif wceq cA cV cB cdif wceq cA cB cV ssdifim ex $.
$}
${
cut-lemma-11 $p |- ( ( B i^i A ) \ C ) = ( ( A i^i B ) \ C ) $= cB cA cin cA cB cin cC cB cA incom difeq1i $.
$}
${
cut-boundary-38 $e |- ( B i^i C ) = ( C i^i B ) $.
cut-lemma-12 $p |- ( ( A i^i C ) u. ( B i^i C ) ) = ( ( C i^i A ) u. ( C i^i B ) ) $= cA cC cin cC cA cin cB cC cin cC cB cin cA cC incom cut-boundary-38 uneq12i $.
$}
${
cut-boundary-35 $e |- ( A i^i C ) = ( C i^i A ) $.
cut-lemma-13 $p |- ( ( A i^i C ) u. ( B i^i C ) ) = ( ( C i^i A ) u. ( C i^i B ) ) $= cA cC cin cC cA cin cB cC cin cC cB cin cut-boundary-35 cB cC incom uneq12i $.
$}
${
cut-boundary-38 $e |- ( B u. C ) = ( C u. B ) $.
cut-lemma-14 $p |- ( ( A u. C ) i^i ( B u. C ) ) = ( ( C u. A ) i^i ( C u. B ) ) $= cA cC cun cC cA cun cB cC cun cC cB cun cA cC uncom cut-boundary-38 ineq12i $.
$}
${
cut-boundary-35 $e |- ( A u. C ) = ( C u. A ) $.
cut-lemma-15 $p |- ( ( A u. C ) i^i ( B u. C ) ) = ( ( C u. A ) i^i ( C u. B ) ) $= cA cC cun cC cA cun cB cC cun cC cB cun cut-boundary-35 cB cC uncom ineq12i $.
$}
${
cut-boundary-38 $e |- ( B i^i C ) = ( C i^i B ) $.
cut-lemma-16 $p |- ( ( A i^i C ) \ ( B i^i C ) ) = ( ( C i^i A ) \ ( C i^i B ) ) $= cA cC cin cC cA cin cB cC cin cC cB cin cA cC incom cut-boundary-38 difeq12i $.
$}
${
cut-boundary-35 $e |- ( A i^i C ) = ( C i^i A ) $.
cut-lemma-17 $p |- ( ( A i^i C ) \ ( B i^i C ) ) = ( ( C i^i A ) \ ( C i^i B ) ) $= cA cC cin cC cA cin cB cC cin cC cB cin cut-boundary-35 cB cC incom difeq12i $.
$}
${
cut-lemma-18 $p |- ( A \ ( B u. C ) ) = ( A \ ( C u. B ) ) $= cB cC cun cC cB cun cA cB cC uncom difeq2i $.
$}
${
cut-lemma-19 $p |- ( ( A C_ C /\ B C_ C ) -> ( C \ ( C \ A ) ) = A ) $= cA cC wss cC cC cA cdif cdif cA wceq cB cC wss cA cC dfss4 birani $.
$}
${
cut-lemma-20 $p |- ( ( A C_ C /\ B C_ C ) -> ( C \ ( C \ B ) ) = B ) $= cB cC wss cC cC cB cdif cdif cB wceq cA cC wss cB cC dfss4 bilani $.
$}
${
cut-boundary-47 $e |- ( A C_ C <-> ( C \ ( C \ A ) ) = A ) $.
cut-boundary-57 $e |- ( ( A C_ C /\ B C_ C ) -> ( C \ ( C \ B ) ) = B ) $.
cut-lemma-21 $p |- ( ( A C_ C /\ B C_ C ) -> ( ( C \ ( C \ A ) ) C_ ( C \ ( C \ B ) ) <-> A C_ B ) ) $= cA cC wss cB cC wss wa cC cC cA cdif cdif cA cC cC cB cdif cdif cB cA cC wss cC cC cA cdif cdif cA wceq cB cC wss cut-boundary-47 birani cut-boundary-57 sseq12d $.
$}
