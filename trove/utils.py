import logging
from google.appengine.ext import db, deferred
from models import User, Tweet, Place, Source, MentionArchive

def make_tweet(user, tweetobj):
    """Creates a Tweet entity for the given tweepy API tweet object.  The new
    Tweet is never put to the datastore and any post-processing tasks are NOT
    fired off."""
    logging.info('Making Tweet %s' % tweetobj.id)

    # Copy fields that are a 1-to-1 match
    exclude = set(('coordinates', 'place', 'source', 'source_url'))
    fields = set(Tweet.properties()) - exclude
    props = dict((field, getattr(tweetobj, field, None)) for field in fields)

    # Create a Tweet entity with the properties copied from the tweepy object
    key = db.Key.from_path('User', str(user.id), 'Tweet', str(tweetobj.id))
    tweet = Tweet(key=key, **props)

    if tweetobj.source:
        tweet.source = make_source(
            user, tweetobj.source, getattr(tweetobj, 'source_url', None))
        tweet.has_source = True

    if tweetobj.coordinates:
        # Twitter's coordinates are backwards
        coords = reversed(tweetobj.coordinates['coordinates'])
        tweet.coordinates = db.GeoPt(*coords)
        tweet.has_coordinates = True

    if tweetobj.place:
        tweet.place = make_place(user, tweetobj.place)
        tweet.has_coordinates = True

    return tweet

def make_place(user, placedata):
    """Makes a Place object for the given user's account with the given place
    data.  The data given will have coordinates for its bounding box, which
    will be averaged into a single coordinate for the place."""
    key = db.Key.from_path('User', str(user.id),
                           'Place', str(placedata['id']))
    def txn(placedata=placedata):
        place = Place.get(key)
        if not place:
            # Average the bounding box to get a single coordinate point for
            # the place
            bbox = placedata.pop('bounding_box')
            coords = bbox['coordinates'][0]
            num = float(len(coords))
            lat = sum(lat for lon, lat in coords) / num
            lon = sum(lon for lon, lat in coords) / num

            # Make sure placedata keys are not unicode
            placedata = dict((str(k), v) for k,v in placedata.iteritems())

            # Create the place with the calculated coordinates
            placedata['coordinates'] = db.GeoPt(lat, lon)
            place = Place(key=key, **placedata)
            place.put()
        return place

    return db.run_in_transaction(txn)

def make_source(user, name, url=None):
    """Makes a Source object for the given user's account with the given name
    and optional URL."""
    key = db.Key.from_path('User', str(user.id),
                           'Source', str(name))
    def txn():
        source = Source.get(key)
        if not source:
            source = Source(key=key, name=name)
            if url:
                try:
                    source.url = url
                except:
                    logging.warn('Invalid source URL: %s' % url)
            source.put()
        return source
    return db.run_in_transaction(txn)

def make_mention_archive(user, mentioned_user, tweet):
    """Adds the given tweet to the given user's archive of mentions of the
    given mentioned_user, creating the archive if necessary."""
    key = db.Key.from_path('User', str(user.id),
                           'MentionArchive', str(mentioned_user))
    def txn():
        archive = MentionArchive.get(key)
        if not archive:
            archive = MentionArchive(key=key, screen_name=mentioned_user)
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
