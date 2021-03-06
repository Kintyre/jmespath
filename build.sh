#!/bin/bash
set -e

APP="jmespath"
BUILD="build/$APP"
VER=$(grep version default/app.conf | cut -f2 -d=)
VER=${VER/ /}
if [[ $(git status --porcelain | grep -v "^\?") != '' ]]; then
    VER=${VER}-dirty
fi
TARBALL=jmespath-for-splunk-${VER}.tgz
echo "Building JMESPath for Splunk ${VER}"
echo

[[ -d "$BUILD" ]] || rm -rf "$BUILD"
mkdir -p "$BUILD"

echo "Creating build into $BUILD"
cp -a ./*.md bin default metadata static "$BUILD"
find "$BUILD" \( -name '*.py[co]' -o -name '__pycache__' -o -name '*.log*' \) -delete
find "$BUILD" -name '.DS_Store' -delete

echo "Exporting to $TARBALL"
[[ -d "dist" ]] || mkdir dist


# MAC OSX undocumented hack to prevent creation of '._*' folders
export COPYFILE_DISABLE=1

(
cd build
tar -czvf "../dist/$TARBALL" "$APP"
)
echo "dist/$TARBALL" > .latest_release
