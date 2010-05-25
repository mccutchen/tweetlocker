#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

# Copied from
#     http://github.com/caio/bizarrice/raw/HEAD/remote_api_shell.py
# which was itself based on the remote_api_shell.py that ships with the SDK.


import atexit
import code
import getpass
import optparse
import os
import sys
import re

from google.appengine.ext.remote_api import remote_api_stub
from google.appengine.api import datastore
from google.appengine.api import memcache
from google.appengine.api import urlfetch
from google.appengine.api import users
from google.appengine.ext import db
from google.appengine.ext import search


USAGE ="""An interactive python shell that uses remote_api.

Usage:
  %s [-s HOSTNAME] APPID [-p PATH] [-c COMMAND]
""" % os.path.basename(__file__)

DEFAULT_PATH = '/remote_api'
BANNER = """App Engine remote_api shell
Python %s
The db, users, urlfetch, and memcache modules are imported.""" % sys.version

def auth_func():
    return (raw_input('Email: '), getpass.getpass('Password: '))

def bpython_shell(appid=None):
    from bpython import cli
    cli.main(args=[], banner=BANNER)

def ipython_shell(appid=None):
    import IPython
    shell = IPython.Shell.IPShell(argv=[])
    shell.mainloop(banner=BANNER)

def plain_shell(appid):
    try: #{{{ trying to setup tab completion
        import readline
    except ImportError:
        import sys
        print >> sys.stderr, 'readline unavailable - tab completion disabled.'
    else:
        import rlcompleter

        class TabCompleter(rlcompleter.Completer):
            """Completer that supports indenting"""

            def complete(self, text, state):
                if not text:
                    return ('    ', None)[state]
                else:
                    return rlcompleter.Completer.complete(self, text, state)

        readline.parse_and_bind('tab: complete')
        readline.set_completer(TabCompleter().complete)

        import atexit
        import os

        history_path = os.path.expanduser(HISTORY_PATH)
        atexit.register(lambda: readline.write_history_file(history_path))
        if os.path.isfile(history_path):
            readline.read_history_file(history_path)#}}}
    import sys
    sys.ps1 = '%s> ' % appid
    sys.ps2 = '%s| ' % re.sub('\w', ' ', appid)
    code.interact(banner=BANNER, local=globals())

def main(argv):
    parser = optparse.OptionParser()
    parser.add_option('-s', '--server', dest='server',
                      help='The hostname your app is deployed on. '
                           'Defaults to <app_id>.appspot.com.')
    parser.add_option('-p', '--path', dest='path', default=DEFAULT_PATH,
                      help='The RemoteAPI path on your deployed app. '
                           'Defaults to /remote_api.')
    parser.add_option('-c', dest='cmd',
                      help='Program to run passed in as string.')
    (options, args) = parser.parse_args()

    if not args or len(args) > 1:
        print >> sys.stderr, USAGE
        if len(args) > 1:
          print >> sys.stderr, 'Unexpected arguments: %s' % args[1:]
        sys.exit(1)
    appid = args[0]

    remote_api_stub.ConfigureRemoteApi(appid, options.path, auth_func,
                                       servername=options.server)
    remote_api_stub.MaybeInvokeAuthentication()

    import os
    os.environ['SERVER_SOFTWARE'] = 'Development (remote_api_shell)/1.0'

    # If we have a command to run, run it.
    if options.cmd:
        exec options.cmd

    # Otherwise, start the interactive shell
    else:
        try:
            bpython_shell(appid)
        except ImportError:
            try:
                ipython_shell(appid)
            except ImportError:
                plain_shell(appid)


if __name__ == '__main__':
  main(sys.argv)
