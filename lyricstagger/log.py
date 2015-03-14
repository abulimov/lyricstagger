"""Set up logging"""

import logging
import os
# set up logging
if 'DEBUG' in os.environ:
    LOGGING_LEVEL = logging.DEBUG
else:
    LOGGING_LEVEL = logging.WARNING

logging.basicConfig(format=u'%(filename)s[LINE:%(lineno)d]#\
        %(levelname)-8s [%(asctime)s]  %(message)s', level=LOGGING_LEVEL)


class cli_logger:
    def __init__(self):
        self.stats = dict()
        for key in ["processed", "written", "removed", "not_found", "not_saved"]:
            self.stats[key] = 0

    def log_processing(self, filepath):
        logging.debug("processing audio file '%s'", filepath)
        self.stats["processed"] += 1

    def log_writing(self, filepath):
        logging.debug("writing LYRICS tag to file '%s'", filepath)
        self.stats["written"] += 1

    def log_removing(self, filepath):
        logging.debug("removing LYRICS tag from file '%s'", filepath)
        self.stats["removed"] += 1

    def log_no_lyrics_saved(self, filepath):
        logging.debug("no lyrics saved for edited file '%s'", filepath)
        self.stats["not_saved"] += 1

    def log_not_found(self, filepath):
        logging.debug("no lyrics found for file '%s'", filepath)
        self.stats["not_found"] += 1

    def show_stats(self):
        report = "Summary -"
        for key in self.stats:
            report += (" %s: %d" % (key, self.stats[key]))
        return(report)

debug = logging.debug

warning = logging.warning
