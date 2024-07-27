#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
from environs import Env


def main():
    """Run administrative tasks."""
    env = Env()
    env.read_env()
    os.environ.setdefault('DJANGO_SECRET_KEY', env('DJANGO_SECRET_KEY'))
    os.environ.setdefault('DJANGO_DEBUG', env.bool('DJANGO_DEBUG'))
    os.environ.setdefault('BOT_TOKEN', env('BOT_TOKEN'))
    os.environ.setdefault('PAYMENT_PROVIDER_TOKEN', env('PAYMENT_PROVIDER_TOKEN'))
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
