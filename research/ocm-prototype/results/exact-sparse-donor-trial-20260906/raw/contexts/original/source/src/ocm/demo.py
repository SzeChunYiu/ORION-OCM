from __future__ import annotations
import argparse, json, tempfile
from pathlib import Path
from .historical import load_reference, repository_root
from .runtime import OCMRuntime

def _stage(name,fn,limitation):
 try:
  result=fn(); terminal=result.get("terminal")
  if terminal is None and "terminals" in result: terminal=result["terminals"].get("M0_FINITE_MATH_CORE")
  return {"stage":name,"terminal":terminal,"limitation":limitation,"result":result}
 except Exception as exc:
  label=type(exc).__name__; terminal="CANNOT_CHECK" if "CannotCheck" in label or "CANNOT_CHECK" in str(exc) else "FAIL"
  return {"stage":name,"terminal":terminal,"limitation":limitation,"reason":f"{label}: {exc}"}

def _state_restart():
 with tempfile.TemporaryDirectory(prefix="ocm-m0-state-") as td:
  log=Path(td)/"events.jsonl"; r=OCMRuntime(log); r.learn_procedure("AND",(0,0,0,1),7001); before=r.snapshot(); assert r.run("AND",(1,1))==("PASS",1)
  r=OCMRuntime(log); assert r.snapshot()==before; r.revoke(7001); r=OCMRuntime(log); assert r.run("AND",(1,1))==("GAP_REVOKED_PROCEDURE",None); r.reinstate(7001); r=OCMRuntime(log); assert r.run("AND",(1,1))==("PASS",1)
  return {"terminal":"M0_STATE_REPLAY_GREEN","learn_restart_exact":True,"revocation_survives_restart":True,"reinstate_survives_restart":True,"state_hash":r.state_hash}

def run_controlled():
 root=repository_root(); m0=load_reference("kso_m0_freeze_checks_v1",root); m3=load_reference("kso_m3_learning_v1",root); m4=load_reference("kso_m4_jump_v1",root); lang=load_reference("kso_language_v0",root); rec=load_reference("recursive_kso_v0",root); m6=load_reference("kso_m6_formal_math_v1",root)
 stages=[_stage("KSO_MATH_SANITY",m0.run_all,"finite math calibration; GENERAL_NOVELTY remains NOT_ESTABLISHED"),_stage("EXACT_PROCEDURE_LIFECYCLE",m3.run_m3,"finite Boolean learning calibration"),_stage("GOVERNED_FINITE_JUMP",m4.run_m4,"finite governed Jump calibration; novelty false"),_stage("CONTROLLED_LANGUAGE_L0",lang.run_language_l0,"controlled language only; open-domain false"),_stage("RECURSIVE_KSO_REVOCATION_ISOLATION",rec.run_recursive_kso_v0,"candidate organization; scale/topology not established"),_stage("FORMAL_PROOF_RECEIPT_ADMISSION",m6.run_m6a,"immutable Lean receipt replay; upstream PARENT_SUFFICIENT"),_stage("PERSIST_RESTART_REVOKE_REINSTATE",_state_restart,"M0 custody check; not M2 unified runtime")]
 fail=[x for x in stages if x["terminal"]=="FAIL"]; cc=[x for x in stages if str(x["terminal"]).startswith("CANNOT_CHECK")]; terminal="M0_CONTROLLED_DEMO_GREEN" if not fail and not cc else ("M0_CONTROLLED_DEMO_FAIL" if fail else "M0_CONTROLLED_DEMO_CANNOT_CHECK")
 return {"terminal":terminal,"stages":stages,"authority":{"M2_full_solve_parent_tie":"PARENT_SUFFICIENT","M6a_upstream_scientific_terminal":"PARENT_SUFFICIENT","general_novelty":"NOT_ESTABLISHED","language_alpha_claimed":False,"later_milestones_started":False}}
def main(argv=None):
 p=argparse.ArgumentParser(); p.add_argument("--controlled",action="store_true"); p.add_argument("--json",action="store_true"); a=p.parse_args(argv)
 if not a.controlled: p.error("M0 exposes only --controlled")
 r=run_controlled()
 if a.json: print(json.dumps(r,indent=2,sort_keys=True,default=str))
 else:
  for x in r["stages"]: print(f"{x['stage']}: {x['terminal']} | {x['limitation']}")
  print(f"M0_DEMO: {r['terminal']} | no scientific authority upgrade")
 return 0 if r["terminal"]=="M0_CONTROLLED_DEMO_GREEN" else (2 if r["terminal"].endswith("CANNOT_CHECK") else 1)
if __name__=="__main__": raise SystemExit(main())
