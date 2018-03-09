#!/usr/bin/env bash

for i in $(seq $1 $2)
do
    export PYTHONPATH=..; python3.6 generate_traintest.py $i 00 &
    export PYTHONPATH=..; python3.6 generate_traintest.py $i 10 &
    export PYTHONPATH=..; python3.6 generate_traintest.py $i 01 &
    export PYTHONPATH=..; python3.6 generate_traintest.py $i 11 &
done
