import argparse
import codecs
import logging
import os
import random
import string
import sys
import subprocess
import time

import re
from uiautomator import Device

import Utility
from Clickable import Clickable
from Config import Config
from Data import Data
from DataActivity import DataActivity
from Mongo import Mongo

d = Device(Config.device_name)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

mongo = Mongo()

activities = {}
clickables = {}
click_hash = {}
scores = {}
visited = {}
parent_map = {}
zero_counter = 0


def init():
    """
    Initializing all global variables back to its original state after every testing is done on APK
    :return:
    """
    global clickables, scores, visited, parent_map, activities, click_hash, zero_counter
    activities.clear()
    clickables.clear()
    click_hash.clear()
    scores.clear()
    visited.clear()
    parent_map.clear()
    zero_counter = 0


def click_button(new_click_els, pack_name, app_name):
    # Have to use packageName since there might be buttons leading to popups,
    # which can continue exploding into more activity if not limited.
    global d, clickables, parent_map, visited, scores, mask, zero_counter
    old_state = Utility.get_state(d, pack_name)

    click_els = d(clickable='true', packageName=pack_name) if new_click_els is None else new_click_els

    btn_result = make_decision(click_els, visited[old_state])
    logger.info(len(parent_map))
    if btn_result == -1 or zero_counter == 5:
        d.press('back')

        # Issue with clicking back button prematurely
        if Utility.get_package_name(d) == 'com.google.android.apps.nexuslauncher':
            d(text=app_name).click.wait()
        return None, Utility.get_state(d, pack_name)
    else:
        try:
            if click_els[btn_result].exists:
                click_btn_key = Utility.btn_to_key(click_els[btn_result])
                click_btn_class = click_els[btn_result].info['className']
                click_btn = click_els[btn_result]

                # Check if the key of button to be clicked is equal to the key of button stored in clickables
                if click_btn_key == clickables[old_state][btn_result].name:
                    click_btn.click()

                # Search through list to see if the button is of another number
                else:
                    ind = 0
                    found = False
                    for i in clickables[old_state]:
                        if click_btn_key == i.name:
                            click_btn.click.wait()
                            btn_result = ind
                            found = True
                        ind += 1
                    if not found:
                        logger.info('button to be found: ' + click_btn_key)
                        logger.info(clickables[old_state][btn_result].name)
                        logger.info(clickables[old_state][btn_result].name == click_btn_key)

                        # If no such clickable is found, we append the clickable into the list
                        logger.info(old_state)
                        logger.info(Utility.get_state(d, pack_name))
                        new_parent = Utility.create_child_to_parent(dump=d.dump(compressed=False))
                        Utility.merge_dicts(parent_map[old_state], new_parent)
                        logger.info(len(parent_map[old_state]))
                        _parent = Utility.get_parent_with_key(click_btn_key, parent_map[old_state])
                        if _parent != -1:
                            sibs = Utility.get_siblings(_parent)
                            children = Utility.get_children(_parent)
                        else:
                            sibs = None
                            children = None
                        clickables[old_state].append(Clickable(name=click_btn_key,
                                                               _parent_activity_state=old_state,
                                                               _parent_app_name=app_name,
                                                               _parent=Utility.xml_btn_to_key(_parent),
                                                               _siblings=[Utility.xml_btn_to_key(sib) for sib in
                                                                          sibs],
                                                               _children=[Utility.xml_btn_to_key(child) for child in
                                                                          children]))
                        visited[old_state].append([1, 0])
                        scores[old_state].append(1)

                # If the button that is clicked is EditText or TextView, it might cause autocomplete tab to appear
                # We have to add this to close the tab that appears.
                if click_btn_class == 'android.widget.EditText' or click_btn_class == 'android.widget.TextView':
                    click_els = d(clickable='true', packageName=pack_name)
                    for i in click_els:
                        if i.info['text'] == 'ADD TO DICTIONARY':
                            click_els[0].click.wait()
                            break

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
                    clickables[old_state][btn_result].next_transition_state = old_state
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
            exit(0)


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
        if total_score < 0.5 * len(_scores_arr):
            return -1
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


def main(app_name, pack_name):
    global clickables, scores, visited, parent_map, activities
    logger.info('Starting UI testing')
    d.screen.on()
    d.press('home')

    # logger.info('Getting the package name with the application name: ' + app_name)
    # d(text=app_name).click.wait()
    # pack_name = Utility.get_package_name(d)
    # logger.info('Package name is: ' + pack_name)

    logger.info('Force stopping ' + pack_name + ' to reset states')
    os.system('adb shell am force-stop ' + pack_name)
    d(resourceId='com.google.android.apps.nexuslauncher:id/all_apps_handle').click()
    d(scrollable=True).scroll.toEnd()
    d(scrollable=True).scroll.vert.to(text=app_name)
    d(text=app_name).click.wait()

    learning_data = Data(_appname=app_name,
                         _packname=pack_name,
                         _data_activity=[])

    # To ensure that loading page and everything is done before starting testing
    time.sleep(10)

    old_state = Utility.get_state(d, pack_name)

    def rec(local_state):
        global parent_map
        if Utility.get_package_name(d) == 'com.google.android.apps.nexuslauncher':
            raise KeyboardInterrupt
        elif Utility.get_package_name(d) != pack_name:
            initstate = Utility.get_state(d, pack_name)
            d.press('back')
            nextstate = Utility.get_state(d, pack_name)
            if nextstate != initstate:
                return -1

            # Prepare for the situation of when pressing back button doesn't work
            elif nextstate == initstate:
                while True:
                    tryclick_btns = d(clickable='true')
                    random.choice(tryclick_btns).click()
                    nextstate = Utility.get_state(d, pack_name)
                    if nextstate != initstate:
                        return -1

        da = DataActivity(local_state, Utility.get_activity_name(d, pack_name), app_name, [])
        activities[local_state] = da
        click_els = d(clickable='true', packageName=pack_name)
        parent_map[local_state] = Utility.create_child_to_parent(dump=d.dump(compressed=False))
        ar = []
        arch = []
        ars = []
        arv = []
        for btn in click_els:
            arch.append(Utility.btn_to_key(btn))
        click_hash[local_state] = arch
        for btn in click_hash[local_state]:
            # logger.info('getting parents')
            # logger.info(old_state)
            # logger.info(Utility.get_state(d, pack_name))
            _parent = Utility.get_parent_with_key(btn, parent_map[local_state])
            if _parent != -1:
                sibs = Utility.get_siblings(_parent)
                children = Utility.get_children(_parent)
            else:
                sibs = None
                children = None
            ar.append(Clickable(name=btn,
                                _parent_activity_state=local_state,
                                _parent_app_name=app_name,
                                _parent=Utility.xml_btn_to_key(_parent),
                                _siblings=[Utility.xml_btn_to_key(sib) for sib in sibs or []],
                                _children=[Utility.xml_btn_to_key(child) for child in children or []]))
            ars.append(1)
            arv.append([1, 0])

        clickables[local_state] = ar
        scores[local_state] = ars
        visited[local_state] = arv
        Utility.dump_log(d, pack_name, local_state)
        return 1

    rec(old_state)
    new_click_els = None
    counter = 0

    while True:
        try:
            edit_btns = d(clickable='true', packageName=pack_name, className='android.widget.EditText')
            for i in edit_btns:
                if i.text == '':
                    i.set_text(Utility.get_text())
            Utility.get_state(d, pack_name)
            if d(scrollable='true').exists:
                r = random.uniform(0, Config.scroll_probability[2])
                logger.info(r)
                if r < Config.scroll_probability[0]:
                    new_click_els, new_state = click_button(new_click_els, pack_name, app_name)
                else:
                    if r < Config.scroll_probability[1]:
                        d(scrollable='true').fling()
                    elif r < Config.scroll_probability[2]:
                        d(scrollable='true').fling.backward()

                    new_state = Utility.get_state(d, pack_name)
                    new_click_els = d(clickable='true', packageName=pack_name)
            else:
                new_click_els, new_state = click_button(new_click_els, pack_name, app_name)

            logger.info(visited)
            logger.info(counter)
            if new_state != old_state and new_state not in scores:
                rec(new_state)

            if counter % 10 == 0:
                logger.info('Saving data to database...')
                Utility.store_data(learning_data, activities, clickables, mongo)

            counter += 1
            if counter >= 200:
                return

        except KeyboardInterrupt:
            logger.info('KeyboardInterrupt...')
            Utility.store_data(learning_data, activities, clickables, mongo)
            return
        except KeyError:
            logger.info('KeyError...')
            Utility.store_data(learning_data, activities, clickables, mongo)
            return
        except IndexError:
            logger.info('IndexError...')
            Utility.store_data(learning_data, activities, clickables, mongo)
            return


def official():
    dir = Config.apkdir
    ANDROID_HOME = Config.ANDROID_HOME
    x = subprocess.check_output(['ls', dir])
    apks = (x.split(b'\n'))
    apks = [x.decode('utf-8') for x in apks]
    timestr = time.strftime("%Y%m%d%H%M%S")
    file = codecs.open('information-' + timestr + '.txt', 'w', 'utf-8')

    for i in apks:
        english = True
        m = re.findall('^(.*)\_.*\.apk', i)
        apk_packname = m[0]
        subprocess.Popen(['adb', 'install', dir + i]).wait()
        ps = subprocess.Popen([ANDROID_HOME + 'build-tools/26.0.1/aapt', 'dump', 'badging', dir + i],
                              stdout=subprocess.PIPE)
        output = subprocess.check_output(('grep', 'application-label:'), stdin=ps.stdout)
        label = output.decode('utf-8')
        m = re.findall('^application-label:(.*)$', label)
        appname = m[0][1:-1]
        Config.app_name = appname
        logger.info('====================')
        logger.info('testing ' + appname)
        for i in m[0]:
            if i not in string.printable:
                english = False
                break
        attempts = 0
        if english:
            init()
            while attempts <= 3:
                main(appname, apk_packname)
                attempts += 1

        act_c = mongo.activity.count({"_type": "activity", "parent_app": Config.app_name})
        click_c = mongo.clickable.count({"_type": "clickable", "parent_app_name": Config.app_name})
        file.write(appname + '|' + apk_packname + '|' + str(english) + '|' + str(act_c) + '|' + str(click_c) + '\n')
        subprocess.Popen(['adb', 'uninstall', apk_packname]).wait()
        # break


# if len(sys.argv) <= 2:
#     print('Error. Not enough input')
# else:
# device_name = sys.argv[1]
# device_port = sys.argv[2]
device_name = 'Nexus_5X_API_26'
device_port = '5554'
device_serial = 'emulator-' + device_port
subprocess.Popen(['emulator', '-avd', device_name, '-port', device_port, '-noaudio', '-no-window'])

while True:
    output = subprocess.check_output(['adb', 'devices'])
    m = re.findall(device_serial + '\t(.*)', output.decode('utf-8'))
    if len(m) >= 1:
        if m[0] == 'offline':
            pass
        elif m[0] == 'device':
            logger.info('Device is online. Unlocking screen...')
            d.screen.on()
            d.press('menu')
            c = d(clickable='true')
            if len(c) >= 10:
                logger.info('Unlocked screen... Continuing with testing.')
            break

    time.sleep(5)

official()
