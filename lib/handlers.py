import tornado.web
from lib.jinja import render_to_string
from models import User


DEFAULT_STATUS = 200
DEFAULT_MIMETYPE = 'text/html'


class RequestHandler(tornado.web.RequestHandler):
    """A custom Tornado RequestHandler that knows how to tell if a user has
    logged in via Twitter and renders Jinja2 templates."""

    def get_current_user(self):
        """A user is considered to be logged in via Twitter if they have their
        user_id stored in a secure cookie."""
        user_id = self.get_secure_cookie('user_id')
        return User.get_by_key_name(user_id) if user_id else None

    def render(self, template, context=None, status=None, mimetype=None):
        context = context or {}
        self.set_status(status or DEFAULT_STATUS)
        self.set_header('Content-type', mimetype or DEFAULT_MIMETYPE)
        return super(RequestHandler, self).render(template, **context)

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
