import os
HERE=os.path.dirname(os.path.abspath(__file__)); ROOT=os.path.dirname(HERE)
FIG=os.path.join(ROOT,'figures')
import json, matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt, numpy as np
S=json.load(open(os.path.join(HERE,'summary.json')))
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':7,'axes.linewidth':0.6,'xtick.major.width':0.6,'ytick.major.width':0.6,
                     'axes.spines.top':False,'axes.spines.right':False,'legend.frameon':False})
LAB={'raw':'Raw','wg':'WG','ovpn-udp':'OV-U','ovpn-udp-chacha':'OV-U-C','ovpn-tcp':'OV-T','ssh-L':'SSH-L','ssh-L-aes':'SSH-L-A','ssh-w':'SSH-W'}
COL={'raw':'#7f7f7f','wg':'#1f77b4','ovpn-udp':'#ff7f0e','ovpn-udp-chacha':'#ffbb78','ovpn-tcp':'#d62728','ssh-L':'#2ca02c','ssh-L-aes':'#98df8a','ssh-w':'#9467bd'}
C=S['clean']; order=[k for k in ['raw','wg','ovpn-udp','ovpn-udp-chacha','ovpn-tcp','ssh-L','ssh-L-aes','ssh-w'] if k in C]
# ---- Fig 2: clean throughput (log) + CPU efficiency
fig,(a1,a2)=plt.subplots(2,1,figsize=(3.3,3.0),gridspec_kw={'hspace':0.55})
x=np.arange(len(order)); w=0.38
for i,k in enumerate(order):
    a1.bar(i-w/2,C[k]['p1'][0],w,yerr=C[k]['p1'][1],color=COL[k],ec='black',lw=0.4,capsize=1.5,error_kw={'lw':0.6})
    a1.bar(i+w/2,C[k]['p4'][0],w,yerr=C[k]['p4'][1],color=COL[k],ec='black',lw=0.4,hatch='////',capsize=1.5,error_kw={'lw':0.6})
    a1.text(i,max(C[k]['p1'][0],C[k]['p4'][0])*1.35,f"{C[k]['p1'][0]/1000:.2f}" if C[k]['p1'][0]>=1000 else f"{C[k]['p1'][0]:.0f}",ha='center',fontsize=5.6)
a1.set_yscale('log'); a1.set_ylim(100,1.5e5); a1.set_ylabel('Throughput (Mbit/s)'); a1.set_xticks(x); a1.set_xticklabels([LAB[k] for k in order],fontsize=5.8,rotation=20)
from matplotlib.patches import Patch
a1.legend(handles=[Patch(fc='white',ec='black',lw=0.4,label='1 stream'),Patch(fc='white',ec='black',lw=0.4,hatch='////',label='4 streams')],fontsize=6,ncol=2,loc='upper right')
a1.set_title('(a) Clean-link throughput (label: 1 stream; decimals = Gbit/s)',fontsize=6.6,loc='left')
for i,k in enumerate(order):
    a2.bar(i,C[k]['eff'][0],0.6,yerr=C[k]['eff'][1],color=COL[k],ec='black',lw=0.4,capsize=1.5,error_kw={'lw':0.6})
    a2.text(i,C[k]['eff'][0]*1.35,f"{C[k]['eff'][0]:.1f}",ha='center',fontsize=5.6)
a2.set_yscale('log'); a2.set_ylim(1,1500); a2.set_ylabel('Mbit/s per vCPU-%'); a2.set_xticks(x); a2.set_xticklabels([LAB[k] for k in order],fontsize=5.8,rotation=20)
a2.set_title('(b) CPU efficiency (1 stream, both vCPUs)',fontsize=6.6,loc='left')
plt.savefig(os.path.join(FIG,'fig3_clean.png'),dpi=300,bbox_inches='tight',pad_inches=0.02)
# ---- Fig 3: loss sweep
L=S['loss'].get('cubic',{})
if L:
    fig,(a,b)=plt.subplots(2,1,figsize=(3.3,3.3),gridspec_kw={'hspace':0.5,'height_ratios':[1.35,1]})
    mk={'raw':'o','wg':'s','ovpn-udp':'^','ovpn-tcp':'v','ssh-L':'D','ssh-w':'P'}
    for k in ['raw','wg','ovpn-udp','ovpn-tcp','ssh-L','ssh-w']:
        if k not in L: continue
        ps=sorted(L[k],key=float); xs=[max(float(p)*100,0.03) for p in ps]
        ys=[L[k][p]['mbps'][0] for p in ps]; es=[L[k][p]['mbps'][1] for p in ps]
        a.errorbar(xs,ys,yerr=es,marker=mk[k],ms=3,lw=0.9,capsize=1.5,color=COL[k],label=LAB[k],elinewidth=0.6)
        if 'raw' in L:
            rel=[L[k][p]['mbps'][0]/max(1e-9,L['raw'][p]['mbps'][0]) for p in ps if p in L['raw']]
            b.plot(xs[:len(rel)],rel,marker=mk[k],ms=3,lw=0.9,color=COL[k],label=LAB[k])
    for ax in (a,b):
        ax.set_xscale('log'); ax.set_xticks([0.03,0.1,0.5,1,2,5]); ax.set_xticklabels(['0','0.1','0.5','1','2','5'])
        ax.set_xlabel('Random packet loss p (%)')
    a.set_yscale('log'); a.set_ylabel('Throughput (Mbit/s)'); a.legend(fontsize=5.8,ncol=3,loc='lower left')
    a.set_title('(a) Throughput vs. loss (100 Mbit/s, RTT 20 ms, CUBIC)',fontsize=6.6,loc='left')
    b.axhline(1,color='black',lw=0.5,ls=':'); b.set_ylabel('Retention R(p)'); b.set_title('(b) Throughput relative to raw TCP at the same p',fontsize=6.6,loc='left')
    plt.savefig(os.path.join(FIG,'fig6_loss.png'),dpi=300,bbox_inches='tight',pad_inches=0.02)
# ---- Fig 4: CUBIC vs BBR
B=S['loss'].get('bbr',{})
if B and L:
    fig,ax=plt.subplots(figsize=(3.3,1.55))
    ks=[k for k in ['raw','wg','ovpn-tcp','ssh-L','ssh-w'] if k in B]; x=np.arange(len(ks)); w=0.2
    for j,(cc,D,p,h) in enumerate([('CUBIC',L,'0.01',''),('BBR',B,'0.01',''),('CUBIC',L,'0.05','////'),('BBR',B,'0.05','////')]):
        vals=[D[k][p]['mbps'][0] for k in ks]; err=[D[k][p]['mbps'][1] for k in ks]
        ax.bar(x+(j-1.5)*w,vals,w,yerr=err,color='#4c72b0' if cc=='CUBIC' else '#dd8452',hatch=h,ec='black',lw=0.4,capsize=1.2,error_kw={'lw':0.5},
               label=f"{cc}, p={float(p)*100:.0f}%")
    ax.set_yscale('log'); ax.set_ylabel('Mbit/s'); ax.set_xticks(x); ax.set_xticklabels([LAB[k] for k in ks]); ax.legend(fontsize=5.6,ncol=2,loc='upper center',bbox_to_anchor=(0.5,1.32))
    plt.savefig(os.path.join(FIG,'fig7_bbr.png'),dpi=300,bbox_inches='tight',pad_inches=0.02)
print('figs ok')
