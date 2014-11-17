"""
Misc functions for lyrics_tagger
"""
import os
import sys
import lyricstagger.debug as debug
import lyricstagger.helpers as hlp
import mutagen

SUPPORTED_FILES = ['.ogg', '.flac', '.mp3']


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
    if "audio/mp3" in audio.mime:
        tag_map = {"artist": "TPE1", "album": "TALB", "title": "TIT2"}
        lyrics_tag = "USLT:None:eng"
        getter = lambda x: x.text
    else:
        tag_map = {"artist": "artist", "album": "album", "title": "title"}
        lyrics_tag = "lyrics"
        getter = lambda x: x

    for name, tag in tag_map.items():
        if tag in audio:
            if isinstance(getter(audio[tag]), list):
                data[name] = getter(audio[tag])[0]
            else:
                data[name] = getter(audio[tag])
        else:
            debug.warning("Failed to find tag %s", tag)
            return None
    if lyrics_tag in audio:
        data["lyrics"] = True

    return data


def get_audio(file_path):
    """Get audio object from file"""
    return mutagen.File(file_path)


def show_no_lyrics():
    """Search and show files without lyrics"""
    path = sys.argv[1]

    for filepath in get_file_list(path):
        audio = get_audio(filepath)
        data = get_tags(audio)
        if data and not 'lyrics' in data:
            print("No lyrics in file '%s'" % filepath)


def write_lyrics(audio, lyrics):
    """Write lyrics to audio object"""
    if "audio/mp3" in audio.mime:
        audio["USLT:None:'eng'"] = mutagen.id3.USLT(encoding=3, lang="eng",
                                                    desc="None", text=lyrics)
    else:
        audio["LYRICS"] = lyrics
    return audio


def main():
    """Main function"""
    path = sys.argv[1]

    for file_path in get_file_list(path):
        debug.debug("processing file %s", file_path)
        audio = get_audio(file_path)
        data = get_tags(audio)
        if data and not "lyrics" in data:
            lyrics = fetch(data["artist"], data["title"], data["album"])
            if lyrics:
                debug.debug("writing LYRICS tag to file '%s'", file_path)
                audio = write_lyrics(audio, lyrics)
                audio.save()
            else:
                debug.debug("no lyrics found for file '%s'", file_path)
