from google.appengine.ext import db


class User(db.Model):
    id = db.IntegerProperty(required=True)
    screen_name = db.StringProperty(required=True)
    tweet_count = db.IntegerProperty(default=0)
    import_finished = db.BooleanField(default=False)


class Tweet(db.Model):
    id = db.IntegerProperty(required=True)
    text = db.StringProperty(required=True)
    created_at = db.DateTimeProperty(required=True)
    source = db.StringProperty()
    in_reply_to_user = db.IntegerProperty()
    in_reply_to_status = db.IntegerProperty()
    favorited = db.BooleanProperty(default=False)

    # TODO: Geolocation?
