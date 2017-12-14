import codecs
import json
import random
import re
import string
import collections
import sys
from tqdm import *
from pathlib import Path


def pre_process():
    with codecs.open('./data.json', "r", 'utf-8') as f:
        datainput = [x.strip() for x in tqdm(f)]
    text_list = []
    obj_list = []
    for i in tqdm(datainput):
        json_obj = json.loads(i)
        curr_text = json_obj['text']
        if curr_text:
            not_english = False
            for scii in curr_text:
                if scii not in string.printable:
                    not_english = True
                    break

            if not not_english:
                text_list.append(curr_text.lower())
                obj_list.append(json_obj)
    with codecs.open('./dataformatted.json', 'w', 'utf-8') as f:
        for i in obj_list:
            f.write('{}\n'.format(json.dumps(i)))


""" Pre-processing the original data.json to remove any non-english sets of data, as well as null texts dataset """


# pre_process()

def split_to_pd():
    with open('./dataformatted.json', 'r') as f:
        lines = [x.strip() for x in f.readlines()]
    obj_list = []
    next_ts_list = []
    pdata = []
    ndata = []

    for line in lines:
        obj_loaded = json.loads(line)
        if obj_loaded['next_transition_state'] is not None:
            if obj_loaded['parent_activity_state'] == obj_loaded['next_transition_state']:
                ndata.append(obj_loaded)
            else:
                pdata.append(obj_loaded)

    # print(len(ndata))
    # print(len(pdata))
    min_amt = min(len(ndata), len(pdata))
    # with open('./ndata', 'w') as f:
    #     for i in range(min_amt):
    #         f.write(json.dumps(ndata[i]) + '\n')

    # with open('./pdata', 'w') as f:
    #     for i in range(min_amt):
    #         f.write(json.dumps(pdata[i]) + '\n')


split_to_pd()

def prep_data_for_fasttext():
    with open('./pdata', 'r') as f:
        pdata = [x.strip() for x in f.readlines()]

    print(len(pdata))
    for i in range(len(pdata)):
        jp = json.loads(pdata[i])
        pdata[i] = '__label__p ' + jp['text'].lower()

    with open('./ndata', 'r') as f:
        ndata = [x.strip() for x in f.readlines()]

    print(len(ndata))
    for i in range(len(ndata)):
        jn = json.loads(ndata[i])
        ndata[i] = '__label__n ' + jn['text'].lower()

    # print(len(ndata))
    # print(len(pdata))

    # training_amt = int(len(ndata) * 2 / 3)
    # with open('./train.txt', 'w') as f:
    #     for i in range(training_amt):
    #         f.write(pdata[i] + '\n')
    #         f.write(ndata[i] + '\n')
    #
    # with open('./test.txt', 'w') as f:
    #     try:
    #         for i in range(training_amt, len(ndata) * 2):
    #             f.write(pdata[i][11:] + '\n')
    #             f.write(ndata[i][11:] + '\n')
    #     except Exception:
    #         pass


prep_data_for_fasttext()
