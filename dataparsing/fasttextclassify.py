import re
import subprocess

import itertools

import time

learning_rate = [x * 0.005 for x in range(1, 11)]
# dimension = [x for x in range(1, 11)]
dimension = [10]
# epoch = [x for x in range(1, 11)]
epoch = [10]
min_count = 1

s = [learning_rate, dimension, epoch]
p = list(itertools.product(*s))
print(len(p))
maxf1 = 0
max_i = ()
for i in p:
    subprocess.Popen(
        ['fasttext', 'supervised', '-input', '../data/fastTextTrain.txt', '-output', 'model', '-lr', str(i[0]),
         '-dim', str(i[1]), '-epoch', str(i[2]), '-minCount', str(min_count)])
    time.sleep(1)
    omsg = subprocess.Popen(['fasttext', 'test', './model.bin', '../data/fastTextTest.txt'],
                            stdout=subprocess.PIPE)
    o = omsg.communicate()[0].decode('utf-8')
    no = re.findall('\d*\.?\d+', o, re.MULTILINE)
    precision = float(no[2])
    recall = float(no[4])
    f1 = 2 * (precision * recall) / (precision + recall)
    maxf1 = max(f1, maxf1)
    max_i = i
    print(maxf1)
    print(max_i)
    time.sleep(1)
