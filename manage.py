#!/usr/bin/env python
import os
import sys

if __name__ == "__main__":
    # If a 'settings_local' file is present, use it
    try:
        from dpaste.settings import local
        settings_module = "dpaste.settings.local"
    except ImportError:
        settings_module = "dpaste.settings"

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", settings_module)
    from django.core.management import execute_from_command_line
    execute_from_command_line(sys.argv)
