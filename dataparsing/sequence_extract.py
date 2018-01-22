import codecs
from os import listdir
from os.path import isfile, join

import re

import sys

directory = sys.argv[1]
sequence_list = []
onlyfiles = [f for f in listdir(directory) if isfile(join(directory, f))]
for file in onlyfiles:
    if file.endswith('.txt'):
        with codecs.open(join(directory, file), 'r', 'utf-8') as f:
            lines = [x.strip() for x in f.readlines()]

        start = False
        for line in lines:
            if re.search('=== END OF SEQUENCE', line):
                sequence_list.append('===END')
                start = False
            if start:
                if re.search('=== BEGIN OF SEQUENCE ===', line):
                    continue
                elif re.search('=== END ATTEMPT', line):
                    sequence_list.append('===CLOSE')
                    continue
                if not re.search('\t', line):
                    sequence_list[-1][-2] = sequence_list[-1][-2] + '\n' + line
                    continue
                lsplit = line.split('\t')
                if len(lsplit) == 2:
                    lsplit.append('')
                if sequence_list:
                    if sequence_list[len(sequence_list) - 1][0] == lsplit[0]:
                        lsplit.append('negative')
                    else:
                        lsplit.append('positive')
                sequence_list.append(lsplit)
            if re.search('=== BEGIN OF SEQUENCE ===', line):
                sequence_list.append('===START')
                start = True

with codecs.open('./sequence_combination.txt', 'w', 'utf-8') as f:
    for i in sequence_list:
        if type(i) is list:
            f.write('\t'.join(i[1:]))
        else:
            f.write(i)
        f.write('\n')