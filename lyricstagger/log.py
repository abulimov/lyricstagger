"""Set up logging"""

import logging
import os
import click
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
        self.states = [
            "processed", "written", "removed", "not_found", "not_saved"
        ]
        for key in self.states:
            self.stats[key] = 0

    def log_processing(self, filepath):
        logging.debug("processing audio file '%s'",
                      click.format_filename(filepath))
        self.stats["processed"] += 1

    def log_writing(self, filepath):
        logging.debug("writing LYRICS tag to file '%s'",
                      click.format_filename(filepath))
        self.stats["written"] += 1

    def log_removing(self, filepath):
        logging.debug("removing LYRICS tag from file '%s'",
                      click.format_filename(filepath))
        self.stats["removed"] += 1

    def log_no_lyrics_saved(self, filepath):
        logging.debug("no lyrics saved for edited file '%s'",
                      click.format_filename(filepath))
        self.stats["not_saved"] += 1

    def log_not_found(self, filepath):
        logging.debug("no lyrics found for file '%s'",
                      click.format_filename(filepath))
        self.stats["not_found"] += 1

    def show_stats(self):
        report_tpl = "-----\n" \
            "Processed " + click.style("{processed}", fg="blue") + " files, operations summary: \n" \
            "Tags written: " + click.style("{written}", fg="green") + ", " \
            "Tags removed: " + click.style("{removed}", fg="yellow") + ",\n" \
            "Lyrics missing: " + click.style("{not_found}", fg="red") + ", " \
            "Lyrics not saved: " + click.style("{not_saved}", fg="red")
        report = report_tpl.format(
            processed=self.stats["processed"],
            written=self.stats["written"],
            removed=self.stats["removed"],
            not_found=self.stats["not_found"],
            not_saved=self.stats["not_saved"],
        )
        return(report)

debug = logging.debug

warning = logging.warning
