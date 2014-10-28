"""Set up logging"""

import logging
import os
#set up logging
if 'DEBUG' in os.environ:
    LOGGING_LEVEL = logging.DEBUG
else:
    LOGGING_LEVEL = logging.WARNING

logging.basicConfig(format=u'%(filename)s[LINE:%(lineno)d]#\
        %(levelname)-8s [%(asctime)s]  %(message)s', level=LOGGING_LEVEL)

debug = logging.debug

warning = logging.warning
