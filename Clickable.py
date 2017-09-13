class Clickable(object):
    def __init__(self, name, _parent_activity_state, score=1, next_transition_state=None, _parent_name=None):
        self.name = name
        self.score = score
        self.next_transition_state = next_transition_state
        self.parent_name = _parent_name
        self.parent_activity_state = _parent_activity_state

    def __str__(self):
        return '\n' + 'name: ' + self.name + '; score: ' + str(self.score)
