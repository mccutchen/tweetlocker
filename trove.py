import logging

from google.appengine.ext import db
import tornado.web
import tweepy

import settings
from models import User


class IndexHandler(tornado.web.RequestHandler):

    def get(self):
        auth = tweepy.OAuthHandler(
            settings.CONSUMER_KEY,
            settings.CONSUMER_SECRET,
            settings.OAUTH_CALLBACK)

        key = self.get_secure_cookie('access_token_key')
        secret = self.get_secure_cookie('access_token_secret')

        if key and secret:
            auth.set_access_token(key, secret)
            api = tweepy.API(auth)
            user = User.get_by_key_name(str(api.me().id))
        else:
            user = None

        tweets = user.tweets.order('-created_at').fetch(20) if user else []
        self.render('templates/index.html', user=user, tweets=tweets)
