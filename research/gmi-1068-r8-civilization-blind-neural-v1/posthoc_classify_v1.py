#!/usr/bin/env python3
import json,sys
MAPPING={
 "AFFINE":"POSTHOC_MATCH_AFFINE_PREDICTOR",
 "BRANCH":"POSTHOC_MATCH_RULE_OR_DECISION_PARTITION",
 "HINGE":"POSTHOC_MATCH_SHALLOW_RECTIFIED_WEIGHTED_SUM_NEURAL_LIKE",
 "TABLE":"POSTHOC_MATCH_LOOKUP",
}
def classify(kinds):
 return [MAPPING.get(k,"UNKNOWN") for k in kinds]
if __name__=="__main__":
 print(json.dumps(classify(sys.argv[1:]),sort_keys=True))
