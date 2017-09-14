class State():
    def __init__(self, tag_name, state_rep):
        self.tag_name = tag_name
        self.state_rep = state_rep
        self.next_state = None

    def add_next(self, next_state):
        self.next_state = next_state
        



