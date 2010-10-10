# -*- coding: utf-8 -*-

import os.path
import re
import zope.component
import zeam.form.base

from grokcore.component import zcml

from zope.app.testing.functional import ZCMLLayer, FunctionalTestSetup
from zope.component.interfaces import IComponentLookup
from zope.configuration.config import ConfigurationMachine
from zope.container.interfaces import ISimpleReadContainer
from zope.container.traversal import ContainerTraversable
from zope.interface import Interface
from zope.site.folder import rootFolder
from zope.site.site import LocalSiteManager, SiteManagerAdapter
from zope.testing import renormalizing
from zope.traversing.interfaces import ITraversable


ftesting_zcml = os.path.join(
    os.path.dirname(zeam.form.base.__file__), 'ftesting.zcml')
FunctionalLayer = ZCMLLayer(
    ftesting_zcml, __name__, 'FunctionalLayer')


def setUp(test):
    # Set up site manager adapter
    zope.component.provideAdapter(
        SiteManagerAdapter, (Interface,), IComponentLookup)

    # Set up traversal
    zope.component.provideAdapter(
        ContainerTraversable, (ISimpleReadContainer,), ITraversable)

    # Set up site
    site = rootFolder()
    site.setSiteManager(LocalSiteManager(site))
    zope.component.hooks.setSite(site)
    FunctionalTestSetup().setUp()


def tearDown(test):
    FunctionalTestSetup().tearDown()


def grok(module_name):
    config = ConfigurationMachine()
    zcml.do_grok(module_name, config)
    config.execute_actions()


checker = renormalizing.RENormalizing([
    # str(Exception) has changed from Python 2.4 to 2.5 (due to
    # Exception now being a new-style class).  This changes the way
    # exceptions appear in traceback printouts.
    (re.compile(r"ConfigurationExecutionError: <class '([\w.]+)'>:"),
                r'ConfigurationExecutionError: \1:')])
