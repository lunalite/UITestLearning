class DataActivity(object):
    def __init__(self, state, clickables=[]):
        # state is the key
        self.state = state
        self.clickables = clickables

    def __str__(self):
        return 'state: ' + self.state + '; clickables: ' + ''.join(str(c) for c in self.clickables)

    def get_clickable_by_name(self, name):
        for c in self.clickables:
            if c.name == name:
                return c
        return None
