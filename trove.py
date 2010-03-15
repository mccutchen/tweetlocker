import tornado.web
from google.appengine.ext import db


class IndexHandler(tornado.web.RequestHandler):

    def get(self):
        self.render('templates/index.html', user=None)
