#!/bin/bash
# Really?!?! Why did I have to write this myself?  c'mon Splunk!!
USERNAME=${USERNAME-lalleman}
PACKAGE=${PACKAGE-$(<.latest_release)}

# jp - jmsepath CLI tool.

if [[ ! -x $(command -v jp) ]]
then
    echo "Install the 'jp' command line too.  https://github.com/jmespath/jp"
    exit 1
fi

set -e

t=$(mktemp)

if [[ -z $token ]]
then
    echo "No token found.  Logging in."
    curl -s -X GET \
         -u "$USERNAME" \
         --url "https://api.splunk.com/2.0/rest/login/splunk" -o "$t"
    cat "$t"
    echo
    token=$(jp -f "$t" -u data.token)
    echo "To reuse the token later, run this in your shell:"
    echo "export token=$token"
fi

echo "Uploading $PACKAGE to AppInspect via APIs"
curl -s -X POST \
     -H "Authorization: bearer $token" \
     -H "Cache-Control: no-cache" \
     -F "app_package=@\"$PACKAGE\"" \
     --url "https://appinspect.splunk.com/v1/app/validate" -o "$t"
cat "$t"
echo
request_id=$(jp -f "$t" -u request_id)
echo "Request id:  $request_id"

while true
do
    curl -s -X GET \
         -H "Authorization: bearer $token" \
         -H "Cache-Control: no-cache" \
         --url "https://appinspect.splunk.com/v1/app/validate/status/${request_id}" -o "$t"

    status=$(jp -f "$t" -u status)

    echo "STATUS:  $status"
    #cat "$t"

    if [[ $status = "SUCCESS" ]]; then break; fi

    sleep 10

done

RPT="app_inspect.report-${request_id}.json"
echo "Downloading report."
curl -s -X GET -H "Authorization: bearer $token" \
     -H "Cache-Control: no-cache" \
     --url "https://appinspect.splunk.com/v1/app/report/${request_id}" \
     -o "${RPT}"

echo "Downloading HTML report."
curl -s -X GET -H "Authorization: bearer $token" \
     -H "Content-Type: text/html" \
     -H "Cache-Control: no-cache" \
     --url "https://appinspect.splunk.com/v1/app/report/${request_id}" \
     -o "${RPT/.json/.html}"

echo "Summary"
jp -f "$RPT" 'reports[0].{name:app_name,description:app_description,author:app_author,version:app_version,hash:app_hash,appinspect_ver:run_parameters.appinspect_version}'

jp -f "$RPT" 'reports[0].summary'

jp -f "$RPT" "reports[0].groups[].checks[].{name:name,description:description,result:result} | [?result!='success' && result!='not_applicable'] | [][name, description, result]"

echo "See $RPT"
