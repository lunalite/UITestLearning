from __future__ import print_function
from uiautomator import Device
import xml.etree.ElementTree as ET
import random

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


def click_random_button_from(buttons):
    random.choice(buttons).click.wait()


def click_random_button():
    click_els = d(clickable='true', packageName=package_name)
    random.choice(click_els).click()


# els.append(target)
# for target in els:
#     for sib in target.itersiblings():
#         print sib.attrib['resource-id']


def get_text():
    return 'random'


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
        print(btn.info)
        print(btn.info['contentDescription'])
        print(btn.info['text'])
        print(btn.info['resourceName'])
    click_random_button_from(buttons)
    click_random_button()
    click_random_button()

    click_random_button()
    click_random_button()
    click_random_button()
    click_random_button()

main()
