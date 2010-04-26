import tweepy
from settings import CONSUMER_KEY, CONSUMER_SECRET, OAUTH_CALLBACK

def make_auth(token_key=None, token_secret=None):
    """Creates a tweepy.OAuthHandler based on the consumer keys defined in the
    settings.  If an access token key and secret are given, the auth object
    will have its access token set."""
    auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET, OAUTH_CALLBACK)
    if token_key and token_secret:
        auth.set_access_token(token_key, token_secret)
    return auth

def make_api(token_key=None, token_secret=None):
    """Creates a tweepy.API instance that is authorized with the given access
    token key and secret."""
    auth = None
    if token_key and token_secret:
        auth = make_auth(token_key, token_secret)
    return tweepy.API(auth)
