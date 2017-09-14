class Clickable(object):
    def __init__(self, name, _parent_activity_state, score=1, next_transition_state=None, _parent=None,
                 _siblings=None):
        self.name = name
        self.score = score
        self.next_transition_state = next_transition_state
        self.parent = _parent
        self.parent_activity_state = _parent_activity_state
        self.siblings = _siblings

    @staticmethod
    def encode_data(clickable):
        return {"_type": "clickable", "name": clickable.name, "score": clickable.score,
                "next_transition_state": clickable.next_transition_state, "parent_name": clickable.parent_name,
                "parent_activity_state": clickable.parent_activity_state, "siblings": clickable.siblings}

    @staticmethod
    def decode_data(document):
        assert document['_type'] == 'clickable'
        return Clickable(name=document['name'], _parent_activity_state=document['parent_activity_state'],
                         score=document['score'], next_transition_state=document['next_transition_state'],
                         _parent=document['parent'], _siblings=document['siblings'])
