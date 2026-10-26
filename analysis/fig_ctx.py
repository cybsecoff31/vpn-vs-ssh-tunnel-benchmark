import os
HERE=os.path.dirname(os.path.abspath(__file__)); ROOT=os.path.dirname(HERE)
FIG=os.path.join(ROOT,'figures')
import json, numpy as np, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':7,'axes.spines.top':False,'axes.spines.right':False})
X=json.load(open(os.path.join(HERE,'ctx.json')))
LAB={'raw':'Raw','wg':'WG','ovpn-udp':'OV-U','ovpn-tcp':'OV-T','ssh-L':'SSH-L','ssh-w':'SSH-W'}
COL={'raw':'#7f7f7f','wg':'#1f77b4','ovpn-udp':'#ff7f0e','ovpn-tcp':'#d62728','ssh-L':'#2ca02c','ssh-w':'#9467bd'}
fig,ax=plt.subplots(figsize=(3.3,1.7))
xs=[];ys=[]
for k,v in X.items():
    ax.scatter(v['sys'],v['mbps'],s=22,color=COL[k],ec='black',lw=0.4,zorder=3)
    dx,dy,ha={'ovpn-udp':(1.12,1.15,'left'),'ovpn-tcp':(0.85,1.0,'right'),'ssh-w':(1.12,0.85,'left'),'ssh-L':(0.85,1.0,'right')}.get(k,(1.15,1.0,'left'))
    ax.text(v['sys']*dx,v['mbps']*dy,LAB[k],fontsize=6.2,va='center',ha=ha)
    xs.append(np.log10(v['sys'])); ys.append(np.log10(v['mbps']))
r=np.corrcoef(xs,ys)[0,1]; m,c=np.polyfit(xs,ys,1)
gx=np.linspace(min(xs)-0.1,max(xs)+0.1,10); ax.plot(10**gx,10**(m*gx+c),ls='--',lw=0.7,color='black')
ax.set_xscale('log'); ax.set_yscale('log'); ax.set_xlabel('Context switches per MB delivered'); ax.set_ylabel('Throughput (Mbit/s)')
ax.text(0.98,0.92,f'log–log fit: slope {m:.2f}, r = {r:.2f}',transform=ax.transAxes,ha='right',fontsize=6.2)
ax.set_xlim(5,4000); ax.set_ylim(300,6e4)
plt.savefig(os.path.join(FIG,'fig4_ctx.png'),dpi=300,bbox_inches='tight',pad_inches=0.02)
json.dump({'r':r,'slope':m},open(os.path.join(HERE,'ctxfit.json'),'w')); print(r,m)
