#!/bin/bash

LIB=bin/lib

python2.7 -m pip install --upgrade jmespath --target=$LIB
rm -rf ${LIB:?}/bin $LIB/*.dist-info
