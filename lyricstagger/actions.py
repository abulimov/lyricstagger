"""
Actions with musical files
"""

import lyricstagger.log as log
import lyricstagger.misc as misc
from functools import update_wrapper
from threading import Thread
try:
    # python3
    from queue import Queue
except ImportError:
    # python2
    from Queue import Queue
import click

class ActionThread(Thread):
    """Thread to perform action"""
    def __init__(self, logger, action, file_queue, result_queue=None):
        Thread.__init__(self)
        self.action = action
        self.logger = logger
        self.file_queue = file_queue
        self.result_queue = result_queue

    def run(self):
        while True:
            filepath = self.file_queue.get()
            self.logger.log_processing(filepath)
            self.action(self.logger, filepath)
            self.file_queue.task_done()
            if self.result_queue:
                self.result_queue.put(filepath)

def _massive_action_with_progress(logger, path_list, action, threads, label=""):
    file_queue = Queue()
    result_queue = Queue()
    for _ in range(threads):
        t = ActionThread(logger, action, file_queue, result_queue)
        t.setDaemon(True)
        t.start()

    # get length of generator without converting it to list,
    # saves memory on large file lists, but can be a bit slower
    max_files = sum(1 for _ in misc.get_file_list(path_list))
    with click.progressbar(label=label,
                           length=max_files) as bar:
        for filepath in misc.get_file_list(path_list):
            file_queue.put(filepath)

        for progress in range(0, max_files):
            result_queue.get()
            bar.update(progress)

        file_queue.join()


def _massive_action_without_progress(logger, path_list, action, threads, label=""):
    file_queue = Queue()
    for _ in range(threads):
        t = ActionThread(logger, action, file_queue)
        t.setDaemon(True)
        t.start()
    if label:
        click.echo(label)
    for filepath in misc.get_file_list(path_list):
        file_queue.put(filepath)
    file_queue.join()


def massive_action(logger, path_list, action, threads=1, progress=False, label=""):
    if progress:
        _massive_action_with_progress(logger, path_list, action, threads, label)
    else:
        _massive_action_without_progress(logger, path_list, action, threads, label)


def summary(f):
    def new_func(**kwargs):
        logger = log.CliLogger()
        f(logger, **kwargs)
        click.echo(logger.show_stats())
    return update_wrapper(new_func, f)


def tag(logger, filepath):
    audio = misc.get_audio(filepath)
    data = misc.get_tags(audio)
    if data and "lyrics" not in data:
        lyrics = misc.fetch(data["artist"],
                            data["title"],
                            data["album"])
        if lyrics:
            logger.log_writing(filepath)
            audio = misc.write_lyrics(audio, lyrics)
            audio.save()
        else:
            logger.log_not_found(filepath)


def remove(logger, filepath):
    audio = misc.get_audio(filepath)
    logger.log_removing(filepath)
    misc.remove_lyrics(audio)
    audio.save()


def edit(logger, filepath):
    audio = misc.get_audio(filepath)
    lyrics = misc.edit_lyrics(audio)
    if lyrics:
        logger.log_writing(filepath)
        audio = misc.write_lyrics(audio, lyrics)
        audio.save()
    else:
        logger.log_no_lyrics_saved(filepath)


def show(logger, filepath):
    audio = misc.get_audio(filepath)
    data = misc.get_tags(audio)
    if data and "lyrics" in data:
        click.secho("%s" % click.format_filename(filepath), fg="blue")
        click.secho("Artist: %s, Title: %s" % (data["artist"],
                                               data["title"]),
                    fg="blue")
        click.echo()
        click.echo(data["lyrics"])
        click.echo()
    else:
        logger.log_not_found(filepath)
        click.secho("No lyrics in file '%s'" % filepath, fg="red")


def report(logger, filepath):
    audio = misc.get_audio(filepath)
    data = misc.get_tags(audio)
    if data and 'lyrics' not in data:
        logger.log_not_found(filepath)
        click.secho("no lyrics:    ", nl=False, fg="red")
    else:
        click.secho("lyrics found: ", nl=False, fg="green")
    click.echo("%s" % click.format_filename(filepath))
