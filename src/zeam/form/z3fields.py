
from zeam.form import interfaces
from zeam.form.fields import Field

from zope.schema import interfaces as schema_interfaces

from grokcore import component as grok


class SchemaField(Field, grok.Adapter):
    grok.provides(interfaces.IField)
    grok.context(schema_interfaces.IField)

    def __init__(self, field):
        super(SchemaField, self).__init__(field.title, field.__name__)
        self.description = field.description
        self._field = field


