import logging

from google.appengine.ext import db, deferred
import tweepy

from models import User, Tweet, Place
import utils
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

    api = utils.make_api(token_key, token_secret)
    tweets = api.user_timeline(since_id=since_id, count=settings.BATCH_SIZE)
    if tweets:
        entities = []
        for tweet in tweets:
            entities.extend(make_tweet(tweet))
        db.put(entities)
        deferred.defer(fetch_new_tweets, user_id, token_key, token_secret,
                       tweets[-1].id)


def initial_import(user_id, token_key, token_secret, max_id=None):
    logging.info('Importing all tweets for user %d...' % user_id)
    user = User.get_by_key_name(str(user_id))
    if not user:
        return logging.error('User not found.')

    if user.import_finished:
        return logging.error('Import already finished for user.')

    # Get a batch of tweets to work on
    api = utils.make_api(token_key, token_secret)
    tweets = api.user_timeline(max_id=max_id, count=settings.BATCH_SIZE)

    # Are there any tweets in the batch?
    if tweets:
        logging.info('Importing %d tweets in this batch' % len(tweets))
        entities, max_id = [], None
        for tweet in tweets:
            entities.append(utils.make_tweet(tweet, commit=False))
            max_id = tweet.id
        user.tweet_count += len(tweets)
        db.put(entities + [user])

        # Spawn deferred tasks to process each tweet we just created
        # (necessary because of the commit=False param given to make_tweet)
        for tweet in tweets:
            deferred.defer(post_process_tweet, tweet.id)

        # Spawn another instance of this task to continue the import process
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

def post_process_tweet(tweet_id):
    """A deferred task that should be called after a Tweet is created."""
    pass
