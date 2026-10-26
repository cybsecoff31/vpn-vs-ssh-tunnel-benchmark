#!/bin/bash
pkill -x iperf3; pkill -f "rr.py s"; sleep 0.3
ip netns exec srv taskset -c 1 iperf3 -s -D
ip netns exec srv taskset -c 1 python3 /opt/lab/rr.py s 7000 >/dev/null 2>&1 &
sleep 0.5
