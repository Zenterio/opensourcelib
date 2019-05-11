#!/usr/bin/env bash
#
# $1 local name for the image
# $2 local tag for the image
image_name=$1
image_tag=$2

source ./maketools/docker/common.sh

# shellcheck disable=SC2086
docker run ${DOCKER_FLAGS} --user "${USER_UID}:${USER_GID}" "${image_name}:${image_tag}" /bin/bash -c "${@:3}"
