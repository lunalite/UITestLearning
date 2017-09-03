class Clickables(object):
    def __init__(self, name, score=0, next_transition_state=None):
        self.name = name
        self.score = score
        self.next_transition_state = next_transition_state

    def __str__(self):
        return '\n' + str(self.id) + '; name: ' + self.name + '; score: ' + str(self.score)
