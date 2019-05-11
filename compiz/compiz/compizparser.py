class Parser(object):

    def __init__(self, db):
        self.db = db

    def parse_db(self):
        raise NotImplementedError
