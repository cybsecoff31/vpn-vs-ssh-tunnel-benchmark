#!/bin/bash
python3 /opt/lab/exp_clean.py >> /opt/lab/results_clean.log 2>&1
python3 /opt/lab/exp_loss.py cubic > /opt/lab/results_loss.log 2>&1
python3 /opt/lab/exp_loss.py bbr > /opt/lab/results_bbr.log 2>&1
python3 /opt/lab/probe.py > /opt/lab/results_probe.log 2>&1
python3 /opt/lab/exp_ctx.py > /opt/lab/results_ctx.log 2>&1
echo CHAIN_DONE
