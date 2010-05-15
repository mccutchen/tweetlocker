import logging
from google.appengine.ext import deferred

logging.info('Setting up immediate deferred tasks...')

def immediate_defer(obj, *args, **kwargs):
    logging.info('deferred.defer(%r, %r, %r)' % (obj, args, kwargs))
    if '_queue' in kwargs:
        del kwargs['_queue']
    obj(*args, **kwargs)

deferred.defer = immediate_defer
