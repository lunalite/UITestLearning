class Graph:
    def __init__(self, parent, btn, state):
        self.parent = parent
        self.btn = btn
        self.state = state

    def __str__(self):
        print "Graph is vertex X with edge to parent Y"

    def get_state(self):
        return self.state
