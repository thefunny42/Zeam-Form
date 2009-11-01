"""
We are going to define a simple form with an action.

Let's grok our example:

  >>> from zeam.form.base.testing import grok
  >>> grok('zeam.form.base.ftests.forms.simpleform')

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
                     name="form.action.change-me" value="Change Me" />
           </div>
        </div>
      </form>
    </body>
  </html>


Integration tests
-----------------

Let's try to take a browser and submit that form:

  >>> root = getRootFolder()
  >>> root['content'] = context

  >>> from zope.testbrowser.testing import Browser
  >>> browser = Browser()
  >>> browser.handleErrors = False

  >>> browser.open('http://localhost/content/change')
  >>> action = browser.getControl('Change Me')
  >>> action
  <SubmitControl name='form.action.change-me' type='submit'>

  >>> action.click()

  >>> 'I completely changed everything' in browser.contents
  True

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
