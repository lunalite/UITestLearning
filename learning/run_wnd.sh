#!/usr/bin/env bash

export PYTHONPATH=..; python3.6 widenrnn.py $1 00 wnd --epoch 5&
export PYTHONPATH=..; python3.6 widenrnn.py $1 01 wnd --epoch 5&
export PYTHONPATH=..; python3.6 widenrnn.py $1 10 wnd --epoch 5&
export PYTHONPATH=..; python3.6 widenrnn.py $1 11 wnd --epoch 5&
