#!/bin/bash

docker-compose down

docker network rm ioam12_network
docker network rm ioam23_network

docker volume rm elasticsearch

