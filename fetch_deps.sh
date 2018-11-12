#!/bin/bash

LIB=bin

python2.7 -m pip install --upgrade jmespath splunk-sdk --target=$LIB
rm -rf ${LIB:?}/bin $LIB/*.dist-info
