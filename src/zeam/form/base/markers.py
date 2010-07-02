# -*- coding: utf-8 -*-

from zeam.form.base.interfaces import IModeMarker
from zope.interface import implements


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


class ModeMarker(Marker):
    """A Marker defining a form mode. It has a specific attribute,
    extractable, that defines if the mode allows the data extraction
    """
    implements(IModeMarker)

    def __init__(self, name, extractable=True):
        Marker.__init__(self, name)
        self.extractable = extractable


# Data extraction markers
NO_VALUE = Marker('NO_VALUE')
NO_CHANGE = Marker('NO_CHANGE')
NOT_EXTRACTED = Marker('NOT_EXTRACTED')
SUCCESS = Marker('SUCCESS')
FAILURE = Marker('FAILURE')
NOTHING_DONE = Marker('NOTHING_DONE')

# Mode markers
DISPLAY = ModeMarker('DISPLAY', extractable=False)
DEFAULT = ModeMarker('DEFAULT')
INPUT = ModeMarker('INPUT')
HIDDEN = ModeMarker('HIDDEN')


def getValue(object, attr, default_object):
    """Retrieve the attr value from object. If it's DEFAULT, try to
    look up it on the default_object.
    """
    value = getattr(object, attr, DEFAULT)
    if value is DEFAULT:
        value = getattr(default_object, attr)
    return value
