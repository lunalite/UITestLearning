import hashlib
import json
import logging
import operator
import random
import string
import subprocess
import xml.etree.ElementTree as ET

import re

import os

import errno

from Config import Config
from Clickable import Clickable
from Data import Data
from DataActivity import DataActivity

logger = logging.getLogger(__name__)


def store_data(data, activities, clickables, mongo):
    for state, activity in activities.items():
        if state not in data.data_activity:
            data.data_activity.append(activity.state)
        for clickable in clickables[state]:
            if clickable.name not in activity.clickables:
                activity.clickables.append(clickable.name)

    logger.info('Storing data to database.')
    mongo.app.update({"_type": "data", "appname": Config.app_name}, Data.encode_data(data), upsert=True)
    for state, activity in activities.items():
        mongo.activity.update({"state": state, "parent_app": Config.app_name, "name": activity.name},
                              DataActivity.encode_data(activity),
                              upsert=True)
    for state, v in clickables.items():
        for clickable in v:
            mongo.clickable.update(
                {"name": clickable.name, "parent_activity_state": state, "parent_app_name": Config.app_name},
                Clickable.encode_data(clickable),
                upsert=True)


def load_data(mongo):
    mongo.app.find({"_type": "data", "appname": Config.app_name})
    return 1


def get_state(device, pn):
    with open(Config.classwidgetdict) as f:
        content = json.load(f)
        dict_of_widget = content

    def get_bit_rep(pn):
        xml = device.dump(compressed=False)
        root = ET.fromstring(xml.encode('utf-8'))
        bit_rep = ''
        btn_rep = ''
        for element in root.iter('node'):
            bit_rep += element.get('index')
            btn_rep += str(dict_of_widget[element.attrib['class']])


            # TODO: Add the widgetType for lower abstraction

        return bit_rep, btn_rep

    # Assumes that there is a consecutive index from 0 to 32 within dump itself
    a = '01234567891011121314151617181920212223242526272829303132'

    try:
        if a in get_bit_rep(pn)[0]:
            device.press.back()

        final_rep = get_bit_rep(pn)
        key = final_rep[0] + final_rep[1]
        hash_key = hashlib.md5(key.encode('utf-8'))
        return pn + '-' + hash_key.hexdigest()
    except KeyError:
        get_class_dict(device, Config.classwidgetdict)
        return get_state(device, pn)


def create_child_to_parent(dump):
    dump = dump.encode('ascii', 'replace')
    tree = ET.fromstring(dump)
    pmap = dict((c, p) for p in tree.iter() for c in p)
    return pmap


def get_parent_with_key(key, _parent_map):
    for child, parent in _parent_map.items():
        if key == xml_btn_to_key(child) and child.attrib['clickable'] == 'true':
            return parent
    return -1
    # raise Exception('No parent when getting parent with bound')


def get_siblings(p):
    siblings = []
    for sibling in p:
        siblings.append(sibling)
    return siblings


def get_children(p):
    children = []
    for child in p[0]:
        children.append(child)
    return children


def get_bounds_from_key(key):
    m = re.findall('({.*?})', key)
    return m[-1][1:-1]


def btn_to_key(btn):
    info = btn.info
    cd = '' if info['contentDescription'] is None else str(info['contentDescription'])
    key = '{' + info['className'].split('.')[-1] + '}-{' + cd + '}-{' + convert_bounds(btn) + '}'
    return key


def xml_btn_to_key(xml_btn):
    if xml_btn == -1:
        return None
    info = xml_btn.attrib
    # return info
    cd = '' if info['content-desc'] is None else str(info['content-desc'])
    key = '{' + info['class'].split('.')[-1] + '}-{' + cd + '}-{' + info['bounds'] + '}'
    return key


def convert_bounds(node):
    sbound = ''
    if hasattr(node, 'info'):
        bounds = node.info['bounds']
        sbound += '[' + str(bounds['left']) + ',' + str(bounds['top']) + '][' + str(bounds['right']) + ',' + str(
            bounds['bottom']) + ']'
    else:
        logger.warning('No "info" in node')
    return sbound


def get_package_name(d):
    info = d.info
    return info['currentPackageName']


def get_activity_name(d, pn):
    android_home = Config.android_home
    ps = subprocess.Popen([android_home + 'platform-tools/adb', 'shell', 'dumpsys'],
                          stdout=subprocess.PIPE)
    result = subprocess.check_output(['grep', 'mFocusedApp'], stdin=ps.stdout)
    a = result.decode()
    m = re.findall(pn + r'.*(\b.+\b)\s\w\d+\}\}', a)
    return m[0]


def get_class_dict(d, fi):
    x = d.dump(compressed=False)
    root = ET.fromstring(x)
    arr = []

    with open(fi) as f:
        content = json.load(f)
    dict = content

    if dict:
        ind = max(dict.items(), key=operator.itemgetter(1))[1]
        ind += 1
    else:
        ind = 0
    for i in root.iter():
        if 'class' in i.attrib:
            if i.attrib['class'] not in dict:
                dict[i.attrib['class']] = ind
                ind += 1

    with open(fi, 'w') as f:
        json.dump(dict, f)


def get_text():
    # TODO: Improve the way text is chosen
    return ''.join(random.choices(string.ascii_lowercase + string.ascii_uppercase + string.digits, k=10))


def merge_dicts(d1, d2):
    for k, v in d2.items():
        if k not in d1:
            d1[k] = v


def dump_log(d, packname, state):
    location = Config.log_location
    directory = location + packname + '/'
    if not os.path.exists(directory):
        os.makedirs(directory)

    d.screenshot(directory + state + '.png')
    d.dump(directory + state + '.xml')
