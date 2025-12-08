"""
Django management command to check application health
Usage: python manage.py check_health
"""
from django.core.management.base import BaseCommand
from django.core.management import execute_from_command_line
from django.test.client import Client
from django.db import connections
import sys
import os


class Command(BaseCommand):
    help = 'Check application health for Railway deployment'

    def add_arguments(self, parser):
        parser.add_argument(
            '--detailed',
            action='store_true',
            help='Run detailed health checks including database',
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('🏥 Running Rejlers EDRS Health Check...')
        )
        
        # Check Django setup
        try:
            from django.conf import settings
            self.stdout.write(
                self.style.SUCCESS(f'✅ Django settings loaded: {settings.SETTINGS_MODULE}')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Django settings error: {e}')
            )
            return

        # Check health endpoint
        try:
            client = Client()
            response = client.get('/api/v1/health/')
            if response.status_code == 200:
                self.stdout.write(
                    self.style.SUCCESS(f'✅ Health endpoint responding: {response.status_code}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'⚠️ Health endpoint status: {response.status_code}')
                )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Health endpoint error: {e}')
            )

        # Detailed checks
        if options['detailed']:
            # Database check
            try:
                db_conn = connections['default']
                db_conn.cursor()
                self.stdout.write(
                    self.style.SUCCESS('✅ Database connection successful')
                )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'❌ Database connection failed: {e}')
                )

            # Environment variables check
            required_vars = ['SECRET_KEY', 'DATABASE_URL']
            for var in required_vars:
                if os.environ.get(var):
                    self.stdout.write(
                        self.style.SUCCESS(f'✅ {var} is set')
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING(f'⚠️ {var} not found in environment')
                    )

        self.stdout.write(
            self.style.SUCCESS('🎯 Health check completed!')
        )