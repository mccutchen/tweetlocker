import base64
import calendar
import datetime
import email
import logging
import re
import time

from google.appengine.ext import webapp
from lib.jinja import render_to_string
import utils

from models import User


DEFAULT_STATUS = 200
DEFAULT_MIMETYPE = 'text/html'


class RequestHandler(webapp.RequestHandler):
    """A custom Tornado RequestHandler that knows how to tell if a user has
    logged in via Twitter and renders Jinja2 templates."""

    @property
    def user(self):
        """A user is considered to be logged in via Twitter if they have their
        user_id stored in a secure cookie."""
        if not hasattr(self, '_user'):
            user_id = self.get_secure_cookie('user_id')
            self._user = User.get_by_key_name(user_id) if user_id else None
            if user_id and not self._user:
                logging.warn('User %s missing from datastore' % user_id)
        return self._user

    def render(self, template, context=None, status=None, mimetype=None):
        """Renders the given template (or list of templates to choose) with
        the given context using Jinja2."""
        context = context or {}
        self.response.set_status(status or DEFAULT_STATUS)
        self.response.headers['Content-type'] = mimetype or DEFAULT_MIMETYPE
        self.response.out.write(render_to_string(template, context))

    ##########################################################################
    # Cookie API and implementation ported from Tornado:
    # http://github.com/facebook/tornado/blob/master/tornado/web.py
    ##########################################################################
    def get_cookie(self, name, default=None):
        return self.request.cookies.get(name, default)

    def set_cookie(self, name, value, domain=None, expires=None, path="/",
                     expires_days=None):
        """Sets the given cookie name/value with the given options."""
        name = utils.utf8(name)
        value = utils.utf8(value)
        if re.search(r"[\x00-\x20]", name + value):
            # Don't let us accidentally inject bad stuff
            raise ValueError("Invalid cookie %r: %r" % (name, value))
        cookie = '%s=%s' % (name, value)
        buf = [cookie]
        if domain:
            buf.append('domain=%s' % domain)
        if expires_days is not None and not expires:
            expires = datetime.datetime.utcnow() + datetime.timedelta(
                days=expires_days)
        if expires:
            timestamp = calendar.timegm(expires.utctimetuple())
            expires = email.utils.formatdate(
                timestamp, localtime=False, usegmt=True)
            buf.append('expires=%s' % expires)
        if path:
            buf.append('path=%s' % path)
        self.response.headers.add_header('Set-Cookie', '; '.join(buf))

    def set_secure_cookie(self, name, value, **kwargs):
        """Signs and timestamps a cookie so it cannot be forged.

        You must specify the 'cookie_secret' setting in your Application
        to use this method. It should be a long, random sequence of bytes
        to be used as the HMAC secret for the signature.

        To read a cookie set with this method, use get_secure_cookie().
        """
        timestamp = str(int(time.time()))
        value = base64.b64encode(value)
        signature = utils.cookie_signature(name, value, timestamp)
        value = "|".join([value, timestamp, signature])
        self.set_cookie(name, value, **kwargs)

    def get_secure_cookie(self, name, value=None):
        """Returns the given signed cookie if it validates, or None.

        In older versions of Tornado (0.1 and 0.2), we did not include the
        name of the cookie in the cookie signature. To read these old-style
        cookies, pass include_name=False to this method. Otherwise, all
        attempts to read old-style cookies will fail (and you may log all
        your users out whose cookies were written with a previous Tornado
        version).
        """
        if value is None: value = self.get_cookie(name)
        if not value: return None
        parts = value.split("|")
        if len(parts) != 3: return None
        signature = utils.cookie_signature(name, parts[0], parts[1])
        if not utils.time_independent_equals(parts[2], signature):
            logging.warning("Invalid cookie signature %r", value)
            return None
        timestamp = int(parts[1])
        if timestamp < time.time() - 31 * 86400:
            logging.warning("Expired cookie %r", value)
            return None
        try:
            return base64.b64decode(parts[0])
        except:
            return None

    def clear_cookie(self, name, path="/", domain=None):
        """Deletes the cookie with the given name."""
        expires = datetime.datetime.utcnow() - datetime.timedelta(days=365)
        self.set_cookie(name, value="", path=path, expires=expires,
                        domain=domain)
