import tornado.web
from google.appengine.ext import db


class IndexHandler(tornado.web.RequestHandler):
	def get(self):
		if 'count' in self.cookies:
			count = int(self.get_secure_cookie('count'))
		else:
			count = 1
		self.write('Hello, World!  This is visit #%d' % count)
		self.set_secure_cookie('count', str(count + 1))
