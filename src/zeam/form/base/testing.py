
import os.path
import re

import zeam.form.base

from zope.testing import renormalizing
from zope.app.testing.functional import ZCMLLayer, FunctionalTestSetup
from zope.configuration.config import ConfigurationMachine
from grokcore.component import zcml

ftesting_zcml = os.path.join(
    os.path.dirname(zeam.form.base.__file__), 'ftesting.zcml')
FunctionalLayer = ZCMLLayer(
    ftesting_zcml, __name__, 'FunctionalLayer')

def setUp(test):
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
                r'ConfigurationExecutionError: \1:'),
    ])
