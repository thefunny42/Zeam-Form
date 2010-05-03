==============
zeam.form.base
==============

Summary
-------

``zeam.form.base`` is a form framework for Zope related web
framework. It goes the same way than ``formlib`` or ``z3c.form``,
except it tries:

- to define small components reusable without everything: you don't
  need a full flavored form to render and display only few widgets in
  your application,

- to be easily customizable without using hundreds of adapters: most
  of settings are set with properties on your form/fields,

- to prevent ZCML at all, by using Grok to register the few adapters
  needed, who are only widgets and widget value extractors in fact,

- to always keep the context untouched: the form work on a content
  that can be something else than the context, it can even be a
  dictionnary. That means everywhere in the form, including in
  widgets, and actions, you can either access the context as the real
  context of the form, and have a way to access the content that the
  form is working on. This help greatly if you have complicated
  widgets working, including when they are embbed in other widgets
  (like in a list or a table),

- to let people easily change form templates, by using
  ``megrok.pagetemplate`` by default, selecting which fields goes
  where they want,

- to let people define easily their widgets, and use them,

- to be able to create complicated forms, like composed or table
  forms, where each form can modify the data it needs without having
  to hack-o-refresh other sub-forms: *all* actions are executed before
  any widget compute its value to render,

By default it is unware of things like Zope-schema. Generating fields
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
