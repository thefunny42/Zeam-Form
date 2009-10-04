
from zeam.form.base import interfaces
from zeam.form.base.components import Component, Collection
from zeam.form.base.markers import NO_VALUE

from zope.interface import implements


class Field(Component):
    implements(interfaces.IField)

    description = u''

    def getContentValue(self, context):
        return getattr(context, self.identifier, NO_VALUE)

    def getDefaultValue(self):
        raise NO_VALUE

    def validate(self, value):
        return None


class Fields(Collection):
    implements(interfaces.IFields)

    type = interfaces.IField
    factory = interfaces.IFieldFactory

