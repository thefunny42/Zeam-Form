# -*- coding: utf-8 -*-

import martian
import grokcore.view
import grokcore.component
import grokcore.security

from grokcore.security.util import protect_getattr
from grokcore.view.meta.views import TemplateGrokker

from zeam.form.base.widgets import Widget
from zeam.form.base.form import StandaloneForm, GrokViewSupport

from zope import interface, component
from zope.publisher.interfaces.browser import IBrowserPage
from zope.publisher.interfaces.browser import IDefaultBrowserLayer


class WidgetTemplateGrokker(TemplateGrokker):
    martian.component(Widget)

    def has_render(self, factory):
        return factory.render != Widget.render

    def has_no_render(self, factory):
        return not self.has_render(factory)


class FormTemplateGrokker(TemplateGrokker):
    martian.component(GrokViewSupport)

    def has_render(self, factory):
        return factory.render != GrokViewSupport.render

    def has_no_render(self, factory):
        return False


class FormGrokker(grokcore.view.meta.views.ViewGrokker):
    martian.component(StandaloneForm)
    martian.directive(grokcore.component.context)
    martian.directive(grokcore.view.layer, default=IDefaultBrowserLayer)
    martian.directive(grokcore.component.name,
                      get_default=grokcore.view.meta.views.default_view_name)

    def execute(self, factory, config, context, layer, name, **kw):
        # __view_name__ is needed to support IAbsoluteURL on views
        factory.__view_name__ = name
        adapts = (context, layer)

        config.action(
            discriminator=('adapter', adapts, interface.Interface, name),
            callable=component.provideAdapter,
            args=(factory, adapts, interface.Interface, name))
        return True


class FormSecurityGrokker(martian.ClassGrokker):
    martian.component(StandaloneForm)
    martian.directive(grokcore.security.require, name='permission')

    def execute(self, factory, config, permission, **kw):
        # XXX use something else than IBrowserPage ? (trollfot)
        for method_name in IBrowserPage:
            config.action(
                discriminator=('protectName', factory, method_name),
                callable=protect_getattr,
                args=(factory, method_name, permission))
        return True
