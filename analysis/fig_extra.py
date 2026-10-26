import os
HERE=os.path.dirname(os.path.abspath(__file__)); ROOT=os.path.dirname(HERE)
FIG=os.path.join(ROOT,'figures')
import json, matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt, numpy as np
from matplotlib.patches import Rectangle
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':7,'axes.spines.top':False,'axes.spines.right':False,'legend.frameon':False})
# ---- encapsulation stacks
stacks=[('Raw',['App','TCP','IP']),
        ('WG',['App','TCP','IP','WG hdr','UDP','IP']),
        ('OV-U',['App','TCP','IP','OVPN hdr','UDP','IP']),
        ('OV-T',['App','TCP','IP','OVPN hdr','TCP','IP']),
        ('SSH-L',['App','SSH chan','SSH trans','TCP','IP']),
        ('SSH-W',['App','TCP','IP','SSH chan','SSH trans','TCP','IP'])]
col={'App':'#eeeeee','TCP':'#f4a6a6','IP':'#cfe2f3','UDP':'#b6d7a8','WG hdr':'#9fc5e8','OVPN hdr':'#f9cb9c','SSH chan':'#d9d2e9','SSH trans':'#b4a7d6'}
fig,ax=plt.subplots(figsize=(3.3,2.05)); ax.set_xlim(0,7.4); ax.set_ylim(-0.6,6.1); ax.axis('off')
for i,(n,s) in enumerate(stacks):
    x=0.3+i*1.18
    ax.text(x+0.5,5.85,n,ha='center',fontsize=7,fontweight='bold')
    for j,l in enumerate(s):
        y=5.2-j*0.75
        enc = n!='Raw' and ((j>=0 and j<3 and n not in('SSH-L',)) or (n=='SSH-L' and j<3))
        tcpdup = l=='TCP' and n in ('OV-T','SSH-W')
        ax.add_patch(Rectangle((x,y),1.0,0.62,fc=col[l],ec='#c00000' if tcpdup else '#333',lw=1.4 if tcpdup else 0.5))
        ax.text(x+0.5,y+0.31,l,ha='center',va='center',fontsize=5.0)
    # encrypted bracket
    if n=='Raw': continue
    k = {'WG':3,'OV-U':3,'OV-T':3,'SSH-L':1,'SSH-W':3}[n]
    ytop=5.82; ybot=5.2-(k-1)*0.75
    ax.plot([x-0.07,x-0.07],[ybot,ytop-0.01],color='#2e7d32',lw=1.6)
ax.plot([0.25,0.55],[-0.35,-0.35],color='#2e7d32',lw=1.6); ax.text(0.62,-0.35,'encrypted payload',va='center',fontsize=5.8)
ax.add_patch(Rectangle((3.15,-0.52),0.3,0.32,fc=col['TCP'],ec='#c00000',lw=1.4)); ax.text(3.52,-0.35,'TCP carried twice (TCP-in-TCP)',va='center',fontsize=5.8)
plt.savefig(os.path.join(FIG,'fig2_stacks.png'),dpi=300,bbox_inches='tight',pad_inches=0.02)
# ---- CPU attribution + latency
S=json.load(open(os.path.join(HERE,'summary.json')))['clean']
order=['raw','wg','ovpn-udp','ovpn-tcp','ssh-L','ssh-L-aes','ssh-w']
LAB={'raw':'Raw','wg':'WG','ovpn-udp':'OV-U','ovpn-tcp':'OV-T','ssh-L':'SSH-L','ssh-L-aes':'SSH-L-A','ssh-w':'SSH-W'}
fig,(a,b)=plt.subplots(1,2,figsize=(3.3,1.75),gridspec_kw={'wspace':0.45})
x=np.arange(len(order))
dm=[S[k]['daemon'][0] for k in order]; rest=[S[k]['busy'][0]-S[k]['daemon'][0] for k in order]
a.bar(x,dm,0.65,color='#4c72b0',ec='black',lw=0.4,label='tunnel daemons (user+sys)')
a.bar(x,rest,0.65,bottom=dm,color='#c7c7c7',ec='black',lw=0.4,label='kernel + iperf3')
a.set_ylim(0,270); a.set_ylabel('CPU (% of one vCPU)'); a.set_xticks(x); a.set_xticklabels([LAB[k] for k in order],rotation=60,fontsize=5.6)
a.legend(fontsize=5.0,loc='upper left',ncol=1); a.set_title('(a) CPU attribution',fontsize=6.4,loc='left')
med=[S[k]['rr64'][0] for k in order]; p99=[S[k]['p99_64'][0] for k in order]
b.bar(x-0.18,med,0.36,yerr=[S[k]['rr64'][1] for k in order],color='#55a868',ec='black',lw=0.4,capsize=1.2,error_kw={'lw':0.5},label='median')
b.bar(x+0.18,p99,0.36,color='#c44e52',ec='black',lw=0.4,label='p99')
b.set_ylabel('64 B RTT (µs)'); b.set_xticks(x); b.set_xticklabels([LAB[k] for k in order],rotation=60,fontsize=5.6)
b.set_ylim(0,520); b.legend(fontsize=5.0,ncol=2,loc='upper left'); b.set_title('(b) Request/response latency',fontsize=6.4,loc='left')
plt.savefig(os.path.join(FIG,'fig5_cpu_latency.png'),dpi=300,bbox_inches='tight',pad_inches=0.02)
print('ok')
