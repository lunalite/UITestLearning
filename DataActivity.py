import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataActivity(object):
    def __init__(self, _state, _name, _parent_app, _clickables=None):
        # state is the key
        self.state = _state
        self.name = _name
        self.parent_app = _parent_app
        self.clickables = [] if _clickables is None else _clickables

    def __str__(self):
        return json.dumps(self.__dict__)

    @staticmethod
    def encode_data(activity):
        return {"_type": "activity",
                "state": activity.state,
                "name": activity.name,
                "parent_app": activity.parent_app,
                "clickables": activity.clickables}

    @staticmethod
    def decode_data(document):
        assert document['_type'] == 'data'
        return DataActivity(_state=document['state'],
                            _name=document['name'],
                            _parent_app=document['parent_app'],
                            _clickables=document['clickables'])
