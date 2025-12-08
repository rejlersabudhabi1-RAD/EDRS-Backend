"""
WSGI config for rejlers_api project - MINIMAL VERSION
"""
import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rejlers_api.minimal_settings')
application = get_wsgi_application()