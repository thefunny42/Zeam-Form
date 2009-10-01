
from zeam.form.base import interfaces
from zeam.form.base.components import Component, Collection
from zeam.form.base.markers import NO_VALUE

from zope.interface import implements
from zope import component, schema
import zope.schema.interfaces
import zope.interface.interface


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

    def extend(self, *components):
        for cmp in components:
            # Interface class
            if isinstance(cmp, zope.interface.interface.InterfaceClass):
                for name, field in schema.getFieldsInOrder(cmp):
                    self.append(interfaces.IField(field))
            # Schema field
            elif zope.schema.interfaces.IField.providedBy(cmp):
                int = cmp.interface
                if not int:
                    raise ValueError("Field has no interface")
                self.append(interfaces.IField(cmp))
            # Form field
            elif interfaces.IField.providedBy(cmp):
                self.append(cmp)
            # Form fields
            elif interfaces.IFields.providedBy(cmp):
                for field in cmp:
                    self.append(field)
            else:
                raise TypeError("Unrecognized argument type", cmp)

