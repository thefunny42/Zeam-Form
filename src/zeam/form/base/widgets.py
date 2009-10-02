
from zeam.form.base import interfaces
from zeam.form.base.components import Component, Collection
from zeam.form.base.markers import NO_VALUE

from zope.interface import Interface
from zope import component

from grokcore import component as grok


class Widget(Component, grok.MultiAdapter):
    grok.baseclass()
    grok.implements(interfaces.IWidget)
    grok.provides(interfaces.IWidget)

    def __init__(self, component, form, request):
        identifier = '%s.%s' % (str(form.prefix), component.identifier)
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
    grok.adapts(interfaces.IComponent, interfaces.IFormCanvas, Interface)

    def __init__(self, component, form, request):
        self.identifier = '%s.%s' % (str(form.prefix), component.identifier)
        self.component = component
        self.form = form
        self.request = request

    def extract(self):
        return (self.request.form.get(self.identifier, NO_VALUE), None)

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
                    widget = component.getMultiAdapter(
                        (cmp, self.form, self.request), interfaces.IWidget)
                    self.append(widget)
            else:
                raise TypeError("Unrecognized argument type", cmp)

    def update(self):
        for widget in self:
            widget.update()


# After follow the implementation of some really generic default
# widgets

class ActionWidget(Widget):
    grok.adapts(interfaces.IAction, interfaces.IFormCanvas, Interface)



class FieldWidget(Widget):
    grok.adapts(interfaces.IField, interfaces.IFormCanvas, Interface)

    def __init__(self, component, form, request):
        super(FieldWidget, self).__init__(component, form, request)
        self.description = component.description

    def value(self):
        # First lookup the request
        if not self.form.ignoreRequest:
            extractor = component.getMultiAdapter(
                (self.component, self.form, self.request),
                interfaces.IWidgetExtractor)
            return extractor.extractRaw()

        # After, the context
        if not self.form.ignoreContext:
            content = self.form.getContent()
            value = self.component.getContentValue(content)
            if value is not None:
                return self.prepareValue(value)

        # Take any default value
        value = self.component.getDefaultValue()
        return self.prepareValue(value)

    def prepareValue(self, value):
        if value is NO_VALUE:
            return u''
        return unicode(value)
