import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'imlo.settings')
os.environ.setdefault('SITE_URL', 'https://ibroo.uz')
os.environ.setdefault('DEBUG', 'False')
os.environ.setdefault('ALLOWED_HOSTS', 'ibroo.uz,www.ibroo.uz')

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
