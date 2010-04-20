

class Marker(object):
    """Marker object, designed to be used as singleton (like None,
    True, False).
    """

    def __init__(self, name):
        self.name = name

    def __str__(self):
        return self.name.lower()

    def __repr__(self):
        return '<Marker %s>' % (self.name.upper())


NO_VALUE = Marker('NO_VALUE')
NOT_EXTRACTED = Marker('NOT_EXTRACTED')
DEFAULT = Marker('DEFAULT')
DISPLAY = Marker('DISPLAY')
INPUT = Marker('INPUT')
HIDDEN = Marker('HIDDEN')
SUCCESS = Marker('SUCCESS')
FAILURE = Marker('FAILURE')
NOTHING_DONE = Marker('NOTHING_DONE')


def getValue(object, attr, default_object):
    """Retrieve the attr value from object. If it's DEFAULT, try to
    look up it on the default_object.
    """
    value = getattr(object, attr, DEFAULT)
    if value is DEFAULT:
        value = getattr(default_object, attr)
    return value
