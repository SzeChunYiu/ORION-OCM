import importlib
from ocm.kso import jump as active

def _proposal(m):
 t=m.JumpTrigger("t",m.TriggerKind.EXPRESSIVE_CEILING,m.JumpLevel.LOCAL_REPAIR_COMPOSITION,("w",),("lower-exhausted",)); return m.JumpProposal("p",t,m.JumpLevel.REPRESENTATION_REGIME_TRANSITION,"registered transform",("parent",),("correspondence",),("preserve",),("predict",),("falsify",))
def test_active_jump_matches_parent_owned_copy():
 parent=importlib.import_module("orion_v2.jump"); assert [(x.name,x.value) for x in active.JumpLevel]==[(x.name,x.value) for x in parent.JumpLevel]; assert [(x.name,x.value) for x in active.TriggerKind]==[(x.name,x.value) for x in parent.TriggerKind]; a=_proposal(active); p=_proposal(parent)
 for lower in (False,True):
  for donor in (False,True): assert active.assess_jump(a,lower_level_sufficient=lower,donor_product_ties=donor).value==parent.assess_jump(p,lower_level_sufficient=lower,donor_product_ties=donor).value
