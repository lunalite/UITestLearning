#!/usr/bin/env bash

export PYTHONPATH=..; python3.6 generate_traintest.py 7 00
export PYTHONPATH=..; python3.6 rnn.py 7 00 c
export PYTHONPATH=..; python3.6 widenrnn.py 7 00
