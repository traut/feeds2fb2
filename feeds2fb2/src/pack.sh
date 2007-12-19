#!/bin/bash
if [ "$1" == "" ]; then
    echo Wrong usage. Please specify version numver in format XX.YY
else
    ALIAS=feeds2fb2-v
    tar cf - --exclude='*.log' --exclude='*.pyc' --exclude='*.timestamp' ./feeds2fb2 | gzip -f9 > "./distribs/$ALIAS$1.tar.gz" && echo "$ALIAS$1.tar.gz created."
    zip -r ./distribs/$ALIAS$1.zip ./feeds2fb2 -x \*.pyc -x \*.log -x \*.timestamp && echo "$ALIAS$1.zip created."
fi