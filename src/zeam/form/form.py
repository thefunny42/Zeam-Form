
from zeam.form.actions import Actions
from zeam.form.fields import Fields
from zeam.form.widgets import Widgets
from zeam.form import interfaces

from zope.interface import implements
from zope.publisher.publish import mapply
from zope import component


class FormSet(object):
    implements(interfaces.IFormSet)

    prefix = u'form'
    title = u''
    description = u''

    actions = Actions()
    fields = Fields()

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.submission = None

    def getContent(self):
        return self.context

    def update(self):
        pass

    def updateActions(self):
        self.submission = self.actions.process(self, self.request)

    def updateWidgets(self):
        self.field_widgets = Widgets(
            self.fields, form=self, request=self.request)
        self.action_widgets = Widgets(
            self.actions, form=self, request=self.request)

    def render(self):
        pass


class Form(FormSet):
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


class SubForm(FormSet):
    implements(interfaces.ISubForm)

    def __init__(self, context, parent, request):
        super(SubForm, self).__init__(context, request)
        self.parent = parent


class ComposedForm(Form):
    implements(interfaces.IComposedForm)

    def __init__(self, context, request):
        super(ComposedForm, self).__init__(context, request)

        subforms = map(lambda x: x[1], component.getAdapters(
                (self.context, self,  self.request), interfaces.ISubForm))
        # TODO sort forms
        self.subforms = []
        for subform in subforms:
            if subform.available():
                self.subforms.append(subform)


    def updateForm(self):
        # Set/run actions for all forms
        for subform in self.subforms:
            subform.updateActions()
        # Run our actions
        self.updateActions()
        # Set widgets for all forms
        for subform in self.subforms:
            subfrom.updateWidgets()
