#!/bin/bash
set -e
: "${PROJECT_ROOT:="$(dirname "$(realpath "$0")")"}"
: "${TOOL_SRC:=$PROJECT_ROOT/tool_src}"
: "${TOOL_BIN:=$PROJECT_ROOT/tool_bin}"
: "${ARCH:="$(dpkg --print-architecture)"}"

cd $PROJECT_ROOT
git submodule init
git submodule update

# make wit
cd $TOOL_SRC/wiimms-iso-tools/project
make -j $(nproc)
mkdir -p $TOOL_BIN/wit
cp $TOOL_SRC/wiimms-iso-tools/project/bin/* $TOOL_BIN/wit | true

# make nfs2iso2nfs
cd $TOOL_SRC/nfs2iso2nfs
dotnet publish -c Release -r linux-$ARCH --self-contained=true
mkdir -p $TOOL_BIN/nfs2iso2nfs
cp $TOOL_SRC/nfs2iso2nfs/bin/Release/net6.0/linux-$ARCH/publish/* $TOOL_BIN/nfs2iso2nfs

# make JNUSTool
cd $TOOL_SRC/JNUSTool
mvn package
mkdir -p $TOOL_BIN/JNUSTool
cp $TOOL_SRC/JNUSTool/jar/* $TOOL_BIN/JNUSTool

# make CNUSPacker
cd $TOOL_SRC/CNUS_Packer
dotnet publish -c Release -r linux-$ARCH --self-contained=true -p:PublishSingleFile=true -p:PublishTrimmed=true
mkdir -p $TOOL_BIN/CNUS_Packer
cp $TOOL_SRC/CNUS_Packer/CNUSPACKER/bin/Release/netcoreapp3.0/linux-arm64/publish/* $TOOL_BIN/CNUS_Packer
