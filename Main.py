from __future__ import print_function

import logging
import random
import string
import sys

import os
from uiautomator import Device

import Utility
from Config import Config
from Data import Data

d = Device(Config.device_name)

pack_name = Config.pack_name
app_name = Config.app_name

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def click_button_intelligently_from(buttons, data_activity, curr_state):
    """
    Choosing the right button to click by determining if state changes, and changing the respective scores.
    :param buttons: all possible button choices.
    :param data_activity: activity data structure
    :param curr_state: current state
    :return:
    """
    btn_to_click = make_button_decision(buttons, data_activity)
    old_clickable = data_activity.get_clickable_by_name(Utility.btn_to_key(btn_to_click))
    if btn_to_click is None:
        logger.info('No observable buttons to click from after making decision')
        return None
    logger.info('Clicking button, ' + str(btn_to_click.info['text']))
    btn_to_click.click()
    new_state = Utility.get_state(d)
    if new_state == curr_state:
        logger.info('Nothing changed in state')
        # old_clickable.score -= 1
        return -1
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
            new_length_of_clickables = len(_new_click_els)
            score_increment = new_length_of_clickables // 5 + 1
            # Currently, its not addition but rather, giving an absolute value of score.
            old_clickable.score = score_increment
            logger.info('Appending score ' + str(score_increment))
            return _new_click_els

        _new_click_els = increase_score()
        return new_state


def make_button_decision(buttons, data_activity):
    """
    Supervised learning, to make the decision of choosing the right buttons to click.
    :param buttons: all possible button choices.
    :param data_activity: current activity data storage
    :return: returns the button to be clicked.
    """
    logger.info(len(buttons))
    if len(buttons) == 0:
        logger.info('No clickable buttons available. Returning None.')
        return None
    elif len(buttons) == 1:
        logger.info('One clickable button available. Returning button.')
        return buttons[0]
    else:
        total_score = 0
        score_arrangement = {}
        for btn in buttons:
            clickable = data_activity.get_clickable_by_name(Utility.btn_to_key(btn))
            total_score += clickable.score
            score_arrangement[total_score] = btn
        value = random.uniform(0, total_score)
        for i in score_arrangement:
            if i >= value:
                return score_arrangement[i]


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

    def classify_buttons():
        edit_box = []
        buttons = []
        click_els = d(clickable='true', packageName=pack_name)
        for el in click_els:
            if el.info['className'] == Config.edit_widget:
                edit_box.append(el)
            else:
                buttons.append(el)
        for edit in edit_box:
            edit.set_text(Utility.get_text())
        return buttons

    buttons = classify_buttons()

    while True:
        try:
            curr_state = Utility.get_state(d)
            dat = learning_data.get_activity_by_state(curr_state)
            btn_click_result = click_button_intelligently_from(buttons, dat,
                                                               curr_state)
            if btn_click_result is None:
                # No buttons to click
                break
            elif btn_click_result == -1:
                # No change states
                continue
            elif type(btn_click_result) == str:
                if learning_data.get_activity_by_state(btn_click_result) is None:
                    learning_data.add_new_activity(d, btn_click_result)
                buttons = classify_buttons()

        except KeyboardInterrupt:
            logger.info('KeyboardInterrupt...')
            Utility.store_data(learning_data, app_name)
            sys.exit(0)


main()
# print(Utility.get_state(d))
# print(d.dump())
# click_els = d(clickable='true', packageName=pack_name)
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
