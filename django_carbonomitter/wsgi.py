"""
WSGI config for django_carbonomitter project.

It exposes the WSGI callable as a module-level variable named ``application``.

"""

import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_carbonomitter.settings')

# Initialize Django first
django.setup()

from django.core.wsgi import get_wsgi_application
from django.core.management import call_command
from django.db import connection
from django.core.exceptions import ImproperlyConfigured

# Run migrations on Vercel startup
try:
    # Check if we're on Vercel (production environment)
    if os.environ.get('VERCEL') or os.environ.get('VERCEL_ENV'):
        print("🚀 Vercel environment detected - checking database migrations...")
        
        # Try to query auth_user table to see if migrations ran
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1 FROM auth_user LIMIT 1")
            print("✅ Database tables already exist")
        except Exception as db_check_error:
            print(f"⚠️  Database tables missing: {db_check_error}")
            print("🔄 Running migrations...")
            try:
                call_command('migrate', '--noinput', verbosity=2)
                print("✅ Migrations completed successfully!")
            except Exception as migrate_error:
                print(f"❌ Migration failed: {migrate_error}")
                # Don't crash - let the app start and handle errors gracefully
except Exception as startup_error:
    print(f"⚠️  Startup warning (non-blocking): {startup_error}")

application = get_wsgi_application()
