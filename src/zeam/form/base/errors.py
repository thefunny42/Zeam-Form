# -*- coding: utf-8 -*-

from zeam.form.base import interfaces
from zeam.form.base.components import Component, Collection
from zope.interface import implements, directlyProvides
from zope.i18nmessageid import MessageFactory

_ = MessageFactory('zeam.form.base')


class Error(Component):
    implements(interfaces.IError)


class Errors(Collection):
    implements(interfaces.IErrors)

    type = interfaces.IError

    def __init__(self, *components, **options):
        Collection.__init__(self, *components, **options)
        if 'identifier' in options:
            directlyProvides(self, interfaces.IError)

    @property
    def title(self):
        if interfaces.IError.providedBy(self):
            default_error = self.get(self.identifier, None)
            if default_error is not None:
                return default_error.title
            return _(u"There were errors.")
        raise AttributeError('property')

    def append(self, component):
        if self.type.providedBy(component):
            if component.identifier in self:
                previous = self[component.identifier]
                if not interfaces.IErrors.providedBy(previous):
                    previous.identifier += '.0'
                    collection = self.__class__(
                        previous, identifier=component.identifier)
                    self[component.identifier] = collection
                else:
                    collection = previous
                component.identifier += '.%d' % len(collection)
                collection.append(component)
            else:
                super(Errors, self).append(component)
        else:
            raise TypeError(u"Invalid type", component)

    def clone(self, new_identifier=None):
        raise NotImplementedError(u'Errors collections are not clonable.')

    def __repr__(self):
        if interfaces.IError.providedBy(self):
            return "<%s for %r>" % (self.__class__.__name__, self.identifier)
        return Collection.__repr__(self)
