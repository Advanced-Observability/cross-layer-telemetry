#!/bin/bash

if [ ! -f /usr/include/linux/ioam.h ]; then
	echo "Not an IOAM kernel"
	exit 1
fi

if [ ! -f src/athos/ioam.h ]; then
	cp /usr/include/linux/ioam.h src/athos/
fi
if [ ! -f src/porthos/ioam.h ]; then
	cp /usr/include/linux/ioam.h src/porthos/
fi
if [ ! -f src/aramis/ioam.h ]; then
	cp /usr/include/linux/ioam.h src/aramis/
fi

if [ ! -f src/aramis/ioam_trace.proto ]; then
	cp src/ioam_trace.proto src/aramis/
fi
if [ ! -f src/ioam-collector/ioam_trace.proto ]; then
	cp src/ioam_trace.proto src/ioam-collector/
fi

docker image inspect python:3 &> /dev/null
[ $? != 0 ] && HAD_PYTHON_IMAGE=false || HAD_PYTHON_IMAGE=true

docker image inspect golang:1.14-alpine &> /dev/null
[ $? != 0 ] && HAD_GOLANG_IMAGE=false || HAD_GOLANG_IMAGE=true

docker image inspect static-supervisord:latest &> /dev/null
if [ $? != 0 ]; then
	docker build --tag static-supervisord src/static-supervisord/.
	rm static-supervisord.tar
	docker save static-supervisord > static-supervisord.tar
fi
docker image inspect athos:latest &> /dev/null
if [ $? != 0 ]; then
	docker build --tag athos src/athos/.
	rm athos.tar
	docker save athos > athos.tar
	docker image rm athos:latest -f
fi
docker image inspect porthos:latest &> /dev/null
if [ $? != 0 ]; then
	docker build --tag porthos src/porthos/.
	rm porthos.tar
	docker save porthos > porthos.tar
	docker image rm porthos:latest -f
fi
docker image inspect aramis:latest &> /dev/null
if [ $? != 0 ]; then
	docker build --tag aramis src/aramis/.
	rm aramis.tar
	docker save aramis > aramis.tar
	docker image rm aramis:latest -f
fi
docker image inspect ioam-collector:latest &> /dev/null
if [ $? != 0 ]; then
	docker build --tag ioam-collector src/ioam-collector/.
	rm ioam-collector.tar
	docker save ioam-collector > ioam-collector.tar
	docker image rm ioam-collector:latest -f
fi

docker image prune --filter label=stage=builder -f
docker image rm static-supervisord:latest -f

if ! $HAD_PYTHON_IMAGE; then
	docker image rm python:3 -f
fi
if ! $HAD_GOLANG_IMAGE; then
	docker image rm golang:1.14-alpine -f
fi

docker pull jaegertracing/jaeger-collector:latest
docker pull jaegertracing/jaeger-query:latest
docker pull elasticsearch:7.6.2

rm src/athos/ioam.h
rm src/porthos/ioam.h
rm src/aramis/ioam.h
rm src/aramis/ioam_trace.proto
rm src/ioam-collector/ioam_trace.proto

