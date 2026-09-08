"""Source/data custody and method payloads; no teaching history or receipt authority."""
from pathlib import Path
import hashlib,json
from native_contract import fields,require,CONTEXT
from native_bundle import PINS
from vendor import common as C
import native_data as D
S=C.load("native_scope")
class Inputs:
    def __init__(self,root,work):
        self.root=Path(root);self.work=work;self.loaded={}
        self.parent=self.read("PARENT.json");self.bank=self.read("BANK.json")
        self.methods=self.read("METHODS.json");self.binding=self.read("BINDING.json")
        self.identity=D.parse(D.raw({k:v for k,v in PINS.items() if k not in ("positive.json","false.json")}))
        require(len(self.parent)==4191 and len(self.bank["class"])==15 and len(self.bank["wff"])==255,"FINITE_INVENTORY")
        require(self.binding["projection"]==PINS["METHODS.json"],"PROJECTION_BINDING")
        for name,key in (("PARENT.json","parent"),("BANK.json","bank")):
            require({k:self.binding[key][k] for k in ("bytes","sha256")}==PINS[name],"LIBRARY_BINDING")
        require(set(self.methods)==set().union(*(set(v) for v in self.binding["eligible"].values())),"ELIGIBILITY_POPULATION")
        parent={x["label"]:x for x in self.parent}
        for mid,item in self.methods.items():
            fields(item,("id","body","trace","contracts","admission"))
            require(item["id"]==mid==C.raw_id(C.canonical(item["body"]))["sha256"],"METHOD_ID")
            require(item["admission"]==self.binding["admission"],"OPAQUE_PROVENANCE_BINDING")
            for label,row in item["contracts"].items():
                if row["kind"] in ("$a","$p"):
                    require({k:v for k,v in row.items() if k!="span"}==parent.get(label),"ORDINARY_CONTRACT_BINDING")
            D.bump(work,"method_payloads_validated")
        scope=S.certify(self.parent,[["|-"]+r["tokens"] for r in self.bank["wff"]])
        D.bump(work,"syntax_contracts_checked",scope["syntax_assertions"])
    def read(self,name):
        require(name in PINS and name!="PREFIX.mm","SEARCH_INPUT_ALLOWLIST")
        require((self.root/name).stat().st_size==PINS[name]["bytes"],"INPUT_BYTES_CHANGED")
        raw=(self.root/name).read_bytes();D.bump(self.work,"input_bytes_read",len(raw));D.bump(self.work,"input_files_read")
        require(C.raw_id(raw)==PINS[name],"INPUT_BYTES_CHANGED")
        value=json.loads(raw);require(C.canonical(value)==raw,"INPUT_CANONICAL")
        self.loaded[name]=C.raw_id(C.canonical(value))["sha256"]
        return value
    def check(self):
        require(self.identity=={k:v for k,v in PINS.items() if k not in ("positive.json","false.json")},"LIBRARY_IDENTITY_CHANGED")
        for name in tuple(self.loaded):self.read(name)
        for name,value in (("PARENT.json",self.parent),("BANK.json",self.bank),("METHODS.json",self.methods),("BINDING.json",self.binding)):
            require(C.raw_id(C.canonical(value))["sha256"]==self.loaded[name],"MUTATED_INPUT_OBJECT")
