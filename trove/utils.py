import logging
from google.appengine.ext import db, deferred
from models import *


def make_tweet(user, tweetobj):
    """Creates a Tweet entity for the given tweepy API tweet object.  The new
    Tweet is never put to the datastore and any post-processing tasks are NOT
    fired off."""
    logging.debug('Making tweet %s for user %s' % (tweetobj.id, user.id))

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
    logging.debug('Making place archives for %s from user %s' %
                  (placedata['id'], user.id))
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
    logging.debug('Making source archives for %s from user %s' %
                  (name, user.id))
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
    logging.debug('Making mention archives for %s in tweet %s from user %s' %
                  (mentioned_user.id, tweet.id, user.id))
    key = db.Key.from_path('User', str(user.id),
                           'MentionArchive', str(mentioned_user.id))
    def txn():
        archive = MentionArchive.get(key)
        if not archive:
            archive = MentionArchive(
                key=key, id=mentioned_user.id,
                screen_name=mentioned_user.screen_name)
        archive = archive_tweet(archive, tweet)
        db.put(archive)
        return archive
    return db.run_in_transaction(txn)

def make_tag_archive(user, tag, tweet):
    """Adds the given tweet to the given user's archive for the given tag,
    creating the archive if necessary."""
    logging.debug('Making tag archives for tag %s in tweet %s from user %s' %
                  (tag, tweet.id, user.id))
    key = db.Key.from_path('User', str(user.id), 'TagArchive', tag)
    def txn():
        archive = TagArchive.get(key)
        if not archive:
            archive = TagArchive(key=key, tag=tag)
        archive = archive_tweet(archive, tweet)
        db.put(archive)
        return archive
    return db.run_in_transaction(txn)


def make_date_archives(user, tweet):
    """Adds the given tweet to the appropriate date archives, based on the
    tweet's date, for the given user."""
    logging.debug('Making date archives for tweet %s from user %s' %
                  (tweet.id, user.id))
    created_at = tweet.created_at

    # We'll build a list of archives to which the given tweet needs to be
    # added.
    archives = []

    # Year
    key = created_at.strftime(YearArchive.KEY_NAME)
    archives.append(
        YearArchive.get_or_insert(key, parent=user, year=created_at.year))

    # Month
    key = created_at.strftime(MonthArchive.KEY_NAME)
    archives.append(
        MonthArchive.get_or_insert(
            key, parent=user, year=created_at.year, month=created_at.month))

    # Day
    key = created_at.strftime(DayArchive.KEY_NAME)
    archives.append(
        DayArchive.get_or_insert(
            key, parent=user, year=created_at.year, month=created_at.month,
            day=created_at.day, weekday=created_at.weekday()))

    # Week
    key = created_at.strftime(WeekArchive.KEY_NAME)
    week = int(created_at.strftime('%U'))
    archives.append(
        WeekArchive.get_or_insert(
            key, parent=user, year=created_at.year, week=week))

    # Add the tweet to all of the archives in one transaction
    db.run_in_transaction(
        lambda: db.put([archive_tweet(a, tweet) for a in archives]))
    return archives

def archive_tweet(archive, tweet):
    """Utility function to add a tweet to an archive.  Adds the Tweet's key to
    the archive's tweets list and updates the archive's denormalized
    tweet_count."""
    archive.tweets.append(tweet.key())
    archive.tweet_count = len(archive.tweets)
    return archive

def increment_counter(key, field='tweet_count', amount=1, commit=True):
    """A utility function, designed to be used in a transaction, that will
    update a field on a object by an arbirtrary amount."""
    obj = db.get(key)
    setattr(obj, field, getattr(obj, field) + amount)
    if commit:
        obj.put()
    return obj

def add_to_list(key, field, value, commit=True):
    """Adds the given value to the given field on the entity with the given
    key.  The field must be a ListProperty, and the value must be of the
    correct type.  Expected to be used in a transaction."""
    obj = db.get(key)
    values = getattr(obj, field)
    values.append(value)
    setattr(obj, field, values)
    if commit:
        obj.put()
    return obj
