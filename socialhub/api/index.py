import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'backend'))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'social_media.settings')

from django.core.wsgi import get_wsgi_application

app = get_wsgi_application()