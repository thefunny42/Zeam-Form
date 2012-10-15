
from zeam.form.base import interfaces
from zeam.form.base.components import Component, Collection
from zeam.form.base.markers import NO_VALUE, DEFAULT, Marker

from zope.interface import implements
from zope.i18nmessageid import MessageFactory

_ = MessageFactory('zeam.form.base')


class Field(Component):
    implements(interfaces.IField)

    description = u''
    required = False
    prefix = 'field'
    readonly = False
    htmlAttributes = {}
    interface = None
    ignoreContent = DEFAULT
    ignoreRequest = DEFAULT
    mode = DEFAULT
    defaultValue = NO_VALUE

    def __init__(self,
                 title=None,
                 identifier=None,
                 description=u"",
                 required=False,
                 readonly=False,
                 defaultValue=NO_VALUE,
                 constrainValue=None,
                 interface=None,
                 **htmlAttributes):
        super(Field, self).__init__(title, identifier)
        self.description = description
        self.required = required
        self.readonly = readonly
        self.defaultValue = defaultValue
        self.interface = interface
        if constrainValue is not None:
            self.constrainValue = constrainValue
        self.htmlAttributes = htmlAttributes.copy()

    def clone(self, new_identifier=None):
        copy = self.__class__(title=self.title, identifier=self.identifier)
        copy.__dict__.update(self.__dict__)
        if new_identifier is not None:
            copy.identifier = new_identifier
        return copy

    def available(self, form):
        return True

    def isRequired(self, form):
        if callable(self.required):
            return self.required(form)
        return self.required

    def isEmpty(self, value):
        return value is NO_VALUE

    def getDefaultValue(self, form):
        if callable(self.defaultValue):
            return self.defaultValue(form)
        return self.defaultValue

    def constrainValue(self, value):
        return True

    def validate(self, value, form):
        if self.isRequired(form) and self.isEmpty(value):
            return _(u"Missing required value.")
        if not isinstance(value, Marker):
            try:
                if not self.constrainValue(value):
                    return _(u"The constraint failed.")
            except Exception as error:
                if hasattr(error, 'doc'):
                    return error.doc()
                return _(u"The constraint failed.")
        return None


class Fields(Collection):
    implements(interfaces.IFields)

    type = interfaces.IField
    factory = interfaces.IFieldFactory
