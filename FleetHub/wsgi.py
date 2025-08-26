import os
from django.core.wsgi import get_wsgi_application

# Cambiar esta línea:
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'FleetHub.settings.development')
# En lugar de: 'fleethub.settings'

application = get_wsgi_application()