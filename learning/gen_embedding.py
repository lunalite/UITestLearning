import codecs
import re
from itertools import chain

import numpy as np
from gensim.models import Word2Vec
from tqdm import *

with codecs.open('../data/serverdata/sequence_combination.txt', 'r', 'utf-8') as f:
    lines = [x.strip('\n') for x in f.readlines()]

dataset = []
labeldataset = []
templist = []
labeltemplist = []
count = 0
start = False
name_diff_line = False
name_diff_temp = ''
multi_line = False
multi_line_temp = ''
wordList = set()

"""Change value"""
grams = 4
treat_as_individual_word = False
"""END Change value"""

if treat_as_individual_word:
    suffix = 'iw'
else:
    suffix = ''


def append_to_temp(tempstr, _templist, _labeltemplist):
    _lsplit = tempstr.split('\t')
    _templist.append(_lsplit[1])
    _labeltemplist.append(_lsplit[2])
    if len(_lsplit) < 3:
        print(_lsplit)
    return False, ''


for line in tqdm(lines):
    if re.search('===START', line):
        if name_diff_line:
            name_diff_line, name_diff_temp = append_to_temp(name_diff_temp, templist, labeltemplist)
        elif multi_line:
            multi_line, multi_line_temp = append_to_temp(multi_line_temp, templist, labeltemplist)
        start = True
        templist = []
        labeltemplist = []
        continue
    elif re.search('===END', line):
        if name_diff_line:
            name_diff_line, name_diff_temp = append_to_temp(name_diff_temp, templist, labeltemplist)
        elif multi_line:
            multi_line, multi_line_temp = append_to_temp(multi_line_temp, templist, labeltemplist)
        start = False
        dataset.append(templist)
        labeldataset.append(labeltemplist)
        continue
    elif re.search('===CLOSE', line):
        if name_diff_line:
            name_diff_line, name_diff_temp = append_to_temp(name_diff_temp, templist, labeltemplist)
        elif multi_line:
            multi_line, multi_line_temp = append_to_temp(multi_line_temp, templist, labeltemplist)
        templist.append('~!@#CLOSE#@!~')
        labeltemplist.append('neutral')
        continue

    if start:
        if len(line.split('\t')) <= 2 or (line.split('\t')[2] != 'negative' or 'positive'):
            '''In case the content description is long like {ImageView}-{Lorem ipsum dolor sit amet, consectetur 
            adipiscing elit. Mauris et magna ut erat elementum cursus in quis ipsum. Nam faucibus ultrices eros, 
            vel tempor leo semper sit amet. Duis magna quam, congue vitae interdum nec, condimentum ut lectus. Sed 
            commodo venenatis eros a dignissim. Nunc adipiscing turpis nec magna venenatis at ultricies ipsum 
            bibendum. Sed volutpat urna quis nisi vulputate egestas. Etiam eu dui a enim lacinia dapibus. 
            Pellentesque habitant morbi tristique senectus et netus et malesuada fames ac turpis egestas. '''
            if name_diff_line:
                if len(name_diff_temp.split('\t')) == 3:
                    name_diff_line, name_diff_temp = append_to_temp(name_diff_temp, templist, labeltemplist)
            elif multi_line:
                if len(multi_line_temp.split('\t')) == 3:
                    multi_line, multi_line_temp = append_to_temp(multi_line_temp, templist, labeltemplist)

            if not re.search('^{.+}-{.*}-{.+}', line) and re.search('^{.+', line):
                name_diff_line = True
                name_diff_temp += line
            else:
                if name_diff_line:
                    name_diff_temp += '\n' + line
                elif multi_line:
                    multi_line_temp += '\n' + line
                else:
                    # for cases where text spans multiple line
                    multi_line = True
                    multi_line_temp += line
            continue
        if name_diff_line:
            name_diff_line, name_diff_temp = append_to_temp(name_diff_temp, templist, labeltemplist)
        elif multi_line:
            multi_line, multi_line_temp = append_to_temp(multi_line_temp, templist, labeltemplist)
        lsplit = line.split('\t')
        templist.append(lsplit[1])
        labeltemplist.append(lsplit[2])

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
for i in range(len(dataset)):
    if len(dataset[i]) >= grams:
        for j in range(len(dataset[i]) - grams + 1):
            newdata.append(dataset[i][j:j + grams])
            newlabel.append(labeldataset[i][j + grams - 1])
print(len(newdata))
print(len(newlabel))

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

# print(wordList)

# word embedding model
flattened_dataset=[]
for sentence in dataset:
    tempdata = []
    for data in sentence:
        if type(data) == list:
            for x in data:
                tempdata.append(x)
        else:
            tempdata.append(data)
    flattened_dataset.append(tempdata)

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
