from __future__ import print_function

import os
import sys
from uiautomator import Device
import xml.etree.ElementTree as ET
import random
import string
import json

from Data import Data

package_name = ['me.danielbarnett.addresstogps',
                'me.dbarnett.acastus']
application_name = ['AddressToGPS', 'Acastus']

"""#########################################
Change variables below to suit your settings
#########################################"""

# Sets the device name of emulator
device_name = 'emulator-5554'

# Selecting the package and application name for the application to be used
selection_num = 0

# Selecting the data where data is being stored at.
data_store_location = './data/'

"""#########################################
End of variable setting
#########################################"""

d = Device(device_name)

edit_text_widget_text = 'android.widget.EditText'
button_widget_text = 'android.widget.Button'
image_button_widget_text = 'android.widget.ImageButton'
image_view_button_widget_text = 'android.widget.ImageView'

pack_name = package_name[selection_num]
app_name = application_name[selection_num]


def get_state():
    """
    Get state of the current UI via getting a dump of the XML structure before forming a string with the indices of node.
    :return: the bit representation of current state
    """

    def get_bit_rep():
        xml = d.dump()
        root = ET.fromstring(xml.encode('utf-8'))
        bit_rep = ''
        for element in root.iter('node'):
            bit_rep += element.get('index')
        return bit_rep

    if len(get_bit_rep()) >= 75:
        d.press.back()

    return get_bit_rep()


def click_button_intelligently_from(buttons, state_dict):
    """
    Choosing the right button to click by determining if state changes, and changing the respective scores.
    :param buttons: all possible button choices.
    :param state_dict: the dictionary of word to score pairs.
    :return: void
    """
    old_state = get_state()
    btn_to_click = make_button_decision(buttons, state_dict)
    print(btn_to_click.info['text'])
    btn_to_click.click.wait()
    if get_state() == old_state:
        print('nothing changed')
        state_dict[btn_to_click.info['text'].lower()] -= 1
    elif get_state() != old_state:
        print('changed state')
        # add mutation


def make_button_decision(buttons, state_dict):
    """
    Supervised learning, to make the decision of choosing the right buttons to click.
    :param buttons: all possible button choices.
    :param state_dict: the dictionary of word to score pairs.
    :return: returns the button to be clicked.
    """
    max_val = -9999
    max_btns = []
    for btn in buttons:
        if state_dict[btn.info['text'].lower()] > max_val:
            max_btns = [btn]
            max_val = state_dict[btn.info['text'].lower()]
        elif state_dict[btn.info['text'].lower()] == max_val:
            max_btns.append(btn)
    return random.choice(max_btns)


def click_random_button():
    click_els = d(clickable='true', packageName=pack_name)
    random.choice(click_els).click()


def get_text():
    """
    Getting random 15 characters and join them.
    :return: random string
    """
    chars = "".join([random.choice(string.letters) for i in xrange(15)])
    return chars


def store_data(data_dictionary, name):
    """
    Storing data into dictionary
    :param data_dictionary:
    :param name: contains the filename of the file to be saved to.
    """
    with open(data_store_location + name + '.txt', 'w+') as f:
        json.dump(data_dictionary, f)


def load_data(name):
    """
    Loading data from file to dictionary
    :param name: filename of the file to be read from.
    :return: a dictionary file
    """
    with open(data_store_location + name + '.txt') as f:
        return json.load(f)


def main():
    d.screen.on()
    d.press('home')
    d(resourceId='com.google.android.apps.nexuslauncher:id/all_apps_handle').click()
    d(text=app_name).click.wait()

    learning_data = Data(app_name)
    if os.path.isfile(data_store_location + app_name + '.txt'):
        learning_data.dictionary = load_data(app_name)

    click_els = d(clickable='true', packageName=pack_name)
    edit_box = []
    buttons = []
    for el in click_els:
        if el.info['className'] == edit_text_widget_text:
            edit_box.append(el)
        elif el.info['className'] in (button_widget_text, image_button_widget_text, image_view_button_widget_text):
            buttons.append(el)

    for edit in edit_box:
        edit.set_text(get_text())
    print(get_state())

    # Set this only if resetting the data
    # for btn in buttons:
    #     state_dict[btn.info['text'].lower()] = 0

    while True:
        try:
            click_button_intelligently_from(buttons, learning_data.dictionary)
        except KeyboardInterrupt:
            print
            'boohoohoo'
            store_data(learning_data.dictionary, app_name)
            sys.exit(0)


# main()

x = d.dump()
tree = ET.fromstring(x)
parent_map = dict((c, p) for p in tree.iter() for c in p)
# print(parent_map)
click_els = d(clickable='true', packageName=pack_name)

# print(click_els[0].info['className'])
print(click_els[0].info['bounds'])


def convert_bounds(node):
    if hasattr(node, 'info'):
        print(node.info)
    else:
        print('no info in node')


convert_bounds(click_els[0])


def get_parent(_child, _parent_map):
    for child, parent in _parent_map.iteritems():
        # print(child.attrib['package'])
        # print(_child.info['packageName'])
        if child.attrib['class'] == _child.info['className'] and child.attrib['package'] == _child.info['packageName'] \
                and child.attrib['text'] == _child.info['text']:
            print('hi')
            print(parent.attrib['bounds'])


#
#
get_parent(click_els[0], parent_map)
