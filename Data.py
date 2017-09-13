import json
import logging

import Utility
from Clickable import Clickable
from Config import Config
from DataActivity import DataActivity

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Data(object):
    def __init__(self, appname, packname, _data_activity=None):
        self.appname = appname
        self.packname = packname
        self.app_description = None
        self.category = None
        self.data_activity = [] if _data_activity is None else _data_activity

        # self.store_content = {}
        # self.vocabulary = []

    def __str__(self):
        return json.dumps(self, default=lambda o: o.__dict__)

    def add_new_activity(self, device, current_state=None, _click_els=None):
        if current_state is None:
            current_state = Utility.get_state(device)
        # Check if state in data_activity if not, add
        da = DataActivity(current_state)
        # click_els = device(clickable='true', packageName=Config.pack_name) if _click_els is None else _click_els
        click_els = device(clickable='true') if _click_els is None else _click_els
        parent_map = Utility.create_child_to_parent(dump=device.dump())
        for btn in click_els:
            key = Utility.btn_to_key(btn)
            da.clickables.append(
                Clickable(name=key, _parent_activity_state=current_state, _parent_name=Utility.xml_btn_to_key(
                    Utility.get_parent(btn, _parent_map=parent_map))))
            da.clickables_score.append(1)
        self.data_activity.append(da)
        logger.info('Added new activity to data.')

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__)

    def get_activity_by_state(self, state):
        logger.info('Getting activity by state: ' + state)
        for activity in self.data_activity:
            if activity.activity_state == state:
                return activity
        return None
