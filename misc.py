"""
Misc functions for lyrics_tagger
"""
import os
import lyrics_tagger.debug as debug
import lyrics_tagger.helpers as hlp
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
