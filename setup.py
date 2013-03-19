#!/usr/bin/env python
from setuptools import setup, find_packages

setup(name='dpaste',
      version='1.0',
      packages=find_packages(),
      package_data={'dpaste': ['static/*.*', 'templates/*.*']},
      scripts=['manage.py'])
