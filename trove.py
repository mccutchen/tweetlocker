import logging

from google.appengine.ext import db
import tornado.web
import tweepy

import settings


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
            user = api.me()
        else:
            user = None

        self.render('templates/index.html', user=user)
