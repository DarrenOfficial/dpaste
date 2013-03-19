#!/usr/bin/env python
from setuptools import setup, find_packages

setup(name='dpaste',
      version='0.1',
      packages=find_packages(),
      package_data={'dpaste': ['bin/*.*', 'static/*.*', 'templates/*.*']},
      exclude_package_data={'dpaste': ['bin/*.pyc']},
      scripts=['dpaste/bin/manage.py'])
