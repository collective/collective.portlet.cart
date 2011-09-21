from setuptools import setup, find_packages
import sys, os

version = '0.9'
shortdesc = 'collective.portlet.cart'
longdesc = open(os.path.join(os.path.dirname(__file__), 'README.rst')).read()

setup(name='collective.portlet.cart',
      version=version,
      description=shortdesc,
      long_description=longdesc,
      classifiers=[],
      keywords='',
      author='BlueDynamics Alliance',
      author_email='dev@bluedynamics.com',
      url=u'https://bluedynamics.com',
      license='GNU General Public Licence',
      packages=find_packages('src'),
      package_dir = {'': 'src'},
      namespace_packages=['collective',],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'interlude',
          'simplejson',
          'Plone',
          'bda.plone.ajax',
      ],
      extras_require = dict(
      ),
      entry_points={
      },
      )