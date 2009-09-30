
import sys

from zeam.form import interfaces
from zeam.form.components import Component, Collection

from zope.interface import implements
from zope import component


class Action(Component):
    """A form action.
    """
    implements(interfaces.IAction)

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
        for action in self:
            extractor = component.getMultiAdapter(
                (action, form, request), interfaces.IWidgetExtractor)
            value, error = extractor.extract()
            if value is not None:
                if action.validate(form):
                    action(form)
                    return True
        return False


# Convience API, decorator to add action

class DecoratedAction(Action):
    """An action created by a decorator.
    """

    def __init__(self, title, callback, identifiant=None, validator=None):
        super(Action, self).__init__(title, identifiant)
        self._callback = callback
        self._validator = validator

    def validate(self, form):
        if self._validator is not None:
            self._validator(form)

    def __call__(self, form):
        assert self._callback is not None
        self._callback(form)


def action(title, identifiant=None, validator=None):
    def createAction(callback):
        new_action = DecoratedAction(title, callback, identifiant, validator)

        # Magic to access the parent action list to add the action
        frame = sys._getframe(1)
        f_locals = frame.f_locals
        actions = f_locals.setdefault('actions', Actions())

        actions.append(new_action)

        # We keep the same callback, so we can do super in
        # subclass. Registering it is enough, we do not need something
        # else.
        return callback
    return createAction
