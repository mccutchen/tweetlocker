from google.appengine.ext import db, deferred
from models import User, Tweet, Place

def make_tweet(user, tweetobj):
    """Creates a Tweet entity for the given tweepy API tweet object.  The new
    Tweet is never put to the datastore and any post-processing tasks are NOT
    fired off."""

    # Copy fields that are a 1-to-1 match
    exclude = set(('coordinates', 'place'))
    fields = set(Tweet.properties()) - exclude
    props = dict((field, getattr(tweetobj, field, None)) for field in fields)

    # Create a Tweet entity with the properties copied from the tweepy object
    tweet = Tweet(parent=user, key_name=str(tweetobj.id), **props)

    # Copy over the coordinates, if they're available
    if tweetobj.coordinates:
        tweet.coordinates = db.GeoPt(*tweetobj.coordinates['coordinates'])

    return tweet
