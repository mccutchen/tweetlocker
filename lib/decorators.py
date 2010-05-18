def login_required(method):
    """A decorator for tornado.web.RequestHandler view methods.  Ensures that
    the request is coming from a user who has logged in via Twitter.  The
    indicator of this is the presence of a "user_id" secure cookie."""

    def decorated_method(self, *args, **kwargs):
        if self.current_user:
            return method(self, *args, **kwargs)
        else:
            self.set_status(403)
            return self.render('403.html')

    return decorated_method
