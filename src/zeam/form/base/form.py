import operator
import sys
import binascii

from grokcore import component as grok
from grokcore.view import util

from zeam.form.base import interfaces
from zeam.form.base.actions import Actions
from zeam.form.base.datamanager import ObjectDataManager
from zeam.form.base.errors import Errors, Error
from zeam.form.base.fields import Fields
from zeam.form.base.markers import NO_VALUE, INPUT
from zeam.form.base.widgets import Widgets, WidgetFactory
from zeam.form.base.interfaces import ICollection, IError, InvalidCSRFToken

from zope import component, interface
from zope.interface import implementer
from zope.cachedescriptors.property import Lazy
from zope.i18nmessageid import MessageFactory
from zope.pagetemplate.interfaces import IPageTemplate
from zope.publisher.browser import BrowserPage
from zope.publisher.interfaces.http import MethodNotAllowed
from zope.publisher.publish import mapply


_ = MessageFactory('zeam.form.base')


@implementer(interfaces.IGrokViewSupport)
class GrokViewSupport:
    """Support Grok view like behavior, without inheriting of Grok
    view (not to get any grokker at all, or inherit from BrowerView,
    BrowserPage).

    The render method support IPageTemplate in addition to Grok template.
    """
    grok.baseclass()

    def __init__(self, context, request):
        super(GrokViewSupport, self).__init__(context, request)
        self.context = context
        self.request = request

        static_name = getattr(self, '__static_name__', None)
        if static_name is not None:
            self.static = component.queryAdapter(
                self.request,
                interface.Interface,
                name=static_name)
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
        if isinstance(obj, str):
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
                     'static': self.static,
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


_marker = object()


def cloneFormData(original, content=_marker, prefix=None):
    assert interfaces.IFieldExtractionValueSetting.providedBy(original)
    clone = FormData(original.context, original.request, content)
    clone.ignoreRequest = original.ignoreRequest
    clone.ignoreContent = original.ignoreContent
    clone.mode = original.mode
    clone.parent = original
    if prefix is None:
        clone.prefix = original.prefix
    else:
        clone.prefix = prefix
    # XXX Those fields are not checked by the interface
    clone.methods = original.methods
    clone.widgetFactoryFactory = original.widgetFactoryFactory
    errors = original.errors.get(clone.prefix, None)
    if errors is not None:
        clone.errors = errors
    return clone


class FieldsValues(dict):
    """Dictionary to contains values of fields. get default by default
    on the default value of a field.
    """

    def __init__(self, form, fields):
        self.form = form
        self.fields = fields

    def getWithDefault(self, key, default=None):
        value = super(FieldsValues, self).get(key, default)
        if value is NO_VALUE:
            value = self.fields[key].getDefaultValue(self.form)
            if value is NO_VALUE:
                return default
        return value

    def getDictWithDefault(self, default=None):
        result = {}
        for key in self.keys():
            result[key] = self.getWithDefault(key, default=default)
        return result

    # BBB
    getDefault = getWithDefault


@implementer(interfaces.IFormData)
class FormData:
    """This represent a submission of a form. It can be used to update
    widgets and run actions.
    """
    grok.baseclass()

    prefix = 'form'
    parent = None
    mode = INPUT
    dataManager = ObjectDataManager
    dataValidators = []
    widgetFactoryFactory = WidgetFactory
    methods = frozenset(('POST', 'GET'))

    ignoreRequest = False
    ignoreContent = True

    status = u''

    def __init__(self, context, request, content=_marker):
        self.context = context
        self.request = request
        self.errors = Errors()
        self.__extracted = {}
        self.__content = None
        if content is _marker:
            content = context
        self.setContentData(content)

    @Lazy
    def widgetFactory(self):
        return self.widgetFactoryFactory(self, self.request)

    @property
    def formErrors(self):
        error = self.errors.get(self.prefix, None)
        if error is None:
            return []
        if ICollection.providedBy(error):
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
        errors = Errors()
        for factory in self.dataValidators:
            validator = factory(self, fields)
            for error in validator.validate(data):
                if not IError.providedBy(error):
                    error = Error(error, self.prefix)
                errors.append(error)
        return errors

    def extractData(self, fields):
        # XXX to review this
        cached = self.__extracted.get(fields)
        if cached is not None:
            return cached
        data = FieldsValues(self, fields)
        self.errors = errors = Errors()
        self.__extracted[fields] = (data, errors)

        for field in fields:
            if not field.available(self):
                continue

            # Widget extraction and validation
            extractor = self.widgetFactory.extractor(field)
            if extractor is not None:
                value, error = extractor.extract()
                if error is None:
                    error = field.validate(value, self)
                if error is not None:
                    if not IError.providedBy(error):
                        error = Error(error, extractor.identifier)
                    errors.append(error)
                data[field.identifier] = value

        # Generic form validation
        errors.extend(self.validateData(fields, data))
        if len(errors):
            # Add a form level error if not already present
            if self.prefix not in errors:
                errors.append(Error(_(u"There were errors."), self.prefix))
        self.errors = errors
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

    protected = False
    csrftoken = None

    def __init__(self, context, request):
        super(FormCanvas, self).__init__(context, request)
        self.actionWidgets = Widgets(form=self, request=self.request)
        self.fieldWidgets = Widgets(form=self, request=self.request)

    def setUpToken(self):
        self.csrftoken = self.request.getCookies().get('__csrftoken__')
        if self.csrftoken is None:
            # It is possible another form, that is rendered as part of
            # this request, already set a csrftoken. In that case we
            # should find it in the response cookie and use that.
            setcookie = self.request.response.getCookie('__csrftoken__')
            if setcookie is not None:
                self.csrftoken = setcookie['value']
            else:
                # Ok, nothing found, we should generate one and set
                # it in the cookie ourselves. Note how we ``str()``
                # the hex value of the ``os.urandom`` call here, as
                # Python-3 will return bytes and the cookie roundtrip
                # of a bytes values gets messed up.
                self.csrftoken = str(binascii.hexlify(os.urandom(32)))
                self.request.response.setCookie(
                    '__csrftoken__',
                    self.csrftoken,
                    path='/',
                    expires=None,  # equivalent to "remove on browser quit"
                    httpOnly=True,  # no javascript access please.
                    )

    def checkToken(self):
        cookietoken = self.request.getCookies().get('__csrftoken__')
        if cookietoken is None:
            # CSRF is enabled, so we really should get a token from the
            # cookie. We didn't get it, so this submit is invalid!
            raise InvalidCSRFToken(_('Invalid CSRF token'))
        if cookietoken != self.request.form.get('__csrftoken__', None):
            # The token in the cookie is different from the one in the
            # form data. This submit is invalid!
            raise InvalidCSRFToken(_('Invalid CSRF token'))

    def extractData(self, fields=None):
        if fields is None:
            fields = self.fields
        return super(FormCanvas, self).extractData(fields)

    def haveRequiredFields(self):
        for field in self.fields:
            if field.required:
                return True
        return False

    def updateActions(self):
        if self.protected:
            # This form has CSRF protection enabled.
            self.checkToken()

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
        return self, None, None

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


@implementer(interfaces.ISimpleForm)
class Form(FormCanvas, StandaloneForm):
    """A full simple standalone form.
    """
    grok.baseclass()


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
