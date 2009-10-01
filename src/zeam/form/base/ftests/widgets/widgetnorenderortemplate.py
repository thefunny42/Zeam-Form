"""
We are going to define a custom widget which doesn't provides its own
to render himself:

Let's grok our example:

  >>> from zeam.form.base.testing import grok
  >>> grok('zeam.form.base.ftests.widgets.widgetnorenderortemplate')
  Traceback (most recent call last):
    ...
  ConfigurationExecutionError: <class 'martian.error.GrokError'>: Widget <class 'zeam.form.base.ftests.widgets.widgetnorenderortemplate.MyWidget'> has no associated template or 'render' method.
    in:

"""

from zeam.form.base.fields import Field
from zeam.form.base.widgets import Widget
from zeam.form.base import interfaces

from zope.interface import Interface

from grokcore import component as grok


class MyField(Field):
    """A custom field.
    """


class MyWidget(Widget):
    """Custom widget to render my field
    """
    grok.adapts(MyField, interfaces.IFormCanvas, Interface)
