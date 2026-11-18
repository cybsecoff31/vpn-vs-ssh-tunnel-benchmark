# Re-run every loss-sweep run that failed. Usage: rerun_failed.py cubic|bbr
import json, sys
sys.path.insert(0, "/opt/lab")
from run import *
CC = sys.argv[1]
path = f"/opt/lab/results/loss_{CC}.jsonl"
state = {}
for line in open(path):
    x = json.loads(line)
    state[(x["cfg"], x["trial"], x["loss"])] = "error" in x
failed = [k for k, bad in state.items() if bad]
print("failed runs:", failed)
for cfg, t, L in failed:
    for attempt in range(3):
        sh("/opt/lab/topo.sh clean"); sh("/opt/lab/servers.sh"); tunnel_up(cfg)
        sh(f"/opt/lab/topo.sh impair {L} 10 100 {1000*t+int(L*1000)}"); time.sleep(2)
        try:
            r = iperf(cfg, dur=20, par=1)
            log(f"loss_{CC}", {"cfg": cfg, "trial": t, "loss": L, "cc": CC, "rerun": True, **r})
            break
        except Exception as ex:
            print("attempt", attempt + 1, "failed:", str(ex)[:60])
sh("/opt/lab/topo.sh clean"); sh("/opt/lab/tun.sh down")
print("DONE")
