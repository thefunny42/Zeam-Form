import martian
import grokcore.view
import grokcore.component
import grokcore.security

from grokcore.security.util import protect_getattr

from zeam.form.widgets import Widget
from zeam.form.form import Form, FormCanvas
from zope.publisher.interfaces.browser import IBrowserPage
from zope.publisher.interfaces.browser import IDefaultBrowserLayer


class WidgetTemplateGrokker(martian.ClassGrokker):
    martian.component(Widget)

    def grok(self, name, factory, module_info, **kw):
        # Need to store the module info object on the view class so that it
        # can look up the 'static' resource directory.
        factory.module_info = module_info
        return super(WidgetTemplateGrokker, self).grok(
            name, factory, module_info, **kw)

    def execute(self, factory, config):
        templates = factory.module_info.getAnnotation('grok.templates', None)
        if templates is not None:
            config.action(
                discriminator=None,
                callable=self.checkTemplates,
                args=(templates, factory.module_info, factory))
            return True
        return False

    def checkTemplates(self, templates, module_info, factory):
        def has_render(factory):
            return factory.render != Widget.render
        def has_no_render(factory):
            return not has_render(factory)
        templates.checkTemplates(
            module_info, factory, 'widget', has_render, has_no_render)


class TemplateGrokker(martian.ClassGrokker):
    martian.component(FormCanvas)

    def grok(self, name, factory, module_info, **kw):
        # Need to store the module info object on the view class so that it
        # can look up the 'static' resource directory.
        factory.module_info = module_iself).grok(name, factory,
                                                 module_info, **kw)

   def execute(self, factory, config, **kw):
        # find templates
        templates = factory.module_info.getAnnotation('grok.templates', None)
        if templates is not None:
            config.action(
                discriminator=None,
                callable=self.checkTemplates,
                args=(templates, factory.module_info, factory)
                )

    def checkTemplates(self, templates, module_info, factory):

        def has_render(factory):
            render = getattr(factory, 'render', None)
            base_method = getattr(render, 'base_method', False)
            return render and not base_method

        def has_no_render(factory):
            return not has_render(factory)
        
        templates.checkTemplates(module_info, factory, 'view',
                                 has_render, has_no_render)
    

class FormGrokker(grokcore.view.meta.views.ViewGrokker):
    martian.component(Form)
    martian.directive(grokcore.component.context)
    martian.directive(grokcore.view.layer, default = IDefaultBrowserLayer)
    martian.directive(grokcore.component.name,
                      get_default = grokcore.view.meta.views.default_view_name)

    def execute(self, factory, config, context, layer, name, **kw):
        methods = util.methods_from_class(factory)
        for method in methods:
            if grokcore.security.require.bind().get(method) is not None:
                raise GrokError('The @grok.require decorator is used for '
                                'method %r in view %r. It may only be used '
                                'for XML-RPC methods.'
                                % (method.__name__, factory), factory)

        # __view_name__ is needed to support IAbsoluteURL on views
        factory.__view_name__ = name
        adapts = (context, layer)

        config.action(
            discriminator=('adapter', adapts, interface.Interface, name),
            callable=component.provideAdapter,
            args=(factory, adapts, interface.Interface, name),
            )
        return True


class FormSecurityGrokker(martian.ClassGrokker):
    martian.component(FormCanvas)
    martian.directive(grokcore.security.require, name='permission')

    def execute(self, factory, config, permission, **kw):
        # XXX use something else than IBrowserPage ? (trollfot)
        for method_name in IBrowserPage:
            config.action(
                discriminator=('protectName', factory, method_name),
                callable=protect_getattr,
                args=(factory, method_name, permission),
                )
        return True
