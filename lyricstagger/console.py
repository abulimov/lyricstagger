"""lyricstagger

Usage:
  lyricstagger (tag|remove|report|edit) (<path>)
  lyricstagger (-h | --help)
  lyricstagger --version

Options:
  -h --help                  Show this screen.
  --version                  Show version.
  <path>                     Path to start recursive search for files, \
or single file.
  remove                     Remove lyrics tags from every found file.
  tag                        Download lyrics and add lyrics tag \
for every found file.
  report                     Show all found files without lyrics tag.
  edit                       Edit lyrics with EDITOR.
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
    arguments = docopt(__doc__, version="lyricstagger 0.6.0")
    path = arguments["<path>"]
    try:
        path = path.decode("utf-8")
    except AttributeError:
        pass

    if arguments['tag']:
        for filepath in misc.get_file_list(path):
            log.debug("processing file %s", filepath)
            audio = misc.get_audio(filepath)
            data = misc.get_tags(audio)
            if data and not "lyrics" in data:
                lyrics = misc.fetch(data["artist"],
                                    data["title"],
                                    data["album"])
                if lyrics:
                    log.debug("writing LYRICS tag to file '%s'", filepath)
                    audio = misc.write_lyrics(audio, lyrics)
                    audio.save()
                else:
                    log.debug("no lyrics found for file '%s'", filepath)

    elif arguments['remove']:
        for filepath in misc.get_file_list(path):
            audio = misc.get_audio(filepath)
            misc.remove_lyrics(audio)
            audio.save()

    elif arguments['edit']:
        for filepath in misc.get_file_list(path):
            audio = misc.get_audio(filepath)
            lyrics = misc.edit_lyrics(audio)
            if lyrics:
                audio = misc.write_lyrics(audio, lyrics)
                audio.save()
            else:
                log.debug("no lyrics saved for edited file '%s'", filepath)

    else:  # report
        for filepath in misc.get_file_list(path):
            audio = misc.get_audio(filepath)
            data = misc.get_tags(audio)
            if data and not 'lyrics' in data:
                print("No lyrics in file '%s'" % filepath)
