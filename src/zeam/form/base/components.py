# -*- coding: utf-8 -*-

import re

from pkg_resources import iter_entry_points
from zope import component
from zope.interface import implements
from zope.testing import cleanup

from zeam.form.base import interfaces


_valid_identifier = re.compile('[A-Za-z][A-Za-z0-9_-]*$')


def createId(name):
    # Create a valid id from any string.
    identifier = unicode(name).strip().encode('utf-8').replace(' ', '-')
    if _valid_identifier.match(identifier):
        return identifier.lower()
    return identifier.encode('hex')


class Component(object):
    implements(interfaces.IComponent)

    identifier = None
    title = None

    def __init__(self, title=None, identifier=None):
        if not self.title:
            if not title:
                # If the title is empty, use the identifier as title
                title = identifier
                if title is None:
                    raise ValueError(
                        u"Need at least a title to build a component.")
            self.title = title
        if identifier is None:
            identifier = createId(self.title)
        self.identifier = str(identifier)

    def clone(self, new_identifier=None):
        return self.__class__(self.title, new_identifier)

    def __repr__(self):
        return "<%s %s>" % (self.__class__.__name__, self.title)


_marker = object()
_loaded = False


def loadComponents():
    """Goes through all available components loaders and call them.
    """
    global _loaded
    if _loaded:
        return
    for loader_entry in iter_entry_points('zeam.form.components'):
        loader = loader_entry.load()
        if not callable(loader):
            raise TypeError(
                'Entry point %r should be a callable to register  components'
                % loader_entry.name)
        loader()
    _loaded = True


def reloadComponents():
    """Reload all zeam components.

    This is mainly used by testing layers.
    """
    global _loaded
    _loaded = False
    loadComponents()


cleanup.addCleanUp(reloadComponents)


class Collection(object):
    """Represent a collection of components.
    """
    implements(interfaces.ICollection)

    type = interfaces.IComponent
    factory = None

    def __init__(self, *components, **options):
        self.__options = {}
        for name, value in options.items():
            if name not in interfaces.ICollection:
                self.__options[name] = value
        self.__dict__.update(self.__options)
        self.__ids = []
        self.__components = []
        if len(components):
            self.extend(*components)

    def reverse(self):
        self.__components = [c for c in reversed(self.__components)]
        self.__ids = [c.identifier for c in self.__components]

    def sort(self, cmp=cmp, key=lambda c: c.identifier, reverse=False):
        self.__components.sort(cmp=cmp, key=key, reverse=reverse)
        self.__ids = [c.identifier for c in self.__components]

    def clear(self):
        self.__ids = []
        self.__components = []

    def get(self, id, default=_marker):
        try:
            return self.__components[self.__ids.index(id)]
        except ValueError:
            if default is _marker:
                raise KeyError(id)
            return default

    def set(self, id, value):
        if not interfaces.IMutableCollection.providedBy(self):
            raise NotImplementedError
        if not self.type.providedBy(value):
            raise TypeError(value)
        try:
            self.__components[self.__ids.index(id)] = value
        except ValueError:
            raise KeyError(id)

    def append(self, component):
        if self.type.providedBy(component):
            if component.identifier not in self.__ids:
                self.__ids.append(component.identifier)
                self.__components.append(component)
            else:
                raise ValueError(
                    u"Duplicate identifier", component.identifier)
        else:
            raise TypeError(u"Invalid type", component)

    def extend(self, *components):
        for cmp in components:
            if self.type.providedBy(cmp):
                self.append(cmp)
            elif interfaces.ICollection.providedBy(cmp):
                for item in cmp:
                    self.append(item)
            else:
                if self.factory is not None:
                    loadComponents()
                    factory = component.queryAdapter(cmp, self.factory)
                    if factory is not None:
                        for item in factory.produce():
                            self.append(item)
                        continue
                raise TypeError(u'Invalid type', cmp)

    def select(self, *ids):
        components = (c for c in self.__components if c.identifier in ids)
        return self.__class__(*components, **self.__options)

    def omit(self, *ids):
        components = (c for c in self.__components if c.identifier not in ids)
        return self.__class__(*components, **self.__options)

    def copy(self):
        return self.__class__(*self.__components, **self.__options)

    def keys(self):
        return list(self.__ids)

    def __add__(self, other):
        if interfaces.ICollection.providedBy(other):
            copy = self.copy()
            for component in other:
                copy.append(component)
            return copy
        if interfaces.IComponent.providedBy(other):
            copy = self.copy()
            copy.append(other)
            return copy
        raise NotImplementedError

    def __getitem__(self, id):
        return self.get(id)

    def __setitem__(self, id, value):
        self.set(id, value)

    def __delitem__(self, id):
        if not interfaces.IMutableCollection.providedBy(self):
            raise NotImplementedError
        try:
            index = self.__ids.index(id)
            self.__ids.remove(id)
            del self.__components[index]
        except ValueError:
            raise KeyError(id)

    def __contains__(self, id):
        return id in self.__ids

    def __iter__(self):
        return self.__components.__iter__()

    def __len__(self):
        return self.__components.__len__()

    def __repr__(self):
        return "<%s>" % (self.__class__.__name__)
