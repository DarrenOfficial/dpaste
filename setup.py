#!/usr/bin/env python
from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand
from sys import exit

class Tox(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        #import here, cause outside the eggs aren't loaded
        import tox
        errno = tox.cmdline(self.test_args)
        exit(errno)

long_description = u'\n\n'.join((
    open('README.rst').read(),
    open('CHANGELOG').read()
))

setup(
    name='dpaste',
    version='2.5',
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
        'Programming Language :: Python',
        'Framework :: Django',
    ],
    packages=find_packages(),
    package_data={
        'dpaste': ['static/*.*', 'templates/*.*'],
        'docs': ['*'],
    },
    include_package_data=True,
    install_requires=[
        'django>=1.4',
        'django-mptt>=0.6.0',
        'pygments>=1.6',
        'requests>=2.0.0',
    ],
    tests_require=[
        'tox>=1.6.1'
    ],
    cmdclass={
        'test': Tox
    },
)
