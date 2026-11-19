"""Scoring for the interviewer: python3 check/run_check.py
Runs your pipeline and your quality checks on files you have not seen, and compares them with
correct results. Do not edit this folder: its fingerprint is printed at the end."""
import base64, hashlib, importlib, importlib.util, json, re, sqlite3, subprocess, sys, tempfile, types
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.dont_write_bytecode = True
from check.hidden import DATA  # noqa: E402

D = json.loads(base64.b64decode("".join(DATA)))
TMP = Path(tempfile.mkdtemp(prefix="check-"))
for name, text in D["files"].items():
    (TMP / name).write_text(text)

ref_dir = TMP / "ref"
(ref_dir / "models").mkdir(parents=True)
(ref_dir / "run.py").write_text(D["reference"]["run"])
(ref_dir / "models" / "claims_latest.sql").write_text(D["reference"]["claims_latest"])
(ref_dir / "models" / "daily_summary.sql").write_text(D["reference"]["daily_summary"])
spec = importlib.util.spec_from_file_location("ref_run", ref_dir / "run.py")
ref = importlib.util.module_from_spec(spec); spec.loader.exec_module(ref)


def rows(conn):
    return sorted((d, s, int(c), round(float(t), 2)) for d, s, c, t in conn.execute(
        "SELECT loss_date, state, claim_count, total_incurred FROM daily_summary"))


def run(fn, files):
    conn = sqlite3.connect(":memory:")
    for f in files:
        fn(conn, TMP / f)
    return conn


SCENARIOS = [
    ("a normal day", ["day1.csv"]),
    ("the same file run twice", ["day1.csv", "day1.csv"]),
    ("a late update to a day already published", ["day1.csv", "late.csv"]),
    ("two versions of a claim with the same updated_at", ["tie.csv"]),
]

print("Checking your work (a few seconds)...\n")
try:
    cand = importlib.import_module("pipeline.run")
except Exception as e:  # noqa: BLE001
    cand = None
    print(f"pipeline/run.py does not load: {type(e).__name__}: {e}")
passed = []
for label, files in SCENARIOS:
    try:
        ok = cand is not None and rows(run(cand.run_batch, files)) == rows(run(ref.run_batch, files))
    except Exception:  # noqa: BLE001
        ok = False
    passed.append(ok)
    print(f"   {'yes' if ok else 'no '}  {label}")
print(f"T2 Fix: {sum(passed)}/4 situations give the correct summary\n")

correct = run(ref.run_batch, ["day1.csv", "late.csv", "tie.csv"])


def broken(sql):
    c = sqlite3.connect(":memory:"); correct.backup(c); c.executescript(sql); return c


BROKEN = [
    "INSERT INTO daily_summary SELECT * FROM daily_summary WHERE rowid = 1;",
    "INSERT INTO claims_latest SELECT * FROM claims_latest WHERE rowid = 1;",
    "UPDATE daily_summary SET total_incurred = total_incurred - 100 WHERE rowid = 1;",
    "DELETE FROM daily_summary WHERE rowid = (SELECT max(rowid) FROM daily_summary);",
]
try:
    quality = importlib.import_module("pipeline.quality")
    false_alarms = len(quality.check_quality(correct))
    caught = 0
    for sql in BROKEN:
        try:
            caught += bool(quality.check_quality(broken(sql)))
        except Exception:  # noqa: BLE001
            pass
except Exception as e:  # noqa: BLE001
    print(f"pipeline/quality.py does not run: {type(e).__name__}: {e}")
    false_alarms, caught = 1, 0
if false_alarms:
    print(f"T3 Quality checks: they report problems on correct data ({false_alarms}), so they score 0 of 4")
else:
    print(f"T3 Quality checks: catch {caught} of 4 broken tables, no false alarms on correct data")

notes = (ROOT / "NOTES.md").read_text() if (ROOT / "NOTES.md").exists() else ""
notes = re.sub(r"<!--.*?-->", "", notes, flags=re.S)
sections = sum(1 for s in re.split(r"^## ", notes, flags=re.M)[1:]
               if len(re.findall(r"[A-Za-z]{2,}", " ".join(s.split("\n")[1:]))) >= 10)
print(f"T4 Notes: {min(sections, 3)}/3 sections written\n")

t = subprocess.run([sys.executable, "-B", "-m", "unittest", "-q"], cwd=ROOT, capture_output=True, text=True)
m = re.search(r"Ran (\d+) test", t.stderr)
print(f"The team's tests: {m.group(1) if m else 0} ran, {'all pass' if t.returncode == 0 else 'some fail'}")
files = ["check/run_check.py", "check/hidden.py"]
fp = hashlib.sha256("".join((ROOT / f).read_text().replace("\r\n", "\n") for f in files).encode()).hexdigest()[:8]
print(f"Check files: {fp}")
