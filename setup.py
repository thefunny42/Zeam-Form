from setuptools import setup, find_packages
import os

version = '1.1'

tests_require = [
    'zope.app.authentication',
    'zope.app.testing',
    'zope.app.zcmlfiles',
    'zope.configuration',
    'zope.securitypolicy',
    'zope.testbrowser',
    ]

setup(name='zeam.form.base',
      version=version,
      description="Grok based form framework",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='grok form framework',
      author='Sylvain Viollon',
      author_email='thefunny@gmail.com',
      url='http://pypi.python.org/pypi/zeam.form.base',
      license='BSD',
      package_dir={'': 'src'},
      packages=find_packages('src'),
      namespace_packages=['zeam', 'zeam.form'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'grokcore.component',
          'grokcore.security',
          'grokcore.view >= 2.2',
          'martian',
          'megrok.chameleon',
          'megrok.pagetemplate >= 0.7',
          'setuptools',
          'zope.component',
          'zope.i18n',
          'zope.interface',
          'zope.pagetemplate',
          'zope.publisher',
          'zope.testing',
          ],
      tests_require = tests_require,
      extras_require = {'test': tests_require},
      )
