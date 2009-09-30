
from grokcore import view as grok
from megrok import pagetemplate as pt

from zeam.form import form

grok.templatedir('default_templates')


class FormTemplate(pt.PageTemplate):
    pt.view(form.Form)
