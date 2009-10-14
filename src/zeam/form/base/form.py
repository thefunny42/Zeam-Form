
from zeam.form.base.actions import Actions
from zeam.form.base.fields import Fields
from zeam.form.base.errors import Errors, Error
from zeam.form.base.markers import INPUT, NOT_EXTRACTED
from zeam.form.base.widgets import Widgets
from zeam.form.base import interfaces

from zope.interface import implements
from zope.pagetemplate.interfaces import IPageTemplate
from zope.publisher.browser import BrowserPage
from zope.publisher.publish import mapply
from zope import component

from grokcore.view import util


class GrokViewSupport(object):
    """Support Grok view methods, without inheriting of Grok view (not
    to get any grokker at all, or inherit from BrowerView, BrowserPage).
    """

    def __init__(self, context, request):
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
        pass


class FormCanvas(GrokViewSupport):
    """Basic form alike support.
    """
    implements(interfaces.IFormCanvas)

    prefix = 'form'
    label = u''
    description = u''

    status = u''
    ignoreRequest = False
    ignoreContent = True
    mode = INPUT

    actions = Actions()
    fields = Fields()
    errors = Errors()

    def __init__(self, context, request):
        super(FormCanvas, self).__init__(context, request)
        self.actionWidgets = Widgets(form=self, request=self.request)
        self.fieldWidgets = Widgets(form=self, request=self.request)
        self._data = NOT_EXTRACTED

    @property
    def formError(self):
        return self.errors.get(self.prefix, None)

    def getContent(self):
        return self.context

    def extractData(self):
        if self._data is not NOT_EXTRACTED:
            return (self._data, self.errors)
        self._data = data = dict()

        for field in self.fields:
            extractor = component.getMultiAdapter(
                (field, self, self.request), interfaces.IWidgetExtractor)
            value, error = extractor.extract()
            if error is None:
                error = field.validate(value)
            if error is not None:
                self.errors.append(Error(error, field.identifier))
            data[field.identifier] =  value

        return (data, self.errors)

    def updateActions(self):
        self.actions.process(self, self.request)

    def updateWidgets(self):
        self.fieldWidgets.extend(self.fields)
        self.actionWidgets.extend(self.actions)

        self.fieldWidgets.update()
        self.actionWidgets.update()

    def render(self):
        # Try grok template first
        template = getattr(self, 'template', None)
        if template is not None:
            return self.template.render(self)
        # Fallback on IPageTemplate
        template = component.getMultiAdapter(
            (self, self.request), IPageTemplate)
        return template()


class Form(FormCanvas, BrowserPage):
    implements(interfaces.IForm)

    def updateForm(self):
        self.updateActions()
        self.updateWidgets()

    def __call__(self):
        mapply(self.update, (), self.request)
        if self.request.response.getStatus() in (302, 303):
            # A redirect was triggered somewhere in update().  Don't
            # continue processing the form
            return

        self.updateForm()
        if self.request.response.getStatus() in (302, 303):
            return

        return self.render()

