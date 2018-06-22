#!/usr/bin/env python

from setuptools import find_packages, setup

long_description = '\n\n'.join((
    open('README.rst').read(),
    open('CHANGELOG.rst').read()
))

setup(
    name='dpaste',
    version='3.0',
    description='dpaste is a Django based pastebin. It\'s intended to run '
                'separately but its also possible to be installed into an '
                'existing Django project like a regular app.',
    long_description=long_description,
    author='Martin Mahner',
    author_email='martin@mahner.org',
    url='https://github.com/bartTC/dpaste/',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Framework :: Django',
    ],
    python_requires='>=3.4',
    packages=find_packages(),
    package_data={
        'dpaste': ['static/*.*', 'templates/*.*'],
        'docs': ['*'],
    },
    include_package_data=True,
    install_requires=[
        # Essential packages
        'django>=1.11',
        'pygments>=1.6',
        'django-staticinline>=1.0',

        # Additional Code Lexer
        'pygments-lexer-solidity>=0.1.0',

        # Additional Text Lexer
        'misaka>=2.1.0',
        'docutils',

        # Testsuite
        'tox',
        'coverage',
    ],
    extras_require={
        # Packages required for a standalone setup
        # (not integrated into an existing setup and settings)
        'standalone': [
            'django-csp>=3.3',
        ],
        # Useful tools for local development
        'local-development': [
            'django-csp>=3.3',
            'django-sslserver',
            'sphinx',
            'sphinx-autobuild',
            'sphinx-rtd-theme',
            'sphinxcontrib-httpdomain',
        ]
    }
)

