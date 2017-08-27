from __future__ import print_function

import operator
from uiautomator import Device
import xml.etree.ElementTree as ET
import random
import string

device_name = 'emulator-5554'
d = Device(device_name)

package_name = 'me.danielbarnett.addresstogps'
# package_name = 'me.dbarnett.acastus'
application_name = 'AddressToGPS'
# application_name = 'Acastus'

edit_text_widget_text = 'android.widget.EditText'
button_widget_text = 'android.widget.Button'
image_button_widget_text = 'android.widget.ImageButton'
image_view_button_widget_text = 'android.widget.ImageView'


def get_state():
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

    # def convert_xml():
    #     xml = d.dump()

    # print xml
    # root = ET.fromstring(xml.encode('utf-8'))
    # print type(obj)
    # print obj.name
    # print obj.get_attribute()
    # for element in root.iter('node'):
    #     print element
    # els = []
    # predicate = './/node[@package="' + package_name + '"]'
    # print predicate
    # print xml
    xml_arr = []
    curr_index = 0
    # for target in root.findall(predicate):
    #     if target.attrib['index'] == curr_index:
    #         xml_arr.append(target)
    #         curr_index += 1
    #     else:


state_dict = {}


def click_button_intelligently_from(buttons):
    old_state = get_state()
    btn_to_click = make_button_decision(buttons)
    print(btn_to_click.info['text'])
    btn_to_click.click.wait()
    if get_state() == old_state:
        print('nothing changed')
        state_dict[btn_to_click.info['text'].lower()] -= 1
    elif get_state() != old_state:
        print('changed state')
        # add mutation


def make_button_decision(buttons):
    max_val = -9999
    max_btns = []
    for btn in buttons:
        if state_dict[btn.info['text'].lower()] > max_val:
            max_btns = []
            max_btns.append(btn)
            max_val = state_dict[btn.info['text'].lower()]
        elif state_dict[btn.info['text'].lower()] == max_val:
            max_btns.append(btn)
    return random.choice(max_btns)


def click_random_button():
    click_els = d(clickable='true', packageName=package_name)
    random.choice(click_els).click()


# els.append(target)
# for target in els:
#     for sib in target.itersiblings():
#         print sib.attrib['resource-id']


def get_text():
    chars = "".join([random.choice(string.letters) for i in xrange(15)])
    return chars


def main():
    """Traversing to the application"""
    d.screen.on()
    d.press('home')
    d(resourceId='com.google.android.apps.nexuslauncher:id/all_apps_handle').click()
    d(text=application_name).click.wait()

    # convert_xml()

    click_els = d(clickable='true', packageName=package_name)
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
    for btn in buttons:
        state_dict[btn.info['text'].lower()] = 0
    while True:
        click_button_intelligently_from(buttons)


main()
