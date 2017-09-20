import logging
import xml.etree.ElementTree as ET

import re

from Config import Config
from Clickable import Clickable
from Data import Data
from DataActivity import DataActivity

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def store_data(data, activities, clickables, mongo):
    # print('-----')
    # print(data)r
    # print('-----')
    # print(activities)
    # print('-----')
    # print(clickables)

    for state, activity in activities.items():
        data.data_activity.append(activity.state)
        for clickable in clickables[state]:
            activity.clickables.append(clickable.name)

    # print('-----')
    # print(data)
    # print('-----')
    # print(activities)
    # print('-----')
    # print(clickables)

    logger.info('Storing data to database.')
    mongo.app.update({"_type": "data", "appname": Config.app_name}, Data.encode_data(data), upsert=True)
    for state, activity in activities.items():
        mongo.activity.update({"state": state, "parent_app": Config.app_name}, DataActivity.encode_data(activity),
                              upsert=True)
    for state, v in clickables.items():
        for clickable in v:
            mongo.clickable.update(
                {"name": clickable.name, "parent_activity_state": state, "parent_app": Config.app_name},
                Clickable.encode_data(clickable),
                upsert=True)


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


def create_child_to_parent(dump):
    tree = ET.fromstring(dump)
    parent_map = dict((c, p) for p in tree.iter() for c in p)
    return parent_map


# def get_parent(_child, _parent_map):
#     # TODO: inefficient method. Improve it.
#     print(_child)
#     print(_parent_map)
#     for child, parent in _parent_map.items():
#         if child.attrib['bounds'] == convert_bounds(_child):
#             return parent


def get_parent_with_bound(bound, _parent_map):
    # TODO: What if no parent?
    for child, parent in _parent_map.items():
        if bound == child.attrib['bounds']:
            return parent


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
    key = '{' + info['className'].split('.')[-1] + '}-{' + str(
        info['contentDescription']) + '}-{' + convert_bounds(btn) + '}'
    return key


def xml_btn_to_key(xml_btn):
    info = xml_btn.attrib
    # return info
    key = '{' + info['class'].split('.')[-1] + '}-{' + str(
        info['content-desc']) + '}-{' + info['bounds'] + '}'
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
