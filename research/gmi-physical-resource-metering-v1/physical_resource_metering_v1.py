#!/usr/bin/env python3
"""Physical CPU/GPU/wall/IO (+ calibrated energy) metering at registered scope.

Sibling to research/gmi-resource-lifecycle-ledger-v1 (#805). That package keeps
derivation-only lifecycle coordinates and leaves physical/energy OPEN. This
harness closes physical counters executably and closes energy only when a
calibrated host source is present.
"""

from __future__ import annotations

from contextlib import contextmanager
from dataclasses import asdict, dataclass, field
from hashlib import sha256
import json
import os
from pathlib import Path
import platform
import resource
import shutil
import subprocess
import tempfile
import time
from typing import Any, Callable, Iterator, Mapping


HERE = Path(__file__).resolve().parent
CONTRACT_PATH = HERE / "PHYSICAL_METERING_CONTRACT_V1.json"
SIBLING_LEDGER = HERE.parent / "gmi-resource-lifecycle-ledger-v1" / "RESOURCE_LIFECYCLE_LEDGER_V1.json"

PHYSICAL_IDS = (
    "wall_s",
    "cpu_user_s",
    "cpu_system_s",
    "io_read_bytes",
    "io_write_bytes",
    "gpu_time_s",
    "energy_j",
)


@dataclass(frozen=True)
class MeterStatus:
    coordinate: str
    status: str  # AVAILABLE | UNAVAILABLE | OPEN | UNCALIBRATED
    value: float | None
    unit: str
    source: str
    notes: str = ""


@dataclass
class ScopeRegistration:
    scope_id: str
    description: str
    registered_before_outcomes: bool
    digest: str = ""

    def freeze(self) -> "ScopeRegistration":
        if not self.registered_before_outcomes:
            raise ValueError("scope must be registered before outcomes")
        if not self.scope_id:
            raise ValueError("scope_id required")
        payload = f"{self.scope_id}|{self.description}|{self.registered_before_outcomes}"
        digest = sha256(payload.encode("utf-8")).hexdigest()
        return ScopeRegistration(self.scope_id, self.description, True, digest)


@dataclass
class Sample:
    wall: float
    cpu_user: float
    cpu_system: float
    io_read: int | None
    io_write: int | None
    energy_uj: int | None
    gpu_util_s: float | None


@dataclass
class MeterReceipt:
    scope: ScopeRegistration
    host: dict[str, Any]
    statuses: list[MeterStatus]
    deltas: dict[str, float | None]
    workload: str
    sibling_ledger_physical: str
    sibling_ledger_energy: str
    claim_ceiling: str

    def as_dict(self) -> dict[str, Any]:
        return {
            "schema": "gmi-physical-resource-metering-receipt-v1",
            "scope": asdict(self.scope),
            "host": self.host,
            "statuses": [asdict(s) for s in self.statuses],
            "deltas": self.deltas,
            "workload": self.workload,
            "sibling_ledger_physical": self.sibling_ledger_physical,
            "sibling_ledger_energy": self.sibling_ledger_energy,
            "claim_ceiling": self.claim_ceiling,
        }


def load_contract() -> dict[str, Any]:
    return json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))


def sibling_ledger_gaps() -> dict[str, str]:
    if not SIBLING_LEDGER.is_file():
        raise FileNotFoundError(f"sibling ledger missing: {SIBLING_LEDGER}")
    ledger = json.loads(SIBLING_LEDGER.read_text(encoding="utf-8"))
    return {
        "physical_metering": ledger["physical_metering"]["status"],
        "energy_metering": ledger["energy_metering"]["status"],
    }


def host_identity() -> dict[str, Any]:
    return {
        "hostname": platform.node(),
        "platform": platform.platform(),
        "machine": platform.machine(),
        "python": platform.python_version(),
        "pid": os.getpid(),
    }


def _read_proc_io() -> tuple[int | None, int | None]:
    path = Path("/proc/self/io")
    if not path.is_file():
        return None, None
    data = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        data[key.strip()] = int(value.strip())
    return data.get("read_bytes"), data.get("write_bytes")


def _read_rusage_io_approx() -> tuple[int | None, int | None]:
    """Darwin exposes block counts, not bytes. Tag as approximate."""
    usage = resource.getrusage(resource.RUSAGE_SELF)
    # ru_inblock / ru_oublock are filesystem block operations; treat as proxy.
    in_b = getattr(usage, "ru_inblock", None)
    out_b = getattr(usage, "ru_oublock", None)
    if in_b is None and out_b is None:
        return None, None
    # Keep counts as-is but callers must mark source as rusage_blocks.
    return (None if in_b is None else int(in_b), None if out_b is None else int(out_b))


def _read_rapl_energy_uj() -> int | None:
    base = Path("/sys/class/powercap/intel-rapl")
    if not base.is_dir():
        return None
    total = 0
    found = False
    for pkg in sorted(base.glob("intel-rapl:*")):
        energy = pkg / "energy_uj"
        if energy.is_file():
            try:
                total += int(energy.read_text(encoding="utf-8").strip())
                found = True
            except OSError:
                return None
    return total if found else None


def _probe_gpu_time_s() -> tuple[float | None, str]:
    nvidia = shutil.which("nvidia-smi")
    if not nvidia:
        return None, "UNAVAILABLE:no-nvidia-smi"
    try:
        proc = subprocess.run(
            [
                nvidia,
                "--query-gpu=utilization.gpu",
                "--format=csv,noheader,nounits",
            ],
            check=False,
            capture_output=True,
            text=True,
            timeout=5,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None, "UNAVAILABLE:nvidia-smi-failed"
    if proc.returncode != 0:
        return None, "UNAVAILABLE:nvidia-smi-nonzero"
    # Point sample only — not cumulative GPU seconds. Mark UNCALIBRATED.
    return None, "UNCALIBRATED:point-util-only-not-cumulative"


def take_sample() -> Sample:
    usage = resource.getrusage(resource.RUSAGE_SELF)
    io_r, io_w = _read_proc_io()
    if io_r is None and io_w is None:
        # Prefer honest UNAVAILABLE over silent byte invention on Darwin.
        io_r, io_w = None, None
        _ = _read_rusage_io_approx()  # retained for diagnostics in probes
    return Sample(
        wall=time.perf_counter(),
        cpu_user=float(usage.ru_utime),
        cpu_system=float(usage.ru_stime),
        io_read=io_r,
        io_write=io_w,
        energy_uj=_read_rapl_energy_uj(),
        gpu_util_s=None,
    )


def _delta(before: Sample, after: Sample) -> dict[str, float | None]:
    def sub(a: float | int | None, b: float | int | None) -> float | None:
        if a is None or b is None:
            return None
        return float(a) - float(b)

    return {
        "wall_s": after.wall - before.wall,
        "cpu_user_s": after.cpu_user - before.cpu_user,
        "cpu_system_s": after.cpu_system - before.cpu_system,
        "io_read_bytes": sub(after.io_read, before.io_read),
        "io_write_bytes": sub(after.io_write, before.io_write),
        "energy_j": (
            None
            if after.energy_uj is None or before.energy_uj is None
            else (after.energy_uj - before.energy_uj) / 1_000_000.0
        ),
        "gpu_time_s": None,
    }


def classify_statuses(deltas: Mapping[str, float | None], before: Sample, after: Sample) -> list[MeterStatus]:
    gpu_value, gpu_note = _probe_gpu_time_s()
    statuses: list[MeterStatus] = []

    statuses.append(
        MeterStatus("wall_s", "AVAILABLE", deltas["wall_s"], "seconds", "time.perf_counter")
    )
    statuses.append(
        MeterStatus("cpu_user_s", "AVAILABLE", deltas["cpu_user_s"], "seconds", "resource.ru_utime")
    )
    statuses.append(
        MeterStatus(
            "cpu_system_s", "AVAILABLE", deltas["cpu_system_s"], "seconds", "resource.ru_stime"
        )
    )

    if before.io_read is None or after.io_read is None:
        statuses.append(
            MeterStatus(
                "io_read_bytes",
                "UNAVAILABLE",
                None,
                "bytes",
                "proc_io_or_none",
                "host does not expose process read_bytes; not coerced to zero",
            )
        )
    else:
        statuses.append(
            MeterStatus(
                "io_read_bytes", "AVAILABLE", deltas["io_read_bytes"], "bytes", "/proc/self/io"
            )
        )

    if before.io_write is None or after.io_write is None:
        statuses.append(
            MeterStatus(
                "io_write_bytes",
                "UNAVAILABLE",
                None,
                "bytes",
                "proc_io_or_none",
                "host does not expose process write_bytes; not coerced to zero",
            )
        )
    else:
        statuses.append(
            MeterStatus(
                "io_write_bytes", "AVAILABLE", deltas["io_write_bytes"], "bytes", "/proc/self/io"
            )
        )

    if gpu_value is None:
        status = "UNAVAILABLE" if gpu_note.startswith("UNAVAILABLE") else "UNCALIBRATED"
        statuses.append(MeterStatus("gpu_time_s", status, None, "seconds", "gpu-probe", gpu_note))
    else:
        statuses.append(MeterStatus("gpu_time_s", "AVAILABLE", gpu_value, "seconds", "gpu-probe"))

    if before.energy_uj is None or after.energy_uj is None:
        statuses.append(
            MeterStatus(
                "energy_j",
                "OPEN",
                None,
                "joules",
                "no-calibrated-source",
                "RAPL energy_uj unread; joules not inferred from CPU/wall",
            )
        )
    else:
        statuses.append(
            MeterStatus(
                "energy_j",
                "AVAILABLE",
                deltas["energy_j"],
                "joules",
                "intel-rapl:energy_uj",
                "calibrated host counter",
            )
        )
    return statuses


def default_probe_workload() -> str:
    """CPU + intentional IO so counters move on capable hosts."""
    acc = 0
    for i in range(200_000):
        acc = (acc + i * i) % 1_000_000_007
    with tempfile.NamedTemporaryFile(prefix="gmi-meter-", delete=True) as handle:
        payload = (b"x" * 4096) * 256
        handle.write(payload)
        handle.flush()
        os.fsync(handle.fileno())
        handle.seek(0)
        _ = handle.read()
    return f"cpu_acc={acc};io_bytes={len(payload)}"


@contextmanager
def meter_scope(scope: ScopeRegistration, workload_name: str = "callable") -> Iterator[dict[str, Any]]:
    frozen = scope.freeze()
    before = take_sample()
    bag: dict[str, Any] = {"scope": frozen, "before": before, "workload": workload_name}
    try:
        yield bag
    finally:
        after = take_sample()
        deltas = _delta(before, after)
        statuses = classify_statuses(deltas, before, after)
        gaps = sibling_ledger_gaps()
        energy_status = next(s.status for s in statuses if s.coordinate == "energy_j")
        claim = (
            "PHYSICAL_COUNTERS_CLOSED_AT_SCOPE;ENERGY_CLOSED_CALIBRATED"
            if energy_status == "AVAILABLE"
            else "PHYSICAL_COUNTERS_CLOSED_AT_SCOPE;ENERGY_REMAINS_OPEN_WITHOUT_CALIBRATION"
        )
        bag["receipt"] = MeterReceipt(
            scope=frozen,
            host=host_identity(),
            statuses=statuses,
            deltas=deltas,
            workload=workload_name,
            sibling_ledger_physical=gaps["physical_metering"],
            sibling_ledger_energy=gaps["energy_metering"],
            claim_ceiling=claim,
        )


def run_metered(
    scope: ScopeRegistration,
    fn: Callable[[], Any] | None = None,
    workload_name: str = "default_probe",
) -> MeterReceipt:
    with meter_scope(scope, workload_name=workload_name) as bag:
        if fn is None:
            default_probe_workload()
        else:
            fn()
    return bag["receipt"]


def validate_contract() -> dict[str, Any]:
    contract = load_contract()
    ids = tuple(row["id"] for row in contract["physical_coordinates"])
    if ids != PHYSICAL_IDS:
        raise ValueError(f"coordinate drift: {ids}")
    gaps = sibling_ledger_gaps()
    if gaps["physical_metering"] != "OPEN" or gaps["energy_metering"] != "OPEN":
        # Sibling may later be updated; this package must still be a sibling, not a silent overwrite.
        pass
    return {
        "coordinates": len(ids),
        "sibling_physical": gaps["physical_metering"],
        "sibling_energy": gaps["energy_metering"],
        "energy_default": contract["energy_policy"]["status_default"],
        "schema": contract["schema"],
    }


def write_receipt(receipt: MeterReceipt, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(receipt.as_dict(), indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scope-id", default="gmi-physical-metering-v1-local")
    parser.add_argument("--out", type=Path, default=HERE / "receipts" / "LOCAL_RECEIPT_V1.json")
    parser.add_argument("--host-tag", default="")
    args = parser.parse_args(argv)

    scope = ScopeRegistration(
        scope_id=args.scope_id,
        description="Issue #602 Section N physical metering probe",
        registered_before_outcomes=True,
    )
    receipt = run_metered(scope)
    out = args.out
    if args.host_tag:
        stem = out.stem + f"_{args.host_tag}"
        out = out.with_name(stem + out.suffix)
    write_receipt(receipt, out)
    print(json.dumps({"out": str(out), "claim_ceiling": receipt.claim_ceiling}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
