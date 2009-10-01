

class Marker(object):

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return '<Marker %s>' % (self.name)

NO_VALUE = Marker('NO_VALUE')

