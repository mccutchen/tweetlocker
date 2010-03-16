import os, sys

# See if we're running in production or in development
PRODUCTION = 'Development' not in os.environ.get('SERVER_SOFTWARE', '')

# Set the OAuth callback URL dynamically, based on the current host name. This
# works in development or production.
OAUTH_CALLBACK = 'http://%s/oauth/callback' % os.environ['HTTP_HOST']

# How many tweets to fetch at once
BATCH_SIZE = 50


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
