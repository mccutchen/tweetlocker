import logging
from itertools import groupby
from operator import attrgetter

from google.appengine.ext import db
from google.appengine.api import memcache

import tweepy
from lib.handlers import RequestHandler

import settings
import oauth.utils
from models import User


class IndexHandler(RequestHandler):

    def get(self):
        auth = oauth.utils.make_auth()
        key = self.get_secure_cookie('access_token_key')
        secret = self.get_secure_cookie('access_token_secret')

        # If we don't have a user to work with, bail early.
        if not key or not secret:
            return self.render('welcome.html')

        # Authenticated users will have their Twitter API access token info
        # stored in secure cookies.  The token info is used to store the
        # user's ID in memcache.  That ID can then be used to get the User
        # object from the datastore.
        user_id = memcache.get(key+secret)
        if user_id is None:
            api = oauth.utils.make_api(key, secret)
            user_id = str(api.me().id)
            memcache.set(key+secret, user_id)
        user = User.get_by_key_name(str(user_id))

        # If we still don't have a user to work with, something went wrong.
        # I'm not sure what, though.
        if not user:
            logging.warn('No user %s in the datastore' % user_id)
            return self.render('welcome.html')

        # Gather up the info we need for the front page.
        tweets = user.tweets.order('-created_at').fetch(20)

        months = user.months.fetch(user.tweet_count)
        date_archives = [(k, list(g)) for k, g in
                         groupby(months, attrgetter('year'))]

        mention_archives = user.mentions.fetch(user.tweet_count)
        mention_archives.sort(key=lambda x: len(x.tweets), reverse=True)

        places = user.places.fetch(user.tweet_count)

        context = {
            'user': user,
            'tweets': tweets,
            'date_archives': date_archives,
            'mention_archives': mention_archives,
            'places': places,
            }
        self.render('index.html', context)


class SearchHandler(RequestHandler):
    pass

class DatesHandler(RequestHandler):
    pass

class DateHandler(RequestHandler):
    pass

class PlacesHandler(RequestHandler):
    pass

class PlaceHandler(RequestHandler):
    pass

class ClientsHandler(RequestHandler):
    pass

class ClientHandler(RequestHandler):
    pass

class MentionsHandler(RequestHandler):
    pass

class MentionHandler(RequestHandler):
    pass
