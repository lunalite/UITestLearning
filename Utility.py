"""======================================================

Utility file that holds every single miscellaneous tasks

======================================================"""

import json
import os

from Config import Config

data_store_location = Config.data_store_location


def store_data(data_dictionary, name):
    """
    Storing data into dictionary
    :param data_dictionary:
    :param name: contains the filename of the file to be saved to.
    """
    with open(data_store_location + name + '.txt', 'w+') as f:
        json.dump(data_dictionary, f)


def load_data(name):
    """
    Loading data from file to dictionary
    :param name: filename of the file to be read from.
    :return: a dictionary file
    """
    if os.path.isfile(data_store_location + Config.app_name + '.txt'):
        with open(data_store_location + name + '.txt') as f:
            return json.load(f)
