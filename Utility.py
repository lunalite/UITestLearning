"""======================================================

Utility file that holds every single miscellaneous tasks

======================================================"""

import json
import logging
import os
import random
import string
import xml.etree.ElementTree as ET

from Clickable import Clickable
from Config import Config
from Data import Data
from DataActivity import DataActivity

data_store_location = Config.data_store_location

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def store_data(data, name):
    logger.info('Storing data into file at ' + data_store_location + name + '.txt')
    with open(data_store_location + name + '.txt', 'w') as f:
        json.dump(data, default=lambda o: o.__dict__, fp=f)


def load_data(name):
    carr = {}
    carr_score = {}
    darr = []
    logger.info('Loading data from file ' + data_store_location + name + '.txt')

    def t(j):
        # print(j)
        if 'name' in j:
            parent_activity_state = j['parent_activity_state']
            c = Clickable(j['name'], parent_activity_state, j['score'], j['next_transition_state'],
                          _parent_name=j['parent_name'])
            if parent_activity_state not in carr:
                carr[parent_activity_state] = []
                carr_score[parent_activity_state] = []
            carr[parent_activity_state].append(c)
            carr_score[parent_activity_state].append(c.score)
        elif 'activity_state' in j:
            da = DataActivity(state=j['activity_state'], _clickables=carr[j['activity_state']],
                              _clickables_score=carr_score[j['activity_state']])
            darr.append(da)
        else:
            data = Data(appname=j['appname'], packname=j['packname'], _data_activity=darr)
            return data

    if os.path.isfile(data_store_location + name + '.txt'):
        with open(data_store_location + name + '.txt') as f:
            return json.load(f, object_hook=t)
    else:
        return None


def convert_bounds(node):
    sbound = ''
    if hasattr(node, 'info'):
        bounds = node.info['bounds']
        sbound += '[' + str(bounds['left']) + ',' + str(bounds['top']) + '][' + str(bounds['right']) + ',' + str(
            bounds['bottom']) + ']'
    else:
        logger.warning('No "info" in node')
    return sbound


# a = '[0,210][1080,1316]'
# print(convert_bounds(click_els[0]))

def create_child_to_parent(dump):
    tree = ET.fromstring(dump)
    parent_map = dict((c, p) for p in tree.iter() for c in p)
    return parent_map


def get_parent(_child, _parent_map):
    for child, parent in _parent_map.items():

        # method 1 to compare all these classes
        # if child.attrib['class'] == _child.info['className'] and child.attrib['package'] == _child.info['packageName'] \
        #         and child.attrib['text'] == _child.info['text']:
        #     print(parent.attrib['bounds'])

        # method 2 to to compare bounds
        if child.attrib['bounds'] == convert_bounds(_child):
            return parent


def get_siblings(child_btn, p):
    descendents = [elem for elem in p.iter() if xml_btn_to_key(elem) != btn_to_key(child_btn)]
    return descendents


def get_state(device):
    def get_bit_rep():
        xml = device.dump(compressed=False)
        root = ET.fromstring(xml.encode('utf-8'))
        bit_rep = ''
        for element in root.iter('node'):
            bit_rep += element.get('index')
        return bit_rep

    # Assumes that there is a consecutive index from 0 to 32 within dump itself
    a = '01234567891011121314151617181920212223242526272829303132'

    if a in get_bit_rep():
        device.press.back()

    return get_bit_rep()[-20:]


def btn_to_key(btn):
    info = btn.info
    # key = '{' + info['className'].split('.')[-1] + '}-{' + str(info['text']) + '}-{' + str(
    #     info['contentDescription']) + '}-{' + convert_bounds(btn) + '}'
    key = '{' + info['className'].split('.')[-1] + '}-{' + str(
        info['contentDescription']) + '}-{' + convert_bounds(btn) + '}'
    return key


def xml_btn_to_key(xml_btn):
    info = xml_btn.attrib
    # return info
    key = '{' + info['class'].split('.')[-1] + '}-{' + str(
        info['content-desc']) + '}-{' + info['bounds'] + '}'
    return key


# def key_to_btn(key):
#     attributes = {}
#     print(key)
#     m = re.findall('{(.*?)}', key)
#     # Typically android.widget class name
#     attributes['className'] = 'android.widget.' + m[0]
#     attributes['text'] = m[1]
#     attributes['contentDescription'] = m[2]
#     attributes['bounds'] = m[3]
#     return attributes


def get_text():
    return ''.join(random.choices(string.ascii_lowercase + string.ascii_uppercase + string.digits, k=15))


def create_clickables_hash(_key_to_btn, d):
    # btns_to_click = d(packageName=Config.pack_name, clickable='true')
    btns_to_click = d(clickable='true')
    curr_state = get_state(d)
    for btn in btns_to_click:
        key = btn_to_key(btn)
        _key_to_btn[curr_state + '-' + key] = btn
    _key_to_btn[curr_state] = True
