import logging
from itertools import groupby
from operator import attrgetter

from google.appengine.ext import db
from google.appengine.api import memcache

import tweepy
from lib.handlers import RequestHandler
from lib.decorators import login_required

import settings
import oauth.utils
from models import User


class IndexHandler(RequestHandler):

    def get(self):

        # If we don't have a user to work with, bail early.
        user = self.current_user
        if not user:
            if user_id:
                logging.warn('User %s missing from datastore' % user_id)
            return self.render('welcome.html')

        # Gather up the info we need for the front page.
        tweets = user.tweets.fetch(20)

        # We have to do some special gymnastics to give the templates a usable
        # datastructure for date archives, a list of (year, [months]) tuples.
        months = user.months.fetch(user.tweet_count)
        date_archives = [(k, list(g)) for k, g in
                         groupby(months, attrgetter('year'))]

        # Fetch the top N items from the other categories to display
        mention_archives = user.mentions.fetch(settings.ARCHIVE_LIST_SIZE)
        tag_archives = user.tags.fetch(settings.ARCHIVE_LIST_SIZE)
        places = user.places.fetch(settings.ARCHIVE_LIST_SIZE)
        sources = user.sources.fetch(settings.ARCHIVE_LIST_SIZE)

        context = {
            'user': user,
            'tweets': tweets,
            'date_archives': date_archives,
            'mention_archives': mention_archives,
            'tag_archives': tag_archives,
            'places': places,
            'sources': sources,
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

    @login_required
    def get(self):

        user = self.current_user
        archives = user.mentions.fetch(user.tweet_count)
        last_tweets = db.get([archive.tweets[0] for archive in archives])

        context = {
            'archives': zip(archives, last_tweets),
            }
        self.render('mentions.html', context)

class MentionHandler(RequestHandler):
    pass
