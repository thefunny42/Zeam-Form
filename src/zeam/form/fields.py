
from zeam.form import interfaces
from zeam.form.components import Component, Collection

from zope.interface import implements
from zope import component, schema
import zope.schema.interfaces
import zope.interface.interface


class Field(Component):
    implements(interfaces.IField)

    description = u''

    def value(self, setting):
        raise ValueError


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
                name = cmp.__name__
                if not name:
                    raise ValueError("Field has no name")
                self.append(interfaces.IField(field))
            # Form field
            elif interfaces.IField.providedBy(cmp):
                self.append(cmp)
            # Form fields
            elif interfaces.IFields.providedBy(cmp):
                for field in cmp:
                    self.append(field)
            else:
                raise TypeError("Unrecognized argument type", cmp)

