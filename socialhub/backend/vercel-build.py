import os
import sys
from django.core.management import execute_from_command_line

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'social_media.settings')

execute_from_command_line(['manage.py', 'collectstatic', '--noinput'])
