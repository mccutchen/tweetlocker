import logging
import calendar

from google.appengine.ext import db
from search import Searchable

from oauth.utils import make_api


class User(db.Model):
    """A Twitter user, who has a collection of Tweets and (if they're using
    Twitter's geolocation services) a collection of Places."""
    id = db.IntegerProperty(required=True)
    screen_name = db.StringProperty(required=True)

    # It doesn't feel right to store these, but we have to in order to fetch
    # each user's new tweets automatically.
    api_key = db.StringProperty(required=True)
    api_secret = db.StringProperty(required=True)

    # Helps us figure out where to start requesting new tweets
    latest_tweet_id = db.IntegerProperty()
    import_finished = db.BooleanProperty(default=False)

    # We need to know this for some of the graphs we want to draw
    oldest_tweet_at = db.DateTimeProperty(required=True, auto_now_add=True)

    # We need to denormalize count fields for each of the statistics we're
    # interested in..
    tweet_count = db.IntegerProperty(default=0)
    place_count = db.IntegerProperty(default=0)
    source_count = db.IntegerProperty(default=0)
    mention_count = db.IntegerProperty(default=0)
    tag_count = db.IntegerProperty(default=0)

    @property
    def tweets(self):
        return db.Query(Tweet).ancestor(self).order('-created_at')

    @property
    def unprocessed_tweets(self):
        return db.Query(Tweet).ancestor(self).filter('processed =', False)

    @property
    def places(self):
        return db.Query(Place).ancestor(self).order('-tweet_count')

    @property
    def sources(self):
        return db.Query(Source).ancestor(self).order('-tweet_count')

    @property
    def mentions(self):
        return db.Query(MentionArchive).ancestor(self).order('-tweet_count')

    @property
    def tags(self):
        return db.Query(TagArchive).ancestor(self).order('-tweet_count')

    @property
    def years(self):
        return db.Query(YearArchive).ancestor(self).order('-year')

    @property
    def months(self):
        return db.Query(MonthArchive).ancestor(self)\
            .order('-year').order('-month')

    @property
    def days(self):
        return db.Query(DayArchive).ancestor(self).order('-day')

    @property
    def weeks(self):
        return db.Query(WeekArchive).ancestor(self).order('-week')

    @property
    def api(self):
        """Makes an authenticated tweepy.API object for this user."""
        if hasattr(self, '_api'):
            return self._api
        self._api = make_api(self.api_key, self.api_secret)
        return self._api

    def get_unprocessed_tweets(self):
        """Fetches unprocessed tweets in batches and yields them
        individually."""
        batch_size = 100
        def get_batch(cursor=None):
            q = self.unprocessed_tweets
            q.with_cursor(cursor)
            return q.fetch(batch_size), q.cursor()
        batch, cursor = get_batch()
        while batch:
            for tweet in batch:
                yield tweet
            batch, cursor = get_batch(cursor)

    def __unicode__(self):
        return u'@%s' % self.screen_name


class Place(db.Model):
    """A specific place from which a user has made at least one tweet.  Should
    be created with a specific User instance as its parent."""
    id = db.StringProperty()
    name = db.StringProperty()
    full_name = db.StringProperty()

    place_type = db.StringProperty()
    country = db.StringProperty()
    country_code = db.StringProperty()
    url = db.LinkProperty()
    country_code = db.StringProperty()
    coordinates = db.GeoPtProperty()

    # Denormalized count, should be updated when new tweets are added to the
    # datastore.
    tweet_count = db.IntegerProperty(default=0)

    @property
    def user(self):
        return self.parent()

    def __unicode__(self):
        return self.name


class Source(db.Model):
    """A client used by a user to make a tweet.  Should be created with a
    specific User instance as its parent.  This corresponds to the source and
    source_url info returned by the Twitter API."""
    name = db.StringProperty()
    url = db.LinkProperty()

    tweet_count = db.IntegerProperty(default=0)

    def __unicode__(self):
        return self.name


class Tweet(Searchable, db.Model):
    """An individual tweet.  Should be created with a specific User instance
    as its parent."""
    id = db.IntegerProperty(required=True)
    text = db.TextProperty(required=True)
    created_at = db.DateTimeProperty(required=True)

    in_reply_to_user_id = db.IntegerProperty()
    in_reply_to_status_id = db.IntegerProperty()
    favorited = db.BooleanProperty(default=False)

    has_coordinates = db.BooleanProperty(default=False) # Query optimization
    coordinates = db.GeoPtProperty()
    place = db.ReferenceProperty(Place, collection_name='tweets')

    has_source = db.BooleanProperty(default=False)
    source = db.ReferenceProperty(Source, collection_name='tweets')

    # Has this Tweet been post-processed yet?
    processed = db.BooleanProperty(default=False)

    @property
    def user(self):
        return self.parent()


class Archive(db.Model):
    """A generic archive model. Contains tweets, a list of Tweet keys, and
    tweet_count, the denormalized number of items in the list of Tweets."""

    tweets = db.ListProperty(db.Key)
    tweet_count = db.IntegerProperty(default=0)

    def add_tweet(self, tweet):
        """Adds the given tweet to this archive's list of tweets, and update
        its denormalized count field."""
        self.tweets.append(tweet.key())
        self.tweet_count = len(self.tweets)


class MentionArchive(Archive):
    """A collection of a particular user's mentions of a particular other
    user. Should be created with a User as its parent."""
    id = db.IntegerProperty(required=True)
    screen_name = db.StringProperty(required=True)

    def __unicode__(self):
        return u'@%s' % self.screen_name


class TagArchive(Archive):
    """A collection of a particular user's hashtags."""
    tag = db.StringProperty(required=True)

    def __unicode__(self):
        return u'#%s' % self.tag


class DateArchive(Archive):
    """A generic date-based archive of tweets. Used as the parent of the
    more-specific year, month, day, etc. archives."""

    # A strftime() format string used to create the key name for an instance
    # based on an arbitrary datetime object.
    KEY_NAME = None

    @classmethod
    def make_key(cls, user, date):
        """Makes the key for the date archive for the given date belonging to
        the given user."""
        return db.Key.from_path(
            cls.kind(), date.strftime(cls.KEY_NAME), parent=user.key())

class YearArchive(DateArchive):
    KEY_NAME = '%Y'
    year = db.IntegerProperty(required=True)

    def __unicode__(self):
        return unicode(self.year)

class MonthArchive(DateArchive):
    KEY_NAME = '%Y/%m'
    year = db.IntegerProperty(required=True)
    month = db.IntegerProperty(required=True)

    def __unicode__(self):
        return unicode(calendar.month_name[self.month])

class DayArchive(DateArchive):
    KEY_NAME = '%Y/%m/%d'
    year = db.IntegerProperty(required=True)
    month = db.IntegerProperty(required=True)
    day = db.IntegerProperty(required=True)
    weekday = db.IntegerProperty(required=True)

    def __unicode__(self):
        return unicode(self.day)

class WeekArchive(DateArchive):
    KEY_NAME = '%Y:%U' # Year:Week
    year = db.IntegerProperty(required=True)
    week = db.IntegerProperty(required=True)

    def __unicode__(self):
        return unicode(self.week)
