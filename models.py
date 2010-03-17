from google.appengine.ext import db


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


class Tweet(db.Model):
    """An individual tweet.  Should be created with a specific User instance
    as its parent."""
    id = db.IntegerProperty(required=True)
    text = db.StringProperty(required=True, multiline=True)
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


class DateArchive(db.Model):
    """A collection of tweets that fall in a particular month and year.  TODO:
    Is this too inflexible?  Should we just store counts here so we can show
    it on the front page, but query for tweets-by-date dynamically?"""
    year = db.IntegerProperty(required=True)
    month = db.IntegerProperty(required=True)


class ReplyArchive(db.Model):
    """A collection of a particular user's replies to a particular other
    user. Should be created with a User as its parent."""
    user_id = db.IntegerProperty(required=True)
    screen_name = db.StringProperty(required=True)
    tweets = db.ListProperty(db.Key)
