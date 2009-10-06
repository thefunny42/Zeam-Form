
from zeam.form.base.components import Component, Collection
from zeam.form.base import interfaces

from zope.interface import implements

class Error(Component):
    implements(interfaces.IError)


class Errors(Collection):
    implements(interfaces.IErrors)

    type = interfaces.IError

