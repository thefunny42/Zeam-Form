

class Marker(object):
    """Marker object, designed to be used as singleton (like None,
    True, False).
    """

    def __init__(self, name, value=None):
        self.name = name
        self.value = value

    def __repr__(self):
        return '<Marker %s>' % (self.name)


NO_VALUE = Marker('NO_VALUE')
DEFAULT = Marker('DEFAULT')


def getValue(object, attr, default_object):
    """Retrieve the attr value from object. If it's DEFAULT, try to
    look up it on the default_object.
    """
    value = getattr(object, attr, DEFAULT)
    if value is DEFAULT:
        value = getattr(default_object, attr)
    return value
