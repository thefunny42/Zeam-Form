
from grokcore import view as grok
from megrok import pagetemplate as pt

from zeam.form.base import form

grok.templatedir('default_templates')


class FormCanvasTemplate(pt.PageTemplate):
    pt.view(form.FormCanvas)


class FormTemplate(pt.PageTemplate):
    pt.view(form.Form)
