import logging

from google.appengine.ext import db, deferred
from google.appengine.api import memcache

import tweepy
from lib.webapp import RequestHandler

from models import User
from utils import make_auth
from trove.tasks import initial_import
import settings


class LoginHandler(RequestHandler):

    def get(self):
        auth = make_auth()
        try:
            redirect_url = auth.get_authorization_url(
                signin_with_twitter=True)
        except tweepy.TweepError, e:
            return self.render('error.html', { 'error': e })

        self.set_secure_cookie(
            'request_token_key', auth.request_token.key)
        self.set_secure_cookie(
            'request_token_secret', auth.request_token.secret)
        return self.redirect(redirect_url)


class CallbackHandler(RequestHandler):

    def get(self):
        auth = make_auth()
        token_key = self.get_secure_cookie('request_token_key')
        token_secret = self.get_secure_cookie('request_token_secret')
        self.clear_cookie('request_token_key')
        self.clear_cookie('request_token_secret')

        verifier = self.request.params.get('oauth_verifier')
        auth.set_request_token(token_key, token_secret)

        try:
            access_token = auth.get_access_token(verifier)
        except tweepy.TweepError, e:
            return self.render('error.html', { 'error': e })

        logging.warn('Access tokens: %r, %r' %
                     (access_token.key, access_token.secret))

        api = tweepy.API(auth)
        user = api.me()

        # If we don't have a User object for this Twitter account already,
        # create one and start the import process.
        key = db.Key.from_path('User', str(user.id))
        if User.get(key) is None:
            logging.info('Creating new User object for %s (%d)' % (
                    user.screen_name, user.id))
            user = User(key=key, id=user.id,
                        screen_name=user.screen_name,
                        api_key=access_token.key,
                        api_secret=access_token.secret)
            user.put()
            # Start the initial import for this user
            deferred.defer(initial_import, user.id, _queue='import')

        # Store the user's ID, so we can look them up in the datastore when
        # they return.
        self.set_secure_cookie('user_id', str(user.id))

        return self.redirect('/')
