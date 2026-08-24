"""Turn the harness JSON into a readable pass/fail table."""
import json, sys

rows = json.loads(sys.stdin.read().replace("</pre>", "").strip())
width = max(len(r["test"]) for r in rows)
failed = 0
for r in rows:
    ok = r.get("ok")
    failed += 0 if ok else 1
    extra = " ".join(f"{k}={v}" for k, v in r.items() if k not in ("test", "ok"))
    print(f"{'PASS' if ok else 'FAIL'}  {r['test']:<{width}}  {extra}")
print(f"\n{len(rows) - failed}/{len(rows)} passed")
sys.exit(1 if failed else 0)
