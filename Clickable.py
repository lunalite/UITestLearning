import json


class Clickable(object):
    def __init__(self, name, _parent_activity_state, _parent_app_name, score=1, next_transition_state=None,
                 _parent=None,
                 _siblings=None, _children=None):
        self.name = name
        self.score = score
        self.next_transition_state = next_transition_state
        self.parent = _parent
        self.parent_activity_state = _parent_activity_state
        self.parent_app_name = _parent_app_name
        self.siblings = _siblings
        self.children = _children

    def __str__(self):
        return json.dumps(self.__dict__)

    @staticmethod
    def encode_data(clickable):
        return {"_type": "clickable", "name": clickable.name,
                "score": clickable.score,
                "next_transition_state": clickable.next_transition_state,
                "parent": clickable.parent,
                "parent_activity_state": clickable.parent_activity_state,
                "parent_app_name": clickable.parent_app_name,
                "siblings": clickable.siblings,
                "children": clickable.children}

    @staticmethod
    def decode_data(document):
        assert document['_type'] == 'clickable'
        return Clickable(name=document['name'],
                         _parent_activity_state=document['parent_activity_state'],
                         _parent_app_name=document['parent_app_name'],
                         score=document['score'],
                         next_transition_state=document['next_transition_state'],
                         _parent=document['parent'],
                         _siblings=document['siblings'],
                         _children=document['children'])
