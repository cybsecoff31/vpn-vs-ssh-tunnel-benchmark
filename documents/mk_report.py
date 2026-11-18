import json,re,copy,docx
from docx.shared import Emu
R='/home/claude/cy/run/'
s=json.load(open(R+'analysis/summary.json'));cx=json.load(open(R+'analysis/ctx.json'))
C=s['clean'];L=s['loss'];f=4.0e9
def cb(k): c=C[k]; return c['busy'][0]/100*f/(c['p1'][0]*1e6/8)
CB={k:cb(k) for k in C}; print({k:round(v,2) for k,v in CB.items()})
cap=lambda k:8*1e9/CB[k]/1e6
print('edge',cap('ovpn-udp'),cap('wg'),cap('wg')/cap('ovpn-udp'))
d=docx.Document('/home/claude/report5.docx')
def rep(p,old,new):
    t=''.join(r.text for r in p.runs)
    i=t.find(old)
    if i<0: return False
    pos=0;first=True;end=i+len(old)
    for r in p.runs:
        L_=len(r.text);a=max(i,pos);b=min(end,pos+L_)
        if a<b:
            rt=r.text
            r.text=rt[:a-pos]+(new if first else '')+rt[b-pos:]
            first=False
            pos+=L_
            continue
        pos+=L_
    return True
paras=list(d.paragraphs)
for t in d.tables:
    for row in t.rows:
        for c in row.cells: paras+=c.paragraphs
def R1(old,new,n=1):
    k=0
    for p in paras:
        while rep(p,old,new):
            k+=1
            if old in new: break
    assert k>=1 and (n==0 or k==n),(old,k)
A=[
("reached 8.60 Gbit/s with AES-GCM, user-space WireGuard 1.58 Gbit/s and OpenVPN about 727 Mbit/s","reached 18.49 Gbit/s with AES-GCM, user-space WireGuard 2.89 Gbit/s and OpenVPN about 2.24 Gbit/s"),
("Changing OpenVPN’s cipher did not change its throughput, which points","Changing OpenVPN’s cipher moved its throughput only within the confidence intervals, which points"),
("every tunnel stayed within about 13% of plain TCP","every tunnel stayed within about 23% of plain TCP"),
("With BBR, TCP-in-TCP tunnels ran 28–43% below plain TCP, but they were still about 10–40× faster","With BBR, TCP-in-TCP tunnels ran 18–44% below plain TCP, but they were still about 11–52× faster"),
("I ran all experiments on one Linux 6.18 virtual machine (2 vCPUs, Intel Xeon @ 2.8 GHz with AES-NI, 7 GiB RAM).","I ran all experiments on one Ubuntu Server 24.04.3 virtual machine named cyborg (Linux 6.8 arm64, 2 vCPUs, 8 GiB RAM, 30 GiB disk). The VM runs in UTM (QEMU 9.1 ARM virtual machine with hardware virtualization) on an Apple Silicon Mac. I measured the vCPU clock at about 4.0 GHz, and the processor exposes the ARMv8 AES instructions, the ARM counterpart of AES-NI."),
("I built all tools from source: OpenVPN 2.7.8 (OpenSSL 3.0.13), OpenSSH 10.6p1, wireguard-go (commit b3bc704), iperf3 3.22 (ESnet, 2026) and iproute2.","I built the tunnel and measurement tools from source: OpenVPN 2.7.8 (OpenSSL 3.0.13), OpenSSH 10.6p1, wireguard-tools v1.0.20260223, wireguard-go (commit b3bc704, Go 1.24.7) and iperf3 3.22 (ESnet, 2026). iproute2 6.1 comes from Ubuntu."),
("The kernel lacks the netem queueing discipline, so I leveraged","My first testbed kernel lacked the netem queueing discipline, so I leveraged"),
("with 96, 5.7 and 3.3 Mbit/s at 0, 1 and 2% loss","with 96, 5.5 and 3.3 Mbit/s at 0, 1 and 2% loss"),
("at clock f = 2.8 GHz","at clock f = 4.0 GHz"),
("The raw veth path reaches 28.07 Gbit/s because the kernel moves large offloaded segments (44 KB on average)","The raw veth path reaches 106.03 Gbit/s because the kernel moves large offloaded segments (43 KB on average)"),
("SSH-L moved 4.10 Gbit/s with ChaCha20-Poly1305 and 8.60 Gbit/s with AES-256-GCM.","SSH-L moved 6.48 Gbit/s with ChaCha20-Poly1305 and 18.49 Gbit/s with AES-256-GCM."),
("WireGuard reached 1.58 Gbit/s (1.97 with four streams), OpenVPN-UDP 727, OpenVPN-TCP 652 and SSH-W 575 Mbit/s","WireGuard reached 2.89 Gbit/s (2.81 with four streams), OpenVPN-UDP 2,236, OpenVPN-TCP 1,757 and SSH-W 1,327 Mbit/s"),
("These last three kept each vCPU 81–95% busy","These last three kept each vCPU 77–99% busy"),
("throughput did not change (727 vs. 742 Mbit/s, overlapping CIs). In SSH-L, moving from ChaCha20-Poly1305 to AES-256-GCM (AES-NI) doubled the rate.","throughput moved only within the noise (2,236 vs. 1,742 Mbit/s, overlapping CIs). In SSH-L, moving from ChaCha20-Poly1305 to AES-256-GCM (ARMv8 AES instructions) nearly tripled the rate."),
("Raw 10, SSH-L 43, WG 105, OV-U 1,350, OV-T 1,317, SSH-W 1,361.","Raw 5, SSH-L 57, WG 110, OV-U 1,112, OV-T 1,202, SSH-W 1,105."),
("incurs about 13× fewer switches. Its veth buffers average 27.9 KB","incurs about 10× fewer switches. Its veth buffers average 27.3 KB"),
("The fit has slope -0.69 and r = -0.95.","The fit has slope -0.68 and r = -0.93."),
("(r = -0.95, see Figure 4)","(r = -0.93, see Figure 4)"),
("Among the tunnels, only WireGuard benefited from four parallel streams (1.58 → 1.97 Gbit/s, +25%), because wireguard-go spreads encryption across goroutines. OpenVPN, ssh and sshd each process a tunnel in one thread, so extra streams only share the same core (OV-U 712, SSH-L 4.09 Gbit/s with four streams).","No tunnel benefited from four parallel streams. WireGuard stayed at the same level (2.89 → 2.81 Gbit/s) even though wireguard-go spreads encryption across goroutines. OpenVPN, ssh and sshd each process a tunnel in one thread, so extra streams only share the same core (OV-U 2,247 Mbit/s, SSH-L 5.87 Gbit/s with four streams)."),
("Per payload byte, OpenVPN-UDP cost 53 cycles, SSH-W 72, WireGuard 20, SSH-L 10.4 and raw forwarding 1.3.",f"Per payload byte, OpenVPN-UDP cost {CB['ovpn-udp']:.0f} cycles, SSH-W {CB['ssh-w']:.0f}, WireGuard {CB['wg']:.0f}, SSH-L {CB['ssh-L']:.1f} and raw forwarding {CB['raw']:.1f}."),
("near 152 Mbit/s for OpenVPN and 409 Mbit/s for WireGuard. This 2.7× gap",f"near {cap('ovpn-udp'):.0f} Mbit/s for OpenVPN and {cap('wg'):.0f} Mbit/s for WireGuard. This {cap('wg')/cap('ovpn-udp'):.1f}× gap"),
("give 92.4% for 1368-byte payloads (1368/1480), which is what I measured. Each packet’s","give 92.4% for 1368-byte payloads (1368/1480), and I measured 94.3%, likely because the offloaded counters under-count headers (see Section 4.1). Each packet’s"),
("The same counters explain the 99–100% of Raw and SSH-L, whose buffers average 44 and 33 KB.","The same counters explain the 99.8% of Raw and SSH-L, whose buffers average 43 and 32 KB."),
("All tunnels added 43–113 µs to a 64-byte round trip and 47–121 µs to a 1024-byte one.","All tunnels added 18–25 µs to a 64-byte round trip and 21–31 µs to a 1024-byte one."),
("On the 20 ms path, the extra delay was below 0.4 ms for every tunnel.","On the 20 ms path, the extra delay was at most 2.1 ms, which stays inside the ±2.8 ms interval of plain TCP."),
("consume 145–165% of one vCPU for OpenVPN and SSH-W","consume 154–173% of one vCPU for OpenVPN and SSH-W"),
("wireguard-go needs 126% for more than twice the throughput.","wireguard-go needs 132% for more throughput than any of them."),
("Tail latency (Figure 5b) is 2–3× the median for every tunnel and highest for WireGuard (p99 421 µs)","Tail latency (Figure 5b) is 1.6–2.4× the median for every tunnel and highest for WireGuard (p99 126 µs)"),
("retention stays between 0.87 and 1.02 up to 2%","retention stays between 0.77 and 1.02 up to 2%"),
("retention spreads from 0.94 to 1.32","retention spreads from 0.90 to 1.25"),
("Measured values sit 7–31% below the model up to 2% loss","Measured values sit 4–24% below the model up to 2% loss"),
("(outer: 641 and 199 per run)","(outer: 186 and 191 per run)"),
("Inner retransmissions reached 794 (SSH-W, 0%), 1,031 (SSH-W, 0.1%) and 551 (OV-T, 0.5%) against 5, 36 and 84 for raw TCP, without a collapse.","Inner retransmissions reached 616 (OV-T, 0%), 688 (SSH-W, 0.1%) and 21 (SSH-W, 0.5%) against 14, 35 and 77 for raw TCP, without a collapse."),
("(1.54 and 1.58 Mbit/s) was not below raw TCP (1.20)","(1.44 and 1.42 Mbit/s) was not below raw TCP (1.15)"),
("tracked raw TCP (R between 0.98 and 1.02)","tracked raw TCP (R between 0.90 and 1.02)"),
("sit 28–43% below it and SSH-L 4–31% below it; every BBR bar","sit 18–44% below it and SSH-L 4–30% below it; every BBR bar"),
("so raw TCP and WireGuard sustained 93 and 90 Mbit/s at 1% loss","so raw TCP and WireGuard sustained 94 and 90 Mbit/s at 1% loss"),
("reached only 55 (OV-T), 53 (SSH-W) and 64 Mbit/s (SSH-L)","reached only 57 (OV-T), 52 (SSH-W) and 65 Mbit/s (SSH-L)"),
("yet lost 31% at 1%, though only 4% at 5%","yet lost 30% at 1%, though only 4% at 5%"),
("still ran about 10× faster than under CUBIC at 1% loss and at least 40× faster at 5%","still ran about 11× faster than under CUBIC at 1% loss and at least 47× faster at 5%"),
("Net of the script waits included in Table 2 (0.3 s for SSH, 0.5 s for OpenVPN), WireGuard needed 0.09 s and 1.9 KB (one round trip of fixed-size messages), SSH 0.14–0.17 s and 9.4–11.0 KB, and OpenVPN 1.50–2.21 s and up to 13.6 KB.","Net of the script waits included in Table 2 (0.3 s for SSH, 0.5 s for OpenVPN), WireGuard needed 0.06 s and 1.9 KB (one round trip of fixed-size messages), SSH 0.14 s and 9.4–11.2 KB, and OpenVPN 1.50–1.99 s and up to 13.2 KB."),
("28–43% below raw TCP for TCP-in-TCP and 4–31% for SSH-L, which is not stacked","18–44% below raw TCP for TCP-in-TCP and 4–30% for SSH-L, which is not stacked"),
("and latency costs are sub-millisecond.","and latency costs are small."),
("OpenVPN and SSH -w spent 52–72 cycles per byte and kept both cores 81–95% busy at well under 1 Gbit/s.",f"OpenVPN and SSH -w spent {CB['ovpn-udp']:.0f}–{CB['ssh-w']:.0f} cycles per byte and kept both cores 77–99% busy at under 2.3 Gbit/s."),
("wireguard-go 1.58 Gbit/s at 138% of 200%","wireguard-go 2.89 Gbit/s at 137% of 200%"),
("727 Mbit/s; 1,350 vs 105 switches/MB; cipher-neutral","2.24 Gbit/s; 1,112 vs 110 switches/MB; cipher effect within CIs"),
("SSH-L 4.10 Gbit/s; R(2%) = 1.02","SSH-L 6.48 Gbit/s; R(2%) = 0.94"),
("under BBR 28–43% below raw TCP for TCP-in-TCP, still ≥10× CUBIC","under BBR 18–44% below raw TCP for TCP-in-TCP, still ≥10× CUBIC"),
("Restricted environment.","Apple Silicon."),
("Package mirrors were unreachable, so I compiled OpenVPN, OpenSSH, iperf3, wireguard-tools, wireguard-go (with locally mirrored Go modules), libcap-ng and iproute2 from source.","I rebuilt the testbed as an arm64 VM in UTM. I compiled OpenVPN, OpenSSH, iperf3, wireguard-tools and wireguard-go from source and took everything else from Ubuntu. Absolute clean-link rates are therefore not comparable with x86 runs."),
("I wrote the TUN-based impair emulator","I used my TUN-based impair emulator"),
("Default BBR.","BBR in namespaces."),
("The VM shipped with BBR, which masked loss effects entirely. I switched the namespaces to CUBIC for the main sweep and kept BBR as an ablation.","Ubuntu defaults to CUBIC, ships BBR as a module and does not allow it inside namespaces, so a BBR run would silently stay on CUBIC. I loaded tcp_bbr, added it to the allowed list and kept BBR as an ablation."),
("Four iperf3 runs at 5% loss failed (all three SSH-L trials and one OV-T trial)","Two iperf3 runs at 5% loss failed (SSH-L trials 2 and 3)"),
("(SSH-L 87 vs. 64 Mbit/s)","(SSH-L 88 vs. 65 Mbit/s)"),
("The 28% lower bound comes from these 5% runs, whose intervals are wide (±16–18 Mbit/s).","The 18% lower bound comes from these 5% runs, whose intervals are wide (±6–22 Mbit/s)."),
("The Python RR probe adds a constant ≈50 µs to every round trip.","The Python RR probe adds a constant overhead to every round trip."),
("Under BBR, stacked tunnels ran 28–43% below plain TCP and SSH-L 4–31% below it","Under BBR, stacked tunnels ran 18–44% below plain TCP and SSH-L 4–30% below it"),
]
for o,n in A: R1(o,n)
# Table 2
T=d.tables[1]
order=['raw','wg','ovpn-udp','ovpn-udp-chacha','ovpn-tcp','ssh-L','ssh-L-aes','ssh-w']
def setc(c,t):
    p=c.paragraphs[0]; r=p.runs
    r[0].text=t
    for x in r[1:]: x.text=''
raw=C['raw']
for row,k in zip(T.rows[1:],order):
    c=C[k]
    v=[f"{c['p1'][0]:,.0f} ± {c['p1'][1]:,.0f}",f"{c['busy'][0]:.0f}",f"{c['eff'][0]:.1f}",f"{CB[k]:.1f}",f"{c['good'][0]:.1f}",f"({raw['rr64'][0]:.0f})" if k=='raw' else f"+{c['rr64'][0]-raw['rr64'][0]:.0f}",f"{c['setup_s'][0]:.2f}"]
    print(row.cells[0].text,v)
    for cell,t in zip(row.cells[1:],v): setc(cell,t)
# Table 3
T=d.tables[2]
LR=L['cubic']['raw']; rtt=s['rr_delay']['cubic']['raw'][0]/1e6
ps=['0.001','0.005','0.01','0.02','0.05']
model=[1448*8/rtt*1.2247449/float(p)**.5/1e6 for p in ps]; meas=[LR[p]['mbps'][0] for p in ps]
print(rtt,model,meas,[round(100*(1-m/x)) for m,x in zip(meas,model)])
for c,v in zip(T.rows[1].cells[1:],model): setc(c,f'{v:.1f}')
for c,v in zip(T.rows[2].cells[1:],meas): setc(c,f'{v:.1f}')
# Table 4
T=d.tables[3]
l=L['cubic']
for row,k in zip(T.rows[1:],['raw','wg','ovpn-udp','ovpn-tcp','ssh-L','ssh-w']):
    out=[]
    for p in ['0.005','0.02','0.05']:
        x=l[k][p]
        out.append(f"{x['retx_inner'][0]:,.0f} / {x['outer_retx'][0]:,.0f}" if k in('ovpn-tcp','ssh-L','ssh-w') else f"{x['retx_inner'][0]:,.0f} / —")
    out.append(f"{l[k]['0.02']['mbps'][0]/l['raw']['0.02']['mbps'][0]:.2f}")
    print(row.cells[0].text,out)
    for c,v in zip(row.cells[1:],out): setc(c,v)
# Table 5 net setup
T=d.tables[4]
for row in T.rows:
    if row.cells[0].text.startswith('Net setup'):
        for c,v in zip(row.cells[1:],['0.06 / 1.9','1.64 / 11.4','0.14 / 9.4']): setc(c,v)
    if row.cells[0].text.startswith('SLOC'):
        for c,v in zip(row.cells[1:],['8.7 k (wireguard-go)','87.1 k + OpenSSL','122.8 k']): setc(c,v)
# netem acronym
R1('missing from this kernel.','missing from my first testbed kernel.')
# figures
rels=d.part.rels
m={}
for i,sh in enumerate(d.inline_shapes):
    rid=sh._inline.graphic.graphicData.pic.blipFill.blip.embed
    m[i]=(rid,rels[rid].target_part.partname,sh.width,sh.height)
print(m)
names={2:'fig3_clean.png',3:'fig4_ctx.png',4:'fig5_cpu_latency.png',5:'fig6_loss.png',6:'fig7_bbr.png'}
for i,n in names.items():
    rels[m[i][0]].target_part._blob=open('/home/claude/figures_and_tables/figures/'+n,'rb').read()
d.save('/home/claude/report6.docx')
