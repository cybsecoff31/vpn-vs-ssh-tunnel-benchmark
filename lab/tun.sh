#!/bin/bash
# tun.sh up|down <cfg>; cfg in raw wg ovpn-udp ovpn-tcp ovpn-udp-chacha ssh-L ssh-L-aes ssh-w
# After 'up', inner target host is printed via /tmp/lab_target (host port_iperf port_rr)
K=/opt/lab/keys; C="ip netns exec cli taskset -c 0"; S="ip netns exec srv taskset -c 1"
ovpn_common="--dev-type tun --cipher AES-256-GCM --data-ciphers AES-256-GCM --auth SHA256 --ca $K/ca.crt --tls-crypt $K/tc.key --verb 3 --ping 10 --ping-restart 60 --persist-key"
up(){
 case $1 in
 raw) echo "10.0.2.2 5201 7000" > /tmp/lab_target;;
 wg)
  $S wireguard-go wgs; ip netns exec srv wg set wgs listen-port 51820 private-key $K/wg_srv.key peer $(cat $K/wg_cli.pub) allowed-ips 10.9.0.2/32
  ip -n srv addr add 10.9.0.1/24 dev wgs; ip -n srv link set wgs mtu 1420 up
  $C wireguard-go wgc; ip netns exec cli wg set wgc private-key $K/wg_cli.key peer $(cat $K/wg_srv.pub) allowed-ips 10.9.0.1/32 endpoint 10.0.2.2:51820
  ip -n cli addr add 10.9.0.2/24 dev wgc; ip -n cli link set wgc mtu 1420 up
  echo "10.9.0.1 5201 7000" > /tmp/lab_target;;
 ovpn-udp|ovpn-tcp|ovpn-udp-chacha)
  proto_s=udp4; proto_c=udp4; extra=""
  [ $1 = ovpn-tcp ] && { proto_s=tcp4-server; proto_c=tcp4-client; }
  [ $1 = ovpn-udp-chacha ] && extra="--cipher CHACHA20-POLY1305 --data-ciphers CHACHA20-POLY1305"
  $S openvpn --daemon ovs --log /tmp/ovs.log --dev ovs $ovpn_common $extra --proto $proto_s --local 10.0.2.2 --port 1194 --tls-server --dh none --cert $K/server.crt --key $K/server.key --ifconfig 10.9.0.1 10.9.0.2 --writepid /run/ovs.pid
  sleep 0.5
  $C openvpn --daemon ovc --log /tmp/ovc.log --dev ovc $ovpn_common $extra --proto $proto_c --remote 10.0.2.2 1194 --tls-client --remote-cert-tls server --cert $K/client.crt --key $K/client.key --ifconfig 10.9.0.2 10.9.0.1 --writepid /run/ovc.pid
  echo "10.9.0.1 5201 7000" > /tmp/lab_target;;
 ssh-L|ssh-L-aes)
  ci=chacha20-poly1305@openssh.com; [ $1 = ssh-L-aes ] && ci=aes256-gcm@openssh.com
  [ -f /run/sshd-lab.pid ] || $S /usr/local/sbin/sshd -f /opt/lab/sshd_config
  sleep 0.3
  $C ssh -f -N -i $K/id_ed25519 -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR -o Ciphers=$ci -o Compression=no -o ExitOnForwardFailure=yes -L 127.0.0.1:5202:127.0.0.1:5201 -L 127.0.0.1:7001:127.0.0.1:7000 root@10.0.2.2
  echo "127.0.0.1 5202 7001" > /tmp/lab_target;;
 ssh-w)
  [ -f /run/sshd-lab.pid ] || $S /usr/local/sbin/sshd -f /opt/lab/sshd_config
  sleep 0.3
  $C ssh -f -N -i $K/id_ed25519 -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR -o Ciphers=chacha20-poly1305@openssh.com -o Tunnel=point-to-point -w 7:7 root@10.0.2.2
  for i in $(seq 50); do ip -n srv link show tun7 >/dev/null 2>&1 && ip -n cli link show tun7 >/dev/null 2>&1 && break; sleep 0.1; done
  ip -n cli addr add 10.9.0.2 peer 10.9.0.1 dev tun7; ip -n cli link set tun7 up
  ip -n srv addr add 10.9.0.1 peer 10.9.0.2 dev tun7; ip -n srv link set tun7 up
  echo "10.9.0.1 5201 7000" > /tmp/lab_target;;
 esac
}
down(){
 pkill -x wireguard-go; pkill -x openvpn; pkill -x ssh; [ -f /run/sshd-lab.pid ] && kill $(cat /run/sshd-lab.pid) 2>/dev/null; pkill -x sshd-session; rm -f /run/sshd-lab.pid
 sleep 0.5
 for l in wgs:srv wgc:cli tun7:cli tun7:srv ovs:srv ovc:cli; do ip -n ${l#*:} link del ${l%:*} 2>/dev/null; done; true
}
"$@"
