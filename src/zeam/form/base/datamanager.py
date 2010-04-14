
from zeam.form.base.interfaces import IDataManager
from zeam.form.base.markers import NO_VALUE
from zope.interface import implements


class ObjectDataManager(object):
    """An object data manager, which look up data as attributes on
    objects.
    """
    implements(IDataManager)

    def __init__(self, content):
        self.content = content

    def get(self, identifier):
        try:
            return getattr(self.content, identifier)
        except AttributeError:
            raise KeyError(identifier)

    def set(self, identifier, value):
        setattr(self.content, identifier, value)


class DictDataManager(object):
    """A dictionary data manager, which look up data as keys in the
    dictionary.
    """
    implements(IDataManager)

    def __init__(self, content):
        assert isinstance(content, dict)
        self.content = content

    def get(self, identifier):
        return self.content[identifier]

    def set(self, identifier, value):
        self.content[identifier] = value


class NoneDataManager(object):
    """A null data manager, which return directly the given object as
    data.
    """
    implements(IDataManager)

    def __init__(self, content):
        self.content = content

    def get(self, identifier):
        return self.content

    def set(self, identifier, value):
        # You cannot set values with that data manager
        raise NotImplementedError
