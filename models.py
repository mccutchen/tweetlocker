from google.appengine.ext import db


class OAuthAccessToken(db.Model):
	token = db.StringProperty()
	secret = db.StringProperty()
	created_at = db.DateTimeProperty(auto_now_add=True)


class User(db.Model):
	handle = db.StringProperty(required=True)
	tweet_count = db.IntegerProperty(default=0)


class Tweet(db.Model):
	pass