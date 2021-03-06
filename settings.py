import os, sys

PROJECT_ROOT = os.path.realpath(os.path.dirname(__file__))

# See if we're running in production or in development
PRODUCTION = 'Development' not in os.environ.get('SERVER_SOFTWARE', '')
DEBUG = not PRODUCTION

# Set the OAuth callback URL dynamically, based on the current host name. This
# works in development or production.
OAUTH_CALLBACK = 'http://%s/oauth/callback' % \
    os.environ.get('HTTP_HOST', 'localhost')

# How many tweets to fetch at once
BATCH_SIZE = 100

# How many items of interest to display in each list on the front page
ARCHIVE_LIST_SIZE = 10

TEMPLATE_DIR = os.path.join(PROJECT_ROOT, 'templates')


##############################################################################
# Secrets -- These settings MUST be set in secrets.py, which should not be
# kept in version control.  They should be kept, uh, secret.
##############################################################################

# Twitter API consumer credentials.
CONSUMER_KEY = None
CONSUMER_SECRET = None

# Used to sign cookies.
COOKIE_SECRET = None

# Import the above secret settings from a separate (hopefully private) module.
try:
    from secrets import *
except ImportError:
    raise RuntimeError('Could not import secret settings')


##############################################################################
# Tornado application config
##############################################################################
APP_CONFIG = {
    'cookie_secret': COOKIE_SECRET, # Enables secure cookies
}
