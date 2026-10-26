import random,sys; sys.path.insert(0,'/opt/lab'); from run import *
CFGS=['raw','wg','ovpn-udp','ovpn-tcp','ovpn-udp-chacha','ssh-L','ssh-L-aes','ssh-w']
sh('/opt/lab/topo.sh clean'); sh('/opt/lab/servers.sh')
random.seed(7)
import json as _j
done=set()
try:
    for l in open('/opt/lab/results/rr.jsonl'):
        r=_j.loads(l)
        if r['size']==1024: done.add((r['cfg'],r['trial']))
except FileNotFoundError: pass
for t in range(1,6):
    order=CFGS[:]; random.shuffle(order)
    for cfg in order:
        if (cfg,t) in done: continue
        su=tunnel_up(cfg); log('setup',{'cfg':cfg,'trial':t,**su}); time.sleep(1)
        r=iperf(cfg,dur=20,par=1); log('clean_p1',{'cfg':cfg,'trial':t,'par':1,**r})
        if t<=3:
            r=iperf(cfg,dur=20,par=4); log('clean_p4',{'cfg':cfg,'trial':t,'par':4,**r})
        for size in (64,1024):
            log('rr',{'cfg':cfg,'trial':t,**rr(cfg,size,3000)})
sh('/opt/lab/tun.sh down'); print('DONE')
