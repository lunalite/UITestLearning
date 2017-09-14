import logging
import os
import random

from Config import Config
from Data import Data
from Mongo import Mongo
from uiautomator import Device

d = Device(Config.device_name)

pack_name = Config.pack_name
app_name = Config.app_name

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

mongo = Mongo()


def main():
    # Variable setting

    learning_data = []
    activities = {}
    clickables = {}
    scores = []

    '''============='''

    logger.info('Starting UI testing')
    d.screen.on()
    d.press('home')
    logger.info('Force stopping ' + pack_name + ' to reset states')
    os.system('adb shell am force-stop ' + pack_name)
    d(resourceId='com.google.android.apps.nexuslauncher:id/all_apps_handle').click()
    if d(text=app_name).exists:
        d(text=app_name).click.wait()

    learning_data = Data(_appname=app_name, _packname=pack_name, _data_activity=[])

    while True:
        cc