import logging

from Clickable import Clickable


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataActivity(object):

    def __init__(self, state, _parent_app, _clickable=None):
        # state is the key
        self.state = state
        self.clickable = [] if _clickable is None else _clickable
        self.parent_app = _parent_app

    @staticmethod
    def encode_data(activity):
        return {"_type": "activity", "state": activity.state, "parent_app": activity.parent_app,
                "clickable": activity.clickable}

    @staticmethod
    def decode_data(document):
        assert document['_type'] == 'data'
        return DataActivity(document['state'], document['parent_app'], document['clickable'])

        # def get_clickable_by_name(self, name):
        #     # TODO: Use libraries use dictionary
        #
        #     for c in self.clickables:
        #         if c.name == name:
        #             return c
        #
        #     # TODO: Issue about change in text but not instate, causing error sine no clickable could be found
        #     logger.info('No clickable found. Creating clickable...')
        #     c = Clickables(name)
        #     self.clickables.append(c)
        #     return c
