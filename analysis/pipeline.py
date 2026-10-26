import os
HERE=os.path.dirname(os.path.abspath(__file__)); ROOT=os.path.dirname(HERE)
FIG=os.path.join(ROOT,'figures')
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
plt.rcParams.update({'font.family':'DejaVu Sans'})
W,H=7.0,2.55
fig,ax=plt.subplots(figsize=(W,H)); ax.set_xlim(0,W); ax.set_ylim(0,H); ax.axis('off')
C={'in':'#dbe9f6','tb':'#fde9d4','ms':'#e3f1df','pr':'#efe4f4','out':'#f7f2c9'}
def box(x,y,w,h,title,lines,col,fs=5.0,tfs=5.7,lead=0.128):
    ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle='round,pad=0.02,rounding_size=0.06',fc=col,ec='#333',lw=0.7))
    ax.text(x+w/2,y+h-0.06,title,ha='center',va='top',fontsize=tfs,fontweight='bold')
    for i,l in enumerate(lines): ax.text(x+0.06,y+h-0.29-i*lead,l,ha='left',va='top',fontsize=fs)
def arr(x1,y1,x2,y2):
    ax.annotate('',xy=(x2,y2),xytext=(x1,y1),arrowprops=dict(arrowstyle='-|>',lw=1.0,color='#333',shrinkA=0,shrinkB=0))
# 1 inputs
box(0.02,1.33,1.33,1.18,'(1) Tunnel configs',['• Raw TCP (baseline)','• WireGuard (wireguard-go)','• OpenVPN 2.7.8 UDP / TCP','• SSH -L port forwarding','• SSH -w layer-3 tunnel','• ciphers: AES-256-GCM vs.','  ChaCha20-Poly1305'],C['in'])
box(0.02,0.05,1.33,1.18,'(1) Conditions',['• clean: veth, no shaping','• impaired: 100 Mbit/s,','  RTT ≈ 20 ms','• Bernoulli loss p ∈ {0, 0.1,','  0.5, 1, 2, 5} %','• congestion control:','  CUBIC (main), BBR (ablation)'],C['in'])
# 2 testbed
box(1.55,0.05,2.35,2.46,'(2) Namespace testbed (1 host, 2 vCPU)',[],C['tb'])
for i,(t,s) in enumerate([('cli namespace — pinned to vCPU 0',['iperf3 / RR client, tunnel client','underlay vc0 = 10.0.1.2, inner 10.9.0.2']),
                          ('rtr namespace — impairment',['impair.c: TUN pair, loss + delay','tbf token bucket (rate cap)','attacker vantage point for probes']),
                          ('srv namespace — pinned to vCPU 1',['iperf3 / RR server, tunnel server','underlay vs0 = 10.0.2.2, inner 10.9.0.1'])]):
    y=1.73-i*0.78
    ax.add_patch(FancyBboxPatch((1.63,y),2.19,0.56,boxstyle='round,pad=0.02,rounding_size=0.04',fc='white',ec='#666',lw=0.6))
    ax.text(1.69,y+0.52,t,fontsize=5.1,fontweight='bold',va='top')
    for j,l in enumerate(s): ax.text(1.69,y+0.36-j*0.13,l,fontsize=4.9,va='top')
    if i<2: ax.annotate('',xy=(2.72,y-0.2),xytext=(2.72,y-0.02),arrowprops=dict(arrowstyle='<|-|>',lw=0.8,shrinkA=0,shrinkB=0))
# 3 measurement
box(4.10,1.33,1.40,1.18,'(3) Performance probes',['• iperf3 -J, 20 s, -P 1 / -P 4','• TCP_RR: 64 B and 1024 B','• /proc/stat per-vCPU busy %','• /proc/<pid>/stat daemon CPU','• veth byte & packet counters','• outer TCP RetransSegs','• 3–5 randomized-order trials'],C['ms'])
box(4.10,0.05,1.40,1.18,'(3) Security probes',['• unauthenticated UDP/TCP','  probes from rtr (on-path)','• handshake time and bytes','• negotiated suites (logs)','• implementation size (SLOC)','• known-attack review','  (Sweet32, Terrapin, ...)'],C['ms'])
# 4 processing / 5 output
box(5.70,1.33,1.28,1.18,'(4) Processing',['• JSONL record per trial','• mean ± 95% CI','  (Student t)','• metrics M1–M7','  (Sec. 4.1)'],C['pr'])
box(5.70,0.05,1.28,1.18,'(5) Outputs',['• Tables 2–7','• Figures 3–7','• security matrix','• deployment','  decision guide'],C['out'])
arr(1.37,1.92,1.53,1.92); arr(1.37,0.64,1.53,0.64)
arr(3.92,1.92,4.08,1.92); arr(3.92,0.64,4.08,0.64)
arr(5.52,1.92,5.68,1.92); arr(5.52,0.64,5.68,1.0)
arr(6.34,1.31,6.34,1.25)
plt.savefig(os.path.join(FIG,'fig1_pipeline.png'),dpi=300,bbox_inches='tight',pad_inches=0.02)
