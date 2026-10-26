"""Supplementary: context switches per MB delivered (system-wide /proc/stat ctxt and tunnel daemons)."""
import sys; sys.path.insert(0,'/opt/lab'); from run import *
def ctx_daemons(names):
    tot=0
    for n in names:
        for pid in sh(f'pgrep -x {n}').split():
            try:
                for l in open(f'/proc/{pid}/status'):
                    if 'ctxt_switches' in l: tot+=int(l.split()[1])
            except Exception: pass
    return tot
def sysctx():
    for l in open('/proc/stat'):
        if l.startswith('ctxt'): return int(l.split()[1])
sh('/opt/lab/topo.sh clean'); sh('/opt/lab/servers.sh')
for t in range(1,4):
  for cfg in ['raw','wg','ovpn-udp','ovpn-tcp','ssh-L','ssh-w']:
    tunnel_up(cfg); time.sleep(1); h,p,_=target()
    c0=sysctx(); d0=ctx_daemons(DAEMONS[cfg])
    j=json.loads(ns('cli',f'timeout 60 taskset -c 0 iperf3 -c {h} -p {p} -t 10 -O 0 -J'))
    c1=sysctx(); d1=ctx_daemons(DAEMONS[cfg]); mb=j['end']['sum_received']['bytes']/1e6
    log('ctx',{'cfg':cfg,'trial':t,'mbps':j['end']['sum_received']['bits_per_second']/1e6,'sys_ctx_per_mb':(c1-c0)/mb,'daemon_ctx_per_mb':(d1-d0)/mb})
sh('/opt/lab/tun.sh down'); print('DONE')
