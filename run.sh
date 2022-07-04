#!/bin/sh
set -e

: "${PROJECT_ROOT:="$(dirname "$(realpath "$0")")"}"

docker run -v $PROJECT_ROOT:/project injector python3 /project/main.py