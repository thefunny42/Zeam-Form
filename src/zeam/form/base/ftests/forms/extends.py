"""
Test the extends directive

Let's grok our example:

  >>> from zeam.form.base.testing import grok
  >>> grok('zeam.form.base.ftests.forms.extends')

We can look for the extended form, it will contains fields and action
of the original one:

  >>> from zope.publisher.browser import TestRequest
  >>> request = TestRequest()

  >>> from zeam.form.base.ftests.forms.extends import Context
  >>> context = Context()

  >>> from zope import component
  >>> form = component.getMultiAdapter(
  ...     (context, request), name='othernameform')
  >>> form
  <zeam.form.base.ftests.forms.extends.OtherNameForm object at ...>

  >>> len(form.fields)
  1
  >>> list(form.fields)
  [<Field Name>]

  >>> len(form.actions)
  2
  >>> list(form.actions)
  [<DecoratedAction Register>, <DecoratedAction Kill>]



"""

from zeam.form import base
from grokcore import component as grok

class Context(grok.Context):
    pass


class NameForm(base.Form):

    label = u"Name"
    description = u"Name form"
    fields = base.Fields(base.Field("Name"))
    fields['name'].description = 'Name of the candidate'
    fields['name'].required = True

    @base.action(u"Register")
    def register(self):
        data, errors = self.extractData()
        if errors:
            return
        # In case of success we don't keep request value in the form
        self.ignoreRequest = True
        self.status = u"Registered %(name)s" % data


class OtherNameForm(NameForm):
    base.extends(NameForm)

    @base.action(u"Kill")
    def kill(self):
        data, errors = self.extractData()
        if errors:
            return
        self.status = u"Dead man you are %(name)s" % data
