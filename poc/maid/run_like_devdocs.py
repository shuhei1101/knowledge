"""PoC: dev-docs の run_script と同じ約束（標準入力に文書の YAML・30 秒で打ち切り）でスクリプトを呼ぶ。"""
import subprocess, sys, time
doc = open(sys.argv[1], encoding="utf-8").read()
t = time.monotonic()
try:
    r = subprocess.run([sys.executable, "check_mermaid.py"], input=doc, capture_output=True, text=True, timeout=30)
    print(f"{sys.argv[1]}\texit={r.returncode}\t{time.monotonic()-t:.2f}s\t{r.stdout.strip()}{r.stderr.strip()}")
except subprocess.TimeoutExpired:
    print(f"{sys.argv[1]}\ttimeout")
