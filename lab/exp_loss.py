import random,sys; sys.path.insert(0,'/opt/lab'); from run import *
CFGS=['raw','wg','ovpn-udp','ovpn-tcp','ssh-L','ssh-w']
LOSSES=[0,0.001,0.005,0.01,0.02,0.05]
CC=sys.argv[1] if len(sys.argv)>1 else 'cubic'
if CC!='cubic': LOSSES=[0.01,0.05]; CFGS=['raw','wg','ovpn-tcp','ssh-L','ssh-w']
TR=3
for n in ('cli','rtr','srv'): sh(f'ip netns exec {n} sysctl -qw net.ipv4.tcp_congestion_control={CC}')
sh('/opt/lab/servers.sh')
for cfg in CFGS:
    for t in range(1,TR+1):
        sh('/opt/lab/topo.sh clean'); sh('/opt/lab/servers.sh')
        su=tunnel_up(cfg)
        for L in LOSSES:
            sh(f'/opt/lab/topo.sh impair {L} 10 100 {1000*t+int(L*1000)}'); time.sleep(1)
            try:
                r=iperf(cfg,dur=20,par=1)
                log(f'loss_{CC}',{'cfg':cfg,'trial':t,'loss':L,'cc':CC,**r})
            except Exception as ex:
                log(f'loss_{CC}',{'cfg':cfg,'trial':t,'loss':L,'cc':CC,'mbps':0.0,'error':str(ex)[:200]})
                sh('/opt/lab/topo.sh clean'); sh('/opt/lab/servers.sh'); su=tunnel_up(cfg)
        sh('/opt/lab/topo.sh impair 0 10 100 1'); time.sleep(1)
        log(f'rr_delay_{CC}',{'cfg':cfg,'trial':t,**rr(cfg,64,300)})
sh('/opt/lab/topo.sh clean'); sh('/opt/lab/tun.sh down')
for n in ('cli','rtr','srv'): sh(f'ip netns exec {n} sysctl -qw net.ipv4.tcp_congestion_control=cubic')
print('DONE')
