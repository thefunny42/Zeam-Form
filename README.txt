==============
zeam.form.base
==============

Summary
-------

``zeam.form.base`` is a form framework for Zope. It has common goals and purposes with ``formlib`` or ``z3c.form`` but tries to:

- define small sane and reusable components : you don't
  need a full flavored form to render and display only few widgets in
  your application,

- be easily customizable without using hundreds of adapters: most
  of settings are set with properties on your form/fields,

- prevent ZCML declarations by using Grok to register the few needed
  adapters (widgets and widgets value extractors),

- always keep the context untouched: the form works on a content
  that can be something else than the context, it can even be a
  dictionnary. That means everywhere in the form, including in
  widgets, and actions, you can either access the context as the real
  context of the form, and have a way to access the content that the
  form is working on. This helps greatly if you have complicated
  widgets working, including when they are embedded in other widgets
  (like in a list or a table),

- let people easily change form templates, by using
  ``megrok.pagetemplate`` by default, selecting which fields goes
  where they want,

- let people define easily their widgets, and use them,

- be able to create complex forms, like composed or table
  forms, where each form can modify the data it needs without having
  to hack-o-refresh other sub-forms: *all* actions are executed before
  any widget compute its value to render,

By default, it is unware of things like Zope-schema. Generating fields
from a Zope-schema would be done with the help of ``zeam.form.ztk``.

It work with Python 2.4, 2.5 and 2.6 (tested in Zope 2.10, 2.12 and
Grok 1.0, 1.1).


Example
-------

Let's define a short example. Actions can be defined standalone::

  from zeam.form.base import Action

  class MailAction(Action):

     def available(self, form):
         return form.context.haveMailHost()



For more information
--------------------

You can refer to the functional and doctest included in the
package. Since it tries to be composed of small components, there is
many way to put them together.
