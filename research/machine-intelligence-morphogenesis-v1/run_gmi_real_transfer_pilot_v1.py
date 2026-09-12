import json, math, pickle, platform, sys, time
import numpy as np
import sklearn
from sklearn.datasets import load_iris, load_wine, load_breast_cancer, load_digits
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score

FREEZE_COMMIT="95df76e681e1dd79db5da89732a23cef4f3fde0a"
SEED=int(FREEZE_COMMIT[:8],16)%(2**31)

DATASETS={
 "sklearn_iris":load_iris(return_X_y=True),
 "sklearn_wine":load_wine(return_X_y=True),
 "sklearn_breast_cancer":load_breast_cancer(return_X_y=True),
 "sklearn_digits":load_digits(return_X_y=True),
}

def candidates():
    return {
      "linear_logistic":make_pipeline(StandardScaler(),LogisticRegression(max_iter=5000,random_state=SEED)),
      "rbf_kernel":make_pipeline(StandardScaler(),SVC(kernel="rbf")),
      "exemplar_knn":make_pipeline(StandardScaler(),KNeighborsClassifier(n_neighbors=5)),
      "random_forest_partition_ensemble":RandomForestClassifier(n_estimators=200,random_state=SEED,n_jobs=1),
    }

rows=[]
for dname,(X,y) in DATASETS.items():
    Xdv,Xtest,ydv,ytest=train_test_split(X,y,test_size=.20,random_state=SEED,stratify=y)
    Xdev,Xval,ydev,yval=train_test_split(Xdv,ydv,test_size=.25,random_state=SEED,stratify=ydv)
    sel={}
    for name,model in candidates().items():
        t0=time.perf_counter_ns(); model.fit(Xdev,ydev); fit=time.perf_counter_ns()-t0
        verr=1-accuracy_score(yval,model.predict(Xval))
        state=len(pickle.dumps(model,protocol=5))
        score=verr+.002*math.log10(1+fit)+.0001*(state/1024)
        sel[name]={"validation_error":float(verr),"fit_time_ns":fit,"state_bytes":state,"selector_score":float(score)}
    order=list(candidates())
    chosen=min(order,key=lambda n:(sel[n]["selector_score"],sel[n]["state_bytes"],order.index(n)))

    test={}
    for name,model in candidates().items():
        t0=time.perf_counter_ns(); model.fit(Xdv,ydv); fit=time.perf_counter_ns()-t0
        terr=1-accuracy_score(ytest,model.predict(Xtest))
        test[name]={"test_error":float(terr),"refit_time_ns":fit,"state_bytes":len(pickle.dumps(model,protocol=5))}
    best=min(test,key=lambda n:test[n]["test_error"])
    rows.append({
      "dataset":dname,"selected":chosen,"best_test":best,
      "selected_test_error":test[chosen]["test_error"],"best_test_error":test[best]["test_error"],
      "test_regret":float(test[chosen]["test_error"]-test[best]["test_error"]),
      "selection_metrics":sel,"test_metrics":test
    })

receipt={
 "artifact":"GMI_REAL_TRANSFER_PILOT_RECEIPT_V1",
 "status":"REGISTERED_SELECTOR_REAL_PILOT_RED",
 "freeze_commit":FREEZE_COMMIT,"seed":SEED,
 "environment":{"python":sys.version.split()[0],"sklearn":sklearn.__version__,"platform":platform.platform()},
 "datasets":rows,
 "summary":{
   "datasets":len(rows),
   "zero_test_regret":sum(abs(r["test_regret"])<1e-12 for r in rows),
   "positive_test_regret":sum(r["test_regret"]>1e-12 for r in rows),
   "mean_test_regret":float(np.mean([r["test_regret"] for r in rows])),
   "max_test_regret":float(max(r["test_regret"] for r in rows))
 },
 "disposition":"FAILURE_PRESERVED__DO_NOT_REPAIR_ON_THIS_TEST_SPLIT",
 "terminal":"REAL_TRANSFER_PILOT_V1_SELECTOR_RED"
}
print(json.dumps(receipt,indent=2,sort_keys=True))
