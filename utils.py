import tweepy
from google.appengine.ext import db, deferred

from settings import CONSUMER_KEY, CONSUMER_SECRET, OAUTH_CALLBACK
from models import User, Tweet, Place

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

def make_tweet(user, tweetobj, commit=True):
    """Creates a Tweet entity for the given tweepy API tweet object.  If
    commit is False, the new Tweet is never put to the datastore and any
    post-processing tasks are NOT fired off."""
    tweet = Tweet(parent=user, key_name=str(tweetobj.id))

    # Copy over fields that are a 1-to-1 match
    exclude = set(('coordinates', 'place'))
    fields = set(Tweet.properties) - exclude
    for field in fields:
        setattr(tweet, field, getattr(tweetobj, field))

    # Copy over the coordinates, if they're there available
    if tweetobj.coordinates:
        tweet.coordinates = db.GeoPt(*tweetobj.coordinates['coordinates'])

    if commit:
        tweet.put()
        # Kick off post-processing tasks
        from tasks import post_process_tweet
        deferred.defer(post_process_tweet, tweet.id)

    return tweet

