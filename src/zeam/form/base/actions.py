
import sys
import itertools

from zeam.form.base import interfaces
from zeam.form.base.components import Component, Collection
from zeam.form.base.errors import Error
from zeam.form.base.markers import NO_VALUE, NOTHING_DONE, FAILURE
from zeam.form.base.markers import getValue, DEFAULT

from zope.interface import implements, alsoProvides
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
    html5Validation = True
    postOnly = DEFAULT
    htmlAttributes = {}

    def __init__(self, title=None, identifier=None, **htmlAttributes):
        super(Action, self).__init__(title, identifier)
        self.htmlAttributes = self.htmlAttributes.copy()
        self.htmlAttributes.update(htmlAttributes)

    def available(self, form):
        return True

    def validate(self, form):
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
            if value is not NO_VALUE:
                isPostOnly = getValue(action, 'postOnly', form)
                if isPostOnly and request.method != 'POST':
                    form.errors.append(
                        Error('This form was not submitted properly',
                              form.prefix))
                    return form, None, FAILURE
                try:
                    if action.validate(form):
                        return form, action, action(form)
                except interfaces.ActionError, error:
                    form.errors.append(Error(error.args[0], form.prefix))
                    return form, action, FAILURE
        return form, None, NOTHING_DONE


class CompoundActions(object):
    """Compound different types of actions together.
    """
    implements(interfaces.IIterable)

    def __init__(self, *new_actions):
        self.__actions = []
        self.extend(new_actions)

    def extend(self, new_actions):
        for actions in new_actions:
            self.append(actions)

    def append(self, actions):
        assert interfaces.IActions.providedBy(actions), u"Invalid actions"
        self.__actions.append(actions)

    def copy(self):
        copy = self.__class__()
        copy.extend(self.__actions)
        return copy

    def process(self, form, request):
        for actions in self.__actions:
            action, status = actions.process(form, request)
            if status != NOTHING_DONE:
                break
        return action, status

    def __add__(self, actions):
        copy = self.copy()
        copy.extend(actions)
        return copy

    def __iter__(self):
        return itertools.chain(*self.__actions)


# Convience API, decorator to add action

class DecoratedAction(Action):
    """An action created by a decorator.
    """

    def __init__(self, title, callback,
                 identifier=None, description=None, accesskey=None,
                 validator=None, available=None, **htmlAttributes):
        super(DecoratedAction, self).__init__(
            title, identifier, **htmlAttributes)
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
           validator=None, available=None, implements=None,
           factory=DecoratedAction, category='actions', **htmlAttributes):
    def createAction(callback):
        new_action = factory(
            title, callback, identifier, description, accesskey,
            validator, available, **htmlAttributes)
        if implements is not None:
            alsoProvides(new_action, implements)

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
