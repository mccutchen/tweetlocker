from google.appengine.ext import db, deferred
from models import User, Tweet, Place, MentionArchive

def make_tweet(user, tweetobj):
    """Creates a Tweet entity for the given tweepy API tweet object.  The new
    Tweet is never put to the datastore and any post-processing tasks are NOT
    fired off."""

    # Copy fields that are a 1-to-1 match
    exclude = set(('coordinates', 'place'))
    fields = set(Tweet.properties()) - exclude
    props = dict((field, getattr(tweetobj, field, None)) for field in fields)

    # Create a Tweet entity with the properties copied from the tweepy object
    key = db.Key.from_path('User', user.id, 'Tweet', tweetobj.id)
    tweet = Tweet(key=key, **props)

    # Copy over the coordinates, if they're available. TODO: Handle places
    if tweetobj.coordinates:
        tweet.coordinates = db.GeoPt(*tweetobj.coordinates['coordinates'])

    return tweet

def make_mention_archive(user, mentioned_user, tweet):
    """Adds the given tweet to the given user's archive of mentions of the
    given mentioned_user, creating the archive if necessary."""
    key = db.Key.from_path('User', user.id,
                           'MentionArchive', mentioned_user.id)
    def txn():
        archive = MentionArchive.get(key)
        if not archive:
            archive = MentionArchive(
                key=key, user_id=mentioned_user.id,
                screen_name=mentioned_user.screen_name)
            archive.put()
        return archive

    archive = db.run_in_transaction(txn)
    db.run_in_transaction(add_to_list, archive.key(), 'tweets', tweet.key())

def increment_counter(key, field='tweet_count', amount=1):
    """A utility function, designed to be used in a transaction, that will
    update a field on a object by an arbirtrary amount."""
    obj = db.get(key)
    setattr(obj, field, getattr(obj, field) + amount)
    obj.put()

def add_to_list(key, field, value):
    """Adds the given value to the given field on the entity with the given
    key.  The field must be a ListProperty, and the value must be of the
    correct type.  Expected to be used in a transaction."""
    obj = db.get(key)
    values = getattr(obj, field)
    values.append(value)
    setattr(obj, field, values)
    obj.put()
