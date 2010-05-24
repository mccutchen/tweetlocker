import logging
import re

from google.appengine.ext import db, deferred
import tweepy

from oauth.utils import make_api, make_auth
from utils import (make_tweet, make_mention_archive, make_tag_archive,
                   make_date_archives)

from models import User, Tweet, Place
from models import YearArchive, MonthArchive, DayArchive, WeekArchive

import settings


def fetch_new_tweets(user_id, token_key, token_secret, since_id=None):
    return
    logging.info('Fetching new tweets for user %d...' % user_id)
    user = User.get_by_key_name(str(user_id))
    if not user:
        return logging.error('User not found.')

    if since_id is None:
        last_tweet = user.tweets.order('-created_at').get()
        since_id = last_tweet.id if last_tweet else None
        logging.info('Found last tweet by date: %d' % since_id)

    api = make_api(token_key, token_secret)
    tweets = api.user_timeline(since_id=since_id, count=settings.BATCH_SIZE)
    if tweets:
        entities = []
        for tweet in tweets:
            entities.append(make_tweet(tweet))
        db.put(entities)
        deferred.defer(fetch_new_tweets, user_id, token_key, token_secret,
                       tweets[-1].id)


def initial_import(user_id, max_id=None):
    logging.critical('Importing all tweets older than %s for user %d...' %
                     (max_id, user_id))

    # We should just quit if the user doesn't exist or if their initial import
    # has already finished.
    user = User.get_by_key_name(str(user_id))
    if not user:
        return logging.error('User not found.')

    if user.import_finished:
        return logging.error('Import already finished for user.')

    # Get a batch of tweets to work on
    tweets = user.api.user_timeline(max_id=max_id, count=settings.BATCH_SIZE)

    # Are there any tweets in the batch?
    if tweets:
        logging.info('Importing %d tweets in this batch' % len(tweets))
        entities, max_id = [], None
        for tweet in tweets:
            entities.extend(make_tweet(user, tweet))
            max_id = tweet.id
        user.tweet_count += len(tweets)
        db.put(entities + [user])

        # Spawn another instance of this task to continue the import
        # process. The max_id needs to be decremented here because Twitter's
        # API will include the tweet with that ID, even though you might
        # expect it to only include tweets *older* than that one, like the
        # documentation says.
        max_id -= 1
        deferred.defer(
            initial_import, user_id, max_id, _queue='import')

    # Otherwise, the import has finished.  Update the user accordingly.
    else:
        logging.critical('Initial import finished!')

        # Note the latest tweet, so we know where to start importing new ones.
        last_tweet = user.tweets.get()
        user.latest_tweet_id = last_tweet.id if last_tweet else None

        # Note the date of the oldest tweet for the user, for graphs.
        old_key = db.Key.from_path('Tweet', str(max_id+1), parent=user.key())
        old_tweet = db.get(old_key)
        user.oldest_tweet_at = old_tweet.created_at

        user.put()

        # Now start the post-processing
        deferred.defer(post_process_tweets, user.id, initial_import=True,
                       _queue='postprocess')

def post_process_tweets(user_id, initial_import=False):
    """A deferred task to be called after a batch of tweets are imported.
    Spawns deferred tasks to post-process each unprocessed tweet belonging to
    the user.  If initial_import is True, also spawns a task to monitor the
    user's account to flip its import_finished flag to True once all of its
    tweets have been processed."""
    # Spawn deferred tasks to process each tweet we just created
    # (necessary because of the commit=False param given to make_tweet)
    user = User.get_by_key_name(str(user_id))
    if not user:
        logging.error('Could not post-process tweets for user %s' % user_id)
        return
    for tweet in user.get_unprocessed_tweets():
        deferred.defer(post_process_tweet, tweet.id, user.id,
                       _queue='postprocess')
    if initial_import:
        deferred.defer(monitor_post_processing, user.id, _queue='monitor')

def post_process_tweet(tweet_id, user_id):
    """A deferred task that should be called after a Tweet is created."""
	# TODO: search indexing
    user_key = db.Key.from_path('User', str(user_id))
    tweet_key = db.Key.from_path('User', str(user_id), 'Tweet', str(tweet_id))
    user, tweet = db.get([user_key, tweet_key])
    if tweet is None or user is None:
        return logging.error(
            'Could not post-process tweet %s (%s) for user %s (%s)' %
            (tweet_id, tweet, user_id, user))

    logging.debug('Post-processing tweet %s for user %s' % (tweet_id, user_id))

    def txn():
        tweet.processed = True
        to_put = [tweet]
        fns = (update_date_archives, update_mention_archives,
               update_tag_archives)
        for fn in fns:
            to_put.extend(fn(tweet, user))
        return db.put(to_put)

    # Make the updates in a transaction
    db.run_in_transaction(txn)

def update_mention_archives(tweet, user):
    """Scans the given tweet for mentions of other Twitter users (like
    @username) and adds them to the archive for the given user's mentions of
    the other user.  The archive will be created if it needs to be.

    Attempts to look the users up via the Twitter API's lookup method, so we
    can have authoritative user IDs to go on.

    FIXME: This hits the Twitter API for each transaction retry. Cache the
    user objects between calls."""
    mentions = re.findall(r'@(\w+)', tweet.text)
    if mentions:
        try:
            mentions = user.api.lookup_users(screen_names=mentions)
        except tweepy.TweepError, e:
            logging.error('Could not look up users: %s' % ','.join(mentions))
        else:
            return [make_mention_archive(user, m, tweet) for m in mentions]
    return []

def update_tag_archives(tweet, user):
    """Scans the given tweet for any hashtags (like #tagname) and adds them to
    the archive for the given user's use of that tag.  The archive will be
    created if it needs to be."""
    tags = re.findall(r'#(\w+)', tweet.text)
    return [make_tag_archive(user, tag, tweet) for tag in tags]

def update_date_archives(tweet, user):
    """Just calls the make_date_archives utility function to add the tweet to
    the appropriate date archives for the given user."""
    return make_date_archives(user, tweet)

def monitor_post_processing(user_id):
    """Monitors the user's unprocessed tweets after their initial import.
    Once the user no longer has any unprocessed tweets, marks the initial
    import as finished."""
    user = User.get_by_key_name(str(user_id))
    if not user:
        return logging.error('monitor: User not found: %s' % user_id)
    if user.unprocessed_tweets.count() == 0:
        logging.critical(
            'Initial post-processing for user %s finished!' % user_id)
        # Update denormalized counts
        user.import_finished = True
        for prop in ('tweet', 'place', 'source', 'mention', 'tag'):
            count = getattr(user, prop + 's').count()
            setattr(user, prop + '_count', count)
        user.put()
    else:
        deferred.defer(monitor_post_processing, user_id, _queue='monitor')
