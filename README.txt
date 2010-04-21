==============
zeam.form.base
==============

``zeam.form.base`` is a form framework for Zope related framework. It
goes the same way than ``formlib`` or ``z3c.form``, except it tries:

- to define small components reusable without everything: you don't
  need a full flavored form to render and display only few widgets in
  your application if you just wants this (and not a form),

- to be easily customizable without using hundreds of adapters: most
  of settings are set with properties on your form/fields,

- to prevent ZCML at all, by using Grok to register the few adapters
  needed, who are only widgets and widget value extractors in fact,

- to let people easily change form templates, by using
  ``megrok.pagetemplate`` by default, selecting which fields goes
  where they want,

- to let people define easily their widgets, and use them,

- to be able to create complicated forms, like composed or table
  forms, where each form can modify the data it needs without having
  to hack-o-refresh other sub-forms: *all* actions are executed before
  any widget compute its value to render,

By default it is unware of things like Zope-schema. Generating fields
from a Zope-schema would be done with the help of ``zeam.form.base``.

