"""Enumerated input-wide malformed controls, no expected production semantics."""
from copy import deepcopy
from dataclasses import fields, make_dataclass
from support_v29 import adapter, fixture, core, named, presentation, information


def changed(value, field, replacement):
    result = deepcopy(value)
    object.__setattr__(result,field,replacement)
    return result


def foreign(value):
    cls = make_dataclass('Foreign'+type(value).__name__,[(f.name,object) for f in fields(value)],frozen=True)
    return cls(*(getattr(value,f.name) for f in fields(value)))


def malformed_cases():
    category,mapping = fixture(); current = adapter()
    F = information.Family; source = F(2,1,2,((0,),(1,)))
    cases = []
    def add(fn,*args):cases.append((fn,args))
    for graph in (None,[],(True,()),(-1,()),(1,[]),(1,((0,True),)),(1,((0,1),)),(1,((0,),))):
        add(presentation.GeneratorMap,graph,category,())
    for values in (None,[1,4,2],(1,4),(1,4,2,2),(True,4,2),(0,4,2),(1,4,99)):
        add(presentation.GeneratorMap,mapping.graph,category,values)
    add(presentation.GeneratorMap,(2,()),category,())
    for wrong in (None,(),foreign(category)):
        add(presentation.GeneratorMap,mapping.graph,wrong,(1,4,2))
    for path in (None,[],(True,()),(3,()),(0,[]),(0,(True,)),(0,(3,)),(0,(1,99)),(0,(1,))):
        add(presentation.evaluate_path,mapping,path)
    for fn in (presentation.evaluate_path,presentation.dag_presentation):
        add(fn,None,*(((0,()),) if fn is presentation.evaluate_path else ()))
    for size in (True,-1,6,7.0):add(named.NamedAdapter,category,size,(0,1,3,4,5,6),(2,0,1))
    for labels in (None,[0,1,3,4,5,6],(0,1),(0,0,3,4,5,6),(False,1,3,4,5,6),(0,1,3,4,5,7)):
        add(named.NamedAdapter,category,7,labels,(2,0,1))
    for objects in (None,[2,0,1],(2,0),(2,0,0),(True,0,2),(3,0,1)):
        add(named.NamedAdapter,category,7,(0,1,3,4,5,6),objects)
    bad_trees = (None,(),[],('bad',0),('arrow',),('arrow',True),('arrow',7),('empty',3),
                 ('seq',('arrow',0)),('seq',('arrow',2),('arrow',True)),
                 ('seq',('seq',('empty',0),('empty',1)),('unknown',0)))
    for tree in bad_trees:
        for fn in (named.named_response,named.named_word_response,named.typed_query):add(fn,current,tree)
    for bundle in ((),[0,0,0],(False,0,0),(0,0,9),(1,0,0),(0,0,-1)):
        add(named.encode_bundle,current,bundle)
    for allowed in ((1,3,5),(0,1,3,4,5),(0,0,3,5),(False,1,3,5),[0,1,3,5]):
        add(named.restricted_adapter,current,allowed)
    for values in ((True,1,2,((0,),)),(2,-1,2,((),())),(2,1,True,((0,),(0,))),
                   (2,1,2,[(0,),(1,)]),(2,1,2,((0,),)),(2,1,2,((0,),(True,))),
                   (2,1,2,((0,),(2,))),(2,1,2,((0,),[1]))):add(F,*values)
    for q in (None,[0],(),(True,),(1,)):add(information.transport_report,source,source,q,(0,1),(0,1))
    for out in (None,[0,1],(0,),(False,1),(0,2)):add(information.transport_report,source,source,(0,),out,(0,1))
    for codes in (None,[0,1],(0,),(True,1),(-1,0),(0,1.0)):
        add(information.transport_report,source,source,(0,),(0,1),codes)
    add(information.transport_report,source,F(1,1,2,((0,),)),(0,),(0,1),(0,1))
    add(information.transport_report,source,changed(source,'responses',((0,),(True,))),(0,),(0,1),(0,1))
    for rows in (None,[(0,)],((True,),),([0],),((0.0,),)):
        add(information.attained_recovery,(0,),rows)
    return cases
