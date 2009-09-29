
from zeam.form.widgets import Widget

import martian


class WidgetTemplateGrokker(martian.ClassGrokker):
    martian.component(Widget)

    def grok(self, name, factory, module_info, **kw):
        # Need to store the module info object on the view class so that it
        # can look up the 'static' resource directory.
        factory.module_info = module_info
        return super(ViewletGrokker, self).grok(
            name, factory, module_info, **kw)

    def execute(self, factory, config):
        templates = factory.module_info.getAnnotation('grok.templates', None)
        if templates is not None:
            config.action(
                discriminator=None,
                callable=self.checkTemplates,
                args=(templates, factory.module_info, factory))

    def checkTemplates(self, templates, module_info, factory):
        def has_render(factory):
            return factory.render != Widget.render
        def has_no_render(factory):
            return not has_render(factory)
        templates.checkTemplates(
            module_info, factory, 'widget', has_render, has_no_render)
