"""
WSGI config for django_carbonomitter project.

It exposes the WSGI callable as a module-level variable named ``application``.

"""

import os
import sys

from django.core.wsgi import get_wsgi_application
from django.core.management import call_command

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_carbonomitter.settings')

# Run migrations on first startup (safety fallback)
if 'vercel' in sys.argv or os.environ.get('VERCEL'):
    try:
        print("Running Django migrations on startup...")
        call_command('migrate', '--noinput', verbosity=1)
        print("Migrations completed successfully!")
    except Exception as e:
        print(f"Migration error (non-blocking): {e}")

application = get_wsgi_application()
