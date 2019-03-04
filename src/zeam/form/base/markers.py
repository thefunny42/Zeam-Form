# -*- coding: utf-8 -*-

from zeam.form.base.interfaces import IModeMarker
from zope.interface import implements, implementer


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


implementer(IModeMarker)
class ModeMarker(Marker):
    """A Marker defining a form mode. It has a specific attribute,
    extractable, that defines if the mode allows the data extraction
    """

    def __init__(self, name, extractable=True):
        Marker.__init__(self, name)
        self.extractable = extractable


class HiddenMarker(ModeMarker):
    """A marker that hides a field.
    """
    pass


# Data extraction markers
SUCCESS = Marker('SUCCESS')
FAILURE = Marker('FAILURE')
DEFAULT = Marker('DEFAULT')
NO_VALUE = Marker('NO_VALUE')
NO_CHANGE = Marker('NO_CHANGE')
NOTHING_DONE = Marker('NOTHING_DONE')

# Mode markers
DISPLAY = ModeMarker('DISPLAY', extractable=False)
INPUT = ModeMarker('INPUT')
HIDDEN = HiddenMarker('HIDDEN')


def getValue(object, attr, default_object):
    """Retrieve the attr value from object. If it's DEFAULT, try to
    look up it on the default_object.
    """
    value = getattr(object, attr, DEFAULT)
    if value is DEFAULT:
        value = getattr(default_object, attr)
    return value
