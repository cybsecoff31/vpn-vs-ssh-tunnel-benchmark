"""On-path unauthenticated probing from the router namespace (attacker position)."""
import subprocess as sp, json, time, os, sys
sys.path.insert(0,'/opt/lab'); from run import sh, tunnel_up
PY=r'''
import socket,os,sys,json,time
res={}
def udp(port,payload,label):
    s=socket.socket(socket.AF_INET,socket.SOCK_DGRAM); s.settimeout(3)
    s.sendto(payload,('10.0.2.2',port))
    try: d,_=s.recvfrom(4096); res[label]={'reply':True,'bytes':len(d)}
    except socket.timeout: res[label]={'reply':False}
def tcp(port,payload,label):
    try: s=socket.create_connection(('10.0.2.2',port),timeout=3); s.settimeout(3)
    except Exception as e: res[label]={'connect':False,'error':type(e).__name__}; return
    try: banner=s.recv(256)
    except socket.timeout: banner=b''
    out={'connect':True,'banner':banner.decode(errors="replace").strip()}
    if payload:
        try: s.sendall(payload); d=s.recv(256); out['after_garbage']='data' if d else 'closed'
        except Exception as e: out['after_garbage']=type(e).__name__
    res[label]=out
mode=sys.argv[1]
hr=bytes([0x38])+os.urandom(8)+bytes([0])+(0).to_bytes(4,'big')   # P_CONTROL_HARD_RESET_CLIENT_V2
if mode=='wg':
    udp(51820,os.urandom(148),'wg_random148'); udp(51820,bytes([1,0,0,0])+os.urandom(144),'wg_fake_init')
elif mode=='ovpn-tc': udp(1194,hr,'ovpn_udp_tlscrypt_hardreset'); udp(1194,os.urandom(64),'ovpn_udp_tlscrypt_random')
elif mode=='ovpn-notc': udp(1194,hr,'ovpn_udp_plain_hardreset')
elif mode=='ovpn-tcp': tcp(1194,os.urandom(64),'ovpn_tcp_tlscrypt')
elif mode=='ssh': tcp(22,b'garbage\r\n','ssh')
print(json.dumps(res))
'''
open('/tmp/probe_in.py','w').write(PY)
def probe(m): return json.loads(sh(f'ip netns exec rtr python3 /tmp/probe_in.py {m}'))
sh('/opt/lab/topo.sh clean'); out={}
tunnel_up('wg'); out.update(probe('wg'))
tunnel_up('ovpn-udp'); out.update(probe('ovpn-tc'))
tunnel_up('ovpn-tcp'); r=probe('ovpn-tcp'); out['ovpn_tcp_while_peer_connected']=r['ovpn_tcp_tlscrypt']
sh('/opt/lab/tun.sh down'); K0='/opt/lab/keys'
sh(f'ip netns exec srv openvpn --daemon ovt --log /tmp/ovt.log --dev ovs --dev-type tun --cipher AES-256-GCM --data-ciphers AES-256-GCM --ca {K0}/ca.crt --tls-crypt {K0}/tc.key --proto tcp4-server --local 10.0.2.2 --port 1194 --tls-server --dh none --cert {K0}/server.crt --key {K0}/server.key --ifconfig 10.9.0.1 10.9.0.2')
time.sleep(1); out.update(probe('ovpn-tcp'))
sh('/opt/lab/tun.sh down')
K='/opt/lab/keys'
sh(f'ip netns exec srv openvpn --daemon ovp --log /tmp/ovp.log --dev ovs --dev-type tun --proto udp4 --local 10.0.2.2 --port 1194 --tls-server --dh none --ca {K}/ca.crt --cert {K}/server.crt --key {K}/server.key --ifconfig 10.9.0.1 10.9.0.2')
time.sleep(1); out.update(probe('ovpn-notc')); sh('/opt/lab/tun.sh down')
tunnel_up('ssh-L'); out.update(probe('ssh')); sh('/opt/lab/tun.sh down')
json.dump(out,open('/opt/lab/results/probe.json','w'),indent=1); print(json.dumps(out,indent=1))
