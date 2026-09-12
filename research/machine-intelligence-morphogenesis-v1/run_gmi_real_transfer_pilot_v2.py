import argparse, json, math, pickle, platform, sys, time
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

M=4
DV=0.025
DT=0.025

DATASETS={
 "sklearn_iris":load_iris(return_X_y=True),
 "sklearn_wine":load_wine(return_X_y=True),
 "sklearn_breast_cancer":load_breast_cancer(return_X_y=True),
 "sklearn_digits":load_digits(return_X_y=True),
}

def candidates(seed):
    return {
      "linear_logistic":make_pipeline(StandardScaler(),LogisticRegression(max_iter=5000,random_state=seed)),
      "rbf_kernel":make_pipeline(StandardScaler(),SVC(kernel="rbf")),
      "exemplar_knn":make_pipeline(StandardScaler(),KNeighborsClassifier(n_neighbors=5)),
      "random_forest_partition_ensemble":RandomForestClassifier(n_estimators=200,random_state=seed,n_jobs=1),
    }

def main(freeze_sha):
    seed=int(freeze_sha[:8],16)%(2**31)
    rows=[]
    for dname,(X,y) in DATASETS.items():
        Xdv,Xtest,ydv,ytest=train_test_split(X,y,test_size=.20,random_state=seed,stratify=y)
        Xdev,Xval,ydev,yval=train_test_split(Xdv,ydv,test_size=.25,random_state=seed,stratify=ydv)
        metrics={}
        for name,model in candidates(seed).items():
            t0=time.perf_counter_ns(); model.fit(Xdev,ydev); fit=time.perf_counter_ns()-t0
            verr=1-accuracy_score(yval,model.predict(Xval))
            state=len(pickle.dumps(model,protocol=5))
            penalty=.002*math.log10(1+fit)+.0001*(state/1024)
            metrics[name]={"validation_error":float(verr),"fit_time_ns":fit,"state_bytes":state,
                           "resource_penalty":penalty,"selector_objective":float(verr+penalty)}
        order=list(candidates(seed))
        selected=min(order,key=lambda n:(metrics[n]["selector_objective"],metrics[n]["state_bytes"],order.index(n)))

        test={}
        for name,model in candidates(seed).items():
            model.fit(Xdv,ydv)
            terr=1-accuracy_score(ytest,model.predict(Xtest))
            test[name]={"test_error":float(terr),
                         "test_objective":float(terr+metrics[name]["resource_penalty"])}
        best=min(test,key=lambda n:test[n]["test_objective"])
        regret=test[selected]["test_objective"]-test[best]["test_objective"]
        ev=math.sqrt(math.log(2*M/DV)/(2*len(yval)))
        et=math.sqrt(math.log(2*M/DT)/(2*len(ytest)))
        bound=2*ev+2*et
        rows.append({"dataset":dname,"selected":selected,"retrospective_test_best":best,
                     "n_validation":len(yval),"n_test":len(ytest),
                     "observed_test_objective_regret":float(regret),
                     "epsilon_validation":ev,"epsilon_test":et,"registered_bound":bound,
                     "pass":regret<=bound+1e-12,
                     "selection_metrics":metrics,"test_metrics":test})
    gate=all(r["pass"] for r in rows)
    print(json.dumps({
      "artifact":"GMI_REAL_TRANSFER_PILOT_RECEIPT_V2",
      "freeze_commit":freeze_sha,"seed":seed,
      "environment":{"python":sys.version.split()[0],"sklearn":sklearn.__version__,"platform":platform.platform()},
      "rows":rows,"datasets_passed":sum(r["pass"] for r in rows),"datasets":len(rows),
      "gate_pass":gate,
      "terminal":"REAL_TRANSFER_FINITE_PORTFOLIO_BOUND_GREEN" if gate else "REAL_TRANSFER_FINITE_PORTFOLIO_BOUND_RED"
    },indent=2,sort_keys=True))

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--freeze-sha",required=True)
    main(ap.parse_args().freeze_sha)
