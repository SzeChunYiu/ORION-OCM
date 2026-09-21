"""Independent deterministic accounting for frozen interfaces and source bytes."""
from itertools import product
import json
PACKAGE = "research/gmi-1068-r1-integrated-core-v29"


def codec_costs():
    models = []
    for labels, identities in (((0,1,3,4,5,6),(6,0,4)),((0,1,4,6),(6,0,4))):
        models.append(dict(ambient_size=7,object_decoder=[2,0,1],arrow_labels=list(labels),
            identities=list(identities),ambient_to_local=[labels.index(i) if i in labels else None for i in range(7)],
            local_to_presented=list(range(len(labels))),presented_to_local=list(range(len(labels)))))
    reports=[]
    for width in (2,1):
        for entries in product((None,0,1),repeat=2*width):
            seed=(entries[:width],entries[width:])
            source=seed if width==2 else tuple(row*2 for row in seed)
            target=tuple(tuple(None if x is None else 1-x for x in row) for row in seed)
            restricted=target if width==2 else tuple(row*2 for row in target)
            queries=[0,1] if width==2 else [0,0]
            for codes in ((0,0),(0,1)):
                sizes={}
                for name,rows,row_width in (('source',source,2),('restricted',restricted,2),('full',target,width)):
                    books=len(set(rows))
                    recovery=(codes[0]!=codes[1] or rows[0]==rows[1])
                    sizes[name]=[books,row_width,books*row_width,2,len(set(codes)) if recovery else None]
                reports.append(dict(source_dimensions=[2,2,2],target_dimensions=[2,width,2],
                    query_map=queries,output_map=[1,0],codes=list(codes),
                    attained_code_count=len(set(codes)),recovery_sizes=sizes))
    return {'named':{'models':models},'information':{'family_reports':reports}}


def source_costs(root):
    package=root/PACKAGE
    pins=json.loads((package/'SOURCE_PINS_V29.json').read_text())
    files=[p for p in package.iterdir() if p.is_file() and p.suffix in {'.py','.md','.lean','.json'}
           and p.name not in {'RESULT_V29.json','RUN_TIMINGS_V29.json'}]
    return dict(direct_pinned_records=117,
                direct_pinned_bytes=sum((root/p).stat().st_size for p in pins['sources']),
                inherited_lean_sources=63,inherited_lean_source_bytes=200480,
                python_parents=18,
                python_parent_bytes=sum((root/p).stat().st_size for p in pins['python_load_order']),
                new_python_modules=sum(p.suffix=='.py' for p in files),
                new_python_bytes=sum(p.stat().st_size for p in files if p.suffix=='.py'),
                new_lean_modules=sum(p.suffix=='.lean' for p in files),
                new_lean_bytes=sum(p.stat().st_size for p in files if p.suffix=='.lean'),
                deterministic_package_files=len(files),
                deterministic_package_bytes=sum(p.stat().st_size for p in files))
