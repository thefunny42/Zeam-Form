
from zeam.form.base.actions import Actions
from zeam.form.base.datamanager import ObjectDataManager
from zeam.form.base.fields import Fields
from zeam.form.base.errors import Errors, Error
from zeam.form.base.markers import INPUT, NOT_EXTRACTED
from zeam.form.base.widgets import Widgets, getWidgetExtractor
from zeam.form.base import interfaces

from zope.pagetemplate.interfaces import IPageTemplate
from zope.publisher.browser import BrowserPage
from zope.publisher.publish import mapply
from zope import component

from grokcore.view import util
from grokcore import component as grok


class GrokViewSupport(object):
    """Support Grok view like behavior, without inheriting of Grok
    view (not to get any grokker at all, or inherit from BrowerView,
    BrowserPage).

    The render method support IPageTemplate in addition to Grok template.
    """
    grok.baseclass()
    grok.implements(interfaces.IGrokViewSupport)

    def __init__(self, context, request):
        super(GrokViewSupport, self).__init__(context, request)
        self.context = context
        self.request = request

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
        return {'view': self,
                'context': self.context,
                'request': self.request}

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
    clone.mode = original.mode
    if prefix is None:
        clone.prefix = original.prefix
    else:
        clone.prefix = prefix
    return clone


class FormData(object):
    """This represent a submission of a form. It can be used to update
    widgets and run actions.
    """
    grok.baseclass()
    grok.implements(interfaces.IFormData)

    prefix = 'form'
    mode = INPUT
    dataManager = ObjectDataManager

    ignoreRequest = False
    ignoreContent = True

    status = u''

    def __init__(self, context, request, content=_marker):
        super(FormData, self).__init__(context, request)
        self.context = context
        self.request = request
        self.errors = Errors()
        self.setContentData(content is _marker and context or content)
        self.__extracted = NOT_EXTRACTED

    @property
    def formError(self):
        return self.errors.get(self.prefix, None)

    def getContentData(self):
        return self.__content

    def setContentData(self, content):
        if not interfaces.IDataManager.providedBy(content):
            content = self.dataManager(content)
        self.__content = content

    def extractData(self, fields):
        if self.__extracted is not NOT_EXTRACTED:
            return (self.__extracted, self.errors)
        self.__extracted = data = dict()

        for field in fields:
            extractor = getWidgetExtractor(field, self, self.request)
            value, error = extractor.extract()
            if error is None:
                error = field.validate(value)
            if error is not None:
                self.errors.append(Error(error, field.identifier))
            data[field.identifier] =  value

        errors = None
        if len(self.errors):
            if not self.prefix in self.errors:
                self.errors.append(Error(u"There were errors", self.prefix))
            errors = self.errors
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

    def updateActions(self):
        self.actions.process(self, self.request)

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
        pass

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

        self.updateForm()
        if self.response.getStatus() in (302, 303):
            return

        return self.render()


class Form(FormCanvas, StandaloneForm):
    """A full simple standalone form.
    """
    grok.baseclass()
    grok.implements(interfaces.ISimpleForm)



