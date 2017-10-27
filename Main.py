import codecs
import logging
import random
import re
import signal
import string
import subprocess
import time
import os
import sys

from Mongo import Mongo
from uiautomator import Device

from Config import Config

log_location = Config.log_location
if not os.path.exists(log_location):
    os.makedirs(log_location)
logging.basicConfig(filename=log_location + 'main-' + sys.argv[1] + '.log', level=logging.DEBUG)
logger = logging.getLogger(__name__)
logging.getLogger().addHandler(logging.StreamHandler())
logging.info('================Begin logging==================')

now = time.strftime("%c")
logger.info(now)

import Utility
from Clickable import Clickable
from Data import Data
from DataActivity import DataActivity

mongo = Mongo()

android_home = Config.android_home

activities = {}
clickables = {}
click_hash = {}
scores = {}
visited = {}
parent_map = {}
zero_counter = 0


def signal_handler(signum, frame):
    raise Exception("Timed out!")


signal.signal(signal.SIGALRM, signal_handler)


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
    if old_state not in visited:
        print('===')
        print(old_state)
        print(visited)
        print('errror')
    counter = 0
    while True:
        btn_result = make_decision(click_els, visited[old_state])
        if btn_result < len(click_els):
            break
        else:
            logger.info('trying to make decision and find btn to click again.')
        if counter >= 200:
            raise Exception('No buttons to click')

    logger.info('Length of the parent_map currently: ' + str(len(parent_map)))
    if btn_result == -1 or zero_counter == 5:
        d.press('back')

        # Issue with clicking back button prematurely
        if Utility.get_package_name(d) == 'com.google.android.apps.nexuslauncher':
            subprocess.Popen(
                [android_home + '/platform-tools/adb', '-s', device_name, 'shell', 'monkey', '-p', pack_name, '5'],
                stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
        return None, Utility.get_state(d, pack_name)
    else:
        try:
            if click_els[btn_result].exists:
                click_btn_key = Utility.btn_to_key(click_els[btn_result])
                click_btn_class = click_els[btn_result].info['className']
                click_btn = click_els[btn_result]

                # Check if the key of button to be clicked is equal to the key of button stored in clickables
                if click_btn_key == clickables[old_state][btn_result].name:
                    click_btn.click.wait()

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
                            sibs = [Utility.xml_btn_to_key(sib) for sib in
                                    Utility.get_siblings(_parent)]
                            children = [Utility.xml_btn_to_key(child) for child in
                                        Utility.get_children(_parent)]
                        else:
                            sibs = None
                            children = None
                        clickables[old_state].append(Clickable(name=click_btn_key,
                                                               _parent_activity_state=old_state,
                                                               _parent_app_name=app_name,
                                                               _parent=Utility.xml_btn_to_key(_parent),
                                                               _siblings=sibs,
                                                               _children=children))
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
            logger.info('@@@@@@@@@@@@@@@=============================')
            logger.info("Index error with finding right button to click. Restarting...")
            logger.warning(len(click_els))
            logger.warning(len(visited[old_state]))
            logger.warning(btn_result)
            raise IndexError('')


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
    d.press('home')

    logger.info('Force stopping ' + pack_name + ' to reset states')
    subprocess.Popen([android_home + 'platform-tools/adb', '-s', device_name, 'shell', 'am', 'force-stop', pack_name])
    logger.info('Starting ' + pack_name + ' using monkey...')
    msg = subprocess.Popen(
        [android_home + '/platform-tools/adb', '-s', device_name, 'shell', 'monkey', '-p', pack_name, '5'],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    startmsg = msg.communicate()[0].decode('utf-8')
    if len(re.findall('No activities found to run', startmsg)) > 0:
        return -2

    learning_data = Data(_appname=app_name,
                         _packname=pack_name,
                         _data_activity=[])

    # To ensure that loading page and everything is done before starting testing
    time.sleep(10)

    old_state = Utility.get_state(d, pack_name)

    def rec(local_state):
        global parent_map
        if Utility.get_package_name(d) == 'com.google.android.apps.nexuslauncher':
            return -2, local_state
        elif Utility.get_package_name(d) != pack_name:
            initstate = Utility.get_state(d, pack_name)
            d.press('back')
            nextstate = Utility.get_state(d, pack_name)
            if nextstate != initstate:
                return -1, nextstate

            # Prepare for the situation of when pressing back button doesn't work
            elif nextstate == initstate:
                while True:
                    tryclick_btns = d(clickable='true')
                    random.choice(tryclick_btns).click.wait()
                    nextstate = Utility.get_state(d, pack_name)
                    if nextstate != initstate:
                        return -1, nextstate

        da = DataActivity(local_state, Utility.get_activity_name(d, pack_name, device_name), app_name, [])
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
        return 1, local_state

    rec(old_state)
    new_click_els = None
    counter = 0

    while True:
        try:
            edit_btns = d(clickable='true', packageName=pack_name)
            for i in edit_btns:
                if i.text == '':
                    i.set_text(Utility.get_text())
            if d(scrollable='true').exists:
                r = random.uniform(0, Config.scroll_probability[2])
                if r < Config.scroll_probability[0]:
                    new_click_els, new_state = click_button(new_click_els, pack_name, app_name)
                else:
                    logger.info('Scrolling...')
                    if r < Config.scroll_probability[1]:
                        d(scrollable='true').fling()
                    elif r < Config.scroll_probability[2]:
                        d(scrollable='true').fling.backward()

                    new_state = Utility.get_state(d, pack_name)
                    new_click_els = d(clickable='true', packageName=pack_name)
            else:
                new_click_els, new_state = click_button(new_click_els, pack_name, app_name)

            logger.info('Number of iterations: ' + str(counter))
            if new_state != old_state and new_state not in scores:
                recvalue = -1
                while recvalue == -1:
                    recvalue, new_state = rec(new_state)
                    if new_state in scores:
                        recvalue = 1

            if counter % 10 == 0:
                logger.info('Saving data to database...')
                Utility.store_data(learning_data, activities, clickables, mongo)

            counter += 1
            if counter >= 60:
                return 1

        except KeyboardInterrupt:
            logger.info('@@@@@@@@@@@@@@@=============================')
            logger.info('KeyboardInterrupt...')
            Utility.store_data(learning_data, activities, clickables, mongo)
            return -1
        except KeyError:
            Utility.dump_log(d, pack_name, Utility.get_state(d, pack_name))
            logger.info('@@@@@@@@@@@@@@@=============================')
            logger.info('Crash')
            Utility.store_data(learning_data, activities, clickables, mongo)
            return -3
        except IndexError:
            logger.info('@@@@@@@@@@@@@@@=============================')
            logger.info('IndexError...')
            Utility.store_data(learning_data, activities, clickables, mongo)
            return -1
            # except Exception:
            #     logger.info('@@@@@@@@@@@@@@@=============================')
            #     logger.info("No idea what exception...")
            #     Utility.store_data(learning_data, activities, clickables, mongo)
            #     return -1


def official():
    dir = Config.apkdir
    android_home = Config.android_home
    x = subprocess.check_output(['ls', dir])
    with open(apklist, 'r') as f:
        apks_to_test = [line.rstrip() for line in f]
    timestr = time.strftime("%Y%m%d%H%M%S")

    info_location = Config.info_location
    if not os.path.exists(info_location):
        os.makedirs(info_location)
    file = codecs.open(info_location + '/information-' + timestr + '.txt', 'w', 'utf-8')

    for i in apks_to_test:
        english = True
        attempts = 0
        m = re.findall('^(.*)_.*\.apk', i)
        apk_packname = m[0]

        ''' Get the application name from badge. '''
        ps = subprocess.Popen([android_home + 'build-tools/26.0.1/aapt', 'dump', 'badging', dir + i],
                              stdout=subprocess.PIPE)
        output = subprocess.check_output(('grep', 'application-label:'), stdin=ps.stdout)
        label = output.decode('utf-8')
        m = re.findall('^application-label:(.*)$', label)
        appname = m[0][1:-1]

        Config.app_name = appname

        ''' Check if there is non-ASCII character. '''
        for scii in m[0]:
            if scii not in string.printable:
                logger.info('There is a non-ASCII character in application name. Stop immediately.\n')
                file.write('|' + apk_packname + '|' + 'Non-ASCII character detected in appname.' '\n')
                english = False
                break

        if english:
            ''' Start installation of the APK '''
            x = subprocess.Popen([android_home + 'platform-tools/adb', '-s', device_name, 'install', dir + i],
                                 stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            installmsg = x.communicate()[1].decode('utf-8')
            if len(re.findall('Success', installmsg)) > 0:
                logger.info("Installed success: " + apk_packname + ' APK.')
                pass
            if len(re.findall('INSTALL_FAILED_ALREADY_EXISTS', installmsg)) > 0:
                logger.info("Already exist: " + apk_packname + ' APK.')
                pass
            elif len(re.findall('INSTALL_FAILED_NO_MATCHING_ABIS', installmsg)) > 0:
                logger.info('No Matching ABIs: ' + apk_packname + ' APK.')
                file.write('|' + apk_packname + '|' + 'Failed to install; no matching ABIs' '\n')
                continue
            else:
                pass

            logger.info('\nDoing a UI testing on application ' + appname + '.')

            init()
            while attempts <= 3:
                signal.alarm(400)
                try:
                    retvalue = main(appname, apk_packname)
                    if retvalue == -2:
                        logger.info("Fail to start application using monkey.")
                        file.write('|' + apk_packname + '|' + 'Failed to start application using monkey.' '\n')
                        break
                    elif retvalue == -3:
                        logger.info("Fail to start application using monkey.")
                        file.write('|' + apk_packname + '|' + 'Crashed - KeyError' '\n')
                    attempts += 1
                except Exception:
                    logger.info("Timeout. Stop application.")
                finally:
                    signal.alarm(0)

            logger.info('Force stopping ' + apk_packname + ' to end test for the APK')
            subprocess.Popen(
                [android_home + 'platform-tools/adb', '-s', device_name, 'shell', 'am', 'force-stop', apk_packname])

            act_c = mongo.activity.count({"_type": "activity", "parent_app": Config.app_name})
            click_c = mongo.clickable.count({"_type": "clickable", "parent_app_name": Config.app_name})
            file.write(appname + '|' + apk_packname + '|True|' + str(act_c) + '|' + str(click_c) + '\n')
            subprocess.Popen([android_home + 'platform-tools/adb', '-s', device_name, 'uninstall', apk_packname],
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            logger.info('Uninstalled ' + apk_packname)
            logger.info('@@@@@@@@@@@ End ' + apk_packname + ' APK @@@@@@@@@@@')


try:
    """
    device_name e.g. emulator-5554
    apklist e.g. directory-to-apk-x
    e.g. python3 Main.py emulator-5554 
    """
    device_name = sys.argv[1]
    apklist = sys.argv[2]
    d = Device(device_name)
    official()

except Exception as e:
    logging.exception("message")
