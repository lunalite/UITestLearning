from __future__ import print_function

import logging
import os
import random
import sys

from uiautomator import Device

import Utility
from Config import Config
from Data import Data

d = Device(Config.device_name)

pack_name = Config.pack_name
app_name = Config.app_name

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

key_to_btn = {}


def click_button_intelligently_from(_clickables, data_activity, curr_state):
    btn_to_click = make_button_decision(_clickables, data_activity)

    if btn_to_click is None:
        logger.info('No observable buttons to click from after making decision')
        return None, None
    old_clickable = btn_to_click

    # TODO: Add index hierarchy search
    btn_to_click = key_to_btn[curr_state + '-' + btn_to_click.name]
    logger.info('Clicking button, ' + str(btn_to_click.info['text']))
    btn_to_click.click.wait()
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

            _new_click_els = d(packageName=pack_name, clickable='true')
            if new_state not in key_to_btn:
                for btn in _new_click_els:
                    key = Utility.btn_to_key(btn)
                    key_to_btn[new_state + '-' + key] = btn

            new_length_of_clickables = len(_new_click_els)
            score_increment = new_length_of_clickables // 5 + 1
            # Currently, its not addition but rather, giving an absolute value of score.
            old_clickable.score = score_increment
            logger.info('Appending score ' + str(score_increment))
            return _new_click_els

        new_click_els = increase_score()
        return new_state, new_click_els


def make_button_decision(_clickables, data_activity):
    if len(_clickables) == 0:
        logger.info('No clickable buttons available. Returning None.')
        return None
    elif len(_clickables) == 1:
        logger.info('One clickable button available. Returning button.')
        return _clickables[0]
    else:
        total_score = sum(data_activity.clickables_score)
        # TODO: Improve by using dictionary
        value = random.uniform(0, total_score)
        curr_score = 0
        index = 0
        for i in data_activity.clickables_score:
            curr_score += i
            if curr_score >= value:
                return _clickables[index]
            index += 1


def main():
    logger.info('Starting UI testing')
    d.screen.on()
    d.press('home')
    logger.info('Force stopping ' + pack_name + ' to reset states')
    os.system('adb shell am force-stop ' + pack_name)
    d(resourceId='com.google.android.apps.nexuslauncher:id/all_apps_handle').click()
    d(text=app_name).click.wait()

    learning_data = Utility.load_data(app_name)
    if learning_data is None:
        logger.info('Unable to find loaded data. Initializing Data object.')
        learning_data = Data(appname=app_name, packname=pack_name)
        learning_data.add_new_activity(d)

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
    btns_to_click = d(packageName=pack_name, clickable='true')
    curr_state = Utility.get_state(d)
    for btn in btns_to_click:
        key = Utility.btn_to_key(btn)
        key_to_btn[curr_state + '-' + key] = btn
    key_to_btn[curr_state] = True

    while True:
        try:
            # TODO: Temporary no edit box first. WIll add here later by changing data structure
            curr_state = Utility.get_state(d)
            dat = learning_data.get_activity_by_state(curr_state)
            btn_click_result = click_button_intelligently_from(dat.clickables, dat,
                                                               curr_state)
            state_result, new_click_els = btn_click_result
            if state_result is None:
                # No buttons to click
                break
            elif state_result == -1:
                # No change states
                continue
            elif type(state_result) == str:
                if learning_data.get_activity_by_state(state_result) is None:
                    logger.info('Adding new activity to data')
                    learning_data.add_new_activity(d, state_result)
                    # buttons = classify_buttons(click_els=new_click_els)
        except KeyboardInterrupt:
            logger.info('KeyboardInterrupt...')
            Utility.store_data(learning_data, app_name)
            sys.exit(0)


# main()
# print(Utility.get_state(d))
# print(d.dump(compressed=False))
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



# """ XML Testing """
# x = d.dump()
# tree = ET.fromstring(x)
# parent_map = dict((c, p) for p in tree.iter() for c in p)
# # print(parent_map)
# click_els = d(clickable='true', packageName=pack_name)
#
# # print(click_els[0].info['className'])
# # print(click_els[0].info['bounds'])
# # parent = get_parent(click_els[0], parent_map)
# # children = parent.findall('node')
# # for child in children:
# #     print(child.attrib['bounds'])
# """ End of XML Testing """
