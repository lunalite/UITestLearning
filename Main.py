from __future__ import print_function

import logging
import os
import random

from uiautomator import Device

import xml.etree.ElementTree as ET
import Utility
from Clickable import Clickable
from Config import Config
from Data import Data
from DataActivity import DataActivity
from Mongo import Mongo

d = Device(Config.device_name)

pack_name = Config.pack_name
app_name = Config.app_name

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

key_to_btn = {}
activities = []
clickables = {}
scores = []

mongo = Mongo()


def click_button_intelligently(click_els, curr_state):
    # Click_els is array of UIAutomator buttons
    btn_index = make_button_decision(click_els, curr_state)
    if btn_index == -1:
        logger.info('No observable buttons to click from after making decision')
        return None
    else:
        logger.info('index is ' + str(btn_index))
        click_els[btn_index].click.wait()
        new_state = Utility.get_state(d)
        if new_state == curr_state:
            logger.info('Nothing changed in state')
            return -1
        else:
            # logger.info('A new state. Appending next_transition_state to ' + str(old_clickable))
            for i in range(btn_index, len(clickables[curr_state])):
                if clickables[curr_state][i].name == Utility.btn_to_key(click_els[btn_index]):
                    print('yes')

            # def increase_score():
            #     # TODO: Change scale of increase based on number of clickables for next page
            #     # Currently, the increment is based on absolute number of how many clickables the new state contains.
            #     # The rationale is that the more clickable elements, the greter the chances of having more coverage.
            #     # So, more points will be given to increase the factor of exploration.
            #     # _new_click_els = d(clickable='true', packageName=pack_name)
            #     # old_length_of_clickables = len(data_activity.clickables)
            #
            #     _new_click_els = d(packageName=pack_name, clickable='true')
            #     if new_state not in key_to_btn:
            #         for btn in _new_click_els:
            #             key = Utility.btn_to_key(btn)
            #             key_to_btn[new_state + '-' + key] = btn
            #
            #     new_length_of_clickables = len(_new_click_els)
            #     score_increment = new_length_of_clickables // Config.score_para + 1
            #     # Currently, its not addition but rather, giving an absolute value of score.
            #     old_clickable.score = score_increment
            #     logger.info('Appending score ' + str(score_increment))
            #     return _new_click_els
            #
            # new_click_els = increase_score()
            # return new_state, new_click_els
            return new_state



def click_button_intelligently_from(_clickables, data_activity, curr_state):
    btn_to_click = make_button_decision(_clickables, data_activity)

    if btn_to_click is None:
        logger.info('No observable buttons to click from after making decision')
        return None, None
    old_clickable = btn_to_click

    # TODO: Add index hierarchy search
    btn_to_click = key_to_btn[curr_state + '-' + btn_to_click.name]
    logger.info('Clicking button, ' + str(btn_to_click.info['text']))
    if btn_to_click.exists:
        btn_to_click.click.wait()
    else:
        raise Exception('btn_to_click doesnt exist in click_btn_intelligently_from')
    new_state = Utility.get_state(d)
    if new_state == curr_state:
        logger.info('Nothing changed in state')
        return -1, None
    else:
        logger.info('A new state. Appending next_transition_state to ' + str(old_clickable))
        old_clickable.next_transition_state = new_state

        def increase_score():
            # TODO: Change scale of increase based on number of clickables for next page
            # Currently, the increment is based on absolute number of how many clickables the new state contains.
            # The rationale is that the more clickable elements, the greter the chances of having more coverage.
            # So, more points will be given to increase the factor of exploration.
            # _new_click_els = d(clickable='true', packageName=pack_name)
            # old_length_of_clickables = len(data_activity.clickables)


            # _new_click_els = d(packageName=pack_name, clickable='true')
            _new_click_els = d(clickable='true')

            if new_state not in key_to_btn:
                for btn in _new_click_els:
                    key = Utility.btn_to_key(btn)
                    key_to_btn[new_state + '-' + key] = btn

            new_length_of_clickables = len(_new_click_els)
            score_increment = new_length_of_clickables
            # temporary given score based on number of clickables for next page
            # Possibly give a log score but in future

            # Currently, its not addition but rather, giving an absolute value of score.
            old_clickable.score = score_increment
            logger.info('Appending score ' + str(score_increment))
            return _new_click_els

        new_click_els = increase_score()
        return new_state, new_click_els


def make_button_decision(_click_els, curr_state):
    if len(_click_els) == 0:
        logger.info('No clickable buttons available. Returning None.')
        return -1
    elif len(_click_els) == 1:
        logger.info('One clickable button available. Returning button.')
        return 0
    else:
        #
        total_score = sum(scores)
        # TODO: Improve by using dictionary
        value = random.uniform(0, total_score)
        curr_score = 0
        index = 0
        for i in scores:
            curr_score += i
            if curr_score >= value:
                return index
            index += 1


def main():
    logger.info('Starting UI testing')
    d.screen.on()
    d.press('home')
    logger.info('Force stopping ' + pack_name + ' to reset states')
    os.system('adb shell am force-stop ' + pack_name)
    d(resourceId='com.google.android.apps.nexuslauncher:id/all_apps_handle').click()
    if d(text=app_name).exists:
        d(text=app_name).click.wait()

    logger.info('Unable to find loaded data. Initializing empty data object.')
    learning_data = Data(appname=app_name, packname=pack_name)
    state = Utility.get_state(d)
    da = DataActivity(state, app_name)
    activities.append(da)
    learning_data.data_activity.append(da.state)

    click_els = d(clickable='true', packageName=pack_name)
    parent_map = Utility.create_child_to_parent(dump=d.dump())
    ar = []
    for btn in click_els:
        key = Utility.btn_to_key(btn)
        ar.append(Clickable(name=key, _parent_activity=state, _parent_name=Utility.xml_btn_to_key(
            Utility.get_parent(btn, _parent_map=parent_map))))
        scores.append(1)
    clickables[state] = ar
    click_button_intelligently(click_els, state)

    while True:
        curr_state = Utility.get_state(d)
        dat = learning_data.get_activity_by_state(curr_state)
        print(dat)
        state_result = click_button_intelligently_from(dat.clickables, dat,
                                                           curr_state)
        # state_result, new_click_els = btn_click_result
        if state_result is None:
            # No buttons to click, press back in case any new popups appear
            # Current implementation allow for only applications with the same packagename to be clicked
            d.press('back')
        elif state_result == -1:
            # No change states
            continue
        elif type(state_result) == str:
            if learning_data.get_activity_by_state(state_result) is None:
                logger.info('Adding new activity to data')
                learning_data.add_new_activity(d, state_result)
                # buttons = classify_buttons(click_els=new_click_els)


    # Utility.store_data(learning_data, activities, clickables, mongo)

    # learning_data = Utility.load_data(app_name)
    # if learning_data is None:
    #     logger.info('Unable to find loaded data. Initializing Data object.')
    #     learning_data = Data(appname=app_name, packname=pack_name)
    #     learning_data.add_new_activity(d)

    # def classify_buttons(click_els=None):
    #     edit_box = []
    #     buttons = []
    #     # Only applicable to those within the package. Any external links or applications opened will be ignored.
    #     click_els = d(clickable='true', packageName=pack_name)
    #     for el in click_els:
    #         if el.info['className'] == Config.edit_widget:
    #             edit_box.append(el)
    #         else:
    #             buttons.append(el)
    #     for edit in edit_box:
    #         edit.set_text(get_text())
    #     return buttons

    # buttons = classify_buttons()

    # Create dictionary for more efficient method


    # Utility.create_clickables_hash(key_to_btn, d, mongoClickable)
    # while True:
    # curr_state = Utility.get_state(d)
    # btn_click_result = click_button_intelligently()

    # while True:
    #     try:
    #         # TODO: Temporary no edit box first. WIll add here later by changing data structure
    #         Utility.create_clickables_hash(key_to_btn, d)
    #         curr_state = Utility.get_state(d)
    #         dat = learning_data.get_activity_by_state(curr_state)
            # print(dat)
            # btn_click_result = click_button_intelligently_from(dat.clickables, dat,
            #                                                    curr_state)
            # state_result, new_click_els = btn_click_result
            # if state_result is None:
            #     # No buttons to click, press back in case any new popups appear
            #     # Current implementation allow for only applications with the same packagename to be clicked
            #     d.press('back')
            # elif state_result == -1:
            #     # No change states
            #     continue
            # elif type(state_result) == str:
            #     if learning_data.get_activity_by_state(state_result) is None:
            #         logger.info('Adding new activity to data')
            #         learning_data.add_new_activity(d, state_result)
            #         # buttons = classify_buttons(click_els=new_click_els)
        # except KeyboardInterrupt:
        #     logger.info('KeyboardInterrupt...')
        #     Utility.store_data(learning_data, app_name)
        #     sys.exit(0)


# learning_data = Utility.load_data(app_name)
# print(learning_data)
#

main()
#
click_els = d(clickable='true')
# parent_map = Utility.create_child_to_parent(dump=d.dump(compressed=False))
dump = d.dump(compressed=False)
# tree = ET.fromstring(dump)
# # # print(d.dump(compressed=False))
# for btn in click_els:
#     print(btn.info['text'])
# # click_els[21].click.wait()
# #     p = Utility.xml_btn_to_key(Utility.get_parent(btn, _parent_map=parent_map))
#     p = Utility.get_parent(btn, _parent_map=parent_map)
#     desc = Utility.get_siblings(btn, p)
#     print(desc)
#     print(p)




# a = Utility.load_data(app_name)
# print(a)

# print(Utility.get_state(d))

# print(d.dump(compressed=False))
# a = d(resourceId='com.android.inputmethod.latin:id/keyboard_view')
# a = d(packageName='com.android.inputmethod.latin')
# a = d(clickable='true')
# print(a.child(text=""))
# for i in a:
#     print(i.info)


# for i in range(30):
#     click_els = d(clickable='true', packageName=pack_name, instance=i)
#     print(str(i) + ': ' + click_els.info['contentDescription'])

# click_els.click()
# for i in range(30):
#     click_els.click()
# print(len(click_els))
# print(str(i) + ': ' + click_el.info['text'])

# for btn in click_els:
#     print(btn.info)

#
# random.choice(click_els).click()


""" XML Testing """
# x = d.dump()
# print(x)

# print(parent_map)
# click_els = d(clickable='true', packageName=pack_name)

# Utility.create_clickables_hash(key_to_btn, d)
# click_els = d(resourceId='me.danielbarnett.addresstogps:id/app_title', packageName=pack_name)
# print(click_els[0].info['className'])
# print(click_els[0].info['bounds'])
# parent = Utility.get_parent(click_els[0], Utility.create_child_to_parent(d.dump()))
# # print(parent.attrib)
# print(Utility.xml_btn_to_key(parent))

# children = parent.findall('node')
# for child in children:
#     print(child.attrib['bounds'])
# """ End of XML Testing """
