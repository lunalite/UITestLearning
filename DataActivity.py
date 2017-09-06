import logging

from Clickables import Clickables

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataActivity(object):
    def __init__(self, state, clickables=[]):
        # state is the key
        self.activity_state = state
        self.clickables = clickables

    def __str__(self):
        return 'activity_state: ' + self.state + '; clickables: ' + ''.join(str(c) for c in self.clickables)

    def get_clickable_by_name(self, name):
        for c in self.clickables:
            if c.name == name:
                return c

        # TODO: Issue about change in text but not instate, causing error sine no clickable could be found
        logger.info('No clickable found. Creating clickable...')
        c = Clickables(name)
        self.clickables.append(c)
        return c

