# -*- coding: utf-8 -*-

from zope import interface
from zope.publisher.interfaces.browser import IBrowserPage


class IComponent(interface.Interface):
    """A named component.
    """
    identifier = interface.Attribute(u"Component id")
    title = interface.Attribute(u"Component title")

    def clone(new_identifier=None):
        """Return a clone of the new component, with identifier
        new_identifier if it is not None.
        """


class IComponentFactory(interface.Interface):
    """Component used to built components.
    """

    def produce(self):
        """Should generate components.
        """


class ICollection(interface.Interface):
    """Support to manage a collection of ordered named components.
    """
    type = interface.Attribute(
        u"Interface restricting the type of component")
    factory = interface.Attribute(
        u"Interface to query in order to get a factory to extend "
        u"collection with unknow components.")

    def append(component):
        """Add a new component to the collection. Modify the current
        collection.
        """

    def extend(*component):
        """Create/Add a list of components to the collection. Modify
        the current collection.
        """

    def get(id, default=None):
        """Return the component with the given ID.
        """

    def select(*ids):
        """Return a copy containing only the given named components.
        """

    def omit(*ids):
        """Return a copy containing all but none of the given named
        components.
        """

    def copy():
        """Return a copy of the collection.
        """

    def keys():
        """Return all components id contained in the collection.
        """

    def __add__(other):
        """Create a collection as copy of self, and add value for
        other component or collection.
        """

    def __getitem__(id):
        """Return the given component identified by id or raise
        KeyError.
        """

    def __iter__():
        """Return an iterator on the components.
        """

    def __len__():
        """Return the numbre of components.
        """


class IPrefixable(interface.Interface):
    """An object with a prefix.
    """
    prefix = interface.Attribute("Prefix")


class IRenderableComponent(IPrefixable, IComponent):
    """A component that can be rendered with the help of a widget.
    """
    mode = interface.Attribute(
        u"Mode should be used to render the component")

    def available(context):
        """Return a boolean to qualify if the component wants to be
        rendered in the given context (i.e. form).
        """


class IFieldExtractionValueSetting(IPrefixable):
    """Setting to extract field values.
    """
    ignoreRequest = interface.Attribute(u"Ignore request values")
    ignoreContent = interface.Attribute(u"Ignore content values")
    mode = interface.Attribute(
        u"Mode should be used to render all the widgets")


class IDataManager(interface.Interface):
    """A data manager let you access content.
    """

    def __init__(content):
        """Initialize the data manager for the given content.
        """

    def get(identifier):
        """Return content value associated to the given identifier or
        raise KeyError.
        """

    def set(identifier, value):
        """Modifiy content value associated to the given identifier.
        """


class IFormData(IFieldExtractionValueSetting):
    """Data of a form. It is used to process and setup the form.
    """
    errors = interface.Attribute(u"List of all errors who might occurs")
    status = interface.Attribute(u"Status message")
    formError = interface.Attribute(u"Main error who occurred")
    dataManager = interface.Attribute(
        u"Data manager class to use to access content")

    def getContentData():
        """Return the data from the content that should be used by
        the form.
        """

    def setContentData(content):
        """Use content as base to retrieve the data that should be
        used by the form.
        """

    def extractData(fields):
        """Return form data for the given fields.
        """


class ActionError(Exception):
    """A error happening while processing the form.
    """


class IAction(IRenderableComponent):
    """A form action.
    """

    def validate(submission):
        """Self validation of values in order to run.
        """

    def __call__(submission):
        """Execute the action.
        """


class IActions(ICollection):
    """A list of actions.
    """

    def process(form, request):
        """Execute actions.
        """


class IField(IRenderableComponent, IFieldExtractionValueSetting):
    """A form field.
    """
    description = interface.Attribute(u"Field description")
    required = interface.Attribute(
        u"Boolean indicating if the field is required")

    def getDefaultValue():
        """Return the default value.
        """

    def validate(value, context=None):
        """Validate that the given value fullfil the field
        requirement.
        """


class IFieldFactory(IComponentFactory):
    """Factory to create zeam.form Fields from other components than
    zeam.form ones.
    """


class IFields(ICollection):
    """A collection of fields.
    """


class IError(IComponent):
    """A error.
    """


class IErrors(ICollection):
    """A collection of errors.
    """


class IWidget(IComponent):
    """Display a form component on the page.
    """

    def htmlId():
        """Return the HTML id of the HTML component representing the
        widget.
        """

    def htmlClass():
        """Return an HTML class to mark the widget with.
        """

    def render():
        """Return the rendered HTML of the widget.
        """


class IFieldWidget(IWidget):
    """Widget for fields.
    """
    description = interface.Attribute(u"Description of the field")
    error = interface.Attribute(u"Field error, or None")
    required = interface.Attribute(
        u"Boolean indicating if the field is required")


class IWidgetExtractor(interface.Interface):
    """The counterpart of the Widget, used to extract widget value
    from the request.
    """

    def extract():
        """Return a tuple (value, error). Value must be a valid field
        value. If error is not None, value is discarded.
        """

    def extractRaw():
        """Return request entries needed for the widget to redisplay
        the same information in case of validation failure.
        """


class IWidgets(ICollection):
    """A collection of widgets.
    """


class IGrokViewSupport(interface.Interface):
    """Some usefull methods from Grok View.
    """
    response = interface.Attribute(
        u"Response object that is associated with the current request.")
    i18nLanguage = interface.Attribute(
        u"Language code to translate view content to.")

    def redirect(url):
        """Redirect to given URL.
        """

    def url(obj=None, name=None, data=None):
        """Compute an URL to an object (or self), and add a name, and
        maybe some data.
        """

    def update():
        """User defined pre-update.
        """

    def render():
        """Render the form.
        """


class IFormCanvas(IPrefixable, IFieldExtractionValueSetting, IGrokViewSupport):
    """Definition of a form it have a label, description, fields and
    actions that you can update.

    You can as well render it as a view.
    """
    label = interface.Attribute(u"Form title")
    description = interface.Attribute(u"Form description")

    actions = interface.Attribute(u"Form actions")
    fields = interface.Attribute(u"Form fields")

    def updateActions():
        """Set up and run form actions.
        """

    def updateWidgets():
        """Set up rendering field / action widgets and their value to
        display.
        """


class ISimpleFormCanvas(IFormCanvas, IFormData):
    """A simple form canvas with only fields and actions.
    """
    actionWidgets = interface.Attribute(u"Form widgets")
    fieldWidgets = interface.Attribute(u"Form widgets")


class IForm(IBrowserPage, IFormCanvas):
    """Regular form containing fields and actions, that you can call,
    and will be updated and rendered.
    """

    def updateForm():
        """Update the form mechanism (setup fields, actions, run
        actions, setup widgets).
        """

    def __call__():
        """Update and render the form.
        """


class ISimpleForm(IForm, ISimpleFormCanvas):
    """A simple form, with fields and actions.
    """


class IZeamFormBaseAPI(interface.Interface):
    """Base zeam form API.
    """
    Action = interface.Attribute(
        u"A form action")
    Actions = interface.Attribute(
        u"A collection of actions")
    Field = interface.Attribute(
        u"A form field")
    Fields = interface.Attribute(
        u"A collection of fields")
    Widgets = interface.Attribute(
        u"A collection of widgets")
    FormData = interface.Attribute(
        u"A configuration object to render fields as widgets")
    Form = interface.Attribute(
        u"A basic and simple Form")
    ActionError = interface.Attribute(
        u"An error occuring while processing an Action")

    action = interface.Attribute(
        u"Decorator to use a form method as an Action")

    context = interface.Attribute(
        u"Directive to map form to a context")
    name = interface.Attribute(
        u"Directive to name a form")
    layer = interface.Attribute(
        u"Directive to specify a form layer")
    template = interface.Attribute(
        u"Directive to specify a grok template to render the form")
    require = interface.Attribute(
        u"Directive to require a permission to access the form")

    NO_VALUE = interface.Attribute(
        u"Marker to mark the absence of value")
    DISPLAY = interface.Attribute(
        u"Marker for mode to get display widgets")
    INPUT = interface.Attribute(
        u"Marker for mode to get input widgets")
    DEFAULT = interface.Attribute(
        u"Marker used to use the default value located on the form")
    SUCCESS = interface.Attribute(
        u"Marker used by actions to report a success")
    FAILURE = interface.Attribute(
        u"Marker used by actions to report a failure")
