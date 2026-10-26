import sys; sys.path.insert(0,'/opt/lab'); from run import *
for cfg,t in [('ssh-L',1),('ssh-L',2),('ssh-L',3),('ovpn-tcp',1)]:
    sh('/opt/lab/topo.sh clean'); sh('/opt/lab/servers.sh'); tunnel_up(cfg)
    sh(f'/opt/lab/topo.sh impair 0.05 10 100 {1000*t+50}'); time.sleep(2)
    r=iperf(cfg,dur=20,par=1); log('loss_cubic',{'cfg':cfg,'trial':t,'loss':0.05,'cc':'cubic','rerun':True,**r})
sh('/opt/lab/topo.sh clean'); sh('/opt/lab/tun.sh down')
