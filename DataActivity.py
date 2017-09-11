import logging

from Clickables import Clickables

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataActivity(object):
    def __init__(self, state, _clickables=None, _clickables_score=None, _clickables_length=0):
        # state is the key
        self.activity_state = state
        self.clickables = [] if _clickables is None else _clickables
        self.clickables_score = [] if _clickables_score is None else _clickables_score
        self.clickables_length = _clickables_length

    def __str__(self):
        return 'activity_state: ' + self.activity_state + '; clickables: ' + ''.join(str(c) for c in self.clickables)

    def get_clickable_by_name(self, name):
        # TODO: Use libraries use dictionary

        for c in self.clickables:
            if c.name == name:
                return c

        # TODO: Issue about change in text but not instate, causing error sine no clickable could be found
        logger.info('No clickable found. Creating clickable...')
        c = Clickables(name)
        self.clickables.append(c)
        return c
