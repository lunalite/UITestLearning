#!/usr/bin/env bash

if [ $# -eq 0 ]
  then
    echo "No arguments supplied."
    echo "Usage: ./script.sh (number of db)"
    exit 1
fi

mongoexport -d dataset -c clickable -o clickable1.json
for i in $(seq 2 $1)
do
    mongoexport -d dataset$i -c clickable -o clickable$i.json
done