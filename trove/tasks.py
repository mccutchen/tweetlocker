import logging

from google.appengine.ext import db, deferred
import tweepy

from oauth.utils import make_api, make_auth
from utils import make_tweet

from models import User, Tweet, Place
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


def initial_import(user_id, token_key, token_secret, max_id=None):
    logging.info('Importing all tweets older than %s for user %d...' %
                 (max_id, user_id))

    # We should just quit if the user doesn't exist or if their initial import
    # has already finished.
    user = User.get_by_id(user_id)
    if not user:
        return logging.error('User not found.')

    if user.import_finished:
        return logging.error('Import already finished for user.')

    # Get a batch of tweets to work on
    api = make_api(token_key, token_secret)
    tweets = api.user_timeline(max_id=max_id, count=settings.BATCH_SIZE)

    # Are there any tweets in the batch?
    if tweets:
        logging.info('Importing %d tweets in this batch' % len(tweets))
        entities, max_id = [], None
        for tweet in tweets:
            entities.append(make_tweet(user, tweet))
            max_id = tweet.id
        user.tweet_count += len(tweets)
        db.put(entities + [user])

        # Spawn deferred tasks to process each tweet we just created
        # (necessary because of the commit=False param given to make_tweet)
        for tweet in tweets:
            deferred.defer(post_process_tweet, tweet.id, user.id)

        # Spawn another instance of this task to continue the import
        # process. The max_id needs to be decremented here because Twitter's
        # API will include the tweet with that ID, even though you might
        # expect it to only include tweets *older* than that one, like the
        # documentation says.
        max_id -= 1
        deferred.defer(
            initial_import, user_id, token_key, token_secret, max_id)

    # Otherwise, the import has finished.  Update the user accordingly.
    else:
        logging.info('Initial import finished!')
        last_tweet = user.tweets.order('-created_at').get()
        user.latest_tweet_id = last_tweet.id if last_tweet else None
        user.tweet_count = user.tweets.count()
        user.import_finished = True
        user.put()

def post_process_tweet(tweet_id, user_id):
    """A deferred task that should be called after a Tweet is created."""
	# TODO: place, @mention and date archive aggregation, search indexing
    key = db.Key.from_path('User', user_id, 'Tweet', tweet_id)
    tweet = Tweet.get(key)
    if tweet is None:
        return logging.error('Could not post-process tweet %s' % tweet_id)

    logging.info('Post-processing tweet %s...' % tweet_id)
    update_date_archives(tweet)
    update_mention_archives(tweet)

def update_mention_archives(tweet):
    mentions = re.findall(r'@(\w+)', tweet.text)
    if mentions:
        logging.info('Found mentions of %s in tweet %s' %
                     (', '.join(mentions), tweet.id))

def update_date_archives(tweet):
    """Increments the tweet_count field on each of the date archive models
    (creating them if necessary) for the given tweet."""
    created_at = tweet.created_at

    # Year
    key = created_at.strftime(YearArchive.KEY_NAME)
    archive = YearArchive.get_or_insert(
        key, parent=user, year=created_at.year)
    db.run_in_transcation(increment_counter, archive.key())

    # Month
    key = created_at.strftime(MonthArchive.KEY_NAME)
    archive = MonthArchive.get_or_insert(
        key, parent=user, year=created_at.year, month=created_at.month)
    db.run_in_transcation(increment_counter, archive.key())

    # Day
    key = created_at.strftime(DayArchive.KEY_NAME)
    archive = DayArchive.get_or_insert(
        key, parent=user, year=created_at.year, month=created_at.month,
        day=created_at.day)
    db.run_in_transcation(increment_counter, archive.key())

    # Week
    key = created_at.strftime(WeekArchive.KEY_NAME)
    week = int(created_at.strftime('%U'))
    archive = WeekArchive.get_or_insert(
        key, parent=user, year=created_at.year, week=week)
    db.run_in_transaction(increment_counter, archive.key())

def increment_counter(key, field='tweet_count', amount=1):
    """A utility function, designed to be used in a transaction, that will
    update a field on a object by an arbirtrary amount."""
    obj = db.get(key)
    setattr(obj, field, getattr(obj, field) + amount)
    obj.put()