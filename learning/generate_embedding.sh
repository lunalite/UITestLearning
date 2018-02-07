#!/usr/bin/env bash

for i in $(seq $1 $2)
do
    export PYTHONPATH=..; python3.6 gen_embedding.py $i $i 00
    export PYTHONPATH=..; python3.6 gen_embedding.py $i $i 10
    export PYTHONPATH=..; python3.6 gen_embedding.py $i $i 01
    export PYTHONPATH=..; python3.6 gen_embedding.py $i $i 11
done