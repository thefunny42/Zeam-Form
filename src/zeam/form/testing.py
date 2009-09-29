
import os.path

import zeam.form

from zope.app.testing.functional import ZCMLLayer, FunctionalTestSetup

ftesting_zcml = os.path.join(
    os.path.dirname(zeam.form.__file__), 'ftesting.zcml')
FunctionalLayer = ZCMLLayer(
    ftesting_zcml, __name__, 'FunctionalLayer', allow_teardown=True)

def setUp(test):
    FunctionalTestSetup().setUp()

def tearDown(test):
    FunctionalTestSetup().tearDown()
