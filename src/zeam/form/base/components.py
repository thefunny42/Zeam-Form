
import re

from zeam.form.base import interfaces
from zope.interface import implements
from zope import component

_valid_identifier = re.compile('[A-Za-z][A-Za-z0-9_-]*$')

def createId(name):
    # Create a valid id from any string.
    id = unicode(name.strip()).encode('utf-8')
    id = id.replace(' ', '-')
    if _valid_identifier.match(id):
        return id.lower()
    return id.encode('hex')


class Component(object):
    implements(interfaces.IComponent)

    def __init__(self, title, identifier=None):
        if identifier is None:
            identifier = createId(title)
        self.identifier = identifier
        if not title:
            # If the title is empty, use the identifier as title
            title = identifier
        self.title = title

    def clone(self, new_identifier=None):
        return self.__class__(self.title, new_identifier)

    def __repr__(self):
        return "<%s %s>" % (self.__class__.__name__, self.title)


_marker = object()


class Collection(object):
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
        self.extend(*components)

    def get(self, id, default=_marker):
        try:
            return self.__components[self.__ids.index(id)]
        except ValueError:
            if default is _marker:
                raise KeyError(id)
            return default

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

    def __iter__(self):
        return self.__components.__iter__()

    def __len__(self):
        return self.__components.__len__()

    def __repr__(self):
        return "<%s>" % (self.__class__.__name__)
