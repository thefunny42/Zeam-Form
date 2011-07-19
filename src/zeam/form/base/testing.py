# -*- coding: utf-8 -*-

from grokcore.component import zcml
from zope.app.wsgi.testlayer import BrowserLayer
from zope.configuration.config import ConfigurationMachine
import zeam.form.base


FunctionalLayer = BrowserLayer(zeam.form.base)

def grok(module_name):
    config = ConfigurationMachine()
    zcml.do_grok(module_name, config)
    config.execute_actions()
