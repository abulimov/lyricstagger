"""
Misc functions for lyrics_tagger
"""
from __future__ import unicode_literals
import os
import lyricstagger.log as log
import lyricstagger.helpers as hlp
import mutagen
import requests

SUPPORTED_FILES = ['.ogg', '.flac', '.mp3']


def fetch(artist, song, album):
    """Fetch lyrics with different helpers"""
    helpers = hlp.HELPERS
    for helper in helpers:
        try:
            lyrics = helper.fetch(artist, song, album)
        except requests.ConnectionError as error:
            lyrics = None
            log.warning('Connection error: %s', error)
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
    if "audio/mp3" in audio.mime:
        tag_map = {"artist": "TPE1", "album": "TALB", "title": "TIT2"}
        lyrics_tags = ["USLT:None:eng", "USLT:None:'eng'"]
        getter = lambda x: x.text
    else:
        tag_map = {"artist": "artist", "album": "album", "title": "title"}
        lyrics_tags = ["lyrics"]
        getter = lambda x: x

    for name, tag in tag_map.items():
        if tag in audio:
            if isinstance(getter(audio[tag]), list):
                data[name] = getter(audio[tag])[0]
            else:
                data[name] = getter(audio[tag])
        else:
            log.warning("Failed to find tag %s", tag)
            return None
    for tag in lyrics_tags:
        if tag in audio:
            data["lyrics"] = True

    return data


def get_audio(file_path):
    """Get audio object from file"""
    return mutagen.File(file_path)


def remove_lyrics(audio):
    """Remove lyrics tag from audio"""
    if "audio/mp3" in audio.mime:
        audio.tags.delall("USLT")
    else:
        try:
            del audio["lyrics"]
        except KeyError:
            pass


def write_lyrics(audio, lyrics):
    """Write lyrics to audio object"""
    if "audio/mp3" in audio.mime:
        audio["USLT:None:eng"] = mutagen.id3.USLT(encoding=3, lang="eng",
                                                  desc="None", text=lyrics)
    else:
        audio["LYRICS"] = lyrics
    return audio
