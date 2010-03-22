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
    logging.info('Importing all tweets older than %s for user %d...' %
                 (max_id, user_id))

    # We should just quit if the user doesn't exist or if their initial import
    # has already finished.
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
            entities.append(utils.make_tweet(user, tweet))
            max_id = tweet.id
        user.tweet_count += len(tweets)
        db.put(entities + [user])

        # Spawn deferred tasks to process each tweet we just created
        # (necessary because of the commit=False param given to make_tweet)
        for tweet in tweets:
            pass #deferred.defer(post_process_tweet, tweet.id)

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

def post_process_tweet(tweet_id):
    """A deferred task that should be called after a Tweet is created."""
	# TODO: place, @mention and date archive aggregation, search indexing
    tweet = Tweet.get_by_key_name(str(tweet_id))
    if tweet is None:
        return logging.error('Could not post-process tweet %s' % tweet_id)

    logging.info('Post-processing tweet %s...' % tweet_id)
    user = db.get(tweet.parent())

    # Add this tweet to the appropriate date archive, creating it if needed
    created_at = tweet.created_at
    key = '%d/%d' % (user.id, created_at.year, created_at.month)
    datearchive = DateArchive.get_or_insert(
        key, parent=user, year=created_at.year, month=created_at.month)
    datearchive.tweets.append(tweet)



