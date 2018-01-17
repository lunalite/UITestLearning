from os import listdir
from os.path import isfile, join

import re

import sys

directory = sys.argv[1]
sequence_list = []
onlyfiles = [f for f in listdir(directory) if isfile(join(directory, f))]
for file in onlyfiles:
    if file.endswith('.txt'):
        with open(join(directory, file), 'r') as f:
            lines = [x.strip() for x in f.readlines()]

        start = False
        end = False

        for line in lines:
            if re.search('=== END OF SEQUENCE', line):
                sequence_list.append('===END')
                start = False
            if start:
                if re.search('=== END ATTEMPT', line):
                    sequence_list.append('===CLOSE')
                    continue
                lsplit = line.split('\t')
                if len(lsplit) == 2:
                    lsplit.append('')
                if sequence_list:
                    if sequence_list[len(sequence_list) - 1][0] == lsplit[0]:
                        lsplit.append('negative')
                    else:
                        lsplit.append('positive')
                else:
                    lsplit.append('positive')
                sequence_list.append(lsplit)
            if re.search('=== BEGIN OF SEQUENCE ===', line):
                start = True

with open('./sequence_combination.txt', 'w') as f:
    for i in sequence_list:
        f.write(i)
