#!/usr/bin/env python


import sys

from django import setup
from django.conf import settings
from django.test.runner import DiscoverRunner as TestRunner

from dpaste.settings import tests as test_settings


def runtests(*test_args):
    # Setup settings
    if not settings.configured:
        settings.configure(**test_settings.__dict__)
    setup()
    test_runner = TestRunner(verbosity=1)
    failures = test_runner.run_tests(['dpaste'])
    if failures:
        sys.exit(failures)

if __name__ == '__main__':
    runtests(*sys.argv[1:])
