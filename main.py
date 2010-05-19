from google.appengine.ext.webapp import WSGIApplication
from google.appengine.ext.webapp.util import run_wsgi_app

import lib.env

import settings
from urls import urls

application = WSGIApplication(urls, debug=settings.DEBUG)

def main():
	run_wsgi_app(application)

if __name__ == '__main__':
  main()
