import codecs
import json
import random
import re
import string

import sys
from tqdm import *
from pathlib import Path

datajsonfile = Path("./dataformatted.json")
datanjson = Path("./tndata.json")
datapjson = Path("./tpdata.json")
chosen_obj = []

if datanjson.is_file() and datapjson.is_file():
    pass
elif datajsonfile.is_file():
    with codecs.open('./dataformatted.json', "r", 'utf-8') as f:
        chosen_strlist = [x.strip() for x in tqdm(f)]
    for str in chosen_strlist:

        chosen_obj.append(json.loads(str))
else:
    with codecs.open('./data.json', "r", 'utf-8') as f:
        datainput = [x.strip() for x in tqdm(f)]
    chosen_str = []
    for i in tqdm(datainput):
        json_obj = json.loads(i)
        condesc = re.findall('^{.*}-{(.*)}-{.*}$', json_obj['name'])
        try:
            if condesc[0] != '':
                ne = False
                for scii in condesc[0]:
                    if scii not in string.printable:
                        ne = True
                        break
                if not ne:
                    chosen_obj.append(json_obj)
                    chosen_str.append(i)
        except Exception:
            pass

    with codecs.open('./dataformatted.json', 'w', 'utf-8') as f:
        for i in chosen_str:
            f.write(i + '\n')

if datanjson.is_file() and datapjson.is_file():
    pass
else:
    ndata = []
    pdata = []
    for obj in chosen_obj:
        currs = obj['parent_activity_state']
        nexts = obj['next_transition_state']
        if currs == nexts:
            ndata.append(obj)
        elif currs != nexts:
            pdata.append(obj)

    print('Number of negative data: {}'.format(len(ndata)))
    print('Number of positive data: {}'.format(len(pdata)))

    minvalue = min(len(ndata), len(pdata))

    print('Grabbing a total of {} data from both positive and negative datasets.'.format(minvalue))

    tpdata = pdata[:minvalue]
    tndata = ndata[:minvalue]

    json.dump(tpdata, open('./tpdata.json', 'w'))
    json.dump(tndata, open('./tndata.json', 'w'))

import collections

def add_vocab():
    tndata = json.load(open('./tndata.json'))
    tpdata = json.load(open('./tpdata.json'))
    count = []
    vocab = set()
    strx = ''
    for str in tndata:
        condesc = re.findall('^{.*}-{(.*)}-{.*}$', str['name'])
        strx += condesc[0]
        # for word in condesc[0].split():
        #     str.join(condesc[0].sp)
        #     collections.Counter(word)
        #     vocab.add(word.lower())
    # print(vocab)
    # print(strx)
    print(collections.Counter(strx.lower().split()))
    # vocab2 = set()
    # for str in tpdata:
    #     condesc = re.findall('^{.*}-{(.*)}-{.*}$', str['name'])
    #     for word in condesc[0].split():
    #         vocab.add(word.lower())
    # print(vocab)
    # print('==============')
    #
    #
    # for str in tpdata:
    #     condesc = re.findall('^{.*}-{(.*)}-{.*}$', str['name'])
    #     strx += condesc[0]
    #     # for word in condesc[0].split():
    #     #     str.join(condesc[0].sp)
    #     #     collections.Counter(word)
    #     #     vocab.add(word.lower())
    # # print(vocab)
    # # print(strx)
    # print(collections.Counter(strx.split()))

add_vocab()
