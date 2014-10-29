"""
Misc functions for lyrics_tagger
"""
import os
import sys
import lyricstagger.debug as debug
import lyricstagger.helpers as hlp
import mutagen

SUPPORTED_FILES = ['.ogg', '.flac']


def fetch(artist, song, album):
    """Fetch lyrics with different helpers"""
    helpers = hlp.HELPERS
    for helper in helpers:
        try:
            lyrics = helper.fetch(artist, song, album)
        except ConnectionError as error:
            lyrics = None
            debug.warning('Connection error: %s', error)
        if lyrics:
            break
    return lyrics


def get_file_list(path):
    """Generator of file pathes in directory"""
    for root, _, files in os.walk(path):
        for each in files:
            _, ext = os.path.splitext(each)
            if ext.lower() in SUPPORTED_FILES:
                filepath = os.path.join(root, each)
                yield filepath


def get_tags(audio):
    """Get tags from audio class"""
    if not audio:
        return None
    data = dict()
    for tag in ['artist', 'album', 'title']:
        if tag in audio:
            if isinstance(audio[tag], list):
                data[tag] = audio[tag][0]
            else:
                data[tag] = audio[tag]
        else:
            debug.warning("Failed to find tag %s", tag)
            return None
    return data


def get_audio(file_path):
    """Get audio object from file"""
    return mutagen.File(file_path)


def nolyrics():
    """Main function"""
    path = sys.argv[1]

    for filepath in get_file_list(path):
        audio = get_audio(filepath)
        if audio and not 'lyrics' in audio:
            print("No lyrics in file '%s'" % filepath)


def main():
    """Main function"""
    path = sys.argv[1]

    for file_path in get_file_list(path):
        debug.debug("processing file %s", file_path)
        audio = get_audio(file_path)
        data = get_tags(audio)
        if data and not 'lyrics' in audio:
            lyrics = fetch(data['artist'], data['title'], data['album'])
            if lyrics:
                debug.debug("writing LYRICS tag to file '%s'", file_path)
                audio["LYRICS"] = lyrics
                audio.save()
            else:
                debug.debug("no lyrics found for file '%s'", file_path)
