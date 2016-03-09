"""
Actions with musical files
"""

import lyricstagger.log as log
import lyricstagger.misc as misc
from functools import update_wrapper
import click


def _massive_action_with_progress(logger, path_list, action, label=""):
    # get length of generator without converting it to list,
    # saves memory on large file lists, but can be a bit slower
    max_files = sum(1 for _ in misc.get_file_list(path_list))
    with click.progressbar(misc.get_file_list(path_list),
                           label=label,
                           length=max_files) as files:
        for filepath in files:
            logger.log_processing(filepath)
            action(logger, filepath)


def _massive_action_without_progress(logger, path_list, action, label=""):
    if label:
        click.echo(label)
    for filepath in misc.get_file_list(path_list):
        logger.log_processing(filepath)
        action(logger, filepath)


def massive_action(logger, path_list, action, progress=False, label=""):
    if progress:
        _massive_action_with_progress(logger, path_list, action, label)
    else:
        _massive_action_without_progress(logger, path_list, action, label)


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
