#!/usr/bin/env python
from setuptools import setup, find_packages

setup(name='pastebin',
      version='0.1',
      packages=find_packages(),
      package_data={'pastebin': ['bin/*.*', 'static/*.*', 'templates/*.*']},
      exclude_package_data={'pastebin': ['bin/*.pyc']},
      scripts=['pastebin/bin/manage.py'])
