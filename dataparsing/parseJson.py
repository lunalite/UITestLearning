import codecs
import collections
import getpass
import json
import math
import operator
import random
import re
import string
import sys
from enum import Enum
from os import listdir
from os.path import isfile, join

from tqdm import *


def pre_process(fileno, datafile):
    print('Opening file ' + str(fileno) + ': ' + datafile)
    with codecs.open(datafile, "r", 'utf-8') as f:
        datainput = [x.strip() for x in tqdm(f)]
    text_list = []
    obj_list = []
    for i in tqdm(datainput):
        try:
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
        except Exception:
            print('Error')
    with codecs.open('../data/serverdata/dataformatted' + str(fileno) + '.json', 'w', 'utf-8') as f:
        for i in obj_list:
            f.write('{}\n'.format(json.dumps(i)))


def combine_dataformatted(datano):
    datainput = {}
    for i in range(1, datano + 1):
        with codecs.open('../data/serverdata/dataformatted' + str(i) + '.json', "r", 'utf-8') as f:
            datainput[i] = [x.strip() for x in tqdm(f)]
    text_list = []
    obj_list = []
    for k, v in tqdm(datainput.items()):
        for item in v:
            json_obj = json.loads(item)
            obj_list.append(json_obj)

    with codecs.open('../data/serverdata/dataformattedF.json', 'w', 'utf-8') as f:
        for i in obj_list:
            f.write('{}\n'.format(json.dumps(i)))


def split_to_pd(feature):
    print('Spltting data using %s.' % feature)
    with open('../data/serverdata/dataformattedF.json', 'r') as f:
        lines = [x.strip() for x in f.readlines()]
    pdata = []
    ndata = []
    activitydict = {}
    transitiondict = {}

    """ Pre-processing work """
    if feature == FEATURE.DST or FEATURE.DST_RELAXED:
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
            if feature == FEATURE.DST_RELAXED:
                transitiondict[k] = set(activitydict[k])
            elif feature == FEATURE.DST:
                if len(v) == 1:
                    transitiondict[k] = activitydict[k].pop()
                else:
                    pass

    """ Actual implementation """
    for line in lines:
        obj_loaded = json.loads(line)

        # We exclude cases of NST being none and NST being OUTOFAPK
        if obj_loaded['next_transition_state'] is not None and obj_loaded['next_transition_state'] != 'OUTOFAPK':

            if feature == FEATURE.NST:
                # FEATURE.NST checks if the current state is different from the next state
                # If they are different, means positive data set. Otherwise, negative
                if obj_loaded['parent_activity_state'] == obj_loaded['next_transition_state']:
                    ndata.append(obj_loaded)
                else:
                    pdata.append(obj_loaded)

            elif feature == FEATURE.DST or FEATURE.DST_RELAXED:
                # FEATURE.DST includes checking of previous to the next state
                if obj_loaded['parent_activity_state'] == obj_loaded['next_transition_state']:
                    ndata.append(obj_loaded)
                elif obj_loaded['parent_activity_state'] in transitiondict:
                    # transitiondict[obj_loaded['parent_activity_state']] will give the previous state
                    # Checks if previous state is equivalent to the next state
                    if feature == FEATURE.DST:
                        if transitiondict[obj_loaded['parent_activity_state']] == obj_loaded['next_transition_state']:
                            ndata.append(obj_loaded)
                        else:
                            pdata.append(obj_loaded)
                    elif feature == FEATURE.DST_RELAXED:
                        # RELAXED version of DST checks if any of the previous state is equivalent to the next state
                        if obj_loaded['next_transition_state'] in transitiondict[obj_loaded['parent_activity_state']]:
                            ndata.append(obj_loaded)
                        else:
                            pdata.append(obj_loaded)

                else:
                    pdata.append(obj_loaded)

    print('Current feature: %s' % feature)
    print('Negative data amount: {}'.format(len(ndata)))
    print('Positive data amount: {}'.format(len(pdata)))
    print('Total data amount: %s' % (len(ndata) + len(pdata)))
    min_amt = min(len(ndata), len(pdata))
    with open('../data/ndata.txt', 'w') as f:
        for i in range(min_amt):
            f.write(json.dumps(ndata[i]) + '\n')

    with open('../data/pdata.txt', 'w') as f:
        for i in range(min_amt):
            f.write(json.dumps(pdata[i]) + '\n')


def get_info_on_text_pd():
    with open('../data/pdata.txt', 'r') as f:
        plines = [x.strip() for x in f.readlines()]
    with open('../data/ndata.txt', 'r') as f:
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

    with open('../data/ndatatext.txt', 'w') as f:
        f.write('count\t|norm\t|text\n')
        f.write('==========================\n')
        for i in ncount.most_common():
            f.write('{}\t|{:.6f}\t|{}\n'.format(i[1], (i[1] / len(ndata)), i[0]))

    print('Written to ndatatext.txt')

    with open('../data/pdatatext.txt', 'w') as f:
        f.write('count\t|norm\t|text\n')
        f.write('==========================\n')
        for i in pcount.most_common():
            f.write('{}\t|{:.6f}\t|{}\n'.format(i[1], (i[1] / len(ndata)), i[0]))

    print('Written to pdatatext.txt')


def get_info_on_btn_distribution():
    with open('../data/pdata.txt', 'r') as f:
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
    with open('../data/pscoreavg.txt', 'w') as f:
        f.write('avg_s\t\t|len_arr\t|text\n')
        f.write('==========================\n')
        for v in sorted_pscoredictavg:
            # print(v[0], v[1])
            f.write('{:.6f}\t|{:<10}\t|{:<10}\n'.format(v[1], len(pscoredict[v[0]]), v[0]))

    print('Written to pscoreavg.txt')


def prep_data_for_fasttext():
    print('\nPreparing data for fast text model...')

    with open('../data/pdata.txt', 'r') as f:
        pdata = [x.strip() for x in f.readlines()]

    for i in range(len(pdata)):
        jp = json.loads(pdata[i])
        pdata[i] = '__label__p ' + jp['text'].lower()

    with open('../data/ndata.txt', 'r') as f:
        ndata = [x.strip() for x in f.readlines()]

    for i in range(len(ndata)):
        jn = json.loads(ndata[i])
        ndata[i] = '__label__n ' + jn['text'].lower()

    training_amt = int(len(ndata) * 9 / 10)

    random.shuffle(pdata)
    random.shuffle(ndata)

    fttraintxt = '../data/fastTextTrain.txt'
    fttesttxt = '../data/fastTextTest.txt'
    with codecs.open(fttraintxt, 'w', 'utf-8') as f:
        for i in range(training_amt):
            f.write(pdata[i] + '\n')
            f.write(ndata[i] + '\n')

    print('Written a total of %s amount of data into %s' % (training_amt * 2, fttraintxt))

    with codecs.open(fttesttxt, 'w', 'utf-8') as f:
        try:
            for i in range(training_amt, len(ndata)):
                f.write(pdata[i] + '\n')
                f.write(ndata[i] + '\n')
        except Exception:
            pass

    print('Written a total of %s amount of data into %s' % ((len(ndata) - training_amt) * 2, fttesttxt))


def prep_data_for_wide():
    print('\nPreparing data for wide model...')
    n_dataset_list = []
    p_dataset_list = []
    categorydict = {}
    catfile = '../data/serverdata/category.txt'
    imgdimextfile = '../data/serverdata/img_dimension_extract.txt'
    ndatafile = '../data/ndata.txt'
    pdatafile = '../data/pdata.txt'

    print('\nParsing %s file.' % catfile)
    with open(catfile, 'r') as f:
        categoryinput = [x.strip() for x in tqdm(f)]

    for i in categoryinput:
        isp = i.split('\t')
        categorydict[isp[0]] = isp[1]

    print('\nParsing %s file.' % imgdimextfile)
    with open(imgdimextfile, 'r') as f:
        imgdims = [x.strip() for x in tqdm(f)]

    imgdict = {}

    for i in imgdims:
        isplit = i.split('\t')
        imgdict[isplit[0].split('/')[4]] = (isplit[1], isplit[2])

    print('\nParsing %s file.' % ndatafile)
    with open(ndatafile, 'r') as f:
        ndata = [x.strip() for x in tqdm(f)]

    for i in ndata:
        obj_loaded = json.loads(i)
        packname = obj_loaded['parent_activity_state'].split('-')[0]
        category = categorydict[packname]
        m = re.findall('{(.*?)}', obj_loaded['name'])
        btn_class = m[0]
        btn_location = m[2]
        imgname = obj_loaded['parent_activity_state'] + '.png'
        m = re.findall('\[(-?\d+),(-?\d+)\]', btn_location)
        y = [sum(x) / len(x) for x in zip((int(z) for z in (m[0])), (int(zz) for zz in m[1]))]
        positional_num = []
        try:
            for i in range(len(y)):
                positional_num.append(math.ceil(y[i] / int(imgdict[imgname][i]) * 3))
            btn_positional_representation = str(positional_num[0] + 3 * (positional_num[1] - 1))
        except Exception:
            btn_positional_representation = '-1'
        n_dataset_list.append((category, btn_class, btn_positional_representation, 'negative'))

    print('\nParsing %s file.' % pdatafile)
    with open(pdatafile, 'r') as f:
        pdata = [x.strip() for x in tqdm(f)]

    for i in pdata:
        obj_loaded = json.loads(i)
        packname = obj_loaded['parent_activity_state'].split('-')[0]
        category = categorydict[packname]
        m = re.findall('{(.*?)}', obj_loaded['name'])
        btn_class = m[0]
        btn_location = m[2]
        imgname = obj_loaded['parent_activity_state'] + '.png'
        m = re.findall('\[(\d+),(\d+)\]', btn_location)
        y = [sum(x) / len(x) for x in zip((int(z) for z in (m[0])), (int(zz) for zz in m[1]))]
        positional_num = []
        try:
            for i in range(len(y)):
                positional_num.append(math.ceil(y[i] / int(imgdict[imgname][i]) * 3))
            btn_positional_representation = str(positional_num[0] + 3 * (positional_num[1] - 1))
        except Exception:
            btn_positional_representation = '-1'
        p_dataset_list.append((category, btn_class, btn_positional_representation, 'positive'))

    training_amt = int(len(ndata) * 9 / 10)
    random.shuffle(p_dataset_list)
    random.shuffle(n_dataset_list)

    wndtraintxt = '../data/w-train.txt'
    wndtesttxt = '../data/w-test.txt'
    with codecs.open(wndtraintxt, 'w', 'utf-8') as f:
        for i in range(training_amt):
            f.write(','.join(x.lower() for x in p_dataset_list[i]) + '\n')
            f.write(','.join(x.lower() for x in n_dataset_list[i]) + '\n')

    print('Written a total of %s amount of data into %s' % (training_amt * 2, wndtraintxt))

    with codecs.open(wndtesttxt, 'w', 'utf-8') as f:
        for i in range(training_amt, len(n_dataset_list)):
            f.write(','.join(x.lower() for x in p_dataset_list[i]) + '\n')
            f.write(','.join(x.lower() for x in n_dataset_list[i]) + '\n')

    print('Written a total of %s amount of data into %s' % ((len(n_dataset_list) - training_amt) * 2, wndtraintxt))


def extract_and_combine_files():
    onlyfiles = [f for f in listdir(clickabledir) if isfile(join(clickabledir, f))]
    no_of_data = 0
    for i in onlyfiles:
        if re.match('^clickable\d+\.json$', i) is not None:
            no_of_data += 1
    print('Extracting and combining %d files...' % no_of_data)
    for i in range(1, no_of_data + 1):
        print('\nExtracting file %d' % i)
        datafile = datadir + str(i) + '.json'
        pre_process(i, datafile)
    print('\nCombining files...')
    combine_dataformatted(no_of_data)


class FEATURE(Enum):
    NST = 1  # next_state_transition equal to current state or not
    DST = 2  # Twice of next_state_transition if equal to current state or not
    DST_RELAXED = 3  # Twice of next_state_transition if equal to current state or not


current_user = getpass.getuser()
if current_user == 'hkoh006':
    datadir = '/Users/hkoh006/Desktop/UITestLearning/data/serverdata/clickable'
    clickabledir = '/Users/hkoh006/Desktop/UITestLearning/data/serverdata'
elif current_user == 'root':
    datadir = '/home/hongda/Document/UITestLearning/data/serverdata/clickable'
    clickabledir = '/home/hongda/Document/UITestLearning/data/serverdata'

try:
    """ Pre-processing the original data.json to remove any non-english sets of data, as well as null texts dataset """
    if 'e' in sys.argv[1]:
        extract_and_combine_files()

    """ splitting dataset to positive and negative data """
    if 'n' in sys.argv[1]:
        split_to_pd(FEATURE.NST)
    elif 'd' in sys.argv[1]:
        split_to_pd(FEATURE.DST)
    elif 'r' in sys.argv[1]:
        split_to_pd(FEATURE.DST_RELAXED)
    # get_info_on_text_pd()
    # get_info_on_btn_distribution()

    """ Preparing data for fasttext training and classification """
    if 'f' in sys.argv[1]:
        prep_data_for_fasttext()
    elif 'w' in sys.argv[1]:
        prep_data_for_wide()
except IndexError:
    print('Please enter arguments:')
    print('argv[1] == e: extract and combine files')
    print('argv[1] == n: split to pd with NST')
    print('argv[1] == d: split to pd with DST')
    print('argv[1] == r: split to pd with DST relaxed')
    print('argv[1] == f: preparing data for fasttext')
    print('argv[1] == w: preparing data for wide model')
