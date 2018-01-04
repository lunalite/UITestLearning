#!/usr/bin/env bash

../../fastText/fasttext supervised -input ./train.txt -output model -lr 0.025 -dim 100 -epoch 10 -minCount 1
../../fastText/fasttext test model.bin ./test.txt 1