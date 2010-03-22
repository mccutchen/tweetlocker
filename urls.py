from trove import IndexHandler
from oauth import LoginHandler, CallbackHandler

urls = [
    (r'^/$', IndexHandler),

    (r'^/search/$', SearchHandler),

    (r'^/dates/$', DatesHandler),
    (r'^/dates/(\d+)/(\d+)/$', DateHandler),

    (r'^/places/$', PlacesHandler),
    (r'^/places/(\d+)/$', PlaceHandler),

    (r'^/clients/$', ClientsHandler),
    (r'^/clients/(\d+)/$', ClientHandler),

    (r'^/mentions/$', MentionsHandler),
    (r'^/mentions/(\d+)/$', MentionHandler),

    (r'^/oauth/login$', LoginHandler),
    (r'^/oauth/callback$', CallbackHandler),
]
