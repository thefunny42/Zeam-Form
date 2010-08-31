# -*- coding: utf-8 -*-

import operator
import sys

from grokcore import component as grok
from grokcore.view import util

from zeam.form.base import interfaces
from zeam.form.base.actions import Actions
from zeam.form.base.datamanager import ObjectDataManager
from zeam.form.base.errors import Errors, Error
from zeam.form.base.fields import Fields
from zeam.form.base.markers import NO_VALUE, INPUT, NOT_EXTRACTED
from zeam.form.base.widgets import Widgets, getWidgetExtractor
from zeam.form.base.interfaces import ICollection

from zope import component, i18n, interface
from zope.pagetemplate.interfaces import IPageTemplate
from zope.publisher.browser import BrowserPage
from zope.publisher.publish import mapply


class Object(object):
    """Python object that takes argument to its __init__, in order to
    use super. This is required by Python 2.6.
    """

    def __init__(self, *args, **kwargs):
        pass


class GrokViewSupport(Object):
    """Support Grok view like behavior, without inheriting of Grok
    view (not to get any grokker at all, or inherit from BrowerView,
    BrowserPage).

    The render method support IPageTemplate in addition to Grok template.
    """
    grok.baseclass()
    grok.implements(interfaces.IGrokViewSupport)

    i18nLanguage = None

    def __init__(self, context, request):
        super(GrokViewSupport, self).__init__(context, request)
        self.context = context
        self.request = request

        if getattr(self, 'module_info', None) is not None:
            self.static = component.queryAdapter(
                self.request,
                interface.Interface,
                name=self.module_info.package_dotted_name)
            if self.static is not None:
                # For security in Zope 2
                self.static.__parent__ = self
        else:
            self.static = None

    @property
    def response(self):
        return self.request.response

    def redirect(self, url):
        self.response.redirect(url)

    def url(self, obj=None, name=None, data=None):
        """Return string for the URL based on the obj and name. The data
        argument is used to form a CGI query string.
        """
        if isinstance(obj, basestring):
            if name is not None:
                raise TypeError(
                    'url() takes either obj argument, obj, string arguments, '
                    'or string argument')
            name = obj
            obj = None

        if obj is None:
            obj = self.context
        if data is None:
            data = {}
        else:
            if not isinstance(data, dict):
                raise TypeError('url() data argument must be a dict.')

        return util.url(self.request, obj, name, data=data)

    def default_namespace(self):
        namespace = {'view': self,
                     'context': self.context,
                     'request': self.request}
        if self.i18nLanguage is not None:
            namespace['target_language'] = self.i18nLanguage
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


_marker = object()


def cloneFormData(original, content=_marker, prefix=None):
    assert interfaces.IFieldExtractionValueSetting.providedBy(original)
    clone = FormData(original.context, original.request, content)
    clone.ignoreRequest = original.ignoreRequest
    clone.ignoreContent = original.ignoreContent
    clone.i18nLanguage = original.i18nLanguage
    clone.postOnly = original.postOnly
    clone.mode = original.mode
    clone.parent = original
    if prefix is None:
        clone.prefix = original.prefix
    else:
        clone.prefix = prefix
    return clone


class FieldsValues(dict):
    """Dictionary to contains values of fields. get default by default
    on the default value of a field.
    """

    def __init__(self, fields):
        self.fields = fields

    def getDefault(self, key, default=None):
        value = super(FieldsValues, self).get(key, default)
        if value is NO_VALUE:
            value = self.fields[key].getDefaultValue()
            if value is NO_VALUE:
                return default
        return value


class FormData(Object):
    """This represent a submission of a form. It can be used to update
    widgets and run actions.
    """
    grok.baseclass()
    grok.implements(interfaces.IFormData)

    prefix = 'form'
    parent = None
    mode = INPUT
    dataManager = ObjectDataManager
    postOnly = True
    i18nLanguage = None

    ignoreRequest = False
    ignoreContent = True

    status = u''

    def __init__(self, context, request, content=_marker):
        super(FormData, self).__init__(context, request)
        self.context = context
        self.request = request
        self.errors = Errors()
        self.__extracted = NOT_EXTRACTED
        self.__content = None
        if content is _marker:
            content = context
        self.setContentData(content)

    @property
    def formErrors(self):
        error = self.errors.get(self.prefix, None)
        if error is None or ICollection.providedBy(error):
            return error
        return [error]

    def htmlId(self):
        return self.prefix.replace('.', '-')

    def getContent(self):
        # Shortcut for actions. You should not reimplement that method
        # but getContentData.
        return self.getContentData().getContent()

    def getContentData(self):
        return self.__content

    def setContentData(self, content):
        if not interfaces.IDataManager.providedBy(content):
            content = self.dataManager(content)
        self.__content = content

    def validateData(self, fields, data):
        if len(self.errors):
            if not self.prefix in self.errors:
                self.errors.append(Error(u"There were errors", self.prefix))
            return self.errors
        return None

    def extractData(self, fields):
        if self.__extracted is not NOT_EXTRACTED:
            return (self.__extracted, self.errors)
        self.__extracted = data = FieldsValues(fields)

        for field in fields:

            # Widget extraction and validation
            extractor = getWidgetExtractor(field, self, self.request)
            if extractor is not None:
                value, error = extractor.extract()
                if error is None:
                    error = field.validate(value, self.context)
                if error is not None:
                    self.errors.append(Error(error, field.identifier))
                data[field.identifier] = value

        # Generic form validation
        errors = self.validateData(fields, data)
        return (data, errors)


class FormCanvas(GrokViewSupport, FormData):
    """This represent a sumple form setup: setup some fields and
    actions, prepare widgets for it.
    """
    grok.baseclass()
    grok.implements(interfaces.ISimpleFormCanvas)

    label = u''
    description = u''

    actions = Actions()
    fields = Fields()

    def __init__(self, context, request):
        super(FormCanvas, self).__init__(context, request)
        self.actionWidgets = Widgets(form=self, request=self.request)
        self.fieldWidgets = Widgets(form=self, request=self.request)

    def extractData(self, fields=None):
        if fields is None:
            fields = self.fields
        return super(FormCanvas, self).extractData(fields)

    def haveRequiredFields(self):
        return reduce(
            operator.or_,
            [False] + map(operator.attrgetter('required'), self.fields))

    def updateActions(self):
        return self.actions.process(self, self.request)

    def updateWidgets(self):
        self.fieldWidgets.extend(self.fields)
        self.actionWidgets.extend(self.actions)

        self.fieldWidgets.update()
        self.actionWidgets.update()


class StandaloneForm(GrokViewSupport, BrowserPage):
    """This is a base for a standalone form, process the form.
    """
    grok.baseclass()

    def updateActions(self):
        return None, None

    def updateWidgets(self):
        pass

    def updateForm(self):
        self.updateActions()
        self.updateWidgets()

    def __call__(self):
        mapply(self.update, (), self.request)
        if self.response.getStatus() in (302, 303):
            # A redirect was triggered somewhere in update().  Don't
            # continue processing the form
            return

        if self.i18nLanguage is None:
            self.i18nLanguage = i18n.negotiate(self.request)
        self.updateForm()
        if self.response.getStatus() in (302, 303):
            return

        return self.render()


class Form(FormCanvas, StandaloneForm):
    """A full simple standalone form.
    """
    grok.baseclass()
    grok.implements(interfaces.ISimpleForm)


def extends(*forms, **opts):
    # Extend a class with parents components
    field_type = opts.get('fields', 'all')

    def extendComponent(field_type):
        factory = {'actions': Actions, 'fields': Fields}.get(field_type)
        if factory is None:
            raise ValueError(u"Invalid parameter fields to extends")
        frame = sys._getframe(2)
        f_locals = frame.f_locals
        components = f_locals.setdefault(field_type, factory())
        components.extend(*map(operator.attrgetter(field_type), forms))

    if field_type == 'all':
        extendComponent('actions')
        extendComponent('fields')
    else:
        extendComponent(field_type)
