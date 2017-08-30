class Data():
    """
    @name: name of the application that is being accessed.
    @description: the description of the application being accessed.
    @dictionary: Currently only using a basic form of supervised learning and labeling, and dictionary is used for
    storing word and score ratio.
    @vocabulary: The list of all possible words that are being used in the APK file for RL/NLP later on.
    """

    def __init__(self, name):
        self.name = name
        self.description = None
        self.dictionary = {}

        self.vocabulary = []

    def __str__(self):
        return 'This Data object is ' + self.name
