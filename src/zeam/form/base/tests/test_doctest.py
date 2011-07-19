
import unittest

from zope.testing import doctest
from zeam.form.base.testing import FunctionalLayer

def test_suite():
    optionflags = doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS
    globs= {}

    suite = unittest.TestSuite()
    for filename in ['components.txt', 'actions.txt', 'fields.txt',
                     'forms.txt', 'widgets.txt']:
        test = doctest.DocFileSuite(
            filename,
            optionflags=optionflags,
            globs=globs)
        test.layer = FunctionalLayer
        suite.addTest(test)

    return suite
