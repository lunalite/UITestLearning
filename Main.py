import logging
import os
import random
import sys

from uiautomator import Device

import Utility
from Clickable import Clickable
from Config import Config
from Data import Data
from DataActivity import DataActivity
from Mongo import Mongo

d = Device(Config.device_name)

app_name = Config.app_name

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

mongo = Mongo()

activities = {}
clickables = {}
click_hash = {}
scores = {}
visited = {}
parent_map = {}
mask = {}
zero_counter = 0

def click_button(old_state, new_click_els, pack_name):
    # Have to use packageName since there might be buttons leading to popups,
    # which can continue exploding into more activity if not limited.
    global d, clickables, parent_map, visited, scores, mask, zero_counter
    click_els = d(clickable='true', packageName=pack_name) if new_click_els is None else new_click_els

    if len(click_els) != len(visited[old_state]):
        old_state = Utility.get_state(d, pack_name)
        buffer_check = []
        for click in click_els:
            buffer_check.append((Utility.btn_to_key(click)))
        click_buffer = []
        for click in clickables[old_state]:
            click_buffer.append(click.name)

        logger.info('=======')
        logger.info(buffer_check)
        logger.info(click_buffer)
        logger.info('=======')

        if len(click_buffer) > len(buffer_check):
            # In the case that there's one button less in the current state
            diff = list(set(click_buffer) - set(buffer_check))
            logger.info('=========@@@@@@@=@+@+@=@=@+@+@+@=@==========')
            logger.info(diff)
            logger.info(len(click_buffer))
            logger.info(len(buffer_check))
            for dx in diff:
                ind = 0
                for i in click_buffer:
                    if i == dx:
                        print('000-------000')
                        # print(ind)
                        # print(len(clickables[old_state]))
                        # print(len(visited[old_state]))
                        # del clickables[old_state][ind]
                        # del visited[old_state][ind]
                        # del scores[old_state][ind]
                        # del i
                    ind += 1
        elif len(click_buffer) == len(buffer_check):
            pass
        else:
            # In case there's additional button in current state
            diff = list(set(buffer_check) - set(click_buffer))
            for dx in diff:
                ind = 0
                for i in buffer_check:
                    if i == dx:
                        bound = Utility.get_bounds_from_key(i)
                        _parent = Utility.get_parent_with_bound(bound, parent_map[old_state])
                        sibs = Utility.get_siblings(_parent)
                        children = Utility.get_children(_parent)
                        clickables[old_state].insert(1, Clickable(name=i,
                                                                  _parent_activity_state=old_state,
                                                                  _parent_app_name=app_name,
                                                                  _parent=Utility.xml_btn_to_key(_parent),
                                                                  _siblings=[Utility.xml_btn_to_key(sib) for sib in
                                                                             sibs],
                                                                  _children=[Utility.xml_btn_to_key(child) for child in
                                                                             children]))
                        visited[old_state].insert(ind, [1, 0])
                        scores[old_state].insert(ind, 1)

    btn_result = make_decision(click_els, visited[old_state])
    if btn_result == -1 or zero_counter == 5:
        d.press('back')
        return None, Utility.get_state(d, pack_name)
    else:
        try:
            if click_els[btn_result].exists:
                if Utility.btn_to_key(click_els[btn_result]) == clickables[old_state][btn_result].name:
                    click_els[btn_result].click.wait()
                else:
                    logger.warning('Tracing back reason why buttnon not matched')
                    logger.warning(Utility.btn_to_key(click_els[btn_result]))
                    logger.warning(clickables[old_state][btn_result].name)
                    logger.warning(old_state)
                    raise Exception('Button not matched')

                new_state = Utility.get_state(d, pack_name)

                if new_state != old_state:
                    clickables[old_state][btn_result].next_transition_state = new_state
                    new_click_els = d(clickable='true', packageName=pack_name)
                    score_increment = len(new_click_els)
                    scores[old_state][btn_result] = score_increment
                    visited[old_state][btn_result][1] += 1
                    visited[old_state][btn_result][0] = (score_increment / visited[old_state][btn_result][1])
                    clickables[old_state][btn_result].score = score_increment
                    return new_click_els, new_state
                else:
                    # No change in state so give it a score of 0 since it doesn't affect anything
                    # TODO: possibly increase abstraction so that change in state is determined by change in text too.
                    visited[old_state][btn_result][1] += 1
                    visited[old_state][btn_result][0] = (0 / visited[old_state][btn_result][1])
                    return click_els, new_state
            else:
                raise Exception('Warning, no such buttons available in click_button()')
        except IndexError:
            logger.info("Index error")
            logger.warning(len(click_els))
            logger.warning(len(visited[old_state]))
            logger.warning(btn_result)
            sys.exit(0)


def make_decision(click_els, _scores_arr):
    global zero_counter
    if len(click_els) == 0:
        logger.info('No clickable buttons available. Returning -1.')
        zero_counter = 0
        return -1
    elif len(click_els) == 1:
        logger.info('One clickable button available. Returning 0.')
        zero_counter += 1
        return 0
    else:
        total_score = sum([x[0] for x in _scores_arr])
        value = random.uniform(0, total_score)

        # For the case that a button has 0 score, we ignore them
        # This happens for cases when the button leads to an external link
        zeroes = [idex for idex, iscore in enumerate(_scores_arr) if iscore[0] == 0]

        curr_score = 0
        index = 0
        for i in _scores_arr:
            curr_score += i[0]
            if curr_score >= value:
                if index not in zeroes:
                    return index
            index += 1
        zero_counter = 0
        return -1


def main():
    global clickables, scores, visited, parent_map, activities
    logger.info('Starting UI testing')
    d.screen.on()
    d.press('home')
    d(resourceId='com.google.android.apps.nexuslauncher:id/all_apps_handle').click()
    logger.info('Getting the package name with the application name: ' + app_name)
    d(text=app_name).click.wait()
    pack_name = Utility.get_package_name(d)
    logger.info('Package name is: ' + pack_name)

    logger.info('Force stopping ' + pack_name + ' to reset states')
    os.system('adb shell am force-stop ' + pack_name)
    d(text=app_name).click.wait()

    learning_data = Data(_appname=app_name,
                         _packname=pack_name,
                         _data_activity=[])
    old_state = Utility.get_state(d, pack_name)

    def rec(local_state):
        if Utility.get_package_name(d) == 'com.google.android.apps.nexuslauncher':
            raise KeyboardInterrupt
        elif Utility.get_package_name(d) != pack_name:
            d.press('back')
            return -1
        da = DataActivity(local_state, Utility.get_activity_name(d, pack_name), app_name, [])
        activities[local_state] = da
        click_els = d(clickable='true', packageName=pack_name)

        parent_map[old_state] = Utility.create_child_to_parent(dump=d.dump(compressed=False))
        ar = []
        arch = []
        ars = []
        arv = []
        for btn in click_els:
            arch.append(Utility.btn_to_key(btn))
        click_hash[local_state] = arch
        for btn in click_hash[local_state]:
            bound = Utility.get_bounds_from_key(btn)
            _parent = Utility.get_parent_with_bound(bound, parent_map[old_state])
            sibs = Utility.get_siblings(_parent)
            children = Utility.get_children(_parent)
            clickables[local_state][btn]=Clickable(name=btn,
                                _parent_activity_state=local_state,
                                _parent_app_name=app_name,
                                _parent=Utility.xml_btn_to_key(_parent),
                                _siblings=[Utility.xml_btn_to_key(sib) for sib in sibs],
                                _children=[Utility.xml_btn_to_key(child) for child in children])
            scores[local_state][]
            # ar.append(Clickable(name=btn,
            #                     _parent_activity_state=local_state,
            #                     _parent_app_name=app_name,
            #                     _parent=Utility.xml_btn_to_key(_parent),
            #                     _siblings=[Utility.xml_btn_to_key(sib) for sib in sibs],
            #                     _children=[Utility.xml_btn_to_key(child) for child in children]))
            # ars.append(1)
            # arv.append([1, 0])

        clickables[local_state] = ar
        scores[local_state] = ars
        visited[local_state] = arv
        return 1

    rec(old_state)

    # TODO: Add in storage of clickables into dataactivity
    # TODO: Add in storage of dataactivity into data
    # TODO: Determine if there can be new clickables in an unchanged state

    new_click_els = None
    counter = 0
    while True:
        try:
            edit_btns = d(clickable='true', packageName=pack_name,className='android.widget.EditText')
            for i in edit_btns:
                i.set_text(Utility.get_text())
                click_els = d(clickable='true', packageName=pack_name)
                for i in click_els:
                    if i.info['text'] == 'ADD TO DICTIONARY':
                        click_els[0].click.wait()


            new_click_els, new_state = click_button(old_state, new_click_els, pack_name)
            # logger.info(scores)
            logger.info(visited)
            res = 1
            if new_state != old_state and new_state not in scores:
                res = rec(new_state)

            if res == 1:
                old_state = new_state
            else:
                print('dd')

            if counter % 10 == 0:
                logger.info('Saving data to database...')
                Utility.store_data(learning_data, activities, clickables, mongo)
            counter += 1

        except KeyboardInterrupt:
            logger.info('KeyboardInterrupt...')
            Utility.store_data(learning_data, activities, clickables, mongo)
            sys.exit(0)


main()
# pack_name = Utility.get_package_name(d)
pack_name = 'AutomateIt.mainPackage'
# print(Utility.get_state(d, pack_name))
# click_els = d(clickable='true', packageName=pack_name)
# for i in click_els:
#     print(Utility.btn_to_key(i))
# print(len(click_els))
# print(d.dump(compressed=False))



def rec(local_state):
    if Utility.get_package_name(d) == 'com.google.android.apps.nexuslauncher':
        raise KeyboardInterrupt
    elif Utility.get_package_name(d) != pack_name:
        d.press('back')
        return -1
    # da = DataActivity(local_state, Utility.get_activity_name(d, pack_name), app_name, [])
    # activities[local_state] = da
    # click_els = d(clickable='true', packageName=pack_name)

    # parent_map[old_state] = Utility.create_child_to_parent(dump=d.dump(compressed=False))
    # ar = []
    # arch = []
    # ars = []
    # arv = []
    # for btn in click_els:
    #     arch.append(Utility.btn_to_key(btn))
    # click_hash[local_state] = arch
    # for btn in click_hash[local_state]:
    #     bound = Utility.get_bounds_from_key(btn)
    #     _parent = Utility.get_parent_with_bound(bound, parent_map[old_state])
    #     sibs = Utility.get_siblings(_parent)
    #     children = Utility.get_children(_parent)
    #     ar.append(Clickable(name=btn,
    #                         _parent_activity_state=local_state,
    #                         _parent_app_name=app_name,
    #                         _parent=Utility.xml_btn_to_key(_parent),
    #                         _siblings=[Utility.xml_btn_to_key(sib) for sib in sibs],
    #                         _children=[Utility.xml_btn_to_key(child) for child in children]))
    #     ars.append(1)
    #     arv.append([1, 0])
    #
    # clickables[local_state] = ar
    # scores[local_state] = ars
    # visited[local_state] = arv
    return 1



# s = Utility.get_state(d, pack_name)
# r = rec(s)
# print(r)
#
# print(Utility.get_state(d, pack_name))
