#!/usr/bin/env bash

for i in $(seq 3 7)
do
    export PYTHONPATH=..; python3.6 gen_embedding.py $i $i 0
    export PYTHONPATH=..; python3.6 gen_embedding.py $i $i 1
    export PYTHONPATH=..; python3.6 gen_embedding.py $i $i 01
    export PYTHONPATH=..; python3.6 gen_embedding.py $i $i 11
done