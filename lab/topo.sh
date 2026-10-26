#!/bin/bash
# topo.sh up|down|impair <loss> <delay_ms> <rate_mbit>|clean
# cli(10.0.1.2) --vc-- rtr --vs-- srv(10.0.2.2); rtr forwards.
set -e
up(){
  for n in cli rtr srv; do ip netns add $n; ip -n $n link set lo up; done
  ip link add vc0 netns cli type veth peer name vc1 netns rtr
  ip link add vs1 netns rtr type veth peer name vs0 netns srv
  ip -n cli addr add 10.0.1.2/24 dev vc0; ip -n cli link set vc0 up
  ip -n rtr addr add 10.0.1.1/24 dev vc1; ip -n rtr link set vc1 up
  ip -n rtr addr add 10.0.2.1/24 dev vs1; ip -n rtr link set vs1 up
  ip -n srv addr add 10.0.2.2/24 dev vs0; ip -n srv link set vs0 up
  ip -n cli route add default via 10.0.1.1; ip -n srv route add default via 10.0.2.1
  ip netns exec rtr sysctl -qw net.ipv4.ip_forward=1
  for n in cli rtr srv; do ip netns exec $n sysctl -qw net.ipv4.conf.all.rp_filter=0 net.ipv4.conf.default.rp_filter=0; done
  for n in cli rtr srv; do ip netns exec $n sysctl -qw net.ipv4.tcp_congestion_control=${CC:-cubic}; done
}
clean(){
  pkill -x impair 2>/dev/null || true; sleep 0.3
  ip netns exec rtr ip rule del iif vc1 lookup 100 2>/dev/null || true
  ip netns exec rtr ip rule del iif vs1 lookup 200 2>/dev/null || true
  ip -n rtr link del ta 2>/dev/null || true; ip -n rtr link del tb 2>/dev/null || true
  tc -n rtr qdisc del dev vs1 root 2>/dev/null || true; tc -n rtr qdisc del dev vc1 root 2>/dev/null || true
}
impair(){ # loss(0-1) delay_ms rate_mbit
  clean
  ip netns exec rtr ip tuntap add ta mode tun; ip netns exec rtr ip tuntap add tb mode tun
  ip -n rtr link set ta up mtu 1500; ip -n rtr link set tb up mtu 1500
  ip netns exec rtr sysctl -qw net.ipv4.conf.ta.rp_filter=0 net.ipv4.conf.tb.rp_filter=0
  ip -n rtr route add default dev ta table 100; ip -n rtr route add default dev tb table 200
  ip -n rtr rule add iif vc1 lookup 100; ip -n rtr rule add iif vs1 lookup 200
  ip netns exec rtr taskset -c 1 impair ta tb $1 $2 ${4:-42} >/dev/null 2>&1 &
  sleep 0.3
  if [ -n "$3" ] && [ "$3" != 0 ]; then
    # token bucket with ~2xBDP buffer at 100 Mbit
    tc -n rtr qdisc add dev vs1 root tbf rate ${3}mbit burst 64kb limit 512kb
    tc -n rtr qdisc add dev vc1 root tbf rate ${3}mbit burst 64kb limit 512kb
  fi
}
down(){ clean; for n in cli rtr srv; do ip netns pids $n 2>/dev/null | xargs -r kill 2>/dev/null; ip netns del $n 2>/dev/null; done; true; }
"$@"
