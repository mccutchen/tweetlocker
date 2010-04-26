import trove.views
import oauth.views

urls = [
    (r'^/$', trove.views.IndexHandler),

    (r'^/search/$', trove.views.SearchHandler),

    (r'^/dates/$', trove.views.DatesHandler),
    (r'^/dates/(\d+)/(\d+)/$', trove.views.DateHandler),

    (r'^/places/$', trove.views.PlacesHandler),
    (r'^/places/(\d+)/$', trove.views.PlaceHandler),

    (r'^/clients/$', trove.views.ClientsHandler),
    (r'^/clients/(\d+)/$', trove.views.ClientHandler),

    (r'^/mentions/$', trove.views.MentionsHandler),
    (r'^/mentions/(\d+)/$', trove.views.MentionHandler),

    (r'^/oauth/login$', oauth.views.LoginHandler),
    (r'^/oauth/callback$', oauth.views.CallbackHandler),
]
