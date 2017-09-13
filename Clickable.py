class Clickable(object):
    def __init__(self, name, _parent_activity, score=1, next_transition_state=None, _parent_name=None):
        self.name = name
        self.score = score
        self.next_transition_state = next_transition_state
        self.parent_name = _parent_name
        self.parent_activity = _parent_activity

    def __str__(self):
        return '\n' + 'name: ' + self.name + '; score: ' + str(self.score)

    @staticmethod
    def encode_data(clickable):
        return {"_type": "clickable", "name": clickable.name, "score": clickable.score,
                "next_transition_state": clickable.next_transition_state, "parent_name": clickable.parent_name,
                "parent_activity": clickable.parent_activity}

    @staticmethod
    def decode_data(document):
        assert document['_type'] == 'clickable'
        return Clickable(document['name'], _parent_activity=document['parent_activity'], score=document['score'],
                         next_transition_state=document['next_transition_state'],
                         _parent_name=document['parent_name'])
