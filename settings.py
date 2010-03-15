# Secrets -- These settings MUST be set in secrets.py, which should not be
# kept in version control.  They should be kept, uh, secret.

# Twitter API consumer credentials.
CONSUMER_KEY = None
CONSUMER_SECRET = None

# Used to sign cookies.
COOKIE_SECRET = None

try:
    from secrets import *
except ImportError:
    raise RuntimeError('Could not import secret settings')
