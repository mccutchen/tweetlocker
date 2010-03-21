import os, sys

# Add our external dependencies to the $PYTHONPATH
for lib in ('tornado', 'tweepy', 'python-simplejson', 'appengine-search'):
    sys.path.insert(0, os.path.join('ext', lib))

import tornado.wsgi
import wsgiref.handlers

import settings
from urls import urls

def main():
    app_settings = {
        'cookie_secret': settings.COOKIE_SECRET,
    }
    application = tornado.wsgi.WSGIApplication(urls, **app_settings)
    wsgiref.handlers.CGIHandler().run(application)

if __name__ == '__main__':
  main()
