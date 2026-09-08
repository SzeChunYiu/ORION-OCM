# Result and scope

The single observed Python invocation (PID 2564382) exited successfully. It made two in-process native-wrapper calls: one for the authored source proof, then one for its replacement. Both returned `NATIVE_VERIFIED`; the caller returned `AUTHORED_ALIAS_REPLACEMENT_NATIVE_CHECKED`.

Both calls used the same 4,096-proof prefix and 96-axiom inventory. Each verified its own additional issued claim, yielding 4,097 verified labels. The source target was never added to the replacement prefix. The retained databases reconstruct from that common prefix and each call's own suffix.

The fixed occurrence path `[3]` selected node 25. Its floating arguments were `[9, 10, 11]` and ordered essential arguments `[14, 23]`. Node 9 supplied composite syntax; node 14 supplied an independently derived essential argument. The replacement contained the issued 21-label proof with exactly one `typed-admitted-0` and neither target-label shortcut. The original had 30 normal labels. Both USED maps covered their eight required labels.

The matcher/proposal records correctly retain `native_acceptance=false`: acceptance comes from the separate native result. The ordinary alias remains noneligible for learned-method use. This supplied nonminimal proof is a structural control, not a strong baseline for a compression or learning claim.

Read the [independent outcome review](review/outcome/OUTCOME-REVIEW-01.json), [reconciled counts](review/outcome/OUTCOME-COUNTS-01.json), [caller result](records/native-control-01/RESULT.json), and exact [source](records/native-control-01/native-source/result.json) / [replacement](records/native-control-01/native-replacement/result.json) receipts. No native or proof replay was performed for publication.
