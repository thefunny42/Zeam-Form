
from zeam.form.base import interfaces
from zeam.form.base.components import Component, Collection
from zeam.form.base.markers import NO_VALUE, getValue

from zope.interface import Interface
from zope import component

from grokcore import component as grok


def widget_id(form, component):
    """Create an unique ID for a widget.
    """
    return '.'.join((str(form.prefix), component.prefix, component.identifier,))


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

    def copy(self):
        raise NotImplementedError

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
        interfaces.IRenderableComponent, interfaces.IFormData, Interface)

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


def createWidget(field, form, request):
    """Create a widget (or return None) for the given form and
    request.
    """
    if not field.available(form):
        return None
    mode = str(getValue(field, 'mode', form))
    return component.getMultiAdapter(
        (field, form, request), interfaces.IWidget, name=mode)


class Widgets(Collection):
    grok.implements(interfaces.IWidgets)

    type = interfaces.IWidget

    def extend(self, *args):
        if not args:
            return

        # Ensure the user created us with the right options
        assert self.__dict__.get('form', None) is not None
        assert self.__dict__.get('request', None) is not None

        for arg in args:
            if interfaces.ICollection.providedBy(arg):
                for item in arg:
                    widget = createWidget(item, self.form, self.request)
                    if widget is not None:
                        self.append(widget)
            elif interfaces.IWidget.providedBy(arg):
                self.append(arg)
            elif interfaces.IRenderableComponent.providedBy(arg):
                widget = createWidget(arg, self.form, self.request)
                if widget is not None:
                    self.append(widget)
            else:
                raise TypeError(u'Invalid type', arg)

    def update(self):
        for widget in self:
            widget.update()


# After follow the implementation of some really generic default
# widgets

class ActionWidget(Widget):
    grok.adapts(interfaces.IAction, interfaces.IFormData, Interface)
    grok.name('input')



class FieldWidget(Widget):
    grok.implements(interfaces.IFieldWidget)
    grok.adapts(interfaces.IField, interfaces.IFormData, Interface)
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
            data = self.form.getContentData()
            try:
                value = data.get(self.component.identifier)
                # XXX: Need review
                if value is None:
                    value = NO_VALUE
                return self.prepareValue(value)
            except KeyError:
                # No value on the content for field, continue.
                pass

        # Take any default value
        value = self.component.getDefaultValue()
        return self.prepareValue(value)

    def valueToUnicode(self, value):
        return unicode(value)

    def prepareValue(self, value):
        formatted_value = u''
        if value is not NO_VALUE:
            formatted_value = self.valueToUnicode(value)
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


class HiddenFieldWidget(FieldWidget):
    grok.name('hidden')
