"""
We are going to define a custom widget here which define its rendering
HTML using a render method.

Let's grok our example:

  >>> from zeam.form.testing import grok
  >>> grok('zeam.form.ftests.widgets.widgetrender')

So now should be to lookup our widget:

  >>> from zeam.form.ftests.widgets.widgetrender import MyField
  >>> field = MyField("Cool Test")
  >>> field
  <MyField Cool Test>

  >>> from zope.publisher.browser import TestRequest
  >>> request = TestRequest()

  >>> from zeam.form.form import Form
  >>> form = Form(None, request)

  >>> from zeam.form import interfaces
  >>> from zope import component
  >>> widget = component.getMultiAdapter(
  ...     (field, form, request), interfaces.IWidget)
  >>> widget
  <MyWidget Cool Test>

And we are able now to call its render method:

  >>> print widget.render()
  <p>Too complicated widget for Cool Test</p>

"""

from zeam.form.fields import Field
from zeam.form.widgets import Widget
from zeam.form import interfaces

from zope.interface import Interface

from grokcore import component as grok


class MyField(Field):
    """A custom field.
    """


class MyWidget(Widget):
    """Custom widget to render my field
    """
    grok.adapts(MyField, interfaces.IFormCanvas, Interface)


    def render(self):
        return u"<p>Too complicated widget for %s</p>" % (
            self.component.title)
