import codecs
import json
import re
from tqdm import *

with codecs.open('./data.json', "r", 'utf-8') as f:
    datainput = [x.strip() for x in tqdm(f)]
    
chosen_obj = []
for i in tqdm(datainput):
    json_obj = json.loads(i)
    # print(json_obj['name'])
    condesc = re.findall('^{.*}-{(.*)}-{.*}$', json_obj['name'])
    try:
        if condesc[0] != '':
            chosen_obj.append(i)
    except:
        pass

print(len(chosen_obj))

with codecs.open('./dataformatted.json', 'w', 'utf-8') as f:
    for i in chosen_obj:
        f.write(i + '\n')
