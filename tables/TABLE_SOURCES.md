# Sources of the tables in report6.docx

| Table | Kind | Source | How it is made |
|---|---|---|---|
| 1 Tunnel configurations | Written by hand | lab/tun.sh, lab/sshd_config | Written from the settings in the scripts |
| 2 Clean-link results | Measured | results/clean_p1.jsonl, rr.jsonl, setup.jsonl, tables/inputs.json | analyze.py, then equations (1)-(4) and (6) in make_tables.py |
| 3 Raw TCP vs. Mathis model | Measured and model | results/loss_cubic.jsonl, rr_delay_cubic.jsonl | Model: (1448·8/RTT)·√(3/2)/√p, RTT = median raw RTT at CUBIC (23.0 ms) |
| 4 Retransmissions | Measured | results/loss_cubic.jsonl | analyze.py; R(2%) is equation (5) |
| 5 Security comparison | Mixed | Cells with † are measured: results/probe.json, results/setup.jsonl, inputs.json. Other cells come from the cited papers | Net setup removes the fixed script waits (0.5 s OpenVPN, 0.3 s SSH) |
| 6 Milestone claims | Mixed | Left column: my milestone. Middle column: this run. Right column: my conclusion | make_tables.py fills in the middle column |
| 7 Deployment guide | Conclusion, written by hand | Sections 4.2-4.4 of the report | No script: it is a judgement from the results |

Text in the report (for example the context switches and the BBR percentages) comes from the same summary.json and ctx.json.
