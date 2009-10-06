
import re

from zeam.form.base import interfaces
from zope.interface import implements
from zope import component

_valid_identifier = re.compile('[A-Za-z][A-Za-z0-9_-]*$')

def createId(name):
    # Create a valid id from any string.
    id = str(name.encode('utf-8'))
    id = id.replace(' ', '-')
    if _valid_identifier.match(id):
        return id.lower()
    return id.encode('hex')


class Component(object):
    implements(interfaces.IComponent)

    def __init__(self, title, identifier=None):
        self.title = title
        if identifier is None:
            identifier = createId(title)
        self.identifier = identifier

    def __repr__(self):
        return "<%s %s>" % (self.__class__.__name__, self.title)

_get_marker = object()

class Collection(object):
    implements(interfaces.ICollection)

    type = interfaces.IComponent
    factory = None

    def __init__(self, *components, **options):
        for name, value in options.items():
            if name not in interfaces.ICollection:
                self.__dict__[name] = value
        self._ids = []
        self._components = []
        self.extend(*components)

    def get(self, id, default=_get_marker):
        try:
            return self._components[self._ids.index(id)]
        except ValueError:
            if default is _get_marker:
                raise KeyError, id
            return default

    def append(self, component):
        if self.type.providedBy(component):
            if component.identifier not in self._ids:
                self._ids.append(component.identifier)
                self._components.append(component)
            else:
                raise ValueError(
                    "Duplicate identifier", component.identifier)
        else:
            raise TypeError("Invalid type", component)

    def extend(self, *components):
        for cmp in components:
            if interfaces.IComponent.providedBy(cmp):
                self.append(cmp)
            elif interfaces.ICollection.providedBy(cmp):
                for item in cmp:
                    self.append(item)
            else:
                if self.factory is not None:
                    factory = component.queryAdapter(cmp, self.factory)
                    if factory is not None:
                        for item in factory.produce():
                            self.append(item)
                        continue
                raise TypeError("Invalid type", cmp)

    def select(self, *ids):
        copy = self.__class__()
        for component in self._components:
            if component.identifier in ids:
                copy.append(component)
        return copy

    def omit(self, *ids):
        copy = self.__class__()
        for component in self._components:
            if component.identifier not in ids:
                copy.append(component)
        return copy

    def copy(self):
        copy = self.__class__()
        for component in self._components:
            copy.append(component)
        return copy

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

    def __iter__(self):
        return self._components.__iter__()

    def __len__(self):
        return self._components.__len__()

    def __repr__(self):
        return "<%s>" % (self.__class__.__name__)
