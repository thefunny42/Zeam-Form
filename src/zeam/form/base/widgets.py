# -*- coding: utf-8 -*-

import warnings

from grokcore import component as grok
from zeam.form.base import interfaces
from zeam.form.base.components import Component, Collection
from zeam.form.base.interfaces import IModeMarker, IWidgetFactory
from zeam.form.base.markers import NO_VALUE, getValue, HiddenMarker
from zope import component
from zope.interface import Interface
from zope.pagetemplate.interfaces import IPageTemplate


def widgetId(form, component):
    """Create an unique ID for a widget.
    """
    return '.'.join(
        (iditem for iditem in
         (str(form.prefix), component.prefix, component.identifier,)
         if iditem))


def getWidgetExtractor(field, form, request):
    warnings.warn(
        u"getWidgetExtractor is deprecated in favor of "
        u"form.widgetFactory.extractor", DeprecationWarning)
    return form.widgetFactory.extractor(field)


class WidgetFactory(object):
    """Generic API to create widgets and extractors.
    """
    grok.implements(IWidgetFactory)

    def __init__(self, form, request):
        self.form = form
        self.request = request

    def widget(self, field):
        """Create a widget for the given field.
        """
        if not field.available(self.form):
            return None
        mode = str(getValue(field, 'mode', self.form))
        return component.getMultiAdapter(
            (field, self.form, self.request),
            interfaces.IWidget,
            name=mode)

    def extractor(self, field):
        """Create a widget extractor for the given field.
        """
        mode = getValue(field, 'mode', self.form)

        # The field mode should be extractable or we skip it.
        if (IModeMarker.providedBy(mode) and mode.extractable is False):
            return None

        extractor = component.queryMultiAdapter(
            (field, self.form, self.request),
            interfaces.IWidgetExtractor,
            name=str(mode))
        if extractor is not None:
            return extractor
        # Default to the default extractor
        return component.getMultiAdapter(
            (field, self.form, self.request),
            interfaces.IWidgetExtractor)


class Widgets(Collection):
    grok.implements(interfaces.IWidgets)

    type = interfaces.IWidget

    def extend(self, *args):
        if not args:
            return

        # Ensure the user created us with the right options
        assert self.__dict__.get('form', None) is not None
        factory = self.form.widgetFactory.widget

        for arg in args:
            if interfaces.IWidgets.providedBy(arg):
                for widget in arg:
                    self.append(widget)
            elif interfaces.IIterable.providedBy(arg):
                for field in arg:
                    widget = factory(field)
                    if widget is not None:
                        self.append(widget)
            elif interfaces.IWidget.providedBy(arg):
                self.append(arg)
            elif interfaces.IRenderableComponent.providedBy(arg):
                widget = factory(arg)
                if widget is not None:
                    self.append(widget)
            else:
                raise TypeError(u'Invalid type', arg)

    def update(self):
        for widget in self:
            widget.update()


class Widget(Component, grok.MultiAdapter):
    grok.baseclass()
    grok.implements(interfaces.IWidget)
    grok.provides(interfaces.IWidget)

    defaultHtmlClass = ['field']

    def __init__(self, component, form, request):
        identifier = widgetId(form, component)
        super(Widget, self).__init__(component.title, identifier)
        self.component = component
        self.form = form
        self.request = request
        self._htmlAttributes = {}

    def clone(self, new_identifier=None):
        raise NotImplementedError

    def htmlId(self):
        # Return an identifier suitable for CSS usage
        return self.identifier.replace('.', '-')

    def htmlClass(self):
        result = self.defaultHtmlClass
        if self.required:
            result = result + ['field-required',]
        return ' '.join(result)

    def htmlAttribute(self, name):
        value = self._htmlAttributes.get(name)
        if value:
            # Boolean return as value the name of the property
            if isinstance(value, bool):
                return name
            return value
        return None

    def isVisible(self):
        return not isinstance(self.component.mode, HiddenMarker)

    def default_namespace(self):
        namespace = {'widget': self,
                     'request': self.request}
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
        self.identifier = widgetId(form, component)
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


class ReadOnlyWidgetExtractor(WidgetExtractor):
    grok.name('readonly')


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
        self._htmlAttributes.update({
                'accesskey': component.accesskey,
                'formnovalidate': not component.html5Validation})

    def htmlClass(self):
        return 'action'


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
        self.required = component.isRequired(form)
        self._htmlAttributes.update(component.htmlAttributes)
        self._htmlAttributes.update({
                'readonly': component.readonly,
                'required': self.required})

    @property
    def error(self):
        return self.form.errors.get(self.identifier, None)

    def computeValue(self):
        # First lookup the request
        ignoreRequest = getValue(self.component, 'ignoreRequest', self.form)
        if not ignoreRequest:
            extractor = self.form.widgetFactory.extractor(self.component)
            if extractor is not None:
                value = extractor.extractRaw()
                if value:
                    return self.prepareRequestValue(value, extractor)

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
        value = self.component.getDefaultValue(self.form)
        return self.prepareContentValue(value)

    def valueToUnicode(self, value):
        return unicode(value)

    def prepareRequestValue(self, value, extractor):
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


class ReadOnlyFieldWidget(FieldWidget):
    grok.name('readonly')
