import os, sys

# Add our external dependencies to the $PYTHONPATH
extlibs = ('tornado', 'jinja2', 'tweepy', 'python-simplejson',
           'appengine-search')
for lib in extlibs:
    sys.path.insert(0, os.path.join('ext', lib))

import tornado.wsgi
import wsgiref.handlers

import settings
from urls import urls

if not settings.PRODUCTION:
    import lib.devmode

def main():
    application = tornado.wsgi.WSGIApplication(urls, **settings.APP_CONFIG)
    wsgiref.handlers.CGIHandler().run(application)

if __name__ == '__main__':
  main()
