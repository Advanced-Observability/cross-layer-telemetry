#!/bin/bash

docker load -q -i images/athos.tar
docker load -q -i images/porthos.tar
docker load -q -i images/aramis.tar
docker load -q -i images/ioam-collector.tar

docker network create --ipv6 --subnet=db01::/64 --gateway=db01::9 ioam12_network
docker network create --ipv6 --subnet=db02::/64 --gateway=db02::9 ioam23_network

docker-compose up -d

docker exec athos /sbin/ip ioam namespace add 123
docker exec athos /sbin/ip -6 r a db02::/64 encap ioam6 trace type 0xc20000 ns 123 size 36 via db01::2 dev eth0

docker exec porthos /sbin/ip ioam namespace add 123
#docker exec porthos /sbin/tc qdisc add dev eth1 root netem delay 1000ms

docker exec aramis /sbin/ip ioam namespace add 123
docker exec aramis /sbin/ip -6 route add db01::/64 via db02::1 dev eth0

