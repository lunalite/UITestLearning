import codecs
import json
import operator
import random
import re
import string
import collections
import sys
from enum import Enum

from tqdm import *
from pathlib import Path


def pre_process(fileno):
    with codecs.open(datafile, "r", 'utf-8') as f:
        datainput = [x.strip() for x in tqdm(f)]
    text_list = []
    obj_list = []
    for i in tqdm(datainput):
        json_obj = json.loads(i)
        if 'text' in json_obj:
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
    with codecs.open('./dataformatted' + str(fileno) + '.json', 'w', 'utf-8') as f:
        for i in obj_list:
            f.write('{}\n'.format(json.dumps(i)))


def combine_dataformatted(datano):
    datainput = {}
    for i in range(1, datano):
        with codecs.open('./dataformatted' + str(i) + '.json', "r", 'utf-8') as f:
            datainput[i] = [x.strip() for x in tqdm(f)]
    text_list = []
    obj_list = []
    for k, v in tqdm(datainput.items()):
        for item in v:
            json_obj = json.loads(item)
            obj_list.append(json_obj)

    with codecs.open('./dataformattedF.json', 'w', 'utf-8') as f:
        for i in obj_list:
            f.write('{}\n'.format(json.dumps(i)))


def split_to_pd(feature):
    with open('./dataformattedF.json', 'r') as f:
        lines = [x.strip() for x in f.readlines()]
    obj_list = []
    next_ts_list = []
    pdata = []
    ndata = []
    activitydict = {}
    transitiondict = {}

    # """ For finding previous and next transition states in the case of double NST """
    # for line in lines:
    #     obj_loaded = json.loads(line)
    #     # if obj_loaded['parent_activity_state'] == 'pha.viz.a0002.alephbetkatakana-552e78c3fba262d55722d2c7cd37d5c8':
    #     # if obj_loaded['next_transition_state'] == 'pha.viz.a0002.alephbetkatakana-86c421435a854b15b264d5d34e226b68':
    #     if obj_loaded['text'] == '3':
    #         if obj_loaded['parent_activity_state'] != obj_loaded['next_transition_state']:
    #             print(obj_loaded)
    #
    if feature == FEATURE.DNST:
        for line in tqdm(lines):
            obj_loaded = json.loads(line)
            # We must exclude cases where NST is none and NST is OUTOFAPK
            # Adding to activitydict a matching between next state with the current state
            # This is done so that we have a dict which we can use to find the previous state
            if obj_loaded['next_transition_state'] is not None and obj_loaded['next_transition_state'] != 'OUTOFAPK':
                if obj_loaded['next_transition_state'] not in activitydict:
                    activitydict[obj_loaded['next_transition_state']] = set()
                activitydict[obj_loaded['next_transition_state']].add(obj_loaded['parent_activity_state'])

        # Excluding cases where there are multiple possibilities of previous states
        for k, v in activitydict.items():
            print(k, v)
            print(len(v))
            if len(v) == 1:
                transitiondict[k] = activitydict[k].pop()

    for line in lines:
        obj_loaded = json.loads(line)

        if feature == FEATURE.NST:
            # We exclude cases of NST being none and NST being OUTOFAPK
            # FEATURE.NST checks if the current state is different from the next state
            # If they are different, means positive data set. Otherwise, negative
            if obj_loaded['next_transition_state'] is not None and obj_loaded['next_transition_state'] != 'OUTOFAPK':
                if obj_loaded['parent_activity_state'] == obj_loaded['next_transition_state']:
                    ndata.append(obj_loaded)
                else:
                    pdata.append(obj_loaded)

        elif feature == FEATURE.DNST:
            # We exclude cases of NST being none and NST being OUTOFAPK
            # FEATURE.DNST includes checking of previous to the next state
            # There are still situations of where the
            if obj_loaded['next_transition_state'] is not None and obj_loaded['next_transition_state'] != 'OUTOFAPK':
                if obj_loaded['parent_activity_state'] == obj_loaded['next_transition_state']:
                    ndata.append(obj_loaded)
                elif obj_loaded['parent_activity_state'] in transitiondict:
                    # transitiondict[obj_loaded['parent_activity_state']] will give the previous state
                    # Checks if previous state is equivalent to the next state
                    if transitiondict[obj_loaded['parent_activity_state']] == obj_loaded['next_transition_state']:
                        ndata.append(obj_loaded)
                    else:
                        pdata.append(obj_loaded)
                else:
                    pdata.append(obj_loaded)

    print('Negative data amount: {}'.format(len(ndata)))
    print('Positive data amount: {}'.format(len(pdata)))
    min_amt = min(len(ndata), len(pdata))
    with open('./ndata.txt', 'w') as f:
        for i in range(min_amt):
            f.write(json.dumps(ndata[i]) + '\n')

    with open('./pdata.txt', 'w') as f:
        for i in range(min_amt):
            f.write(json.dumps(pdata[i]) + '\n')


def get_info_on_text_pd():
    with open('./pdata.txt', 'r') as f:
        plines = [x.strip() for x in f.readlines()]
    with open('./ndata.txt', 'r') as f:
        nlines = [x.strip() for x in f.readlines()]
    obj_list = []
    next_ts_list = []
    pdata = []
    ndata = []

    for pline in plines:
        obj_loaded = json.loads(pline)
        pdata.append(obj_loaded['text'].lower())
    for nline in nlines:
        obj_loaded = json.loads(nline)
        ndata.append(obj_loaded['text'].lower())

    print('Negative data amount: {}'.format(len(ndata)))
    print('Positive data amount: {}'.format(len(pdata)))
    ncount = collections.Counter(ndata)
    pcount = collections.Counter(pdata)

    with open('./ndatatext.txt', 'w') as f:
        f.write('count\t|norm\t|text\n')
        f.write('==========================\n')
        for i in ncount.most_common():
            f.write('{}\t|{:.6f}\t|{}\n'.format(i[1], (i[1] / len(ndata)), i[0]))

    print('Written to ndatatext.txt')

    with open('./pdatatext.txt', 'w') as f:
        f.write('count\t|norm\t|text\n')
        f.write('==========================\n')
        for i in pcount.most_common():
            f.write('{}\t|{:.6f}\t|{}\n'.format(i[1], (i[1] / len(ndata)), i[0]))

    print('Written to pdatatext.txt')


def get_info_on_btn_distribution():
    with open('./pdata.txt', 'r') as f:
        lines = [x.strip() for x in f.readlines()]
    obj_list = []
    pdata = []

    for line in lines:
        obj_loaded = json.loads(line)
        pdata.append(obj_loaded)

    pscoredict = {}
    pscoredictavg = {}
    for obj_loaded in pdata:
        curr_state = obj_loaded['parent_activity_state']
        next_state = obj_loaded['next_transition_state']
        if obj_loaded['text'].lower() not in pscoredict:
            pscoredict[obj_loaded['text'].lower()] = []
        pscoredict[obj_loaded['text'].lower()].append(obj_loaded['score'])

    for k, v in pscoredict.items():
        pscoredictavg[k] = sum(pscoredict[k]) / len(pscoredict[k])

    sorted_pscoredictavg = sorted(pscoredictavg.items(), key=operator.itemgetter(1), reverse=True)
    with open('./pscoreavg.txt', 'w') as f:
        f.write('avg_s\t\t|len_arr\t|text\n')
        f.write('==========================\n')
        for v in sorted_pscoredictavg:
            # print(v[0], v[1])
            f.write('{:.6f}\t|{:<10}\t|{:<10}\n'.format(v[1], len(pscoredict[v[0]]), v[0]))

    print('Written to pscoreavg.txt')


def prep_data_for_fasttext():
    with open('./pdata.txt', 'r') as f:
        pdata = [x.strip() for x in f.readlines()]

    for i in range(len(pdata)):
        jp = json.loads(pdata[i])
        pdata[i] = '__label__p ' + jp['text'].lower()

    with open('./ndata.txt', 'r') as f:
        ndata = [x.strip() for x in f.readlines()]

    for i in range(len(ndata)):
        jn = json.loads(ndata[i])
        ndata[i] = '__label__n ' + jn['text'].lower()

    training_amt = int(len(ndata) * 9 / 10)
    with open('./train.txt', 'w') as f:
        for i in range(training_amt):
            f.write(pdata[i] + '\n')
            f.write(ndata[i] + '\n')

    with open('./test.txt', 'w') as f:
        try:
            for i in range(training_amt, len(ndata) * 2):
                f.write(pdata[i] + '\n')
                f.write(ndata[i] + '\n')
        except Exception:
            pass


class FEATURE(Enum):
    NST = 1  # next_state_transition equal to current state or not
    DNST = 2  # Twice of next_state_transition if equal to current state or not
    SCORE = 3  # Classifying by score. If 0, negative. Otherwise, positive


datafile = '/Users/hkoh006/Desktop/data/clickable'

""" Pre-processing the original data.json to remove any non-english sets of data, as well as null texts dataset """
# for i in range(1, 5):
#     datafile = '/Users/hkoh006/Desktop/data/clickable' + str(i) + '.json'
#     pre_process(i)
# combine_dataformatted(5)


""" splitting dataset to positive and negative data """
# split_to_pd(FEATURE.NST)
split_to_pd(FEATURE.DNST)
# split_to_pd(FEATURE.SCORE)
# get_info_on_text_pd()
# get_info_on_btn_distribution()

""" Preparing data for fasttext training and classification """
# prep_data_for_fasttext()
