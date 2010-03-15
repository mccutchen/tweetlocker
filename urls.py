from trove import IndexHandler
from oauth import LoginHandler, CallbackHandler

urls = [
    (r'^/$', IndexHandler),
    (r'^/oauth/login$', LoginHandler),
    (r'^/oauth/callback$', CallbackHandler),
]
