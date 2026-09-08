$( Ordinary derived-lemma projection. Variables V0 V1 V2 stand for class parameters.
   Native checking of a successor library is UNKNOWN under the frozen PREFIX pin. $)
$v V0 V1 V2 $.
cV0 $f class V0 $.
cV1 $f class V1 $.
cV2 $f class V2 $.

${
cut-h0 $e |- ( V0 C_ V1 -> ( V0 i^i V2 ) C_ V1 ) $.
ocm-cut-00 $p |- ( V0 C_ V1 -> ( V2 i^i V0 ) C_ V1 ) $= cV0 cV1 wss cV2 cV0 cin cV0 cV2 cin cV1 cV2 cV0 incom cut-h0 eqsstrid $.
$}

${
cut-h0 $e |- ( V0 i^i V1 ) = ( V1 i^i V0 ) $.
ocm-cut-01 $p |- ( V1 C_ V2 -> ( V0 i^i V1 ) C_ V2 ) $= cV1 cV2 wss cV0 cV1 cin cV1 cV0 cin cV2 cut-h0 cV1 cV0 cV2 ssinss1 eqsstrid $.
$}

${
cut-h0 $e |- ( V0 = V1 -> ( V2 \ V0 ) = ( V2 \ V1 ) ) $.
ocm-cut-02 $p |- ( V0 = V1 -> ( ( V0 \ V2 ) u. ( V2 \ V0 ) ) = ( ( V1 \ V2 ) u. ( V2 \ V1 ) ) ) $= cV0 cV1 wceq cV0 cV2 cdif cV1 cV2 cdif cV2 cV0 cdif cV2 cV1 cdif cV0 cV1 cV2 difeq1 cut-h0 uneq12d $.
$}

${
cut-h0 $e |- ( V0 = V1 -> ( V0 \ V2 ) = ( V1 \ V2 ) ) $.
ocm-cut-03 $p |- ( V0 = V1 -> ( ( V0 \ V2 ) u. ( V2 \ V0 ) ) = ( ( V1 \ V2 ) u. ( V2 \ V1 ) ) ) $= cV0 cV1 wceq cV0 cV2 cdif cV1 cV2 cdif cV2 cV0 cdif cV2 cV1 cdif cut-h0 cV0 cV1 cV2 difeq2 uneq12d $.
$}

${
cut-h0 $e |- ( V0 e. ( V1 \ V2 ) <-> ( V0 e. V1 /\ -. V0 e. V2 ) ) $.
ocm-cut-04 $p |- ( ( V0 e. ( V2 \ V1 ) \/ V0 e. ( V1 \ V2 ) ) <-> ( ( V0 e. V2 /\ -. V0 e. V1 ) \/ ( V0 e. V1 /\ -. V0 e. V2 ) ) ) $= cV0 cV2 cV1 cdif wcel cV0 cV2 wcel cV0 cV1 wcel wn wa cV0 cV1 cV2 cdif wcel cV0 cV1 wcel cV0 cV2 wcel wn wa cV0 cV2 cV1 eldif cut-h0 orbi12i $.
$}

${
cut-h0 $e |- ( V0 e. ( V1 \ V2 ) <-> ( V0 e. V1 /\ -. V0 e. V2 ) ) $.
ocm-cut-05 $p |- ( ( V0 e. ( V1 \ V2 ) \/ V0 e. ( V2 \ V1 ) ) <-> ( ( V0 e. V1 /\ -. V0 e. V2 ) \/ ( V0 e. V2 /\ -. V0 e. V1 ) ) ) $= cV0 cV1 cV2 cdif wcel cV0 cV1 wcel cV0 cV2 wcel wn wa cV0 cV2 cV1 cdif wcel cV0 cV2 wcel cV0 cV1 wcel wn wa cut-h0 cV0 cV2 cV1 eldif orbi12i $.
$}

${
cut-h0 $e |- ( ( V0 e. ( V1 \ V2 ) \/ V0 e. ( V2 \ V1 ) ) <-> ( ( V0 e. V1 /\ -. V0 e. V2 ) \/ ( V0 e. V2 /\ -. V0 e. V1 ) ) ) $.
ocm-cut-06 $p |- ( V0 e. ( ( V1 \ V2 ) u. ( V2 \ V1 ) ) <-> ( ( V0 e. V1 /\ -. V0 e. V2 ) \/ ( V0 e. V2 /\ -. V0 e. V1 ) ) ) $= cV0 cV1 cV2 cdif cV2 cV1 cdif cun wcel cV0 cV1 cV2 cdif wcel cV0 cV2 cV1 cdif wcel wo cV0 cV1 wcel cV0 cV2 wcel wn wa cV0 cV2 wcel cV0 cV1 wcel wn wa wo cV0 cV1 cV2 cdif cV2 cV1 cdif elun cut-h0 bitri $.
$}

${
cut-h0 $e |- ( V0 e. ( ( V1 \ V2 ) u. ( V2 \ V1 ) ) <-> ( V0 e. ( V1 \ V2 ) \/ V0 e. ( V2 \ V1 ) ) ) $.
cut-h1 $e |- ( V0 e. ( V1 \ V2 ) <-> ( V0 e. V1 /\ -. V0 e. V2 ) ) $.
cut-h2 $e |- ( V0 e. ( V2 \ V1 ) <-> ( V0 e. V2 /\ -. V0 e. V1 ) ) $.
ocm-cut-07 $p |- ( V0 e. ( ( V1 \ V2 ) u. ( V2 \ V1 ) ) <-> ( ( V0 e. V1 /\ -. V0 e. V2 ) \/ ( V0 e. V2 /\ -. V0 e. V1 ) ) ) $= cV0 cV1 cV2 cdif cV2 cV1 cdif cun wcel cV0 cV1 cV2 cdif wcel cV0 cV2 cV1 cdif wcel wo cV0 cV1 wcel cV0 cV2 wcel wn wa cV0 cV2 wcel cV0 cV1 wcel wn wa wo cut-h0 cV0 cV1 cV2 cdif wcel cV0 cV1 wcel cV0 cV2 wcel wn wa cV0 cV2 cV1 cdif wcel cV0 cV2 wcel cV0 cV1 wcel wn wa cut-h1 cut-h2 orbi12i bitri $.
$}

${
ocm-cut-08 $p |- ( V0 e. ( V1 /_\ V2 ) <-> V0 e. ( ( V1 \ V2 ) u. ( V2 \ V1 ) ) ) $= cV1 cV2 csymdif cV1 cV2 cdif cV2 cV1 cdif cun cV0 cV1 cV2 df-symdif eleq2i $.
$}

${
ocm-cut-09 $p |- ( V0 = ( V1 \ V2 ) -> ( V1 \ ( V1 \ V2 ) ) = ( V1 \ V0 ) ) $= cV0 cV1 cV2 cdif wceq cV1 cV0 cdif cV1 cV1 cV2 cdif cdif cV0 cV1 cV2 cdif cV1 difeq2 eqcomd $.
$}

${
ocm-cut-10 $p |- ( V0 C_ V1 -> ( V2 = ( V1 \ V0 ) -> V0 = ( V1 \ V2 ) ) ) $= cV0 cV1 wss cV2 cV1 cV0 cdif wceq cV0 cV1 cV2 cdif wceq cV0 cV2 cV1 ssdifim ex $.
$}

${
ocm-cut-11 $p |- ( ( V0 i^i V1 ) \ V2 ) = ( ( V1 i^i V0 ) \ V2 ) $= cV0 cV1 cin cV1 cV0 cin cV2 cV0 cV1 incom difeq1i $.
$}

${
cut-h0 $e |- ( V0 i^i V1 ) = ( V1 i^i V0 ) $.
ocm-cut-12 $p |- ( ( V2 i^i V1 ) u. ( V0 i^i V1 ) ) = ( ( V1 i^i V2 ) u. ( V1 i^i V0 ) ) $= cV2 cV1 cin cV1 cV2 cin cV0 cV1 cin cV1 cV0 cin cV2 cV1 incom cut-h0 uneq12i $.
$}

${
cut-h0 $e |- ( V0 i^i V1 ) = ( V1 i^i V0 ) $.
ocm-cut-13 $p |- ( ( V0 i^i V1 ) u. ( V2 i^i V1 ) ) = ( ( V1 i^i V0 ) u. ( V1 i^i V2 ) ) $= cV0 cV1 cin cV1 cV0 cin cV2 cV1 cin cV1 cV2 cin cut-h0 cV2 cV1 incom uneq12i $.
$}

${
cut-h0 $e |- ( V0 u. V1 ) = ( V1 u. V0 ) $.
ocm-cut-14 $p |- ( ( V2 u. V1 ) i^i ( V0 u. V1 ) ) = ( ( V1 u. V2 ) i^i ( V1 u. V0 ) ) $= cV2 cV1 cun cV1 cV2 cun cV0 cV1 cun cV1 cV0 cun cV2 cV1 uncom cut-h0 ineq12i $.
$}

${
cut-h0 $e |- ( V0 u. V1 ) = ( V1 u. V0 ) $.
ocm-cut-15 $p |- ( ( V0 u. V1 ) i^i ( V2 u. V1 ) ) = ( ( V1 u. V0 ) i^i ( V1 u. V2 ) ) $= cV0 cV1 cun cV1 cV0 cun cV2 cV1 cun cV1 cV2 cun cut-h0 cV2 cV1 uncom ineq12i $.
$}

${
cut-h0 $e |- ( V0 i^i V1 ) = ( V1 i^i V0 ) $.
ocm-cut-16 $p |- ( ( V2 i^i V1 ) \ ( V0 i^i V1 ) ) = ( ( V1 i^i V2 ) \ ( V1 i^i V0 ) ) $= cV2 cV1 cin cV1 cV2 cin cV0 cV1 cin cV1 cV0 cin cV2 cV1 incom cut-h0 difeq12i $.
$}

${
cut-h0 $e |- ( V0 i^i V1 ) = ( V1 i^i V0 ) $.
ocm-cut-17 $p |- ( ( V0 i^i V1 ) \ ( V2 i^i V1 ) ) = ( ( V1 i^i V0 ) \ ( V1 i^i V2 ) ) $= cV0 cV1 cin cV1 cV0 cin cV2 cV1 cin cV1 cV2 cin cut-h0 cV2 cV1 incom difeq12i $.
$}

${
ocm-cut-18 $p |- ( V0 \ ( V1 u. V2 ) ) = ( V0 \ ( V2 u. V1 ) ) $= cV1 cV2 cun cV2 cV1 cun cV0 cV1 cV2 uncom difeq2i $.
$}

${
ocm-cut-19 $p |- ( ( V0 C_ V1 /\ V2 C_ V1 ) -> ( V1 \ ( V1 \ V0 ) ) = V0 ) $= cV0 cV1 wss cV1 cV1 cV0 cdif cdif cV0 wceq cV2 cV1 wss cV0 cV1 dfss4 birani $.
$}

${
ocm-cut-20 $p |- ( ( V0 C_ V1 /\ V2 C_ V1 ) -> ( V1 \ ( V1 \ V2 ) ) = V2 ) $= cV2 cV1 wss cV1 cV1 cV2 cdif cdif cV2 wceq cV0 cV1 wss cV2 cV1 dfss4 bilani $.
$}

${
cut-h0 $e |- ( V0 C_ V1 <-> ( V1 \ ( V1 \ V0 ) ) = V0 ) $.
cut-h1 $e |- ( ( V0 C_ V1 /\ V2 C_ V1 ) -> ( V1 \ ( V1 \ V2 ) ) = V2 ) $.
ocm-cut-21 $p |- ( ( V0 C_ V1 /\ V2 C_ V1 ) -> ( ( V1 \ ( V1 \ V0 ) ) C_ ( V1 \ ( V1 \ V2 ) ) <-> V0 C_ V2 ) ) $= cV0 cV1 wss cV2 cV1 wss wa cV1 cV1 cV0 cdif cdif cV0 cV1 cV1 cV2 cdif cdif cV2 cV0 cV1 wss cV1 cV1 cV0 cdif cdif cV0 wceq cV2 cV1 wss cut-h0 birani cut-h1 sseq12d $.
$}
