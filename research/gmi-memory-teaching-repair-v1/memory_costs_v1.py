"""Explicit abstract lifetime event counts; no native-memory measurement."""
from collections import Counter
from memory_machine_v1 import encode, setup, service

def lifetime(image, compact, queries=(0,1,2), horizon=3, runtime_bits=256):
    if type(horizon) is not int or horizon<0 or type(runtime_bits) is not int or runtime_bits<1:
        raise ValueError("supplied nonnegative horizon and positive runtime reservation")
    size=len(encode(image))
    events=Counter()
    events["runtime_install_bits"]=runtime_bits
    events["runtime_retention_bit_time"]=runtime_bits*horizon
    events["image_retention_bit_time"]=size*horizon
    install=setup(image,compact)
    for key in ("history_reads","raw_xor","image_writes","validation_checks"):
        events[key]=install[key]
    peak=0
    for q in queries:
        row=service(image,q)
        events["instructions"]+=row["instructions"]
        events["controller_reset_bits"]+=row["workspace_bits"]
        peak=max(peak,row["workspace_bits"])
    events["image_release_bits"]=size
    events["runtime_release_bits"]=runtime_bits
    return dict(events=dict(events),persistent_bits=runtime_bits+size,
                peak_service_workspace_bits=peak,
                runtime_reservation_is_supplied=True)

def intervention_schedule(image, compact, runtime_bits=256):
    from memory_machine_v1 import decode, zero_slot, replace_query
    if type(runtime_bits) is not int or runtime_bits < 1:
        raise ValueError("positive supplied runtime reservation")
    saved=encode(image)
    current=image
    stages=[]
    total=Counter(runtime_install_bits=runtime_bits,
                  snapshot_read_bits=len(saved), snapshot_write_bits=len(saved))
    install=setup(image,compact)
    for key in ("history_reads","raw_xor","image_writes","validation_checks"):
        total[key]+=install[key]
    # Snapshot is external to the decoder and retained for the six service epochs.
    def record(name, current, events):
        rows=[service(current,q) for q in range(3)]
        events["instructions"]=sum(row["instructions"] for row in rows)
        events["controller_reset_bits"]=sum(row["workspace_bits"] for row in rows)
        events["image_retention_bit_time"]=len(encode(current))
        events["snapshot_retention_bit_time"]=len(saved)
        events["runtime_retention_bit_time"]=runtime_bits
        total.update(events)
        stages.append(dict(arm=name,image=encode(current),service=rows,events=dict(events)))
    record("intact",current,Counter())
    for name in ("sham","code_lesion","restore_after_code","slot_lesion","restore_after_slot"):
        old=encode(current)
        if name=="sham":
            after=decode(old)
        elif name=="code_lesion":
            after=replace_query(current,2,("L0","EMIT"))
        elif name=="slot_lesion":
            after=zero_slot(current,0)
        else:
            after=decode(saved)
        events=Counter(old_image_read_bits=len(old),image_write_bits=len(encode(after)))
        if name.startswith("restore"):
            events["snapshot_read_bits"]=len(saved)
        events["validation_checks"]=len(encode(after))+sum(map(len,after.programs))
        current=after
        record(name,current,events)
    total["snapshot_release_bits"]+=len(saved)
    total["image_release_bits"]+=len(encode(current))
    total["runtime_release_bits"]+=runtime_bits
    return dict(stages=stages,events=dict(total),snapshot_bits=saved,
                snapshot_unavailable_to_service=True,
                all_restore_images_exact=all(s["image"]==saved for s in stages
                                             if s["arm"].startswith("restore")))
