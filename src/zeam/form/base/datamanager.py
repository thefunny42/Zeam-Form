
from zeam.form.base.markers import NO_VALUE


class ObjectDataManager(object):
    """An object data manager, which look up data as attributes on
    objects.
    """

    def __init__(self, content):
        self.content = content

    def get(self, identifier):
        try:
            return getattr(self.content, identifier)
        except AttributeError:
            raise ValueError, identifier

    def set(self, identifier, value):
        setattr(self.content, identifier, value)

    def retrieve(self):
        return self.content


class DictDataManager(object):
    """A dictionary data manager, which look up data as keys in the
    dictionary.
    """

    def __init__(self, content):
        assert isinstance(content, dict)
        self.content = content

    def get(self, identifier):
        try:
            return self.content[identifier]
        except KeyError:
            raise ValueError, identifier

    def set(self, identifier, value):
        self.content[identifier] = value

    def retrieve(self):
        return self.content


class NoneDataManager(object):
    """A null data manager, which return directly the given object as
    data.
    """

    def __init__(self, content):
        self.content = content

    def get(self, identifier):
        return self.content

    def set(self, identifier, value):
        self.content = value

    def retrieve(self):
        return self.content
