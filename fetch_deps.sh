#!/bin/bash

LIB=bin
python -m pip install --upgrade --isolated --disable-pip-version-check -r requirements.txt -t "${LIB:?}"
rm -rf ${LIB:?}/bin $LIB/*.{dist,egg}-info
