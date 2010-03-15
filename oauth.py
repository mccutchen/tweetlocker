import logging

from google.appengine.ext import db
import tornado.web
import tweepy

import settings
from models import User


class LoginHandler(tornado.web.RequestHandler):

    def get(self):
        auth = tweepy.OAuthHandler(
            settings.CONSUMER_KEY,
            settings.CONSUMER_SECRET,
            settings.OAUTH_CALLBACK)

        redirect_url = auth.get_authorization_url(signin_with_twitter=True)
        self.set_secure_cookie(
            'request_token_key', auth.request_token.key)
        self.set_secure_cookie(
            'request_token_secret', auth.request_token.secret)
        return self.redirect(redirect_url)


class CallbackHandler(tornado.web.RequestHandler):

    def get(self):
        auth = tweepy.OAuthHandler(
            settings.CONSUMER_KEY,
            settings.CONSUMER_SECRET,
            settings.OAUTH_CALLBACK)

        token_key = self.get_secure_cookie('request_token_key')
        token_secret = self.get_secure_cookie('request_token_secret')
        self.clear_cookie('request_token_key')
        self.clear_cookie('request_token_secret')

        verifier = self.get_argument('oauth_verifier')
        auth.set_request_token(token_key, token_secret)
        access_token = auth.get_access_token(verifier)

        # Store the access token key and secret in secure cookies, so we can
        # use them for Twitter auth (if they're still valid)
        self.set_secure_cookie('access_token_key', access_token.key)
        self.set_secure_cookie('access_token_secret', access_token.secret)

        # Make sure we have an entity for the user that just logged in
        api = tweepy.API(auth)
        user = api.me()
        if User.get_by_key_name(str(user.id)) is None:
            logging.info('Creating new User object for %s (%d)' % (
                    user.screen_name, user.id))
            user = User(key_name=str(user.id), id=user.id,
                        screen_name=user.screen_name)
            user.put()

        return self.redirect('/')
