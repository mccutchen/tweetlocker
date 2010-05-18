from tornado.web import URLSpec as Url

import trove.views
import oauth.views

# A regular expression grouping of the names of the kinds of archives we know
# how to handle generically.
archive_types = '(%s)' % '|'.join(trove.views.GENERIC_ARCHIVE_MAP)

# The pattern for an archive's index page (e.g. /mentions/)
archives_pattern = r'^/%s/$' % archive_types

# The pattern for an individual archive page (e.g. /mentions/1234/)
archive_pattern = r'^/%s/(\d+)/$' % archive_types

urls = [
    Url(r'^/$', trove.views.IndexHandler, name='index'),

    Url(r'^/search/$', trove.views.SearchHandler, name='search'),

    Url(r'^/dates/$', trove.views.DatesHandler, name='dates'),
    Url(r'^/dates/(\d+)/(\d+)/$', trove.views.DateHandler, name='date'),

    Url(archives_pattern, trove.views.ArchivesHandler, name='archives'),
    Url(archive_pattern, trove.views.ArchiveHandler, name='archive'),

    (r'^/oauth/login$', oauth.views.LoginHandler),
    (r'^/oauth/callback$', oauth.views.CallbackHandler),
]
