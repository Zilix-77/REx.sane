"""
WSGI config for REx.sane project.
"""

import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rexsane.settings')
application = get_wsgi_application()
