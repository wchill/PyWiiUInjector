#!/bin/sh
set -e
SCRIPT_PATH="$(python3 -c 'import os, sys; print(os.path.realpath(sys.argv[1]))' "$0")"
: "${PROJECT_ROOT:="$(dirname "$SCRIPT_PATH")"}"

docker build . -t injector
docker run --rm -v "$PROJECT_ROOT":/project injector /bin/bash /project/build_tools.sh
