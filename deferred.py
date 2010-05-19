"""This module only exists to ensure that deferred tasks are run in the
correct environment, which means making necessary adjustments to sys.path and
importing all of the models."""

# The normal deferred request handler, which we will use once we've got all of
# our imports in place
from google.appengine.ext.deferred.handler import main

# Set up the correct environment
import lib.env

# Import all the models we might need to deal with
from models import *

# Run the normal deferred handler
if __name__ == '__main__':
    main()
