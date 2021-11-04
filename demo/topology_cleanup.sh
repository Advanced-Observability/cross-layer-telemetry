#!/bin/bash

docker-compose down

docker network rm ioam12_network
docker network rm ioam23_network

docker volume rm elasticsearch

docker image rm athos
docker image rm porthos
docker image rm aramis
docker image rm ioam-collector
docker image rm jaegertracing/jaeger-query:1.18
docker image rm jaegertracing/jaeger-collector:1.18
docker image rm elasticsearch:7.6.2

