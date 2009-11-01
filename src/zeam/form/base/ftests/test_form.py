
import unittest
from pkg_resources import resource_listdir
from zope.testing import doctest
from zope.app.testing.functional import getRootFolder
from zeam.form.base.testing import FunctionalLayer, setUp, tearDown, checker


def suiteFromPackage(name):
    optionflags = doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS
    globs = {'getRootFolder': getRootFolder}
    files = resource_listdir(__name__, name)
    suite = unittest.TestSuite()
    for filename in files:
        if not filename.endswith('.py'):
            continue
        if filename.endswith('_fixture.py'):
            continue
        if filename == '__init__.py':
            continue

        dottedname = 'zeam.form.base.ftests.%s.%s' % (name, filename[:-3])
        test = doctest.DocTestSuite(dottedname,
                                    setUp=setUp,
                                    tearDown=tearDown,
                                    extraglobs=globs,
                                    checker=checker,
                                    optionflags=optionflags)
        test.layer = FunctionalLayer
        suite.addTest(test)
    return suite


def test_suite():
    suite = unittest.TestSuite()
    for name in ['forms', 'widgets']:
        suite.addTest(suiteFromPackage(name))
    return suite
