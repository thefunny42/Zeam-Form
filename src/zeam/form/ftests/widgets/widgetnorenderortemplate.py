"""
We are going to define a custom widget which doesn't provides its own
to render himself:

Let's grok our example:

  >>> from zeam.form.testing import grok
  >>> grok('zeam.form.ftests.widgets.widgetnorenderortemplate')
  Traceback (most recent call last):
    ...
  ConfigurationExecutionError: <class 'martian.error.GrokError'>: Widget <class 'zeam.form.ftests.widgets.widgetnorenderortemplate.MyWidget'> has no associated template or 'render' method.
    in:

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
