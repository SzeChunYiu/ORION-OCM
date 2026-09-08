${
typed-reconstruct-0.h0 $e |- ( ch -> ph ) $.
typed-reconstruct-0.h1 $e |- ( ph -> ps ) $.
typed-reconstruct-0 $p |- ( ch -> ( ph /\ ps ) ) $= wch wph wps typed-reconstruct-0.h0 wch wph wps typed-reconstruct-0.h0 typed-reconstruct-0.h1 syl jca $.
$}
${
typed-reconstruct-1.h0 $e |- ( ch -> ps ) $.
typed-reconstruct-1.h1 $e |- ( ps -> ph ) $.
typed-reconstruct-1 $p |- ( ch -> ( ps /\ ph ) ) $= wch wps wph typed-reconstruct-1.h0 wch wps wph typed-reconstruct-1.h0 typed-reconstruct-1.h1 syl jca $.
$}
${
typed-reconstruct-2.h0 $e |- ( ph -> ch ) $.
typed-reconstruct-2.h1 $e |- ( ch -> ps ) $.
typed-reconstruct-2 $p |- ( ph -> ( ch /\ ps ) ) $= wph wch wps typed-reconstruct-2.h0 wph wch wps typed-reconstruct-2.h0 typed-reconstruct-2.h1 syl jca $.
$}
${
typed-reconstruct-3.h0 $e |- ( ph -> ps ) $.
typed-reconstruct-3.h1 $e |- ( ps -> ch ) $.
typed-reconstruct-3 $p |- ( ph -> ( ps /\ ch ) ) $= wph wps wch typed-reconstruct-3.h0 wph wps wch typed-reconstruct-3.h0 typed-reconstruct-3.h1 syl jca $.
$}
${
typed-reconstruct-4.h0 $e |- ( ps -> ch ) $.
typed-reconstruct-4.h1 $e |- ( ch -> ph ) $.
typed-reconstruct-4 $p |- ( ps -> ( ch /\ ph ) ) $= wps wch wph typed-reconstruct-4.h0 wps wch wph typed-reconstruct-4.h0 typed-reconstruct-4.h1 syl jca $.
$}
${
typed-reconstruct-5.h0 $e |- ( ps -> ph ) $.
typed-reconstruct-5.h1 $e |- ( ph -> ch ) $.
typed-reconstruct-5 $p |- ( ps -> ( ph /\ ch ) ) $= wps wph wch typed-reconstruct-5.h0 wps wph wch typed-reconstruct-5.h0 typed-reconstruct-5.h1 syl jca $.
$}
${
typed-reconstruct-6.h0 $e |- A C_ B $.
typed-reconstruct-6.h1 $e |- B C_ C $.
typed-reconstruct-6 $p |- A C_ ( B i^i C ) $= cA cB cC typed-reconstruct-6.h0 cA cB cC typed-reconstruct-6.h0 typed-reconstruct-6.h1 sstri ssini $.
$}
