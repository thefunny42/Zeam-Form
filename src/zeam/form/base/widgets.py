# -*- coding: utf-8 -*-

from grokcore import component as grok
from zeam.form.base import interfaces
from zeam.form.base.components import Component, Collection
from zeam.form.base.interfaces import IModeMarker
from zeam.form.base.markers import NO_VALUE, getValue
from zope import component
from zope.interface import Interface
from zope.pagetemplate.interfaces import IPageTemplate


def widget_id(form, component):
    """Create an unique ID for a widget.
    """
    return '.'.join(
        (iditem for iditem in
         (str(form.prefix), component.prefix, component.identifier,)
         if iditem))


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

    def htmlClass(self):
        return 'field'

    def default_namespace(self):
        namespace = {'widget': self,
                     'request': self.request}
        if self.form.i18nLanguage is not None:
            # i18n support for Chameleon
            namespace['target_language'] = self.form.i18nLanguage
        return namespace

    def namespace(self):
        return {}

    def update(self):
        pass

    def render(self):
        # Try grok template first
        template = getattr(self, 'template', None)
        if template is not None:
            return self.template.render(self)
        # Fallback on IPageTemplate
        template = component.getMultiAdapter(
            (self, self.request), IPageTemplate)
        return template()


class WidgetExtractor(grok.MultiAdapter):
    grok.implements(interfaces.IWidgetExtractor)
    grok.provides(interfaces.IWidgetExtractor)
    grok.adapts(
        interfaces.IRenderableComponent,
        interfaces.IFieldExtractionValueSetting,
        Interface)

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


class HiddenWidgetExtractor(WidgetExtractor):
    grok.name('hidden')


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
    grok.adapts(
        interfaces.IAction,
        interfaces.IFieldExtractionValueSetting,
        Interface)
    grok.name('input')

    def __init__(self, component, form, request):
        super(ActionWidget, self).__init__(component, form, request)
        self.description = component.description
        self.accesskey = component.accesskey

    def htmlClass(self):
        return 'action'


def getWidgetExtractor(field, form, request):
    mode = str(getValue(field, 'mode', form))

    # The field mode should be extractable or we skip it.
    if (IModeMarker.providedBy(field.mode) and
        field.mode.extractable is False):
        return None

    extractor = component.queryMultiAdapter(
        (field, form, request), interfaces.IWidgetExtractor, name=mode)
    if extractor is not None:
        return extractor
    return component.getMultiAdapter(
        (field, form, request), interfaces.IWidgetExtractor)


class FieldWidget(Widget):
    grok.implements(interfaces.IFieldWidget)
    grok.adapts(
        interfaces.IField,
        interfaces.IFormData,
        Interface)
    grok.name('input')

    def __init__(self, component, form, request):
        super(FieldWidget, self).__init__(component, form, request)
        self.description = component.description
        self.required = component.required
        self.readonly = component.readonly

    @property
    def error(self):
        return self.form.errors.get(self.component.identifier, None)

    def computeValue(self):
        # First lookup the request
        ignoreRequest = getValue(self.component, 'ignoreRequest', self.form)
        if not ignoreRequest:
            extractor = getWidgetExtractor(
                self.component, self.form, self.request)
            if extractor is not None:
                value = extractor.extractRaw()
                if value:
                    return self.prepareRequestValue(value)

        # After, the context
        ignoreContent = getValue(self.component, 'ignoreContent', self.form)
        if not ignoreContent:
            data = self.form.getContentData()
            try:
                value = data.get(self.component.identifier)
                # XXX: Need review
                if value is None:
                    value = NO_VALUE
                return self.prepareContentValue(value)
            except KeyError:
                # No value on the content for field, continue.
                pass

        # Take any default value
        value = self.component.getDefaultValue()
        return self.prepareContentValue(value)

    def valueToUnicode(self, value):
        return unicode(value)

    def prepareRequestValue(self, value):
        return value

    def prepareContentValue(self, value):
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
