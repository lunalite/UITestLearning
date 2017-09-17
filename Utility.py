import logging
import xml.etree.ElementTree as ET

import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


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


def get_siblings(child_key, p):
    piter = p.iter()
    next(piter)  # skip parent
    descendents = [elem for elem in piter if xml_btn_to_key(elem) != child_key]
    return descendents


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
