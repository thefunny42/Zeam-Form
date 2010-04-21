
from zeam.form.base import interfaces
from zeam.form.base.components import Component, Collection
from zeam.form.base.markers import NO_VALUE, DEFAULT

from zope.interface import implements


class Field(Component):
    implements(interfaces.IField)

    description = u''
    required = False
    prefix = 'field'

    ignoreContent = DEFAULT
    ignoreRequest = DEFAULT
    mode = DEFAULT
    defaultValue = NO_VALUE

    def available(self, context):
        return True

    def getDefaultValue(self):
        if callable(self.defaultValue):
            return self.defaultValue()
        return self.defaultValue

    def validate(self, value, context=None):
        if self.required and value is NO_VALUE:
            return u"Missing required value"
        return None


class Fields(Collection):
    implements(interfaces.IFields)

    type = interfaces.IField
    factory = interfaces.IFieldFactory

