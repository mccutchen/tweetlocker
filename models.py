from google.appengine.ext import db
from search import Searchable


class User(db.Model):
    """A Twitter user, who has a collection of Tweets and (if they're using
    Twitter's geolocation services) a collection of Places."""
    id = db.IntegerProperty(required=True)
    screen_name = db.StringProperty(required=True)

    tweet_count = db.IntegerProperty(default=0)
    latest_tweet_id = db.IntegerProperty()
    import_finished = db.BooleanProperty(default=False)

    @property
    def tweets(self):
        return db.Query(Tweet).ancestor(self)

    @property
    def places(self):
        return db.Query(Place).ancestor(self)


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
    bounding_box = db.ListProperty(db.GeoPt)

    @property
    def user(self):
        return self.parent()


class Tweet(Searchable, db.Model):
    """An individual tweet.  Should be created with a specific User instance
    as its parent."""
    id = db.IntegerProperty(required=True)
    text = db.TextProperty(required=True)
    created_at = db.DateTimeProperty(required=True)

    source = db.StringProperty()
    source_url = db.LinkProperty()
    in_reply_to_user_id = db.IntegerProperty()
    in_reply_to_status_id = db.IntegerProperty()
    favorited = db.BooleanProperty(default=False)
    coordinates = db.GeoPtProperty()
    place = db.ReferenceProperty(Place, collection_name='tweets')

    @property
    def user(self):
        return self.parent()


class MentionArchive(db.Model):
    """A collection of a particular user's mentions of a particular other
    user. Should be created with a User as its parent."""
    user_id = db.IntegerProperty(required=True)
    screen_name = db.StringProperty(required=True)
    tweets = db.ListProperty(db.Key)


class DateArchive(db.Model):
    # A strftime() format string used to create the key name for an instance
    # based on an arbitrary datetime object.
    KEY_NAME = None

    # The keys of the tweets that are in this archive
    tweets = db.ListProperty(db.Key)

class YearArchive(DateArchive):
    KEY_NAME = '%Y'
    year = db.IntegerProperty(required=True)

class MonthArchive(DateArchive):
    KEY_NAME = '%Y/%m'
    year = db.IntegerProperty(required=True)
    month = db.IntegerProperty(required=True)

class DayArchive(DateArchive):
    KEY_NAME = '%Y/%m/%d'
    year = db.IntegerProperty(required=True)
    month = db.IntegerProperty(required=True)
    day = db.IntegerProperty(required=True)

class WeekArchive(DateArchive):
    KEY_NAME = '%Y:%U' # Year:Week
    year = db.IntegerProperty(required=True)
    week = db.IntegerProperty(required=True)

