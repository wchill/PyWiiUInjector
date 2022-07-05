#!/bin/bash
set -e
SCRIPT_PATH="$(python3 -c 'import os, sys; print(os.path.realpath(sys.argv[1]))' "$0")"
NUM_CORES="$(python3 -c 'import multiprocessing; print(multiprocessing.cpu_count())')"
: "${PROJECT_ROOT:="$(dirname "$SCRIPT_PATH")"}"
: "${TOOL_SRC:=$PROJECT_ROOT/tool_src}"
: "${TOOL_BIN:=$PROJECT_ROOT/tool_bin}"
: "${ARCH:="$(dpkg --print-architecture)"}"
unameOut="$(uname -s)"
case "${unameOut}" in
    Linux*)     UNAME=linux;;
    Darwin*)    UNAME=osx;;
    CYGWIN*)    UNAME=linux;;
    MINGW*)     UNAME=linux;;
    *)          UNAME="UNKNOWN:${unameOut}"
esac
: "${OS:="$UNAME"}"

cd "$PROJECT_ROOT"
git submodule init
git submodule update

# make wit
cd "$TOOL_SRC"/wiimms-iso-tools/project
make -j "$NUM_CORES"
mkdir -p "$TOOL_BIN"/wit
cp "$TOOL_SRC"/wiimms-iso-tools/project/bin/* "$TOOL_BIN"/wit || true

# make nfs2iso2nfs
cd "$TOOL_SRC"/nfs2iso2nfs
dotnet publish -c Release -r "$OS"-"$ARCH" --self-contained=true
mkdir -p "$TOOL_BIN"/nfs2iso2nfs
cp "$TOOL_SRC"/nfs2iso2nfs/bin/Release/net6.0/"$OS"-"$ARCH"/publish/* "$TOOL_BIN"/nfs2iso2nfs

# make JNUSTool
cd "$TOOL_SRC"/JNUSTool
mvn package
mkdir -p "$TOOL_BIN"/JNUSTool
cp "$TOOL_SRC"/JNUSTool/jar/* "$TOOL_BIN"/JNUSTool

# make CNUSPacker
cd "$TOOL_SRC"/CNUS_Packer
dotnet publish -c Release -r "$OS"-"$ARCH" --self-contained=true -p:PublishSingleFile=true -p:PublishTrimmed=true
mkdir -p "$TOOL_BIN"/CNUS_Packer
cp "$TOOL_SRC"/CNUS_Packer/CNUSPACKER/bin/Release/net6.0/"$OS"-"$ARCH"/publish/* "$TOOL_BIN"/CNUS_Packer
