from google.appengine.ext import db
import tornado.web
import tweepy

import settings


class LoginHandler(tornado.web.RequestHandler):

    def get(self):
        auth = tweepy.OAuthHandler(
            settings.CONSUMER_KEY, settings.CONSUMER_SECRET,
            'http://localhost:9999/oauth/callback')
        redirect_url = auth.get_authorization_url(signin_with_twitter=True)
        self.set_secure_cookie(
            'request_token_key', auth.request_token.key)
        self.set_secure_cookie(
            'request_token_secret', auth.request_token.secret)
        return self.redirect(redirect_url)


class CallbackHandler(tornado.web.RequestHandler):

    def get(self):
        auth = tweepy.OAuthHandler(
            settings.CONSUMER_KEY, settings.CONSUMER_SECRET,
            'http://localhost:9999/oauth/callback')

        token_key = self.get_secure_cookie('request_token_key')
        token_secret = self.get_secure_cookie('request_token_secret')
        self.clear_cookie('request_token_key')
        self.clear_cookie('request_token_secret')

        verifier = self.get_argument('oauth_verifier')
        auth.set_request_token(token_key, token_secret)
        auth.get_access_token(verifier)

        api = tweepy.API(auth)
        me = api.me()
        self.write(u'%s' % me)
