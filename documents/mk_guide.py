import json,re,os,sys,copy,glob,html
import docx
from docx.shared import Pt,Inches,RGBColor,Emu
from docx.enum.text import WD_ALIGN_PARAGRAPH as AL
from docx.enum.section import WD_SECTION
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
from PIL import Image
sys.path.insert(0,'.'); sys.path.insert(0,'/tmp/claude-0/-home-claude/8542cfb7-bc59-5bbd-ab16-fe85db930752/scratchpad/guide')
import gcontent as G, steps as OLD
REC='/home/claude/cy/rec.d/'; SH='/home/claude/cy/shots/'
def rec(i): return json.load(open(REC+i+'.json'))
DISP={}
for L in (OLD.P2,OLD.P3,OLD.P4,OLD.P5,OLD.P6,OLD.P7,OLD.P8):
    for e in L:
        if e[0]=='R' and e[5]: DISP[e[1]]=e[5]
DISP['x02']='mkdir -p /mnt/share/run && cp -r ~/rerun/analysis ~/rerun/figures ~/rerun/results /mnt/share/run/ &&\ncp ~/rerun_failed.py ~/compare.py ~/clean.log ~/loss_cubic.log ~/loss_bbr.log \\\n   ~/probe.log ~/ctx.log /mnt/share/run/ && ls /mnt/share/run\nsudo tar -C /opt -czf /mnt/share/run/opt-lab-nokeys.tgz --exclude=keys lab\nls -la /mnt/share/run | wc -l'
_x=rec('x04')['cmd']
_x=_x.replace('static double now(void){struct timespec t;clock_gettime(CLOCK_MONOTONIC,&t);','static double now(void){struct timespec t;\nclock_gettime(CLOCK_MONOTONIC,&t);')
_x=_x.replace('int main(void){uint64_t n=20000000,a=1,b=3;for(int k=0;k<5;k++){uint64_t i=n;double t=now();','int main(void){uint64_t n=20000000,a=1,b=3;\nfor(int k=0;k<5;k++){uint64_t i=n;double t=now();')
_x=_x.replace('double mul=now()-t;printf("add-chain %.3f GHz   mul-chain (3 cycles) %.3f GHz\\n",n*64/add/1e9,n/3*64*3/mul/1e9);}return 0;}','double mul=now()-t;\nprintf("add-chain %.3f GHz   mul-chain (3 cycles) %.3f GHz\\n",\n  n*64/add/1e9,n/3*64*3/mul/1e9);}return 0;}')
_x=_x.replace('b.ne 1b\\n":"+r"(a)','b.ne 1b\\n"\n  :"+r"(a)').replace('b.ne 2b\\n":"+r"(a)','b.ne 2b\\n"\n  :"+r"(a)')
DISP['x04']=_x
DISP['x05']="""sudo /opt/lab/topo.sh up
sudo /opt/lab/tun.sh up ssh-L > /dev/null 2>&1
sleep 1
sudo ip netns exec cli /usr/local/bin/ssh -v -i /opt/lab/keys/id_ed25519 \\
  -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o BatchMode=yes \\\\
  root@10.0.2.2 true 2>&1 |
  grep -E "kex: algorithm|host key algorithm|kex: client->server|strict" | cut -c1-110
sudo /opt/lab/tun.sh down
sudo /opt/lab/topo.sh down
echo done"""
DISP['x08']=rec('x08')['cmd'].replace("--exclude-dir=wintun,tests --not-match","--exclude-dir=wintun,tests \\\n  --not-match").replace(" wireguard-go | tail"," \\\n  wireguard-go | tail").replace(" openssh-portable | tail"," \\\n  openssh-portable | tail")
DISP['m01']='sudo apt update\nsudo apt install -y build-essential git autoconf automake libtool pkg-config bison flex \\\n  libssl-dev zlib1g-dev libcap-ng-dev iproute2 python3 python3-venv curl tmux'
def split_cmd(c):
    if len(c)<=93 or '\n' in c: return c
    out=[];cur='';q=None;i=0
    while i<len(c):
        ch=c[i]
        if q:
            if ch==q:q=None
        elif ch in '\'"': q=ch
        if not q and c[i:i+2]=='; ':
            out.append(cur);cur='';i+=2;continue
        cur+=ch;i+=1
    out.append(cur)
    res=[]
    for l in out:
        if len(l)>93 and "'" not in l and '"' not in l: res.append(l.replace(' && ',' &&\n'))
        else: res.append(l)
    return '\n'.join(res)
def norm(s): return re.sub(r'[\s;\\]','',s.replace('\\\n',''))
# numbering
NUM={}
for title,n,intro,ids in G.SECTIONS:
    for k,i in enumerate(ids,1): NUM[i]=f'Step {n}.{k}'
NUM['x02']='Step 9.8';NUM['f06']='Step 9.9';NUM['x04']='Step 9.10';NUM['x05']='Step 9.11';NUM['x08']='Step 9.12'
NUM['mod']=NUM['m03']; NUM['refs']='Table 4'
def sub(t):
    return re.sub(r'\{(\w+)\}',lambda m:NUM[m.group(1)].replace('Step ','') if False else NUM[m.group(1)],t)
d=docx.Document('/home/claude/report5.docx')
body=d.element.body
sect=body.findall(qn('w:sectPr'))[-1]
for el in list(body):
    if el is not sect: body.remove(el)
for c in sect.findall(qn('w:cols')): sect.remove(c)
col=OxmlElement('w:cols');col.set(qn('w:space'),'720')
sect.insert(len(sect)-1,col) if False else None
# insert cols in schema position (after pgMar)
pm=sect.find(qn('w:pgMar')); pm.addnext(col)
for s in d.sections:
    for p in s.header.paragraphs:
        for r in p.runs: r.text=''
        if p.runs: p.runs[0].text='VPN vs. SSH Tunneling: Reproduction Guide'
W=d.sections[0].page_width-d.sections[0].left_margin-d.sections[0].right_margin
print('text width in',W/914400)
CW=W/914400
def para(text='',style=None,align=AL.JUSTIFY,size=None,bold=None,after=4,keep=False):
    p=d.add_paragraph(style=style)
    if align is not None: p.alignment=align
    p.paragraph_format.space_after=Pt(after)
    if keep: p.paragraph_format.keep_with_next=True
    if text:
        r=p.add_run(text)
        if size: r.font.size=Pt(size)
        if bold: r.bold=True
    return p
def lead(a,b,keep=False):
    p=para('',keep=keep); r=p.add_run(a); r.bold=True; p.add_run(sub(b)); return p
def cmd(text):
    lines=text.split('\n')
    for k,l in enumerate(lines):
        assert len(l)<=102,l
    p=d.add_paragraph(); p.paragraph_format.space_after=Pt(4); p.paragraph_format.space_before=Pt(2)
    p.paragraph_format.keep_with_next=True; p.paragraph_format.left_indent=Inches(0.06)
    ppr=p._p.get_or_add_pPr()
    sh=OxmlElement('w:shd');sh.set(qn('w:val'),'clear');sh.set(qn('w:color'),'auto');sh.set(qn('w:fill'),'EEF1F5');sp=ppr.find(qn('w:spacing'))
    sp.addprevious(sh)
    for k,l in enumerate(lines):
        r=p.add_run(l); r.font.name='Courier New'; r.font.size=Pt(7.6)
        r._r.get_or_add_rPr().rFonts.set(qn('w:cs'),'Courier New')
        if k<len(lines)-1: r.add_break()
FIG=[0]
def figure(path,cap,width=None):
    FIG[0]+=1
    p=d.add_paragraph(); p.alignment=AL.CENTER; p.paragraph_format.space_after=Pt(1); p.paragraph_format.keep_with_next=True
    p.add_run().add_picture(path,width=Inches(width or CW))
    c=d.add_paragraph(); c.alignment=AL.JUSTIFY; c.paragraph_format.space_after=Pt(6)
    r=c.add_run(f'Figure {FIG[0]}. '); r.bold=True; r.font.size=Pt(8)
    r=c.add_run(cap); r.font.size=Pt(8)
def table(rows,widths,size=8):
    t=d.add_table(rows=len(rows),cols=len(rows[0])); t.alignment=1
    t.autofit=False
    for j,wd in enumerate(widths): t.columns[j].width=Inches(wd)
    tp=t._tbl.tblPr
    b=OxmlElement('w:tblBorders')
    for e,sz in (('top',8),('bottom',8)):
        x=OxmlElement('w:'+e);x.set(qn('w:val'),'single');x.set(qn('w:sz'),str(sz));x.set(qn('w:color'),'000000');b.append(x)
    lay=tp.find(qn('w:tblLayout'))
    lay.addprevious(b)
    for i,row in enumerate(rows):
        for j,v in enumerate(row):
            c=t.cell(i,j); c.width=Inches(widths[j])
            p=c.paragraphs[0]; p.paragraph_format.space_after=Pt(0)
            r=p.add_run(sub(str(v))); r.font.size=Pt(size)
            if i==0:
                r.bold=True
                tc=c._tc.get_or_add_tcPr(); bb=OxmlElement('w:tcBorders'); x=OxmlElement('w:bottom'); x.set(qn('w:val'),'single');x.set(qn('w:sz'),'4');x.set(qn('w:color'),'000000');bb.append(x);tc.append(bb)
    trp=t.rows[0]._tr.get_or_add_trPr(); h=OxmlElement('w:tblHeader'); trp.append(h)
    for row in t.rows:
        pr=row._tr.get_or_add_trPr(); cs=OxmlElement('w:cantSplit'); pr.append(cs)
    para('',after=4)
def tcap(t):
    p=para('',align=AL.CENTER,after=2,keep=True)
    m=re.match(r'(Table \d+\.)(.*)',t)
    r=p.add_run(m.group(1));r.bold=True;r.font.size=Pt(8)
    r=p.add_run(m.group(2));r.font.size=Pt(8)
def h1(t,br=False):
    p=d.add_paragraph(t,style='Heading 1')
    return p
def h2(t): return d.add_paragraph(t,style='Heading 2')
TMP='crop'; os.makedirs(TMP,exist_ok=True)
def crop(i,k):
    im=Image.open(f'{SH}{i}_{k}.png').convert('L')
    bb=im.point(lambda v:255 if v>30 else 0).getbbox() or (0,0,1280,40)
    h=min(800,bb[3]+14)
    out=f'{TMP}/{i}_{k}.png'
    Image.open(f'{SH}{i}_{k}.png').convert('RGB').crop((0,0,1280,h)).quantize(16).save(out,optimize=True)
    return out
def step(i):
    r=rec(i); title,why,check=G.STEPS[i]
    n=NUM[i].replace('Step ','')
    p=d.add_paragraph(style='Heading 2'); p.add_run(f'Step {n}. {title}'); p.paragraph_format.keep_with_next=True
    para(sub(why),keep=True)
    show=DISP.get(i) or split_cmd(r['cmd'])
    assert norm(show)==norm(r['cmd']),(i,show,r['cmd'])
    assert r['rc']==0,i
    USED.add(i)
    cmd(show)
    pages=sorted(glob.glob(f'{SH}{i}_*.png'),key=lambda s:int(s.rsplit('_',1)[1][:-4]))
    t=r['secs']; tt=('under 1 s' if t<1 else f'{t:.0f} s' if t<60 else f'{int(t//60)} min {int(t%60)} s')
    assert pages,i
    for k,pg in enumerate(pages,1):
        o=crop(i,k)
        c=f'Console of cyborg for {NUM[i]}'+(f', screen {k} of {len(pages)}' if len(pages)>1 else '')+f'. Ran for {tt}.'
        figure(o,c)
    lead('Check. ',check)
USED=set()
# TITLE
para('A step-by-step guide to reproducing the VPN vs. SSH tunneling benchmark',align=AL.CENTER,size=16,bold=True,after=6)
para('Hubert YAKPÉ TROLINDO',align=AL.CENTER,size=11,after=0)
para('hu881229@ucf.edu',align=AL.CENTER,after=0)
para('University of Central Florida, Orlando, Florida, USA',align=AL.CENTER,after=10)
para('ABSTRACT',align=None,size=10,bold=True,after=2)
para(G.ABSTRACT)
p=para('',align=None,after=2); r=p.add_run('Code & artifacts: ');r.bold=True;p.add_run('https://github.com/cybsecoff31/vpn-vs-ssh-tunnel-benchmark')
p=para('',align=None,after=8); r=p.add_run('Keywords: ');r.bold=True;p.add_run(G.KEYWORDS)
para('CONTENTS',align=None,size=10,bold=True,after=2)
for t in ['I- INTRODUCTION','II- THE TESTBED','III- CREATING THE VIRTUAL MACHINE IN UTM']+[s[0] for s in G.SECTIONS]+['X- TROUBLESHOOTING','XI- HOW I RECORDED THIS GUIDE','XII- CONCLUDING REMARKS','REFERENCES']:
    para(t,align=None,after=0)
h1('I- INTRODUCTION')
def blocks(L):
    for b in L:
        k=b[0]
        if k=='p': para(sub(b[1]))
        elif k=='lead': lead(b[1],b[2])
        elif k=='fig': figure(b[1],sub(b[2]),b[3])
        elif k=='tcap': tcap(sub(b[1]))
        elif k=='table': table(b[1],b[2])
        elif k=='h2': h2(b[1])
        elif k=='cmd': cmd(b[1])
        elif k=='ufig':
            im=Image.open(G.B+b[1]); figure(G.B+b[1],b[2],4.6)
        elif k=='warn': lead(b[1],b[2])
        elif k=='TIMES': times()
def S(*ids): return sum(rec(i)['secs'] for i in ids)
def M(s): return f'{round(s/60)} min' if s>=60 else 'under 1 min'
def times():
    b=S('b02','b03','b04','b05','b06','b07','b08','b09','b10','b11','b12','b13')
    tcap('Table 3. Time needed on my Mac.')
    table([['Section','Work','Time'],
     ['III','Create the VM and install Ubuntu','About 15 min (estimate)'],
     ['IV','Packages, Go and system changes',M(S('m01','m02'))],
     ['V','Build the five programs',M(b)],
     ['VI–VII','Lab, keys and testbed checks',M(S('c01','c02','c03','c04','c05','c06','c07','c08','c09','c10','d01','d02','d03','d035','d04','d05','d06','d07','d08','d09','d095','d10'))],
     ['VIII','Clean-link campaign',M(S('e01'))],
     ['VIII','Loss sweep with CUBIC, including the re-run',M(S('e02','e04'))],
     ['VIII','Loss sweep with BBR, probes, context switches',M(S('e05','e055','e06','e07'))],
     ['IX','Analysis, figures, comparison and clean-up',M(S('m04','f03','f04','f05','f06'))]],[1.0,4.6,1.3])
blocks(G.INTRO)
h1('II- THE TESTBED')
blocks(G.TESTBED)
h1('III- CREATING THE VIRTUAL MACHINE IN UTM')
para('I used UTM because it runs on my Mac and gives the VM hardware virtualization. All pictures in this section are real captures of UTM on my Mac.')
blocks(G.UTM)
for title,n,intro,ids in G.SECTIONS:
    h1(title); para(sub(intro))
    for i in ids: step(i)
# 9.1 reading
s=json.load(open('/home/claude/cy/run/analysis/summary.json'));pub=json.load(open('/home/cybsec/vpn-vs-ssh-tunnel-benchmark/analysis/summary.json'))
h2('Reading the comparison')
para('Table 4 summarizes how my arm64 run compares with the x86 data stored in the repository. The two platforms differ, so only some results should match.')
tcap('Table 4. This run (arm64, UTM) against the published data (x86).')
table([['Result','This run vs. published','How to read it'],
 ['Loss sweep, CUBIC','Raw at 1%: 5.5 vs. 5.7 Mbit/s','Close. The emulated link sets these numbers'],
 ['Loss sweep, BBR','Raw at 1%: 93.9 vs. 93.0 Mbit/s','Close, as long as BBR was really active'],
 ['Clean-link throughput','Ratios of 1.6 to 3.8 in favor of arm64','Depends on the processor. Raw, SSH-L-A, SSH-L, WG lead and SSH-W is last in both runs. The three OpenVPN variants swap places, and their intervals overlap'],
 ['64-byte latency','Raw 27.4 vs. 60.3 µs','Depends on the processor'],
 ['Switches per MB, relative to WG','10–11× vs. about 13×','Same order of magnitude'],
 ['BBR penalty at 1%','OV-T −40%, SSH-L −30%, SSH-W −44%','Published: −40%, −31%, −43%'],
 ['Security probes','Same replies, same 26-byte reply and same banner','Should not change'],
 ['Failed runs','2 (SSH-L at 5%)','Published: 4. Random, so it can differ']],[1.8,2.4,2.7])
tcap('Table 5. Fields printed by analyze.py.')
table([['Field','Meaning'],
 ['P1, P4','One-stream and four-stream throughput in Mbit/s (P1 with its 95% interval)'],
 ['busy, cpu0, cpu1','Busy percentage of both vCPUs together, and of each vCPU'],
 ['daemon','CPU percentage used by the tunnel programs'],
 ['eff','Mbit/s delivered for each percent of busy CPU (metric E)'],
 ['good','Goodput ratio in percent (metric G)'],
 ['rr64, rr1k, p99','Median round trip at 64 and 1024 bytes, and 99th percentile at 64 bytes, in µs'],
 ['setup','Time and bytes to bring the tunnel up. The time includes fixed script waits'],
 ['n','Number of trials']],[1.7,5.2])
fw=4.8
figure('/home/claude/cy/run/figures/fig3_clean.png','Clean-link throughput and CPU efficiency from this run. Decimals in panel (a) are Gbit/s.',fw)
figure('/home/claude/cy/run/figures/fig6_loss.png','Loss sweep from this run with CUBIC.',fw)
h2('Saving the results and closing down')
for i in ['x02','f06']: step(i)
h2('Three extra measurements for the report')
para('I ran these three steps after the teardown, because my report needs them. Step 9.11 brings the testbed up again and removes it at the end.')
for i in ['x04','x05','x08']: step(i)
h1('X- TROUBLESHOOTING')
tcap('Table 6. Problems I met while preparing this experiment.')
table([['What appears','Cause','Fix'],
 ['topo.sh up stops with sysctl: Operation not permitted','The namespace may not select that congestion control','Run {m03} and {a10}, then topo.sh down and up'],
 ['An OpenVPN test hangs, or /tmp/ovc.log shows VERIFY KU ERROR','The certificate has no keyUsage extension','Repeat {c08} to {c10}'],
 ['iperf3 never finishes in a tunnel','The tunnel is down, and iperf3 waits forever','Press Ctrl-C, then read /tmp/ovc.log and /tmp/ovs.log, or test the tunnel as in {d10}'],
 ['sudo make install fails in OpenVPN on openvpn-examples.5','The man pages need rst2man','Use the sudo install line of {b04}'],
 ['/opt/lab/sshd_config line 9: Unsupported option UsePAM','This build has no PAM support','Harmless'],
 ['A long warning from wireguard-go','It recommends the kernel module','Harmless. I test the user-space version on purpose'],
 ['[impair] <defunct> in pgrep','The process ended but is not cleaned up yet','Harmless. It disappears within seconds'],
 ["A row in a loss file with 'sum_received' in its error field",'iperf3 returned no summary under heavy loss','Run {e04} or {e055}']],[2.6,2.0,2.3])
tcap('Table 7. Problems that can follow from a skipped step.')
table([['What appears','Likely cause','Fix'],
 ['Permission denied (publickey) in an SSH tunnel','Root is still locked','Repeat {a08}'],
 ['Privilege separation user sshd does not exist','The sshd user is missing','Repeat {a09}'],
 ['iperf3: error while loading shared libraries','ldconfig was not run','sudo ldconfig'],
 ['go: command not found in {b13}','The new PATH is not loaded','source ~/.profile'],
 ['mount: unknown filesystem type 9p','The VM uses another share mode','Set VirtFS in the Sharing settings of the VM']],[2.6,2.0,2.3])
lead('If raw TCP with BBR looks like CUBIC. ','I compare the two raw lines at 1% loss in the output of {f03}. On my run, BBR reached 93.9 Mbit/s against 5.5 Mbit/s. If the two are about equal, BBR was never active. I then repeat {m03} and {a10}, run {d035}, delete /opt/lab/results/loss_bbr.jsonl and /opt/lab/results/rr_delay_bbr.jsonl, and run {e05} again.')
lead('If a campaign is interrupted. ','exp_clean.py can continue: running it again skips what is finished. The loss sweep cannot. For CUBIC, I delete loss_cubic.jsonl and rr_delay_cubic.jsonl in /opt/lab/results, run tun.sh down and topo.sh clean, and repeat {e02}. For BBR, I do the same with the bbr files and repeat {e05}.')
lead('If the VM reboots. ','The namespaces, the BBR module and the allowed list are lost, but the results stay. These lines restore them:')
cmd('sudo modprobe tcp_bbr\nsudo sysctl -w net.ipv4.tcp_allowed_congestion_control="reno cubic bbr"\nsudo /opt/lab/topo.sh up\nsudo /opt/lab/servers.sh')
h1('XI- HOW I RECORDED THIS GUIDE')
para('I drove the UTM wizard from the Mac. The installer needed keyboard input, and the profile page and the first login were typed by hand, because I did not want a password in any file.')
para('After the first login, I mounted the shared folder and started a small Python recorder, agent.py, on tty1. To let it run unattended, I added a sudoers file for cybsec without a password. The recorder reads each command from the shared folder, runs it in a login shell as cybsec, stores the command, working folder, output, exit code and duration in one JSON record, and saves the framebuffer as a PNG file. Both agent.py and all records are in testbed.zip. The recorder is not needed to repeat the experiment, and sudo simply asks for the password instead. To remove the sudoers file afterwards:')
cmd('sudo rm /etc/sudoers.d/90-recorder')
para('A few details differ from a clean run of this guide. I ran some early checks twice while I was setting up the recorder, and the pictures show the last run. Steps 9.10 to 9.12 came after the teardown. I did not use tmux, as Section VIII explains. In testbed.zip, the folder commands holds each step as a small script, which is the easiest way to run them from the shared folder with the source command.')
h1('XII- CONCLUDING REMARKS')
para('I repeated the whole experiment on a new arm64 VM. Every step ran from the commands in this guide, and all seven tunnels worked after the fixes in Sections IV and VI. The loss sweeps stayed very close to the published x86 data, which confirms that the emulated link drives those results. Clean-link rates changed with the processor, as expected, while the main conclusions held: per-packet tunnels stay slower than byte-stream SSH, CUBIC shows no TCP-over-TCP collapse, and BBR exposes the outer-TCP penalty. My report6 uses the values of this run.')
h1('REFERENCES')
refs=["Neal Cardwell, Yuchung Cheng, C. Stephen Gunn, Soheil Hassas Yeganeh, and Van Jacobson. 2016. BBR: Congestion-Based Congestion Control. ACM Queue 14, 5 (2016), 20–53. https://doi.org/10.1145/3012426.3022184",
"Jason A. Donenfeld. 2017. WireGuard: Next Generation Kernel Network Tunnel. In Proceedings of the Network and Distributed System Security Symposium (NDSS ’17). Internet Society. https://doi.org/10.14722/ndss.2017.23160",
"Sangtae Ha, Injong Rhee, and Lisong Xu. 2008. CUBIC: A New TCP-Friendly High-Speed TCP Variant. ACM SIGOPS Operating Systems Review 42, 5 (2008), 64–74. https://doi.org/10.1145/1400097.1400105",
"Matthew Mathis, Jeffrey Semke, Jamshid Mahdavi, and Teunis Ott. 1997. The Macroscopic Behavior of the TCP Congestion Avoidance Algorithm. ACM SIGCOMM Computer Communication Review 27, 3 (1997), 67–82. https://doi.org/10.1145/263932.264023",
"Antonio Quartulli. 2022. Pushing OpenVPN down the Stack: Data Channel Offload (DCO). In Netdev 0x16, The Technical Conference on Linux Networking. Lisbon, Portugal. https://netdevconf.info/0x16/sessions/talk/pushing-openvpn-down-the-stack-data-channel-offload-dco.html",
"Diwen Xue, Reethika Ramesh, Arham Jain, Michalis Kallitsis, J. Alex Halderman, Jedidiah R. Crandall, and Roya Ensafi. 2022. OpenVPN is Open to VPN Fingerprinting. In Proceedings of the 31st USENIX Security Symposium (USENIX Security ’22). USENIX Association, Boston, MA, USA. https://www.usenix.org/conference/usenixsecurity22/presentation/xue-diwen"]
for r in refs: para(r,after=3,size=8)
d.save('Guide.docx')
print('figs',FIG[0],'steps',len(USED),sorted(set(os.path.basename(f)[:-5] for f in glob.glob(REC+'*.json'))-USED))
