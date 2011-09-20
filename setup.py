# Copyright 2003-2009, BlueDynamics Alliance - http://bluedynamics.com
# GNU General Public License Version 2 or later

from setuptools import setup, find_packages
import sys, os

version = '1.0'
shortdesc = 'collective.portlet.cart'
longdesc = ""

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
#          'interlude',
#          'simplejson',
          'Plone',
#          'Products.TextIndexNG3',
#          'Products.izBroschueren',
#          'cornerstone.soup',
#          'cornerstone.browser',
#          'cornerstone.ui.result',
#          'repoze.formapi',
#          'bda.calendar.base',
#          'bda.intellidatetime',
#          'uuid',
          'bda.plone.ajax',
#          'bda.calendar.base',
#          'bda.email',
      ],
      extras_require = dict(
      ),
      entry_points={
      },
      )
