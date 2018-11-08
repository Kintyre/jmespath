#!/bin/bash

set -e

if [[ -d venv ]]; then
    . venv/bin/activate
fi

# brew install libmagic
if [[ ! -f "splunk-appinspect.tar.gz" ]];
then
    curl -sL http://dev.splunk.com/goto/appinspectdownload -o splunk-appinspect.tar.gz
    pip install splunk-appinspect.tar.gz
fi

# Test app inspect
splunk-appinspect list version

splunk-appinspect inspect $(<.latest_release) --mode precert --included-tags cloud
