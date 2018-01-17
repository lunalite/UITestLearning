from os import listdir
from os.path import isfile, join

import re

sequence_list = []
onlyfiles = [f for f in listdir('.') if isfile(join('.', f))]
for file in onlyfiles:

    with open(file, 'r') as f:
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

print('@!@!@!@!@!@!@!@')
for i in sequence_list:
    print(i)
