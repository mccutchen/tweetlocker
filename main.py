import os, sys

# Add our external dependencies to the $PYTHONPATH
extlibs = ('jinja2', 'tweepy', 'python-simplejson', 'appengine-search')
for lib in extlibs:
    sys.path.insert(0, os.path.join('ext', lib))

from google.appengine.ext.webapp import WSGIApplication
from google.appengine.ext.webapp.util import run_wsgi_app

import settings
from urls import urls

if not settings.PRODUCTION:
    import lib.devmode

application = WSGIApplication(urls, debug=settings.DEBUG)

def main():
	run_wsgi_app(application)

if __name__ == '__main__':
  main()
