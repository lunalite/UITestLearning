import json


class Data(object):
    def __init__(self, _appname, _packname, _app_description=None, _category=None, _data_activity=None):
        self.appname = _appname
        self.packname = _packname
        self.app_description = _app_description
        self.category = _category
        self.data_activity = [] if _data_activity is None else _data_activity

    def __str__(self):
        return json.dumps(self.__dict__)

    @staticmethod
    def encode_data(data):
        return {"_type": "data", "appname": data.appname,
                "packname": data.packname,
                "app_description": data.app_description,
                "category": data.category,
                "data-activity": data.data_activity}

    @staticmethod
    def decode_data(document):
        assert document['_type'] == 'data'
        return Data(_appname=document['appname'],
                    _packname=document['packname'],
                    _app_description=document['app_description'],
                    _category=document['category'],
                    _data_activity=document['data_activity'])
