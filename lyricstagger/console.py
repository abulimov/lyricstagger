"""lyricstagger

Usage:
  lyricstagger (tag|remove|report|edit|show) (<path>...)
  lyricstagger (-h | --help)
  lyricstagger --version

Options:
  -h --help                  Show this screen.
  --version                  Show version.
  <path>                     Path to start recursive search for files, \
or list of files.
  remove                     Remove lyrics tags from every found file.
  tag                        Download lyrics and add lyrics tag \
for every found file.
  report                     Show all found files without lyrics tag.
  edit                       Edit lyrics for found files with EDITOR.
  show                       Print lyrics from found files to stdout.
"""
from __future__ import unicode_literals
from __future__ import print_function
import sys
import lyricstagger.log as log
import lyricstagger.misc as misc
import click

try:
    from docopt import docopt
except ImportError:
    sys.exit("Missing docopt module (install: pip install docopt)")


def massive_action_with_progress(logger, path_list, action):
    # get length of generator without converting it to list,
    # saves memory on large file lists, but can be a bit slower
    max_files = sum(1 for _ in misc.get_file_list(path_list))
    with click.progressbar(misc.get_file_list(path_list),
                           length=max_files) as files:
        for filepath in files:
            logger.log_processing(filepath)
            action(logger, filepath)


def massive_action(logger, path_list, action):
    for filepath in misc.get_file_list(path_list):
        logger.log_processing(filepath)
        action(logger, filepath)


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


def report(logger, path_list):
    click.secho("Status         Path", fg="blue")
    for filepath in misc.get_file_list(path_list):
        logger.log_processing(filepath)
        audio = misc.get_audio(filepath)
        data = misc.get_tags(audio)
        if data and 'lyrics' not in data:
            logger.log_not_found(filepath)
            click.secho("no lyrics:    ", nl=False, fg="red")
        else:
            click.secho("lyrics found: ", nl=False, fg="green")
        click.echo("%s" % click.format_filename(filepath))


def main():
    """Main function"""
    arguments = docopt(__doc__, version="lyricstagger 0.7.0")
    path_list = arguments["<path>"]
    for i, path in enumerate(path_list):
        try:
            path_list[i] = path.decode("utf-8")
        except AttributeError:
            pass

    logger = log.cli_logger()

    if arguments['tag']:
        massive_action_with_progress(logger, path_list, tag)

    elif arguments['remove']:
        massive_action_with_progress(logger, path_list, remove)

    elif arguments['edit']:
        massive_action(logger, path_list, edit)

    elif arguments['show']:
        massive_action(logger, path_list, show)

    else:  # report
        report(path_list)

    print(logger.show_stats())
