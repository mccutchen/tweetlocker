import logging

from google.appengine.ext import db
from google.appengine.api import memcache

import tornado.web
import tweepy

import settings
import utils
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
            user_id = memcache.get(key+secret)
            if user_id is None:
                api = utils.make_api(key, secret)
                user_id = api.me().id
                memcache.set(key+secret, user_id)
            user = User.get_by_key_name(str(user_id))
        else:
            user = None

        tweets = user.tweets.order('-created_at').fetch(20) if user else []
        self.render('templates/index.html', user=user, tweets=tweets)
