#!/bin/sh
set -e
SCRIPT_PATH="$(python3 -c 'import os, sys; print(os.path.realpath(sys.argv[1]))' "$0")"
: "${PROJECT_ROOT:="$(dirname "$SCRIPT_PATH")"}"

docker run --rm -it -v "$PROJECT_ROOT":/project -v "$1":/input -v "$2":/output injector python3 /project/main.py --input /input --output /output --processes 1