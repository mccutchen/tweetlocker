
# Twitter API info
CONSUMER_KEY = None
CONSUMER_SECRET = None
REQUEST_TOKEN_URL = 'http://twitter.com/oauth/request_token'
ACCESS_TOKEN_URL = 'http://twitter.com/oauth/access_token'
AUTH_URL = 'http://twitter.com/oauth/authorize'

# Secret key for signing cookies
COOKIE_SECRET = None

try:
	from secrets import *
except ImportError:
	raise RuntimeError('Could not import secret settings')
