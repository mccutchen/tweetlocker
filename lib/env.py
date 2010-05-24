"""Consolidate all environment setup functionality (sys.path changes,
monkeypatches, etc.)  in here."""

import os, sys

# Add our external dependencies to sys.path
extlibs = ('jinja2', 'tweepy', 'python-simplejson', 'appengine-search')
for lib in extlibs:
    sys.path.insert(0, os.path.join('ext', lib))
