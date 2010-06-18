# -*- coding: utf-8 -*-

from zeam.form.base import interfaces
from zeam.form.base.components import Component, Collection
from zope.interface import implements, directlyProvides


class Error(Component):
    implements(interfaces.IError)


class Errors(Collection):
    implements(interfaces.IErrors)

    type = interfaces.IError
    title = u""

    def __init__(self, *components, **options):
        Collection.__init__(self, *components, **options)
        if 'identifier' in options:
            directlyProvides(self, interfaces.IError)

    def clone(self, new_identifier=None):
        raise NotImplementedError(u'Errors collections are not clonable.')
