# -*- coding: utf-8 -*-

from zope import interface
from zope.publisher.interfaces.browser import IBrowserPage


class IInvalidCSRFToken(interface.Interface):

    def doc():
        """The form submit could not be handled as the CSRF token is missing
        or incorrect.
        """


@interface.implementer(IInvalidCSRFToken)
class InvalidCSRFToken(Exception):
    """The form submit could not be handled as the CSRF token is missing
    or incorrect.
    """


class IModeMarker(interface.Interface):
    """This interface identifies a form mode and defines if it allows
    data extraction.
    """
    extractable = interface.Attribute(
        u"Boolean allowing or not the extraction of the data,"
        u" for components in that mode.")


class IComponent(interface.Interface):
    """A named component.
    """
    identifier = interface.Attribute(u"Component id")
    title = interface.Attribute(u"Component title")
    order = interface.Attribute(u"Integer used to specify component order")

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


class IIterable(interface.Interface):
    """An iterable that return a component upon each iteration.
    """

    def __iter__():
        """Return an iterator on the components.
        """


class ICollection(IIterable):
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

    def clear():
        """Empty the collection: remove all components from it.
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

    def __contains__(id):
        """Return true if the collection contains a component
        identified by id.
        """

    def __len__():
        """Return the numbre of components.
        """


class IMutableCollection(ICollection):
    """A collection that can be changed.
    """

    def set(id , value):
        """Change component associated to this id.
        """

    def __setitem__(id, value):
        """Change component associated to this id.
        """

    def __delitem__(id):
        """Remove the component associated to this id.
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

    def available(form):
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

    def getContent():
        """Return the content managed by this data manager.
        """

    def get(identifier):
        """Return content value associated to the given identifier or
        raise KeyError.
        """

    def set(identifier, value):
        """Modifiy content value associated to the given identifier.
        """

    def delete(identifier):
        """Return the content value associated with the given identifier.
        """


class IFormData(IFieldExtractionValueSetting):
    """Form data processing facilities.
    """
    dataManager = interface.Attribute(
        u"Data manager class used to access content.")
    dataValidators = interface.Attribute(
        u"List of extra validators that must be called.")
    status = interface.Attribute(
        u"Form status message.")
    errors = interface.Attribute(
        u"Iterable of the errors that occured during the form processing.")
    formErrors = interface.Attribute(
        u"Main errors that occurred during the form processing.")
    widgetFactory = interface.Attribute(
        u"Callable used to create new widgets."
        u"Called with the form, field and request.")

    def getContent():
        """Return the content that is used by the form.
        """

    def getContentData():
        """Returns a data manager that work on the content used by the
        form.
        """

    def setContentData(content):
        """Sets the content that will be used as the form processing context.
        """

    def validateData(fields, data):
        """Validates the form in a global way and returns a collection
        of errors (if any occured).
        """

    def extractData(fields):
        """Returns the form data and errors for the given fields.
        """


class ActionError(Exception):
    """A error happening while processing the form.
    """


class IAction(IRenderableComponent):
    """A form action.
    """
    description = interface.Attribute(u"Describe the action")
    accesskey = interface.Attribute(u"Accesskey for the action")
    html5Validation = interface.Attribute(
        u"Enable HTML5 validation for this action")

    def validate(form):
        """Self validation of values in order to run.
        """

    def __call__(form):
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
    description = interface.Attribute(
        u"Field description")
    required = interface.Attribute(
        u"Boolean indicating if the field is required")
    readonly = interface.Attribute(
        u"Boolean indicating if the field is read-only")
    htmlAttributes = interface.Attribute(
        u"Dictionnary with extra html attributes to add to the field")
    interface = interface.Attribute(
        u"Optional Zope interface associated to the field")

    def getDefaultValue(form):
        """Return the default value.
        """

    def validate(value, form):
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

    def get(prefix, default=None):
        """Return a sub error identified by the given prefix if
        available.
        """


class IErrors(IMutableCollection):
    """A collection of errors.
    """


class IWidget(IComponent):
    """Display a form component on the page.
    """
    defaultHtmlClass = interface.Attribute(
        u"List of default html class to apply to the widget")
    defaultHtmlAttributes = interface.Attribute(
        u"Set of default authorized html attributes (without data- attributes)")
    alternateLayout = interface.Attribute(
        u"Boolean indicating if the widget can be rendered in a compact way")

    def htmlId():
        """Return the HTML id of the HTML component representing the
        widget.
        """

    def htmlClass():
        """Return an HTML class to mark the widget with.
        """

    def htmlAttribute(name):
        """Return the value of the given extra HTML attribute.
        """

    def htmlAttributes():
        """Return a dictionary with all authorized extra HTML attributes.
        """

    def isVisible():
        """Return True if the widget will render something visible in
        the rendered HTML.
        """

    def update():
        """Update the widget. This must be called before render.
        """

    def render():
        """Return the rendered HTML of the widget.
        """


class IWidgetFactory(interface.Interface):
    """Adapt a form to create widgets.
    """

    def __init__(form, request):
        """Create a factory.
        """

    def widget(field):
        """Create a widget for the given field.
        """

    def extractor(field):
        """Create a widget extractor for the given field.
        """


class IFieldWidget(IWidget):
    """Widget for fields.
    """
    description = interface.Attribute(
        u"Description of the field")
    error = interface.Attribute(
        u"Field error, or None")
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
    """Definition of a form structure.
    Form presentation : label, description
    Form contents and actions : fields, actions and their related methods.
    """
    label = interface.Attribute(u"Form title")
    description = interface.Attribute(u"Form description")

    actions = interface.Attribute(u"Form actions")
    fields = interface.Attribute(u"Form fields")

    def htmlId():
        """Return an identifier that can be used in the HTML code to
        identify the form.
        """

    def haveRequiredFields():
        """Return an boolean True if any of the fields are required.
        """

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
    CompoundActions = interface.Attribute(
        u"A collection of actions that can be managed differently")
    Field = interface.Attribute(
        u"A form field")
    Fields = interface.Attribute(
        u"A collection of fields")
    Error = interface.Attribute(
        u"An error")
    Errors = interface.Attribute(
        u"A collection of errors")
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

    ObjectDataManager = interface.Attribute(
        u"Data manager to work with values as attribute of an object")
    DictDataManager = interface.Attribute(
        u"Data manager to work with values in dictionary")
    NoneDataManager = interface.Attribute(
        u"Data manager to work directly with a value")
    makeAdaptiveDataManager = interface.Attribute(
        u"Data manager to work with from an simple adapter")

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
        u"Marker to mark the absence of a value")
    NO_CHANGE = interface.Attribute(
        u"Marker to mark the non-modification of a value")
    DISPLAY = interface.Attribute(
        u"Marker for mode to get display widgets")
    INPUT = interface.Attribute(
        u"Marker for mode to get input widgets")
    HIDDEN = interface.Attribute(
        u"Marker for mode to get hidden widgets")
    DEFAULT = interface.Attribute(
        u"Marker used to use the default value located on the form")
    SUCCESS = interface.Attribute(
        u"Marker used by actions to report a success")
    FAILURE = interface.Attribute(
        u"Marker used by actions to report a failure")
    NOTHING_DONE = interface.Attribute(
        u"Marker used by actions to report the absence of activity")
