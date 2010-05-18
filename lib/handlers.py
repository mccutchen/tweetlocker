import base64
import hashlib
import hmac
import logging
import time

from google.appengine.ext import webapp
from lib.jinja import render_to_string

import settings
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
        context = context or {}
        self.response.set_status(status or DEFAULT_STATUS)
        self.response.headers['Content-type'] = mimetype or DEFAULT_MIMETYPE
        self.response.out.write(render_to_string(template, context))

    def render_string(self, template, **kwargs):
        """Use Jinja2 to render the given template and context, after doing
        the same context manipulation as the superclass's render_string
        method.  Called internally by the render() method."""
        # Default context copied from tornado.web.RequestHandler.render_string
        args = dict(
            handler=self,
            request=self.request,
            current_user=self.current_user,
            locale=self.locale,
            _=self.locale.translate,
            static_url=self.static_url,
            xsrf_form_html=self.xsrf_form_html,
            reverse_url=self.application.reverse_url
        )
        args.update(self.ui)
        args.update(kwargs)
        return render_to_string(template, args)

    def set_secure_cookie(self, name, value, **kwargs):
        """Signs and timestamps a cookie so it cannot be forged.

        You must specify the 'cookie_secret' setting in your Application
        to use this method. It should be a long, random sequence of bytes
        to be used as the HMAC secret for the signature.

        To read a cookie set with this method, use get_secure_cookie().
        """
        timestamp = str(int(time.time()))
        value = base64.b64encode(value)
        signature = _cookie_signature(name, value, timestamp)
        value = "|".join([value, timestamp, signature])
        self.request.set_cookie(name, value, **kwargs)

    def get_secure_cookie(self, name, value=None):
        """Returns the given signed cookie if it validates, or None.

        In older versions of Tornado (0.1 and 0.2), we did not include the
        name of the cookie in the cookie signature. To read these old-style
        cookies, pass include_name=False to this method. Otherwise, all
        attempts to read old-style cookies will fail (and you may log all
        your users out whose cookies were written with a previous Tornado
        version).
        """
        if value is None: value = self.request.cookies.get(name)
        if not value: return None
        parts = value.split("|")
        if len(parts) != 3: return None
        signature = _cookie_signature(name, parts[0], parts[1])
        if not _time_independent_equals(parts[2], signature):
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


def _cookie_signature(*parts):
    h = hmac.new(settings.COOKIE_SECRET, digestmod=hashlib.sha1)
    for part in parts:
        h.update(part)
    return h.hexdigest()

def _time_independent_equals(a, b):
    if len(a) != len(b):
        return False
    result = 0
    for x, y in zip(a, b):
        result |= ord(x) ^ ord(y)
    return result == 0
