
from zeam.form.base import interfaces
from zeam.form.base.components import Component, Collection
from zeam.form.base.markers import NO_VALUE, getValue

from zope.interface import Interface
from zope import component

from grokcore import component as grok


def widget_id(form, component):
    """Create an unique ID for a widget.
    """
    return '%s.%s.%s' % (
        str(form.prefix), component.prefix, component.identifier)


class Widget(Component, grok.MultiAdapter):
    grok.baseclass()
    grok.implements(interfaces.IWidget)
    grok.provides(interfaces.IWidget)

    def __init__(self, component, form, request):
        identifier = widget_id(form, component)
        super(Widget, self).__init__(component.title, identifier)
        self.component = component
        self.form = form
        self.request = request

    def htmlId(self):
        # Return an identifier suitable for CSS usage
        return self.identifier.replace('.', '-')

    def default_namespace(self):
        return {'widget': self,
                'request': self.request}

    def namespace(self):
        return {}

    def update(self):
        pass

    def render(self):
        return self.template.render(self)


class WidgetExtractor(grok.MultiAdapter):
    grok.provides(interfaces.IWidgetExtractor)
    grok.adapts(
        interfaces.IRenderableComponent, interfaces.IFormSubmission, Interface)

    def __init__(self, component, form, request):
        self.identifier = widget_id(form, component)
        self.component = component
        self.form = form
        self.request = request

    def extract(self):
        value = self.request.form.get(self.identifier, u'')
        if not len(value):
            value = NO_VALUE
        return (value, None)

    def extractRaw(self):
        entries = {}
        sub_identifier = self.identifier + '.'
        for key, value in self.request.form.iteritems():
            if key.startswith(sub_identifier) or key == self.identifier:
                entries[key] = value
        return entries


class Widgets(Collection):
    grok.implements(interfaces.IWidgets)

    type = interfaces.IWidget

    def extend(self, *collections):
        # Ensure the user created us with the right options
        assert self.__dict__.get('form', None) is not None
        assert self.__dict__.get('request', None) is not None

        for collection in collections:
            if interfaces.ICollection.providedBy(collection):
                for cmp in collection:
                    mode = str(getValue(cmp, 'mode', self.form))
                    widget = component.getMultiAdapter(
                        (cmp, self.form, self.request),
                        interfaces.IWidget, name=mode)
                    self.append(widget)
            else:
                raise TypeError("Unrecognized argument type", cmp)

    def update(self):
        for widget in self:
            widget.update()


# After follow the implementation of some really generic default
# widgets

class ActionWidget(Widget):
    grok.adapts(interfaces.IAction, interfaces.IFormSubmission, Interface)
    grok.name('input')



class FieldWidget(Widget):
    grok.implements(interfaces.IFieldWidget)
    grok.adapts(interfaces.IField, interfaces.IFormSubmission, Interface)
    grok.name('input')

    def __init__(self, component, form, request):
        super(FieldWidget, self).__init__(component, form, request)
        self.description = component.description
        self.required = component.required

    @property
    def error(self):
        return self.form.errors.get(self.component.identifier, None)

    def computeValue(self):
        # First lookup the request
        ignoreRequest = getValue(self.component, 'ignoreRequest', self.form)
        if not ignoreRequest:
            extractor = component.getMultiAdapter(
                (self.component, self.form, self.request),
                interfaces.IWidgetExtractor)
            value = extractor.extractRaw()
            if value:
                return value

        # After, the context
        ignoreContent = getValue(self.component, 'ignoreContent', self.form)
        if not ignoreContent:
            content = self.form.getContent()
            value = self.component.getContentValue(content)
            if value is not None:
                return self.prepareValue(value)

        # Take any default value
        value = self.component.getDefaultValue()
        return self.prepareValue(value)

    def prepareValue(self, value):
        formatted_value = u''
        if value is not NO_VALUE:
            formatted_value = unicode(value)
        return {self.identifier: formatted_value}

    def inputValue(self, id=None):
        if id is not None:
            id = '%s.%s' % (self.identifier, id)
        else:
            id = self.identifier
        return self.value.get(id, '')

    def update(self):
        self.value = self.computeValue()


class DisplayFieldWidget(FieldWidget):
    grok.name('display')
