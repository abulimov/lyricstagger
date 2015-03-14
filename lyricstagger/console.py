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

try:
    from docopt import docopt
except ImportError:
    sys.exit("Missing docopt module (install: pip install docopt)")


def main():
    """Main function"""
    arguments = docopt(__doc__, version="lyricstagger 0.7.0")
    path_list = arguments["<path>"]
    logger = log.cli_logger()
    for i, path in enumerate(path_list):
        try:
            path_list[i] = path.decode("utf-8")
        except AttributeError:
            pass

    if arguments['tag']:
        for filepath in misc.get_file_list(path_list):
            logger.log_processing(filepath)
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

    elif arguments['remove']:
        for filepath in misc.get_file_list(path_list):
            logger.log_processing(filepath)
            audio = misc.get_audio(filepath)
            logger.log_removing(filepath)
            misc.remove_lyrics(audio)
            audio.save()

    elif arguments['edit']:
        for filepath in misc.get_file_list(path_list):
            logger.log_processing(filepath)
            audio = misc.get_audio(filepath)
            lyrics = misc.edit_lyrics(audio)
            if lyrics:
                logger.log_writing(filepath)
                audio = misc.write_lyrics(audio, lyrics)
                audio.save()
            else:
                logger.log_no_lyrics_saved(filepath)

    elif arguments['show']:
        for filepath in misc.get_file_list(path_list):
            logger.log_processing(filepath)
            audio = misc.get_audio(filepath)
            data = misc.get_tags(audio)
            if data and "lyrics" in data:
                print("Artist: %s, Title: %s" % (data["artist"],
                                                 data["title"]))
                print()
                print(data["lyrics"])
                print()
            else:
                logger.log_not_found(filepath)
                print("No lyrics in file '%s'" % filepath)

    else:  # report
        for filepath in misc.get_file_list(path_list):
            logger.log_processing(filepath)
            audio = misc.get_audio(filepath)
            data = misc.get_tags(audio)
            if data and 'lyrics' not in data:
                logger.log_not_found(filepath)
                print("No lyrics in file '%s'" % filepath)

    print(logger.show_stats())
