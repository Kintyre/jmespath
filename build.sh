#!/bin/bash
set -e

APP="jmespath"
BUILD="build/$APP"
VER=$(cat default/app.conf | grep version | cut -f2 -d=)
TARBALL=jmespath-for-splunk-${VER}.tgz
echo "Building JMESPath for Splunk ${VER}"
echo

[[ -d "$BUILD" ]] || rm -rf "$BUILD"
mkdir -p "$BUILD"

echo "Creating build into $BUILD"
cp -a *.md bin default metadata "$BUILD"
find "$BUILD" -name '*.py[co]' -delete

echo "Exporting to $TARBALL"
[[ -d "dist" ]] || mkdir dist


# MAC OSX undocumented hack to prevent creation of '._*' folders
export COPYFILE_DISABLE=1

cd build
tar -czvf "../dist/$TARBALL" "$APP"
cd ..
echo "dist/$TARBALL" > .latest_release