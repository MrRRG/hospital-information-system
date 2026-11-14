import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

application = get_wsgi_application()

# On Vercel the database starts empty, so create the tables and the demo data on cold start.
if os.environ.get('VERCEL'):
    from django.core.management import call_command

    call_command('migrate', interactive=False, verbosity=0)
    if os.environ.get('SEED_DEMO', '1') == '1':
        call_command('seed_all', verbosity=0)

app = application  # name that Vercel looks for
