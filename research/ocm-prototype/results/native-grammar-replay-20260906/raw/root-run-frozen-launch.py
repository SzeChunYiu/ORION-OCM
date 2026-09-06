import datetime, hashlib, json, subprocess, sys
from pathlib import Path
launch_path, expected, output = Path(sys.argv[1]), sys.argv[2], Path(sys.argv[3])
raw = launch_path.read_bytes()
assert hashlib.sha256(raw).hexdigest() == expected
launch = json.loads(raw)
output.mkdir()
(output / "launch.json").write_bytes(raw)
record = {"started_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(), "argv": launch["argv"], "cwd": launch["cwd"]}
(output / "started.json").write_text(json.dumps(record, indent=2)+"\n")
with (output / "stdout").open("xb") as out, (output / "stderr").open("xb") as err:
    result = subprocess.run(launch["argv"], cwd=launch["cwd"], stdout=out, stderr=err)
record.update(exit_code=result.returncode, completed_utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
(output / "completed.json").write_text(json.dumps(record, indent=2)+"\n")
print(json.dumps(record), flush=True)
raise SystemExit(result.returncode)
