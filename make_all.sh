#!/bin/bash
# Rebuilds summary.json, ctx.json, Figures 1-7 and Tables 1-7 from results/. Needs numpy and matplotlib.
set -e
cd "$(dirname "$0")"
python3 analysis/analyze.py > analysis/analyze.out
python3 analysis/pipeline.py     # Figure 1
python3 analysis/fig_extra.py    # Figures 2 and 5
python3 analysis/figs.py         # Figures 3, 6 and 7
python3 analysis/fig_ctx.py      # Figure 4
python3 tables/make_tables.py    # Tables 1-7
ls figures tables/output
