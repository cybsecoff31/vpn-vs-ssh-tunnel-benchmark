import json,sys,os,time
S=os.path.dirname(os.path.abspath(__file__))
n=int(os.environ.get('N',900))
t=time.time()
last=sys.argv[-1]
while time.time()-t<38 and not os.path.exists(f'{S}/rec.d/{last}.json'): time.sleep(1)
for i in sys.argv[1:]:
    f=f'{S}/rec.d/{i}.json'
    if os.path.exists(f):
        d=json.load(open(f)); print(f"### {i} rc={d['rc']} {d['secs']}s {d['cwd']}\n{d['out'][-n:]}")
    else: print('###',i,'pending')
