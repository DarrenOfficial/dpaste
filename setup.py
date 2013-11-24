#!/usr/bin/env python
from setuptools import setup, find_packages

setup(
    name='dpaste',
    version='1.2',
    packages=find_packages(),
    package_data={'dpaste': ['static/*.*', 'templates/*.*']},
    scripts=('manage.py',),
    install_requires=(
        'django-mptt>=0.6.0',
        'pygments>=1.6',
        'requests>=2.0.0',
    ),
)
