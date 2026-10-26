#!/usr/bin/env python3
# TCP request/response latency probe (netperf TCP_RR style).
# server: rr.py s <port> ; client: rr.py c <host> <port> <size> <count>
import socket,sys,time,json,statistics
def recvn(c,n):
    b=bytearray()
    while len(b)<n:
        d=c.recv(n-len(b))
        if not d: raise EOFError
        b+=d
    return b
if sys.argv[1]=='s':
    import threading
    ls=socket.socket(); ls.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
    ls.bind(('0.0.0.0',int(sys.argv[2]))); ls.listen(64)
    def h(c):
        c.setsockopt(socket.IPPROTO_TCP,socket.TCP_NODELAY,1)
        try:
            while True:
                hdr=recvn(c,4); n=int.from_bytes(hdr,'big'); data=recvn(c,n); c.sendall(hdr+data)
        except Exception: pass
    while True:
        c,_=ls.accept(); threading.Thread(target=h,args=(c,),daemon=True).start()
else:
    host,port,size,count=sys.argv[2],int(sys.argv[3]),int(sys.argv[4]),int(sys.argv[5])
    c=socket.create_connection((host,port)); c.setsockopt(socket.IPPROTO_TCP,socket.TCP_NODELAY,1)
    payload=b'x'*size; msg=size.to_bytes(4,'big')+payload; lat=[]
    for _ in range(20): c.sendall(msg); recvn(c,4+size)   # warm-up
    for _ in range(count):
        t=time.perf_counter_ns(); c.sendall(msg); recvn(c,4+size); lat.append((time.perf_counter_ns()-t)/1e3)
    lat.sort()
    print(json.dumps({'size':size,'n':count,'median_us':statistics.median(lat),'mean_us':statistics.mean(lat),'p99_us':lat[int(0.99*count)-1],'p01_us':lat[int(0.01*count)]}))
