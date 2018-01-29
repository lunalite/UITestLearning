import sys
from pymongo import MongoClient
from crawler.Config import Config
sys.path.append('/Users/hkoh006/Desktop/UITestLearning')

class Mongo():
    def __init__(self):
        client = MongoClient(Config.mongoHost, Config.mongoPort)
        db = client['dataset11']
        self.app = db.app
        self.activity = db.activity
        self.clickable = db.clickable
