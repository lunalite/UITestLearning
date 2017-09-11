class Clickables(object):
    def __init__(self, name, score=1, next_transition_state=None):
        self.name = name
        self.score = score
        self.next_transition_state = next_transition_state

    def __str__(self):
        return '\n' + 'name: ' + self.name + '; score: ' + str(self.score)
