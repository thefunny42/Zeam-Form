
from zeam.form.base import interfaces
from zeam.form.base.components import Component, Collection
from zeam.form.base.markers import NO_VALUE, DEFAULT

from zope.interface import implements
from zope.i18nmessageid import MessageFactory

_ = MessageFactory('zeam.form.base')


class Field(Component):
    implements(interfaces.IField)

    description = u''
    required = False
    prefix = 'field'
    readonly = False

    ignoreContent = DEFAULT
    ignoreRequest = DEFAULT
    mode = DEFAULT
    defaultValue = NO_VALUE

    def available(self, form):
        return True

    def getDefaultValue(self, form):
        if callable(self.defaultValue):
            return self.defaultValue(form)
        return self.defaultValue

    def isEmpty(self, value):
        return value is NO_VALUE

    def validate(self, value, context=None):
        if self.required and self.isEmpty(value):
            return _(u"Missing required value.")
        return None


class Fields(Collection):
    implements(interfaces.IFields)

    type = interfaces.IField
    factory = interfaces.IFieldFactory
