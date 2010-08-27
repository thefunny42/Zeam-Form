
import sys

from zeam.form.base import interfaces
from zeam.form.base.components import Component, Collection
from zeam.form.base.errors import Error
from zeam.form.base.markers import NO_VALUE, NOTHING_DONE, FAILURE

from zope.interface import implements
from zope import component


class Action(Component):
    """A form action.
    """
    implements(interfaces.IAction)

    prefix = 'action'
    # By default an action is always in input mode (there is not much
    # sense otherwise).
    mode = 'input'
    description = None
    accesskey = None

    def available(self, context):
        return True

    def validate(self, submission):
        return True

    def __call__(self, submission):
        raise NotImplementedError


class Actions(Collection):
    """A list of form action.
    """
    implements(interfaces.IActions)

    type = interfaces.IAction

    def process(self, form, request):
        if form.postOnly and request.method != 'POST':
            return None, FAILURE
        for action in self:
            extractor = component.getMultiAdapter(
                (action, form, request), interfaces.IWidgetExtractor)

            value, error = extractor.extract()
            if value is not NO_VALUE:
                try:
                    if action.validate(form):
                        return action, action(form)
                except interfaces.ActionError, error:
                    form.errors.append(Error(error.args[0], form.prefix))
                    return action, FAILURE
        return None, NOTHING_DONE


# Convience API, decorator to add action

class DecoratedAction(Action):
    """An action created by a decorator.
    """

    def __init__(self, title, callback,
                 identifier=None, description=None, accesskey=None,
                 validator=None, available=None):
        super(Action, self).__init__(title, identifier)
        self._callback = callback
        self._validator = validator
        self._available = available
        self.accesskey = accesskey
        self.description = description

    def validate(self, form):
        if self._validator is not None:
            return self._validator(form)
        return True

    def available(self, form):
        if self._available is not None:
            return self._available(form)
        return True

    def __call__(self, form, *args, **kwargs):
        assert self._callback is not None
        return self._callback(form, *args, **kwargs)


# More convienent, extract the data before calling the action

class ExtractedDecoratedAction(DecoratedAction):

    def __call__(self, form):
        data, errors = form.extractData()
        if errors:
            return FAILURE
        # We directly give data.
        return super(ExtractedDecoratedAction, self).__call__(form, data)


def action(title, identifier=None, description=None, accesskey=None,
           validator=None, available=None,
           factory=DecoratedAction, category='actions'):
    def createAction(callback):
        new_action = factory(
            title, callback, identifier, description, accesskey,
            validator, available)

        # Magic to access the parent action list to add the action
        frame = sys._getframe(1)
        f_locals = frame.f_locals
        actions = f_locals.setdefault(category, Actions())

        actions.append(new_action)

        # We keep the same callback, so we can do super in
        # subclass. Registering it is enough, we do not need something
        # else.
        return callback
    return createAction
