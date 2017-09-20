import logging
import os
import random

import sys

import Utility
from Clickable import Clickable
from Config import Config
from Data import Data
from DataActivity import DataActivity
from Mongo import Mongo
from uiautomator import Device

d = Device(Config.device_name)

pack_name = Config.pack_name
app_name = Config.app_name

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

mongo = Mongo()

activities = {}
clickables = {}
click_hash = {}
scores = {}


def click_button(old_state, new_click_els):
    # Have to use packageName since there might be buttons leading to popups,
    # which can continue exploding into more activity if not limited.
    click_els = d(clickable='true', packageName=pack_name) if new_click_els is None else new_click_els
    btn_result = make_decision(click_els, scores[old_state])
    if btn_result == -1:
        d.press('back')
        return None, Utility.get_state(d)
    else:
        if click_els[btn_result].exists:
            # logger.info('Clicking button, ' + str(click_hash[old_state][btn_result]))
            click_els[btn_result].click.wait()
            new_state = Utility.get_state(d)

            if new_state != old_state:
                clickables[old_state][btn_result].next_state_transition = new_state
                new_click_els = d(clickable='true', packageName=pack_name)
                score_increment = len(new_click_els)
                scores[old_state][btn_result] = score_increment
                clickables[old_state][btn_result].score = score_increment
                return new_click_els, new_state
            else:
                return click_els, new_state
        else:
            raise Exception('Warning, no such buttons available in click_button()')


def make_decision(click_els, _scores_arr):
    if len(click_els) == 0:
        logger.info('No clickable buttons available. Returning -1.')
        return -1
    elif len(click_els) == 1:
        logger.info('One clickable button available. Returning 0.')
        return 0
    else:
        total_score = sum(_scores_arr)
        value = random.uniform(0, total_score)

        # For the case that a button has 0 score, we ignore them
        # This happens for cases when the button leads to an external link
        zeroes = [idex for idex, iscore in enumerate(_scores_arr) if iscore == 0]

        curr_score = 0
        index = 0
        for i in _scores_arr:
            curr_score += i
            if curr_score >= value:
                if index not in zeroes:
                    return index
            index += 1
        return -1


def main():
    logger.info('Starting UI testing')
    d.screen.on()
    d.press('home')
    logger.info('Force stopping ' + pack_name + ' to reset states')
    os.system('adb shell am force-stop ' + pack_name)
    d(resourceId='com.google.android.apps.nexuslauncher:id/all_apps_handle').click()
    # if d(text=app_name).exists:
    d(text=app_name).click.wait()
    # else:
    #     logger.warning('doesnt exist')

    learning_data = Data(_appname=app_name,
                         _packname=pack_name,
                         _data_activity=[])
    old_state = Utility.get_state(d)

    def rec(local_state):
        da = DataActivity(local_state, app_name, [])
        activities[local_state] = da
        click_els = d(clickable='true')
        parent_map = Utility.create_child_to_parent(dump=d.dump(compressed=False))
        ar = []
        arch = []
        ars = []
        for btn in click_els:
            arch.append(Utility.btn_to_key(btn))
        click_hash[local_state] = arch

        for btn in click_hash[local_state]:
            bound = Utility.get_bounds_from_key(btn)
            _parent = Utility.get_parent_with_bound(bound, parent_map)
            sibs = Utility.get_siblings(_parent)
            children = Utility.get_children(_parent)
            ar.append(Clickable(name=btn,
                                _parent_activity_state=local_state,
                                _parent_app_name=app_name,
                                _parent=Utility.xml_btn_to_key(_parent),
                                _siblings=[Utility.xml_btn_to_key(sib) for sib in sibs],
                                _children=[Utility.xml_btn_to_key(child) for child in children]))
            ars.append(1)

        clickables[local_state] = ar
        scores[local_state] = ars

    rec(old_state)

    # TODO: Add in storage of clickables into dataactivity
    # TODO: Add in storage of dataactivity into data
    # TODO: Determine if there can be new clickables in an unchanged state

    new_click_els = None
    counter = 0
    while True:
        try:
            new_click_els, new_state = click_button(old_state, new_click_els)
            logger.info(scores)
            if new_state != old_state and new_state not in scores:
                rec(new_state)

            old_state = new_state
            if counter % 10 == 0:
                logger.info('Saving data to database...')
                Utility.store_data(learning_data, activities, clickables, mongo)
            counter += 1

        except KeyboardInterrupt:
            logger.info('KeyboardInterrupt...')
            sys.exit(0)


main()
# print(d.dump(compressed=False))
# old_state = Utility.get_state(d)
# new_state = old_state
# print(old_state)
# click_els = d(clickable='true', packageName=pack_name)
# for i in click_els:
#     print(i)
# btn_result = make_decision(click_els, scores[old_state])

# rec(new_state)
