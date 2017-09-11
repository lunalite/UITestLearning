class Clickables(object):
    def __init__(self, name, score=1, next_transition_state=None, _parent_name=None):
        self.name = name
        self.score = score
        self.next_transition_state = next_transition_state
        self.parent_name = _parent_name

    def __str__(self):
        return '\n' + 'name: ' + self.name + '; score: ' + str(self.score)
