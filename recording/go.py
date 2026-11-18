#!/usr/bin/env python3
# usage: go.py id [id...]  enqueue plan steps; wait up to 38 s for last
import json,sys,time,os
S=os.path.dirname(os.path.abspath(__file__))
P={x['id']:x for x in json.load(open(S+'/plan.json'))}
t=time.time()
for k,i in enumerate(sys.argv[1:]):
    json.dump(P[i],open(f'{S}/q/{int(t)}{k:03d}-{i}.json.tmp','w'))
    os.replace(f'{S}/q/{int(t)}{k:03d}-{i}.json.tmp',f'{S}/q/{int(t)}{k:03d}-{i}.json')
last=sys.argv[-1]
while time.time()-t<38:
    if os.path.exists(f'{S}/rec.d/{last}.json'): break
    time.sleep(1)
for i in sys.argv[1:]:
    f=f'{S}/rec.d/{i}.json'
    if os.path.exists(f):
        d=json.load(open(f)); print(f"### {i} rc={d['rc']} {d['secs']}s {d['cwd']}\n$ {d['cmd'][:200]}\n{d['out'][-1800:]}")
    else: print('###',i,'pending')
