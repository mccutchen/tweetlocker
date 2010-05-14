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

        if key and secret:
            user_id = memcache.get(key+secret)
            if user_id is None:
                api = oauth.utils.make_api(key, secret)
                user_id = str(api.me().id)
                memcache.set(key+secret, user_id)
            user = User.get_by_key_name(str(user_id))
        else:
            user = None

        tweets = user.tweets.order('-created_at').fetch(20) if user else []
        months = user.months.fetch(user.tweet_count)
        date_archives = [(k, list(g)) for k, g in
                         groupby(months, attrgetter('year'))]
        context = {
            'user': user,
            'tweets': tweets,
            'date_archives': date_archives,
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
