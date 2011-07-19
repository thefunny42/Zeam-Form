"""
We define here a simple form with two fields and one action registered
with a decorator.

Let's grok our example:

  >>> from zeam.form.base.testing import grok
  >>> grok('zeam.form.base.ftests.forms.inputform')

We can now lookup our form by the name of its class:

  >>> from zope.publisher.browser import TestRequest
  >>> request = TestRequest()

  >>> from zeam.form.base.ftests.forms.inputform import Context
  >>> context = Context()

  >>> from zope import component
  >>> form = component.getMultiAdapter(
  ...     (context, request), name='registration')
  >>> form
  <zeam.form.base.ftests.forms.inputform.Registration object at ...>

  >>> len(form.fields)
  2
  >>> len(form.actions)
  1

Integration tests
-----------------

  >>> root = getRootFolder()
  >>> root['content'] = context

  >>> from zope.app.wsgi.testlayer import Browser
  >>> browser = Browser()
  >>> browser.handleErrors = False

Empty submission
~~~~~~~~~~~~~~~~

We are going just to submit the form without giving any required
information, and we should get an error:

  >>> browser.open('http://localhost/content/registration')
  >>> action = browser.getControl('Register')
  >>> action
  <SubmitControl name='form.action.register' type='submit'>

  >>> action.click()

  >>> 'Missing required value' in browser.contents
  True
  >>> 'Registered' in browser.contents
  False

Valid submission
~~~~~~~~~~~~~~~~

Let's get our control for fields and filled them, and submit the form:

  >>> browser.open('http://localhost/content/registration')
  >>> name = browser.getControl('Name')
  >>> name
  <Control name='form.field.name' type='text'>
  >>> name.value = 'Sylvain Viollon'
  >>> job = browser.getControl('Job')
  >>> job
  <Control name='form.field.job' type='text'>
  >>> job.value = 'Developer'

  >>> browser.getControl('Register').click()

  >>> 'Registered Sylvain Viollon as Developer' in browser.contents
  True

Our action says that you can ignore the request if it succeed (and it
is the case here):

  >>> browser.getControl('Name').value
  ''
  >>> browser.getControl('Job').value
  ''

Incomplete submission
~~~~~~~~~~~~~~~~~~~~~

In case of an incomplete submission, fields should keep the value they
got for that submission:

  >>> browser.open('http://localhost/content/registration')
  >>> job = browser.getControl('Job')
  >>> job
  <Control name='form.field.job' type='text'>
  >>> job.value = 'Designer'

  >>> browser.getControl('Register').click()

  >>> 'Missing required value' in browser.contents
  True
  >>> 'Registered' in browser.contents
  False

  >>> new_job = browser.getControl('Job')
  >>> new_job.value
  'Designer'

And so now we can finish to submit the form, and form values should be
gone (as we successfully submit the form):

  >>> browser.getControl('Name').value = 'Wim Boucqueart'
  >>> browser.getControl('Register').click()

  >>> 'Missing required value' in browser.contents
  False
  >>> 'Registered Wim Boucqueart as Designer' in browser.contents
  True

  >>> browser.getControl('Name').value
  ''
  >>> browser.getControl('Job').value
  ''


"""


from zeam.form import base
from grokcore import component as grok

class Context(grok.Context):
    pass


class Registration(base.Form):

    label = u"My form"
    description = u"The description of my form"
    fields = base.Fields(base.Field("Name"), base.Field("Job"))
    fields['name'].description = 'Name of the candidate'
    fields['name'].required = True

    @base.action(u"Register")
    def register(self):
        data, errors = self.extractData()
        if errors:
            return
        # In case of success we don't keep request value in the form
        self.ignoreRequest = True
        self.status = u"Registered %(name)s as %(job)s" % data
