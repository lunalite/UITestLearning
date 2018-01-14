from pymongo import MongoClient

from Config import Config


class Mongo():
    def __init__(self):
        client = MongoClient(Config.mongoHost, Config.mongoPort)
        db = client['dataset8']
        self.app = db.app
        self.activity = db.activity
        self.clickable = db.clickable
