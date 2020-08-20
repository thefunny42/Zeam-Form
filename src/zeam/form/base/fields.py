from zeam.form.base import interfaces
from zeam.form.base.components import Component, Collection
from zeam.form.base.markers import NO_VALUE, DEFAULT, Marker

from zope.interface import implementer
from zope.i18nmessageid import MessageFactory

_ = MessageFactory('zeam.form.base')


@implementer(interfaces.IField)
class Field(Component):

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
                 defaultFactory=None,
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
        self.defaultFactory = defaultFactory
        if constrainValue is not None:
            self.constrainValue = constrainValue
        self.htmlAttributes = self.htmlAttributes.copy()
        self.htmlAttributes.update(htmlAttributes)

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
        # We should take the defaultFactory into account.
        # Not sure how yet.
        if callable(self.defaultValue):
            return self.defaultValue(form)
        return self.defaultValue

    def constrainValue(self, value):
        return True

    def validate(self, value, form):
        if self.isEmpty(value):
            if self.isRequired(form):
                return _(u"Missing required value.")
        elif not isinstance(value, Marker):
            try:
                if not self.constrainValue(value):
                    return _(u"The constraint failed.")
            except Exception as error:
                if hasattr(error, 'doc'):
                    return error.doc()
                return _(u"The constraint failed.")
        return None


@implementer(interfaces.IFields)
class Fields(Collection):

    type = interfaces.IField
    factory = interfaces.IFieldFactory
