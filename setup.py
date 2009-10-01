from setuptools import setup, find_packages
import os

version = '1.0'

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
      url='',
      license='BSD',
      package_dir={'': 'src'},
      packages=find_packages('src'),
      namespace_packages=['zeam', ],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'zope.interface',
          'zope.component',
          'zope.schema',
          'martian',
          'grokcore.component',
          'grokcore.view',
          'megrok.pagetemplate',
          # Test
          'zope.securitypolicy',
          'zope.app.authentication',
          'zope.app.testing',
          'zope.app.zcmlfiles',
          'zope.testing',
          'zope.testbrowser',
          ],
      )
