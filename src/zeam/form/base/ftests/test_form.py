
import unittest
from pkg_resources import resource_listdir
from zope.testing import doctest
from zeam.form.base.testing import FunctionalLayer


def suiteFromPackage(name):
    optionflags = doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS
    globs = {'getRootFolder': FunctionalLayer.getRootFolder}
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
                                    extraglobs=globs,
                                    optionflags=optionflags)
        test.layer = FunctionalLayer
        suite.addTest(test)
    return suite


def test_suite():
    suite = unittest.TestSuite()
    for name in ['forms', 'widgets']:
        suite.addTest(suiteFromPackage(name))
    return suite
