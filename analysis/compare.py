# Print your results next to the published ones.
import json, os
mine = json.load(open(os.path.expanduser("~/rerun/analysis/summary.json")))
pub = json.load(open(os.path.expanduser("~/vpn-vs-ssh-tunnel-benchmark/analysis/summary.json")))
print("Clean link, 1 stream: Mbit/s, then 64-byte round trip in microseconds")
print("%-16s%9s%11s%7s%11s%10s" % ("config", "mine", "published", "ratio", "rr64 mine", "rr64 pub"))
for c in pub["clean"]:
    a, b = mine["clean"][c], pub["clean"][c]
    print("%-16s%9.0f%11.0f%7.2f%11.1f%10.1f" % (c, a["p1"][0], b["p1"][0],
          a["p1"][0] / b["p1"][0], a["rr64"][0], b["rr64"][0]))
for cc in ("cubic", "bbr"):
    print()
    print("Loss sweep with %s: Mbit/s, mine / published" % cc)
    for c in pub["loss"][cc]:
        cells = []
        for L in sorted(pub["loss"][cc][c], key=float):
            m, p = mine["loss"][cc][c][L]["mbps"][0], pub["loss"][cc][c][L]["mbps"][0]
            cells.append("%g%%: %.1f / %.1f" % (float(L) * 100, m, p))
        print("%-10s" % c + "  ".join(cells))
