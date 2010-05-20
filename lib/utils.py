
def clear_datastore():
    """Clears the datastore when called in the remote_api environment."""
    import inspect
    from google.appengine.ext import db
    import lib.env
    import models

    ismodel = lambda x: inspect.isclass(x) and issubclass(x, db.Model)
    xs = inspect.getmembers(models, ismodel)
    for name, x in xs:
        print 'Deleting %s' % name
        keys = db.Query(x, keys_only=True).fetch(1000)
        while keys:
            db.delete(keys)
            keys = db.Query(x, keys_only=True).fetch(1000)

