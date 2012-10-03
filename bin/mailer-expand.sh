#!/bin/bash
# Tool originally from Tim Sammut

URL='http://mailer-api.cisco.com/itsm/mailer/rest/list/members/'

FOLKS=$(curl --silent --user $USER${PW:+:$PW} $URL$1 | \
    grep title\=\'Member: | grep Type:\ EMP | \
    perl -npe's/^.+>([^<]+)<.+$/\1/' | sort | uniq)

for PEEP in $FOLKS; do
    echo $PEEP
done

if [[ -n $FOLKS ]]; then
    exit 0
else
    exit 1
fi

