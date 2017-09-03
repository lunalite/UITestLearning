import Utility
import json

from Clickables import Clickables
from Config import Config
from DataActivity import DataActivity


class Data(object):
    """
    @name: name of the application that is being accessed.
    @description: the description of the application being accessed.
    @dictionary: Currently only using a basic form of supervised learning and labeling, and dictionary is used for
    storing word and score ratio.
    @vocabulary: The list of all possible words that are being used in the APK file for RL/NLP later on.
    """

    def __init__(self, appname, packname, data_activity=[]):
        self.appname = appname
        self.packname = packname
        self.app_description = None
        self.category = None
        self.data_activity = data_activity

        # self.store_content = {}
        # self.vocabulary = []

    def __str__(self):
        return 'Data appname: ' + self.appname + '; packname: ' + self.packname + '; with data activities: ' + str(
            self.data_activity)

    def add_new_activity(self, device):
        current_state = Utility.get_state(device)
        # Check if state in data_activity if not, add
        da = DataActivity(current_state)
        click_els = device(clickable='true', packageName=Config.pack_name)
        for btn in click_els:
            key = Utility.btn_to_key(btn)
            da.clickables.append(Clickables(key))
        self.data_activity.append(da)

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__)

    def get_activity_by_state(self, state):
        for activity in self.data_activity:
            if activity.state == state:
                return activity
        return None

        # def initialize_dictionary(self, clickable_btns):
        #     """
        #     Initialize dictionary with score 0s
        #     Format of key is as follow:
        #     {widget_truncated_className}-{text}-{contentDescription}-{[L,T][R,B]}
        #     Where [L,T] represent left and top bound coords and [R,B] represent right and bottom coords
        #     :param clickable_btns: present buttons on UI with clickable set as True
        #     :return:
        #     """
        #     for btn in clickable_btns:
        #         info = btn.info
        #         key = '{' + info['className'].split('.')[-1] + '}-{' + info['text'] + '}-{' + info[
        #             'contentDescription'] + '}-{' + Utility.convert_bounds(btn) + '}'
        #         if key not in self.dictionary:
        #             self.dictionary[key] = 0
