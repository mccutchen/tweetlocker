import trove.views
import oauth.views

# A regular expression grouping of the names of the kinds of archives we know
# how to handle generically.
archive_types = '(%s)' % '|'.join(trove.views.GENERIC_ARCHIVE_MAP)

# The pattern for an archive's index page (e.g. /mentions/)
archives_pattern = r'^/%s/$' % archive_types

# The pattern for an individual archive page (e.g. /mentions/1234/)
archive_pattern = r'^/%s/(\w+)/$' % archive_types

urls = [
    (r'^/$', trove.views.IndexHandler),

    (r'^/search/$', trove.views.SearchHandler),

    (r'^/dates/$', trove.views.DatesHandler),
    (r'^/dates/(\d+)/(\d+)/$', trove.views.DateHandler),

    (archives_pattern, trove.views.ArchivesHandler),
    (archive_pattern, trove.views.ArchiveHandler),

    (r'^/oauth/login$', oauth.views.LoginHandler),
    (r'^/oauth/callback$', oauth.views.CallbackHandler),
]
