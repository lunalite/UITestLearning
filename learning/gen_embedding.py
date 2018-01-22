import codecs
import re

from gensim.models import Word2Vec

with codecs.open('../data/sequence_combination.txt', 'r', 'utf-8') as f:
    lines = [x.strip() for x in f.readlines()]

dataset = []
templist = []
count = 0
start = False
for line in lines:
    if re.search('===START', line):
        start = True
        templist = []
        continue
    elif re.search('===END', line):
        start = False
        dataset.append(templist)
    elif re.search('===CLOSE', line):
        templist.append('~!@#CLOSE#@!~')
        continue

    if start:
        lsplit = line.split('\t')
        print('===')
        print(line)
        print(lsplit)
        templist.append(lsplit[1])
        print(templist)

print(len(dataset))
for i in dataset:
    print(i)
    break

# sentences = [['this', 'is', 'the', 'first', 'sentence', 'for', 'word2vec'],
# 			['this', 'is', 'the', 'second', 'sentence'],
# 			['yet', 'another', 'sentence'],
# 			['one', 'more', 'sentence'],
# 			['and', 'the', 'final', 'sentence']]
# # train model
# model = Word2Vec(sentences, min_count=1)
# # fit a 2d PCA model to the vectors
# X = model[model.wv.vocab]
# words = list(model.wv.vocab)
# print(words)
# print(model['this'])
