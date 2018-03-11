#!/usr/bin/env bash

export PYTHONPATH=..; python3.6 widenrnn.py $1 00 wnd &
export PYTHONPATH=..; python3.6 widenrnn.py $1 01 wnd &
export PYTHONPATH=..; python3.6 widenrnn.py $1 10 wnd &
export PYTHONPATH=..; python3.6 widenrnn.py $1 11 wnd &
