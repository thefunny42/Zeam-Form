
from zope.publisher.interfaces.browser import IBrowserPage
from zope import interface


class IComponent(interface.Interface):
    """A named component.
    """

    identifier = interface.Attribute(u"Component id")
    title = interface.Attribute(u"Component title")


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

class IFormSubmission(interface.Interface):
    """Submission of a form.
    """

    errors = interface.Attribute(u"List of errors who might occurs")
    status = interface.Attribute(u"Status message")

    def extractData():
        """Return form data.
        """


class IAction(IComponent):
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


class IFieldExtractionValueSetting(interface.Interface):
    """Setting to extract field values.
    """

    ignoreRequest = interface.Attribute(u"Ignore request values")
    ignoreContent = interface.Attribute(u"Ignore content values")


class IField(IComponent, IFieldExtractionValueSetting):

    description = interface.Attribute(u"Field description")
    required = interface.Attribute(
        u"Boolean indicating if the field is required")

    def getContentValue(context):
        """Extract the value from the context.
        """

    def getDefaultValue():
        """Return the default value.
        """

    def validate(value):
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

    def render():
        """Return the rendered HTML of the widget.
        """


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
    pass


class IFormCanvas(IFieldExtractionValueSetting, IFormSubmission):

    prefix = interface.Attribute(u"Prefix to apply on form widgets")
    title = interface.Attribute(u"Form title")
    description = interface.Attribute(u"Form description")

    actions = interface.Attribute(u"Form actions")
    fields = interface.Attribute(u"Form fields")
    action_widgets = interface.Attribute(u"Form widgets")
    field_widgets = interface.Attribute(u"Form widgets")

    response = interface.Attribute(u"Response object that is "
                                   u"associated with the current request.")

    def getContent():
        """Return the form content (which content value should been
        toke).
        """

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

    def updateActions():
        """Set up and run form actions.
        """

    def updateWidgets():
        """Set up rendering field / action widgets and their value to
        display.
        """

    def render():
        """Render the form.
        """


class IDisplayFormCanvas(IFormCanvas):
    """Special form set in display only mode.
    """


class IForm(IBrowserPage, IFormCanvas):
    """Regular form containing fields and actions.
    """

    def updateForm():
        """Update the form mechanism (setup fields, actions, run
        actions, setup widgets).
        """

    def __call__():
        """Update and render the form.
        """

