
from zeam.form.base.interfaces import IDataManager
from zope.interface import implements


class BaseDataManager(object):
    """Base class for a data manager.
    """
    implements(IDataManager)

    def __init__(self, content):
        self.content = content

    def get(self, identifier):
        raise NotImplementedError

    def set(self, identifier, value):
        raise NotImplementedError

    def __repr__(self):
        return '<%s used for %r>' % (self.__class__.__name__, self.content)


class ObjectDataManager(BaseDataManager):
    """An object data manager, which look up data as attributes on
    objects.
    """

    def get(self, identifier):
        try:
            return getattr(self.content, identifier)
        except AttributeError:
            raise KeyError(identifier)

    def set(self, identifier, value):
        setattr(self.content, identifier, value)


class DictDataManager(BaseDataManager):
    """A dictionary data manager, which look up data as keys in the
    dictionary.
    """

    def get(self, identifier):
        return self.content[identifier]

    def set(self, identifier, value):
        self.content[identifier] = value


class NoneDataManager(BaseDataManager):
    """A null data manager, which return directly the given object as
    data.
    """

    def get(self, identifier):
        return self.content


def makeAdaptiveDataManager(interface):

    class AdaptiveDataManager(ObjectDataManager):
        """A data manager that adapt its content to an interface
        before doing anything.
        """

        def __init__(self, content):
            self.content = interface(content)

    return AdaptiveDataManager

