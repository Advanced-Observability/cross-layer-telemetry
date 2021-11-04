#!/bin/bash

PYTHON_IMAGE="python:3.8"
GOLANG_IMAGE="golang:1.14-alpine"
JAEGER_AGENT_IMAGE="jaegertracing/jaeger-agent:1.18"

# Pre-checks
docker image inspect $PYTHON_IMAGE &> /dev/null
[ $? != 0 ] && HAD_PYTHON_IMAGE=false || HAD_PYTHON_IMAGE=true

docker image inspect $GOLANG_IMAGE &> /dev/null
[ $? != 0 ] && HAD_GOLANG_IMAGE=false || HAD_GOLANG_IMAGE=true

docker image inspect $JAEGER_AGENT_IMAGE &> /dev/null
[ $? != 0 ] && HAD_JAEGER_AGENT_IMAGE=false || HAD_JAEGER_AGENT_IMAGE=true

# build static-supervisord image
docker build --tag static-supervisord src/static-supervisord/.

# build athos image
docker build --tag athos src/athos/.
rm athos.tar
docker save athos > athos.tar
docker image rm athos:latest -f

# build porthos image
docker build --tag porthos src/porthos/.
rm porthos.tar
docker save porthos > porthos.tar
docker image rm porthos:latest -f

# build aramis image
docker build --tag aramis src/aramis/.
rm aramis.tar
docker save aramis > aramis.tar
docker image rm aramis:latest -f

# build ioam-collector image
docker build --tag ioam-collector src/ioam-collector/.
rm ioam-collector.tar
docker save ioam-collector > ioam-collector.tar
docker image rm ioam-collector:latest -f

# Cleanup
docker image prune --filter label=stage=builder -f
docker image rm static-supervisord:latest -f

if ! $HAD_PYTHON_IMAGE; then
	docker image rm $PYTHON_IMAGE -f
fi
if ! $HAD_GOLANG_IMAGE; then
	docker image rm $GOLANG_IMAGE -f
fi
if ! $HAD_JAEGER_AGENT_IMAGE; then
	docker image rm $JAEGER_AGENT_IMAGE -f
fi

