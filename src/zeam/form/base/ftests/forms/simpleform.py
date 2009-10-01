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
  ...     (context, request), name='myform')
  >>> form
  <zeam.form.base.ftests.forms.simpleform.MyForm object at ...>

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
            <input type="submit" id="form-change-me"
                   name="form.change-me" value="Change Me" />
        </div>
      </form>
    </body>
  </html>

Let's try to take a browser and submit that form:

  >>> root = getRootFolder()
  >>> root['content'] = context

  >>> from zope.testbrowser.testing import Browser
  >>> browser = Browser()
  >>> browser.handleErrors = False
  >>> browser.open('http://localhost/content/myform')
  >>> action = browser.getControl('Change Me')
  >>> action
  <SubmitControl name='form.change-me' type='submit'>

  >>> action.click()
  >>> print browser.contents
  <html>
    <head>
    </head>
    <body>
      <form action="http://localhost/content/myform" method="post"
            enctype="multipart/form-data">
        <p class="status-message">Changed</p>
        <h1>My form</h1>
        <p>The description of my form</p>
        <div class="actions">
            <input type="submit" id="form-change-me"
                   name="form.change-me" value="Change Me" />
        </div>
      </form>
    </body>
  </html>

"""

from zeam.form.base.actions import action
from zeam.form.base.form import Form

from grokcore import component as grok

class Context(grok.Context):
    pass


class MyForm(Form):

    label = u"My form"
    description = u"The description of my form"

    @action(u"Change Me")
    def changeMe(self):
        self.status = u"Changed"
