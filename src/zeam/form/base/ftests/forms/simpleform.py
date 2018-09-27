"""
We are going to define a simple form with an action.

Let's grok our example:

  >>> from zeam.form.base.testing import grok
  >>> grok('zeam.form.base.ftests.forms.simpleform')

Monkeypatch i18n

  >>> import zope.i18n
  >>> import zope.i18n.config
  >>> old_1, old_2 = zope.i18n.negotiate, zope.i18n.config.ALLOWED_LANGUAGES
  >>> zope.i18n.negotiate = lambda context: 'en'
  >>> zope.i18n.config.ALLOWED_LANGUAGES = ['en']

We can now lookup our form by the name of its class:

  >>> from zope.publisher.browser import TestRequest
  >>> request = TestRequest()

  >>> from zeam.form.base.ftests.forms.simpleform import Context
  >>> context = Context()

  >>> from zope import component
  >>> form = component.getMultiAdapter(
  ...     (context, request), name='change')
  >>> form
  <zeam.form.base.ftests.forms.simpleform.Change object at ...>

  >>> len(form.fields)
  0
  >>> len(form.actions)
  1

And we can render it:

  >>> print form()
  <html>
    <head>
    </head>
    <body>
      <form action="http://127.0.0.1" method="post"
            enctype="multipart/form-data">
        <h1>My form</h1>
        <p>The description of my form</p>
        <div class="actions">
           <div class="action">
              <input type="submit" id="form-action-change-me"
                     name="form.action.change-me" value="Change Me" class="action" />
           </div>
        </div>
      </form>
    </body>
  </html>


Integration tests
-----------------

Let's try to take a browser and submit that form:

  >>> root = getRootFolder()
  >>> root['test_content'] = context

  >>> from zope.testbrowser.wsgi import Browser
  >>> browser = Browser()
  >>> browser.handleErrors = False

  >>> browser.open('http://localhost/test_content/change')
  >>> action = browser.getControl('Change Me')
  >>> action
  <SubmitControl name='form.action.change-me' type='submit'>

  >>> action.click()

  >>> 'I completely changed everything' in browser.contents
  True

  >>> zope.i18n.negotiate, zope.i18n.config.ALLOWED_LANGUAGES = old_1, old_2
"""

from zeam.form import base
from grokcore import component as grok


class Context(grok.Context):
    pass


class ChangeAction(base.Action):

    def __call__(self, submission):
        submission.status = u"I completely changed everything"


class Change(base.Form):

    label = u"My form"
    description = u"The description of my form"
    actions = base.Actions(ChangeAction("Change Me"))
