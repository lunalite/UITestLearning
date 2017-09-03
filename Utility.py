"""======================================================

Utility file that holds every single miscellaneous tasks

======================================================"""

import json
import os
import xml.etree.ElementTree as ET

from Clickables import Clickables
from Config import Config
from Data import Data
from DataActivity import DataActivity

data_store_location = Config.data_store_location


def store_data(data, name):
    """
    Storing data into dictionary
    :param json: json dictionary structure
    :param name: contains the filename of the file to be saved to.
    """
    with open(data_store_location + name + '.txt', 'w+') as f:
        json.dump(data, default=lambda o: o.__dict__, fp=f)


def load_data(name):
    """
    Loading data from file to dictionary
    :param name: filename of the file to be read from.
    :return: a dictionary file
    """
    carr = []
    darr = []

    def t(j):
        if 'name' in j:
            c = Clickables(j['name'], j['score'], j['next_transition_state'])
            carr.append(c)
        elif 'state' in j:
            da = DataActivity(j['state'], carr)
            darr.append(da)
        else:
            data = Data(j['appname'], j['packname'], data_activity=darr)
            return data

    if os.path.isfile(data_store_location + name + '.txt'):
        with open(data_store_location + name + '.txt') as f:
            return json.load(f, object_hook=t)
    else:
        return None


def convert_bounds(node):
    """
    Convert to bound from dictionary to string
    :param node:
    :return: String of [left,top][right,down] representing the bounds of where widget is placed at.
    """
    sbound = ''
    if hasattr(node, 'info'):
        bounds = node.info['bounds']
        sbound += '[' + str(bounds['left']) + ',' + str(bounds['top']) + '][' + str(bounds['right']) + ',' + str(
            bounds['bottom']) + ']'
    else:
        print('no info in node')
    return sbound


# a = '[0,210][1080,1316]'
# print(convert_bounds(click_els[0]))


def get_parent(_child, _parent_map):
    """
    Gets parent of the child in XML dump by iterating through parent to child map - very inefficient.
    :param _child: the child obtained from d(new UISelector).
    :param _parent_map: The parent to child map.
    :return: parent node
    """
    for child, parent in _parent_map.iteritems():

        # method 1 to compare all these classes
        # if child.attrib['class'] == _child.info['className'] and child.attrib['package'] == _child.info['packageName'] \
        #         and child.attrib['text'] == _child.info['text']:
        #     print(parent.attrib['bounds'])

        # method 2 to to compare bounds
        if child.attrib['bounds'] == convert_bounds(_child):
            return parent


def get_state(device):
    """
    Get state of the current UI via getting a dump of the XML structure before forming a string with the indices of node.
    :param device:
    :return: the bit representation of current state
    """

    def get_bit_rep():
        xml = device.dump()
        root = ET.fromstring(xml.encode('utf-8'))
        bit_rep = ''
        for element in root.iter('node'):
            bit_rep += element.get('index')
        return bit_rep

    if len(get_bit_rep()) >= 75:
        device.press.back()

    return get_bit_rep()


def btn_to_key(btn):
    info = btn.info
    key = '{' + info['className'].split('.')[-1] + '}-{' + info['text'] + '}-{' + info[
        'contentDescription'] + '}-{' + convert_bounds(btn) + '}'
    return key
