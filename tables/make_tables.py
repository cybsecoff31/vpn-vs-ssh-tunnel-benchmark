#!/usr/bin/env python3
"""Rebuilds Tables 1-7 of the report as CSV files and one Markdown file.
Measured cells come from analysis/summary.json, analysis/ctx.json, results/probe.json and tables/inputs.json.
Run analysis/analyze.py first. Cells marked with their source in tables/TABLE_SOURCES.md are written by hand."""
import csv, json, os
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
S = json.load(open(ROOT + '/analysis/summary.json'))
CTX = json.load(open(ROOT + '/analysis/ctx.json'))
PROBE = json.load(open(ROOT + '/results/probe.json'))
IN = json.load(open(HERE + '/inputs.json'))
C, L, RD = S['clean'], S['loss'], S['rr_delay']
F = IN['clock_ghz'] * 1e9
LAB = {'raw': 'Raw', 'wg': 'WG', 'ovpn-udp': 'OV-U', 'ovpn-udp-chacha': 'OV-U-C', 'ovpn-tcp': 'OV-T',
       'ssh-L': 'SSH-L', 'ssh-L-aes': 'SSH-L-A', 'ssh-w': 'SSH-W'}
def cycles(k):                    # equation (6) of the report
    return C[k]['busy'][0] / 100 * F / (C[k]['p1'][0] * 1e6 / 8)
T = {}
T[1] = [['ID', 'Layer / transport', 'Crypto (data / handshake)', 'Path'],
 ['Raw', 'none / TCP', '—', 'kernel'],
 ['WG', 'L3 / UDP', 'ChaCha20-Poly1305 / Noise IK, X25519', 'user (wg-go)'],
 ['OV-U', 'L3 / UDP', 'AES-256-GCM / TLS 1.3, RSA-4096', 'user'],
 ['OV-U-C', 'L3 / UDP', 'ChaCha20-Poly1305 / same', 'user'],
 ['OV-T', 'L3 / TCP', 'AES-256-GCM / same', 'user'],
 ['SSH-L', 'L7 / TCP', 'chacha20-poly1305@openssh / Ed25519', 'user'],
 ['SSH-L-A', 'L7 / TCP', 'aes256-gcm@openssh / Ed25519', 'user'],
 ['SSH-W', 'L3 / TCP', 'chacha20-poly1305@openssh / Ed25519', 'user']]
# Table 2: clean link
T[2] = [['Config', 'T (Mbit/s)', 'U0+U1 (%)', 'E', 'CB', 'G (%)', 'dRTT64 (us)', 'Setup (s)']]
for k in LAB:
    c = C[k]; d = c['rr64'][0] - C['raw']['rr64'][0]
    T[2].append([LAB[k], f"{c['p1'][0]:,.0f} ± {c['p1'][1]:,.0f}", f"{c['busy'][0]:.0f}", f"{c['eff'][0]:.1f}",
                 f"{cycles(k):.1f}", f"{c['good'][0]:.1f}",
                 f"({c['rr64'][0]:.0f})" if k == 'raw' else f"+{d:.0f}", f"{c['setup_s'][0]:.2f}"])
# Table 3: Mathis model with the measured RTT of raw TCP
ps = ['0.001', '0.005', '0.01', '0.02', '0.05']
rtt = RD['cubic']['raw'][0] / 1e6
model = [1448 * 8 / rtt * (3 / 2) ** .5 / float(p) ** .5 / 1e6 for p in ps]
T[3] = [['p (%)', '0.1', '0.5', '1', '2', '5'], ['Model (Mbit/s)'] + [f'{v:.1f}' for v in model],
        ['Measured (Mbit/s)'] + [f"{L['cubic']['raw'][p]['mbps'][0]:.1f}" for p in ps]]
# Table 4: retransmissions
T[4] = [['Config', 'p = 0.5%', 'p = 2%', 'p = 5%', 'R(2%)']]
l = L['cubic']
for k in ['raw', 'wg', 'ovpn-udp', 'ovpn-tcp', 'ssh-L', 'ssh-w']:
    r = [LAB[k]]
    for p in ['0.005', '0.02', '0.05']:
        x = l[k][p]
        r.append(f"{x['retx_inner'][0]:,.0f} / {x['outer_retx'][0]:,.0f}" if k in ('ovpn-tcp', 'ssh-L', 'ssh-w')
                 else f"{x['retx_inner'][0]:,.0f} / —")
    r.append(f"{l[k]['0.02']['mbps'][0] / l['raw']['0.02']['mbps'][0]:.2f}")
    T[4].append(r)
# Table 5: security
sl = IN['sloc']
reply = PROBE['ovpn_udp_plain_hardreset']
T[5] = [['Property', 'WireGuard', 'OpenVPN', 'SSH'],
 ['Handshake', 'Noise IK, 1-RTT, X25519 (Perrin, 2018)', 'TLS 1.3 + X.509 (RSA-4096) (Rescorla, 2018)', 'ML-KEM-768+X25519†, Ed25519'],
 ['Crypto agility', 'none (fixed suite)', 'negotiated; legacy BF-CBC risk (Bhargavan & Leurent, 2016)', 'negotiated'],
 ['Formal / attacks', 'proofs (Dowling & Paterson, 2018; Lipp et al., 2019)', 'Sweet32 (Bhargavan & Leurent, 2016), fingerprint (Xue et al., 2022)', 'Terrapin (Bäumer et al., 2024), CBC leak (Albrecht et al., 2009)'],
 ['Unauth. probe†', 'silent' if not PROBE['wg_fake_init']['reply'] else 'reply',
  ('silent' if not PROBE['ovpn_udp_tlscrypt_hardreset']['reply'] else 'reply') + f" (tls-crypt; TCP port visible); {reply['bytes']} B reply w/o", 'version banner'],
 ['Access scope', 'routed subnet', 'routed subnet', '-L: one port; -w: subnet'],
 ['Net setup† (s / KB)', f"{C['wg']['setup_s'][0]:.2f} / {C['wg']['setup_kb'][0]:.1f}",
  f"{C['ovpn-udp']['setup_s'][0] - .5:.2f} / {C['ovpn-udp']['setup_kb'][0]:.1f}",
  f"{C['ssh-L']['setup_s'][0] - .3:.2f} / {C['ssh-L']['setup_kb'][0]:.1f}"],
 ['SLOC†', f"{sl['wireguard-go'] / 1000:.1f} k (wireguard-go)", f"{sl['openvpn'] / 1000:.1f} k + OpenSSL", f"{sl['openssh'] / 1000:.1f} k"]]
# Table 6: milestone claims against this run
T[6] = [['Milestone claim', 'Final evidence', 'Revised claim'],
 ['WireGuard 942 Mbit/s at 14% CPU (kernel)', f"wireguard-go {C['wg']['p1'][0] / 1000:.2f} Gbit/s at {C['wg']['busy'][0]:.0f}% of 200%", 'efficient via batching; kernel variant untested'],
 ['OpenVPN 480 Mbit/s, one thread at 100%, context switching', f"{C['ovpn-udp']['p1'][0] / 1000:.2f} Gbit/s; {CTX['ovpn-udp']['sys']:,.0f} vs {CTX['wg']['sys']:,.0f} switches/MB; cipher effect within CIs", 'per-packet wake-ups limit OpenVPN (supported, narrowed)'],
 ['SSH 310 Mbit/s; meltdown at 2% loss', f"SSH-L {C['ssh-L']['p1'][0] / 1000:.2f} Gbit/s; R(2%) = {l['ssh-L']['0.02']['mbps'][0] / l['raw']['0.02']['mbps'][0]:.2f}", 'no meltdown under CUBIC; under BBR 18–44% below raw TCP for TCP-in-TCP, still ≥10× CUBIC']]
T[7] = [['Scenario', 'Recommendation', 'Reason'],
 ['Site-to-site, edge gateway', 'WireGuard', 'best packet-tunnel E; silent; small code'],
 ['Admin access to one service', 'SSH -L', 'least privilege; fastest single flow; hide port'],
 ['UDP blocked, TCP/443 only', 'OpenVPN-TCP', 'parity under CUBIC; on lossy paths BBR gives ≥10× CUBIC'],
 ['Enterprise PKI, full network', 'OpenVPN-UDP + tls-crypt', 'certificate integration; probe-silent; DCO'],
 ['Production L3 over SSH', 'avoid SSH -w', 'lowest E; root and PermitTunnel needed']]
OUT = HERE + '/output'; os.makedirs(OUT, exist_ok=True)
with open(OUT + '/tables.md', 'w') as md:
    for n, rows in T.items():
        csv.writer(open(f'{OUT}/table{n}.csv', 'w', newline='')).writerows(rows)
        md.write(f'\n## Table {n}\n\n| ' + ' | '.join(rows[0]) + ' |\n|' + '---|' * len(rows[0]) + '\n')
        for r in rows[1:]: md.write('| ' + ' | '.join(r) + ' |\n')
print('wrote', len(T), 'tables to', OUT)
