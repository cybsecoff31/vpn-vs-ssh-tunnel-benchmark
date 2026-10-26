import os
HERE=os.path.dirname(os.path.abspath(__file__)); ROOT=os.path.dirname(HERE)
FIG=os.path.join(ROOT,'figures')
import json,glob,statistics as st,math,os,collections
R=os.path.join(ROOT,'results')
def load(n):
    p=f'{R}/{n}.jsonl'
    rows=[json.loads(l) for l in open(p)] if os.path.exists(p) else []
    seen={}
    for r in rows: seen[(r.get('cfg'),r.get('trial'),r.get('size'),r.get('loss'),r.get('par'))]=r  # keep latest
    return list(seen.values())
T95={1:12.706,2:4.303,3:3.182,4:2.776,5:2.571,6:2.447,9:2.262}
def ms(v):
    v=[x for x in v if x is not None]
    if not v: return (float('nan'),0,0)
    m=st.mean(v); 
    if len(v)<2: return (m,0,len(v))
    return (m,T95.get(len(v)-1,2.0)*st.stdev(v)/math.sqrt(len(v)),len(v))
NAMES={'raw':'Raw TCP','wg':'WireGuard','ovpn-udp':'OpenVPN-UDP','ovpn-tcp':'OpenVPN-TCP','ovpn-udp-chacha':'OpenVPN-UDP (ChaCha)',
       'ssh-L':'SSH -L','ssh-L-aes':'SSH -L (AES-GCM)','ssh-w':'SSH -w'}
ORDER=['raw','wg','ovpn-udp','ovpn-udp-chacha','ovpn-tcp','ssh-L','ssh-L-aes','ssh-w']
def by(rows,*keys):
    g=collections.defaultdict(list)
    for r in rows: g[tuple(r[k] for k in keys)].append(r)
    return g
S={}
p1=by(load('clean_p1'),'cfg'); p4=by(load('clean_p4'),'cfg'); rr=by(load('rr'),'cfg','size'); su=by(load('setup'),'cfg')
for c in ORDER:
    if (c,) not in p1: continue
    rows=p1[(c,)]
    busy=[r['cpu_busy']['cpu0']+r['cpu_busy']['cpu1'] for r in rows]
    eff=[r['mbps']/(r['cpu_busy']['cpu0']+r['cpu_busy']['cpu1']) for r in rows]
    good=[100*(r['rcv_bytes_meas']/r['rcv_seconds'])/(r['wire_tx_bytes']/r['wall']) for r in rows]
    S[c]={'p1':ms([r['mbps'] for r in rows]),'p4':ms([r['mbps'] for r in p4.get((c,),[])]),
          'busy':ms(busy),'cpu0':ms([r['cpu_busy']['cpu0'] for r in rows]),'cpu1':ms([r['cpu_busy']['cpu1'] for r in rows]),
          'daemon':ms([r['daemon_cpu_pct'] for r in rows]),'eff':ms(eff),'good':ms(good),
          'sysirq':ms([r['cpu_sysirq']['cpu0']+r['cpu_sysirq']['cpu1'] for r in rows]),
          'rr64':ms([r['median_us'] for r in rr.get((c,64),[])]),'rr1024':ms([r['median_us'] for r in rr.get((c,1024),[])]),
          'p99_64':ms([r['p99_us'] for r in rr.get((c,64),[])]),
          'setup_s':ms([r['setup_s'] for r in su.get((c,),[])]),'setup_kb':ms([r['setup_bytes']/1024 for r in su.get((c,),[])]),
          'setup_pkts':ms([r['setup_pkts'] for r in su.get((c,),[])])}
L={}
for cc in ('cubic','bbr'):
    for (c,l),rows in by(load(f'loss_{cc}'),'cfg','loss').items():
        L.setdefault(cc,{}).setdefault(c,{})[l]={'mbps':ms([r['mbps'] for r in rows]),'retx_inner':ms([r.get('inner_retx',0) for r in rows]),
              'outer_retx':ms([max(0,r.get('tcp_retx_ns',0)-r.get('inner_retx',0)) for r in rows])}
RD={}
for cc in ('cubic','bbr'):
    for (c,),rows in by(load(f'rr_delay_{cc}'),'cfg').items(): RD.setdefault(cc,{})[c]=ms([r['median_us'] for r in rows])
CX={}
for (c,),rows in by(load('ctx'),'cfg').items():
    CX[c]={'sys':st.mean(r['sys_ctx_per_mb'] for r in rows),'dmn':st.mean(r['daemon_ctx_per_mb'] for r in rows),'mbps':st.mean(r['mbps'] for r in rows)}
json.dump(CX,open(os.path.join(HERE,'ctx.json'),'w'))
json.dump({'clean':S,'loss':L,'rr_delay':RD},open(os.path.join(HERE,'summary.json'),'w'),indent=1)
if __name__=='__main__':
    for c,v in S.items():
        print(f"{c:16s} P1 {v['p1'][0]:8.1f}±{v['p1'][1]:6.1f} P4 {v['p4'][0]:8.1f} busy {v['busy'][0]:6.1f} cpu0 {v['cpu0'][0]:5.1f} cpu1 {v['cpu1'][0]:5.1f} daemon {v['daemon'][0]:6.1f} eff {v['eff'][0]:6.2f} good {v['good'][0]:5.1f} rr64 {v['rr64'][0]:6.1f} rr1k {v['rr1024'][0]:6.1f} p99 {v['p99_64'][0]:6.1f} setup {v['setup_s'][0]:.2f}s {v['setup_kb'][0]:.1f}KB n={v['p1'][2]}")
    for cc,d in L.items():
        for c,dd in d.items(): print(cc,c,{k:round(v['mbps'][0],2) for k,v in sorted(dd.items())})
