#!/bin/bash
container_name="athos"

scratch_container_id=$(docker ps -aqf "name=$container_name")

docker run -d busybox:latest sleep 100
busybox_container_id=$(docker ps -ql)
docker cp "$busybox_container_id":/bin/busybox .

docker cp ./busybox "$scratch_container_id":/busybox

docker exec -it "$scratch_container_id" /busybox sh -c '
export PATH="/busybin:$PATH"
/busybox mkdir /busybin
/busybox --install /busybin
sh'
