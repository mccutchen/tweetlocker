import logging
from itertools import groupby
from operator import attrgetter

from google.appengine.ext import db
from google.appengine.api import memcache

import tweepy
from lib.webapp import RequestHandler
from lib.decorators import login_required

import settings
import oauth.utils

from models import User
from models import MentionArchive, Place, Source, TagArchive


# Map archive types as they appear in URLs to model classes
GENERIC_ARCHIVE_MAP = {
    'tweets': None,
    'mentions': MentionArchive,
    'places': Place,
    'sources': Source,
    'tags': TagArchive,
    }


class IndexHandler(RequestHandler):

    def get(self):

        # If we don't have a user to work with, bail early.
        user = self.user
        if not user:
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

        generic_archives = []
        for kind, model in GENERIC_ARCHIVE_MAP.items():
            if model is None: continue
            archives = getattr(user, kind).fetch(settings.ARCHIVE_LIST_SIZE)
            generic_archives.append((model.__name__, kind, archives))

        context = {
            'user': user,
            'tweets': tweets,
            'date_archives': date_archives,
            'generic_archives': generic_archives,
            }
        self.render('index.html', context)


class SearchHandler(RequestHandler):
    pass


class DatesHandler(RequestHandler):
    pass


class DateHandler(RequestHandler):
    pass


class ArchivesHandler(RequestHandler):

    @login_required
    def get(self, kind):

        user = self.user
        query = getattr(user, kind)
        archives = query.fetch(user.tweet_count)
        last_tweets = db.get([archive.tweets[0] for archive in archives])

        context = {
            'archives': zip(archives, last_tweets),
            }
        self.render('archives.html', context)

class ArchiveHandler(RequestHandler):

    @login_required
    def get(self, kind, id):
        pass
