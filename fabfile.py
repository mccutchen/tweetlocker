from fabric.api import *

def deploy():
    """Deploys the application to App Engine."""
    local('appcfg.py --no_cookies --email=mccutchen@gmail.com update .',
          capture=False)

def clear_datastore():
    """Clears the production datastore."""
    local('lib/remote_api_shell.py tweetlocker -p /_/shell -c '
          '"from lib.utils import clear_datastore; clear_datastore()"',
          capture=False)
