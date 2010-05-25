from fabric.api import *

def deploy():
    cmd = 'appcfg.py --no_cookies --email=mccutchen@gmail.com update .'
    local(cmd, capture=False)