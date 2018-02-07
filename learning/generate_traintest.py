import codecs
import math
import re
import sys
import numpy as np
from gensim.models import Word2Vec
from tqdm import *

dataset = []
labeldataset = []
widedataset = []
templist = []
labeltemplist = []
widetemplist = []
count = 0
start = False
name_diff_line = False
name_diff_temp = ''
multi_line = False
multi_line_temp = ''
wordList = set()
treat_as_individual_word = False
treat_all_null_as_invalid = False
suffix = ''
n_dataset_list = []
p_dataset_list = []
categorydict = {}
catfile = '../data/serverdata/category.txt'
imgdimextfile = '../data/serverdata/img_dimension_extract.txt'
ndatafile = '../data/ndata.txt'
pdatafile = '../data/pdata.txt'
wndtraintxt = '../data/wnd-train.txt'
wndtesttxt = '../data/wnd-test.txt'
imgdict = {}

try:
    grams = int(sys.argv[1])
    if sys.argv[2] == '10':
        suffix = 'iw'
        treat_as_individual_word = True
    elif sys.argv[2] == '00':
        pass
    elif sys.argv[2] == '11':
        suffix = 'iwin'
        treat_as_individual_word = True
        treat_all_null_as_invalid = True
    elif sys.argv[2] == '01':
        suffix = 'in'
        treat_all_null_as_invalid = True

except IndexError:
    print('Please enter arguments:')
    print('argv[1] == n: n-gram.')
    print('argv[2] == 10/00: Treating individual word or not.')
    print('argv[2] == 11/01: Treat all null sequence as invalid.')
    exit(1)

print('Parsing sequences...')
with codecs.open('../data/serverdata/sequence_combination_wnd.txt', 'r', 'utf-8') as f:
    wndcombis = [x.strip() for x in tqdm(f)]

print('Parsing %s file.' % catfile)
with open(catfile, 'r') as f:
    categoryinput = [x.strip() for x in f]

for i in categoryinput:
    isp = i.split('\t')
    categorydict[isp[0]] = isp[1]

print('Parsing %s file.' % imgdimextfile)
with open(imgdimextfile, 'r') as f:
    imgdims = [x.strip() for x in f]

for i in imgdims:
    isplit = i.split('\t')
    imgdict[isplit[0].split('/')[4]] = (isplit[1], isplit[2])

pdict = {}
ndict = {}
extradict = []

print('Parsing wndcombinations...')
for line in tqdm(wndcombis):
    if re.search('===START', line):
        templist = []
        labeltemplist = []
        widetemplist = []
        start = True
        continue
    elif re.search('===END', line):
        dataset.append(templist)
        labeldataset.append(labeltemplist)
        widedataset.append(widetemplist)
        try:
            assert len(templist) == len(labeltemplist) == len(widetemplist)
        except AssertionError:
            print(templist)
            print(labeltemplist)
            print(widetemplist)
            break
        start = False
        continue
    elif re.search('===CLOSE', line):
        templist.append('~!@#CLOSE#@!~')
        widetemplist.append('NONE')
        labeltemplist.append('neutral')
        continue

    if start:
        lsplit = line.split('\t')
        try:
            assert lsplit[-1] == 'positive' or lsplit[-1] == 'negative'
            assert len(lsplit) == 4
        except AssertionError:
            tsplit = []
            tsplit[:1] = lsplit[:1]
            if re.match('{.+}-{.*}-{.+}', lsplit[1]) is None:
                count = 2
                for j in lsplit[2:]:
                    if re.search('}', j) is not None:
                        tsplit.append('_TAB_'.join(lsplit[1:count + 1]))
                    count += 1
                if len(tsplit) == 1:
                    continue
                elif len(tsplit) == 2:
                    if re.search('}', lsplit[-2]) is not None:
                        tsplit.append('')
                    else:
                        tsplit.append(lsplit[-2])
                    tsplit.append(lsplit[-1])
            else:
                tsplit[:2] = lsplit[:2]
                tsplit.append('_TAB_'.join(lsplit[2:-1]))
                tsplit.append(lsplit[-1])
            if len(tsplit) == 4:
                lsplit = tsplit
            else:
                exit(1)
        if lsplit[1] == 'RAND_BUTTON':
            templist.append('~!@#randbutton#@!~')
        elif lsplit[1] == 'SCROLL UP':
            templist.append('~!@#scrollup#@!~')
        elif lsplit[1] == 'SCROLL DOWN':
            templist.append('~!@#scrolldown#@!~')
        elif lsplit[1] == 'BACK':
            templist.append('~!@#back#@!~')
        elif lsplit[1] == 'FLING HORIZONTAL':
            templist.append('~!@#flinghoriz#@!~')
        else:
            if len(lsplit) == 3:
                lab = lsplit[2]
                lsplit[2] = ''
                lsplit[3] = lab
            elif re.match('{.+}-{.*}-{.+}', lsplit[1]) is None:
                tsplit = []
                tsplit[:1] = lsplit[:1]
                count = 2
                for j in lsplit[2:]:
                    if re.search('}', j) is not None:
                        tsplit.append('_TAB_'.join(lsplit[1:count + 1]))
                    count += 1
                if len(tsplit) == 1:
                    continue
                elif len(tsplit) == 2:
                    if re.search('}', lsplit[-2]) is not None:
                        tsplit.append('')
                    else:
                        tsplit.append(lsplit[-2])
                    tsplit.append(lsplit[-1])
                lsplit = tsplit
            templist.append(lsplit[2])
            widetemplist.append((lsplit[0], lsplit[1]))
            labeltemplist.append(lsplit[3])
            continue
        widetemplist.append('NONE')
        labeltemplist.append(lsplit[3])

if treat_as_individual_word:
    for i in range(len(dataset)):
        tempdataset = []
        for x in range(len(dataset[i])):
            if dataset[i][x] == '':
                tempdataset.append('~!@#null#@!~')
            else:
                tempdataset.append(dataset[i][x].lower().split(' '))
        dataset[i] = tempdataset
else:
    for i in range(len(dataset)):
        for x in range(len(dataset[i])):
            if dataset[i][x] == '':
                dataset[i][x] = '~!@#null#@!~'
            else:
                dataset[i][x] = dataset[i][x].lower()

newdata = []
newlabel = []
newwide = []

print('Parsing into new lists...')
for i in tqdm(range(len(dataset))):
    if len(dataset[i]) >= grams:
        for j in range(len(dataset[i]) - grams + 1):
            if treat_all_null_as_invalid:
                checkset = set()
                for item in dataset[i][j:j + grams]:
                    if type(item) == list:
                        for itema in item:
                            checkset.add(itema)
                    else:
                        checkset.add(item)
                if len(checkset) == 1 and list(checkset)[0] == '~!@#null#@!~':
                    continue
            newdata.append(dataset[i][j:j + grams])
            newlabel.append(labeldataset[i][j + grams - 1])
            newwide.append(widedataset[i][j + grams - 1])

print('Number of newdata: %d' % len(newdata))
print('Number of newlabel: %d' % len(newlabel))
print('Number of newwide: %d' % len(newwide))

with codecs.open('../data/datawide-gram' + str(grams) + suffix + '.txt', 'w', 'utf-8') as f:
    for i in tqdm(range(len(newwide))):
        statetuple = newwide[i]
        if len(statetuple) == 2:
            packname = statetuple[0].split('-')[0]
            category = categorydict[packname]
            imgname = statetuple[0] + '.png'
            m1 = re.findall('{(.*?)}', repr(statetuple[1]))
            assert len(m1) > 1
            btn_class = m1[0]
            btn_location = m1[2]
            m2 = re.findall('\[(-?\d+),(-?\d+)\]', btn_location)
            y = [sum(x) / len(x) for x in zip((int(z) for z in (m2[0])), (int(zz) for zz in m2[1]))]
            positional_num = []
            vError = False
            kError = False
            if imgname not in imgdict:
                kError = True
            if not kError:
                if imgdict[imgname][0] == 'err':
                    vError = True
                    btn_positional_representation = '-1'

                if not vError:
                    for i in range(len(y)):
                        if y[i] > int(imgdict[imgname][i]):
                            btn_positional_representation = '-1'
                            vError = True
                if not vError:
                    if int(imgdict[imgname][0]) == 480 and int(imgdict[imgname][1]) == 800:
                        positional_num.append(math.ceil(y[0] / int(imgdict[imgname][0]) * 3))
                        positional_num.append(math.ceil(y[1] / int(imgdict[imgname][1]) * 5))
                        btn_positional_representation = str(positional_num[0] + 3 * (positional_num[1] - 1))
                    elif int(imgdict[imgname][0]) == 800 and int(imgdict[imgname][1]) == 480:
                        positional_num.append(math.ceil(y[0] / int(imgdict[imgname][0]) * 5))
                        positional_num.append(math.ceil(y[1] / int(imgdict[imgname][1]) * 3))
                        btn_positional_representation = str(positional_num[0] + 3 * (positional_num[1] - 1))
                    else:
                        for i in range(len(y)):
                            positional_num.append(math.ceil(y[i] / int(imgdict[imgname][i]) * 3))
                        btn_positional_representation = 'E' + str(positional_num[0] + 3 * (positional_num[1] - 1))
                    try:
                        if 'E' not in btn_positional_representation:
                            assert 15 >= int(btn_positional_representation) >= 1
                        else:
                            assert 9 >= int(btn_positional_representation[1:]) >= 1
                    except AssertionError:
                        btn_positional_representation = '-1'
            else:
                btn_positional_representation = '-1'
            rep = (category, btn_class, btn_positional_representation)
        else:
            rep = None

        if rep is None:
            f.write('NA')
        else:
            f.write(newlabel[i] + ':::')
            try:
                f.write('\t'.join(rep))
            except TypeError:
                print(rep)
                exit(1)
        f.write('\n')

with codecs.open('../data/dataseq-gram' + str(grams) + suffix + '.txt', 'w', 'utf-8') as f:
    for i in range(len(newdata)):
        f.write(newlabel[i] + ':::')
        if treat_as_individual_word:
            tempsection = []
            for section in newdata[i]:
                if type(section) == list:
                    for word in section:
                        tempsection.append(word)
                else:
                    tempsection.append(section)
            f.write('\t'.join(tempsection))
            f.write('\n')
            for word in tempsection:
                wordList.add(word)
        else:
            f.write('\t'.join(newdata[i]))
            f.write('\n')
            for word in newdata[i]:
                wordList.add(word)

flattened_dataset = []
for sentence in dataset:
    tempdata = []
    for data in sentence:
        if type(data) == list:
            for x in data:
                tempdata.append(x)
        else:
            tempdata.append(data)
    flattened_dataset.append(tempdata)

print('Training Word2Vec model with dimension 50.')
model = Word2Vec(flattened_dataset, min_count=1, size=50)
words = list(model.wv.vocab)
model.save('../data/model' + str(grams) + suffix + '.bin')
new_model = Word2Vec.load('../data/model' + str(grams) + suffix + '.bin')
wordVector = np.zeros((len(wordList), 50), dtype='float32')
wordList = list(wordList)
for i in range(len(wordList)):
    wordVector[i][:] = model.wv[wordList[i]]

np.save('../data/wordVector' + str(grams) + suffix, wordVector)
np.save('../data/wordList' + str(grams) + suffix, np.array(wordList))

print('\nCompleted generating word embedding for %d-gram with iw set to %s and treating null invalid set to %s' % (
    grams, treat_as_individual_word, treat_all_null_as_invalid))
