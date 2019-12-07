#!/usr/bin/env python

"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    try:
        import dpaste.settings.local

        settings = "dpaste.settings.local"
        sys.stdout.write("\n🧁  Using local.py settings file.\n\n")
    except ImportError:
        settings = "dpaste.settings.base"
        sys.stdout.write(
            "\n⚠️  local.py settings not found. Using default settings file.\n\n"
        )

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", settings)

    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
