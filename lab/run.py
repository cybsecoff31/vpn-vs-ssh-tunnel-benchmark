#!/usr/bin/env python3
"""Experiment orchestrator. Writes one JSON object per trial to results/*.jsonl"""
import subprocess as sp, json, time, sys, os, socket
LAB='/opt/lab'; os.makedirs(f'{LAB}/results',exist_ok=True)
def sh(cmd,check=False,cap=True):
    r=sp.run(cmd,shell=True,capture_output=cap,text=True)
    return r.stdout
def ns(n,cmd): return sh(f'ip netns exec {n} {cmd}')
def ifbytes(n,dev):
    o=ns(n,f'cat /sys/class/net/{dev}/statistics/tx_bytes /sys/class/net/{dev}/statistics/rx_bytes /sys/class/net/{dev}/statistics/tx_packets /sys/class/net/{dev}/statistics/rx_packets')
    return tuple(int(x) for x in o.split())
def cpustat():
    out={}
    for line in open('/proc/stat'):
        if line.startswith('cpu') and line[3].isdigit():
            f=line.split(); v=list(map(int,f[1:9])); idle=v[3]+v[4]; out[f[0]]=(sum(v),idle,v[0]+v[1],v[2],v[5]+v[6])  # total,idle,user,sys,irq+softirq
    return out
def proc_cpu(names):
    tot=0
    for n in names:
        for pid in sh(f'pgrep -x {n}').split():
            try:
                f=open(f'/proc/{pid}/stat').read().rsplit(')',1)[1].split(); tot+=int(f[11])+int(f[12])
            except Exception: pass
    return tot/os.sysconf('SC_CLK_TCK')
DAEMONS={'raw':[], 'wg':['wireguard-go'], 'ovpn-udp':['openvpn'],'ovpn-tcp':['openvpn'],'ovpn-udp-chacha':['openvpn'],
         'ssh-L':['ssh','sshd-session'],'ssh-L-aes':['ssh','sshd-session'],'ssh-w':['ssh','sshd-session']}
def retrans(n):
    lines=[l.split() for l in ns(n,'cat /proc/net/snmp').splitlines() if l.startswith('Tcp:')]
    d=dict(zip(lines[0][1:],lines[1][1:])); return int(d['RetransSegs']),int(d['OutSegs'])
def target():
    h,p,r=open('/tmp/lab_target').read().split(); return h,int(p),int(r)
def wait_up(h,p,timeout=30):
    t0=time.time()
    while time.time()-t0<timeout:
        r=sp.run(f"ip netns exec cli python3 -c \"import socket;socket.create_connection(('{h}',{p}),timeout=0.5)\"",shell=True,capture_output=True)
        if r.returncode==0: return time.time()-t0
        time.sleep(0.05)
    raise RuntimeError('tunnel not up')
def tunnel_up(cfg):
    sh(f'{LAB}/tun.sh down'); time.sleep(0.3)
    b0=ifbytes('cli','vc0'); t0=time.time()
    sh(f'{LAB}/tun.sh up {cfg}')
    h,p,r=target(); wait_up(h,p); dt=time.time()-t0
    b1=ifbytes('cli','vc0')
    return {'setup_s':dt,'setup_bytes':(b1[0]-b0[0])+(b1[1]-b0[1]),'setup_pkts':(b1[2]-b0[2])+(b1[3]-b0[3])}
def iperf(cfg,dur=20,par=1,omit=2,cc=None):
    h,p,_=target()
    c0=cpustat(); p0=proc_cpu(DAEMONS[cfg]); b0=ifbytes('cli','vc0'); r0=retrans('cli')
    extra=f'-C {cc}' if cc else ''
    out=ns('cli',f'timeout 90 taskset -c 0 iperf3 -c {h} -p {p} -t {dur} -O {omit} -P {par} -J {extra}')
    c1=cpustat(); p1=proc_cpu(DAEMONS[cfg]); b1=ifbytes('cli','vc0'); r1=retrans('cli')
    j=json.loads(out); e=j['end']
    rcv=e['sum_received']; snt=e['sum_sent']
    busy={k:100*(1-(c1[k][1]-c0[k][1])/max(1,c1[k][0]-c0[k][0])) for k in c0}
    sysirq={k:100*((c1[k][3]-c0[k][3])+(c1[k][4]-c0[k][4]))/max(1,c1[k][0]-c0[k][0]) for k in c0}
    wall=dur+omit
    payload=snt['bytes']  # bytes accepted by sender over measured interval (excl omit)
    return {'mbps':rcv['bits_per_second']/1e6,'inner_retx':snt.get('retransmits',0),
            'cpu_busy':busy,'cpu_sysirq':sysirq,'daemon_cpu_pct':100*(p1-p0)/wall,
            'wire_tx_bytes':b1[0]-b0[0],'wire_rx_bytes':b1[1]-b0[1],'wire_tx_pkts':b1[2]-b0[2],
            'rcv_bytes_meas':rcv['bytes'],'rcv_seconds':rcv['seconds'],'wall':wall,
            'tcp_retx_ns':r1[0]-r0[0],'tcp_out_ns':r1[1]-r0[1]}
def rr(cfg,size,count):
    h,_,r=target()
    return json.loads(ns('cli',f'taskset -c 0 python3 {LAB}/rr.py c {h} {r} {size} {count}'))
def log(fn,rec):
    rec['ts']=time.time()
    with open(f'{LAB}/results/{fn}.jsonl','a') as f: f.write(json.dumps(rec)+'\n')
    print(fn,{k:(round(v,2) if isinstance(v,float) else v) for k,v in rec.items() if k in('cfg','loss','trial','mbps','median_us','setup_s','daemon_cpu_pct','par','size','cc')},flush=True)
