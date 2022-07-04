#!/bin/sh
set -e
realpath() (
  OURPWD=$PWD
  cd "$(dirname "$1")"
  LINK=$(readlink "$(basename "$1")")
  while [ "$LINK" ]; do
    cd "$(dirname "$LINK")"
    LINK=$(readlink "$(basename "$1")")
  done
  REALPATH="$PWD/$(basename "$1")"
  cd "$OURPWD"
  echo "$REALPATH"
)
SCRIPT_PATH="$(python -c 'import os, sys; print(os.path.realpath(sys.argv[1]))' "$0")"
: "${PROJECT_ROOT:="$(dirname "$SCRIPT_PATH")"}"

docker build . -t injector
docker run -v ${PROJECT_ROOT}:/project injector /bin/bash /project/build_tools.sh
