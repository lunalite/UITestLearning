import codecs
import re

import numpy as np
from gensim.models import Word2Vec
from tqdm import *

with codecs.open('../data/sequence_combination.txt', 'r', 'utf-8') as f:
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

for i in range(len(dataset)):
    dataset[i] = [x.lower() for x in dataset[i]]

"""Change value"""
grams = 4
"""END Change value"""

newdata = []
newlabel = []
for i in range(len(dataset)):
    if len(dataset[i]) >= grams:
        for j in range(len(dataset[i]) - grams + 1):
            newdata.append(dataset[i][j:j + grams])
            newlabel.append(labeldataset[i][j + grams - 1])
print(len(newdata))
print(len(newlabel))

with codecs.open('../data/dataseq-gram' + str(grams) + '.txt', 'w', 'utf-8') as f:
    for i in range(len(newdata)):
        f.write(newlabel[i] + ':::')
        f.write('\t'.join(newdata[i]))
        f.write('\n')
        print(newdata[i])
        for word in newdata[i]:
            wordList.add(word)

# word embedding model
model = Word2Vec(dataset, min_count=1, size=50)
words = list(model.wv.vocab)
model.save('../data/model.bin')
new_model = Word2Vec.load('../data/model.bin')
wordVector = np.zeros((len(wordList), 50), dtype='float32')
wordList = list(wordList)
for i in range(len(wordList)):
    wordVector[i][:] = model.wv[wordList[i]]

np.save('../data/wordVector' + str(grams), wordVector)
np.save('../data/wordList' + str(grams), np.array(wordList))
