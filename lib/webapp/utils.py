import hashlib
import hmac

from settings import COOKIE_SECRET


##############################################################################
# Cookie utils, ported from Tornado:
# http://github.com/facebook/tornado/blob/master/tornado/web.py
##############################################################################

def cookie_signature(*parts):
    h = hmac.new(COOKIE_SECRET, digestmod=hashlib.sha1)
    for part in parts:
        h.update(part)
    return h.hexdigest()

def time_independent_equals(a, b):
    if len(a) != len(b):
        return False
    result = 0
    for x, y in zip(a, b):
        result |= ord(x) ^ ord(y)
    return result == 0

def utf8(s):
    if isinstance(s, unicode):
        return s.encode("utf-8")
    return str(s)
