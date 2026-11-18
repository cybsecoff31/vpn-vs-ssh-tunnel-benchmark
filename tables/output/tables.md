
## Table 1

| ID | Layer / transport | Crypto (data / handshake) | Path |
|---|---|---|---|
| Raw | none / TCP | — | kernel |
| WG | L3 / UDP | ChaCha20-Poly1305 / Noise IK, X25519 | user (wg-go) |
| OV-U | L3 / UDP | AES-256-GCM / TLS 1.3, RSA-4096 | user |
| OV-U-C | L3 / UDP | ChaCha20-Poly1305 / same | user |
| OV-T | L3 / TCP | AES-256-GCM / same | user |
| SSH-L | L7 / TCP | chacha20-poly1305@openssh / Ed25519 | user |
| SSH-L-A | L7 / TCP | aes256-gcm@openssh / Ed25519 | user |
| SSH-W | L3 / TCP | chacha20-poly1305@openssh / Ed25519 | user |

## Table 2

| Config | T (Mbit/s) | U0+U1 (%) | E | CB | G (%) | dRTT64 (us) | Setup (s) |
|---|---|---|---|---|---|---|---|
| Raw | 106,030 ± 3,743 | 174 | 608.4 | 0.5 | 99.8 | (27) | 0.04 |
| WG | 2,889 ± 63 | 137 | 21.1 | 15.2 | 94.3 | +25 | 0.06 |
| OV-U | 2,236 ± 387 | 178 | 12.5 | 25.5 | 91.9 | +18 | 2.14 |
| OV-U-C | 1,742 ± 287 | 180 | 9.7 | 33.1 | 91.8 | +19 | 2.00 |
| OV-T | 1,757 ± 206 | 176 | 10.0 | 32.1 | 89.8 | +19 | 2.49 |
| SSH-L | 6,479 ± 46 | 199 | 32.6 | 9.8 | 99.8 | +22 | 0.44 |
| SSH-L-A | 18,485 ± 742 | 195 | 95.0 | 3.4 | 99.8 | +21 | 0.44 |
| SSH-W | 1,327 ± 23 | 188 | 7.1 | 45.3 | 91.4 | +22 | 0.44 |

## Table 3

| p (%) | 0.1 | 0.5 | 1 | 2 | 5 |
|---|---|---|---|---|---|
| Model (Mbit/s) | 19.5 | 8.7 | 6.2 | 4.4 | 2.8 |
| Measured (Mbit/s) | 18.8 | 7.3 | 5.5 | 3.3 | 1.2 |

## Table 4

| Config | p = 0.5% | p = 2% | p = 5% | R(2%) |
|---|---|---|---|---|
| Raw | 77 / — | 122 / — | 130 / — | 1.00 |
| WG | 76 / — | 111 / — | 129 / — | 0.88 |
| OV-U | 73 / — | 116 / — | 136 / — | 0.94 |
| OV-T | 0 / 649 | 0 / 186 | 0 / 319 | 0.93 |
| SSH-L | 4 / 106 | 0 / 200 | 0 / 206 | 0.94 |
| SSH-W | 21 / 1,067 | 0 / 191 | 0 / 286 | 0.88 |

## Table 5

| Property | WireGuard | OpenVPN | SSH |
|---|---|---|---|
| Handshake | Noise IK, 1-RTT, X25519 (Perrin, 2018) | TLS 1.3 + X.509 (RSA-4096) (Rescorla, 2018) | ML-KEM-768+X25519†, Ed25519 |
| Crypto agility | none (fixed suite) | negotiated; legacy BF-CBC risk (Bhargavan & Leurent, 2016) | negotiated |
| Formal / attacks | proofs (Dowling & Paterson, 2018; Lipp et al., 2019) | Sweet32 (Bhargavan & Leurent, 2016), fingerprint (Xue et al., 2022) | Terrapin (Bäumer et al., 2024), CBC leak (Albrecht et al., 2009) |
| Unauth. probe† | silent | silent (tls-crypt; TCP port visible); 26 B reply w/o | version banner |
| Access scope | routed subnet | routed subnet | -L: one port; -w: subnet |
| Net setup† (s / KB) | 0.06 / 1.9 | 1.64 / 11.4 | 0.14 / 9.4 |
| SLOC† | 8.7 k (wireguard-go) | 87.1 k + OpenSSL | 122.8 k |

## Table 6

| Milestone claim | Final evidence | Revised claim |
|---|---|---|
| WireGuard 942 Mbit/s at 14% CPU (kernel) | wireguard-go 2.89 Gbit/s at 137% of 200% | efficient via batching; kernel variant untested |
| OpenVPN 480 Mbit/s, one thread at 100%, context switching | 2.24 Gbit/s; 1,112 vs 110 switches/MB; cipher effect within CIs | per-packet wake-ups limit OpenVPN (supported, narrowed) |
| SSH 310 Mbit/s; meltdown at 2% loss | SSH-L 6.48 Gbit/s; R(2%) = 0.94 | no meltdown under CUBIC; under BBR 18–44% below raw TCP for TCP-in-TCP, still ≥10× CUBIC |

## Table 7

| Scenario | Recommendation | Reason |
|---|---|---|
| Site-to-site, edge gateway | WireGuard | best packet-tunnel E; silent; small code |
| Admin access to one service | SSH -L | least privilege; fastest single flow; hide port |
| UDP blocked, TCP/443 only | OpenVPN-TCP | parity under CUBIC; on lossy paths BBR gives ≥10× CUBIC |
| Enterprise PKI, full network | OpenVPN-UDP + tls-crypt | certificate integration; probe-silent; DCO |
| Production L3 over SSH | avoid SSH -w | lowest E; root and PermitTunnel needed |
