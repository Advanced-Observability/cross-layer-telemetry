#!/bin/bash

if [ ! -f /usr/include/linux/ioam.h ]; then
	echo "Not an IOAM kernel"
	exit 1
fi

docker load -q -i images/athos.tar
docker load -q -i images/porthos.tar
docker load -q -i images/aramis.tar
docker load -q -i images/ioam-collector.tar

docker network create --ipv6 --subnet=db01::/64 --gateway=db01::9 ioam12_network
docker network create --ipv6 --subnet=db02::/64 --gateway=db02::9 ioam23_network

docker-compose up -d

sudo nsenter -t $(docker inspect --format '{{ .State.Pid }}' athos) \
             -n ip -6 route add db02::/64 via db01::2 dev eth0

sudo nsenter -t $(docker inspect --format '{{ .State.Pid }}' aramis) \
             -n ip -6 route add db01::/64 via db02::1 dev eth0

