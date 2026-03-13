#!/usr/bin/env python
"""
Standalone migration runner for Django on Vercel.
Safely runs migrations with proper error handling.
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_carbonomitter.settings')
django.setup()

from django.core.management import call_command
from django.db import connection

def run_migrations():
    """Run Django migrations safely."""
    print("=" * 70)
    print("🔄 Running Django Database Migrations")
    print("=" * 70)
    
    try:
        # Attempt to run migrations
        call_command('migrate', '--noinput', verbosity=2)
        print("\n✅ Migrations completed successfully!")
        return True
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        return False

if __name__ == '__main__':
    success = run_migrations()
    sys.exit(0 if success else 1)
