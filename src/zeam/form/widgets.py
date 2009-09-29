
from zeam.form import interfaces
from zeam.form.components import Component, Collection

from zope.interface import Interface

from grokcore import component as grok


class Widget(Component, grok.MultiAdapter):
    grok.baseclass()
    grok.provides(interfaces.IWidget)

    def __init__(self, component, form, request):
        identifier = '%s.%s' % (self.form.prefix, self.component.identifier)
        super(Widget, self).__init__(component.title, identifier)
        self.component = component
        self.form = form
        self.request = request

    def render(self):
        raise NotImplementedError


class WidgetExtractor(grok.MultiAdapter):
    grok.provides(interfaces.IWidgetExtractor)
    grok.adapts(interfaces.IComponent, interfaces.IFormSet, Interface)

    def __init__(self, component, form, request):
        self.component = component
        self.form = form
        self.request = request

    def extract(self):
        identifier = '%s.%s' % (self.form.prefix, self.component.identifier)
        return (self.request.form.get(identifier, None), None)


class Widgets(Collection):

    type = interfaces.IWidget

    def extend(self, *collections):
        # Ensure the user created us with the right options
        assert self.__dict__.get('form', None) is not None
        assert self.__dict__.get('request', None) is not None

        for collection in collections:
            if interfaces.ICollection.providedBy(collection):
                for cmp in collection:
                    widget = component.getAdapter(
                        (cmp, self.form, self.request), interfaces.IWidget)
                    self.append(widget)
            else:
                raise TypeError("Unrecognized argument type", cmp)
