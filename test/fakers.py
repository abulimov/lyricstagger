from __future__ import unicode_literals
from __future__ import print_function
import re
from mutagen import id3
from subprocess import CalledProcessError


# pylint: disable=R0903
class MockResponse:
    """Mock requests.Response class for tests"""
    def __init__(self, code, text):
        self.status_code = code
        self.text = text


class FakeFile(dict):
    """Emulate musical file"""
    def __init__(self, mime, artist, album, title, lyrics=None):
        super(FakeFile, self).__init__()
        if mime == "audio/mp3":
            self["TPE1"] = id3.TPE1(encoding=3, text=artist)
            self["TALB"] = id3.TALB(encoding=3, text=album)
            self["TIT2"] = id3.TIT2(encoding=3, text=title)
            if lyrics:
                self["USLT:None:eng"] = id3.USLT(encoding=3, text=lyrics)
        else:
            self["album"] = album
            self["artist"] = artist
            self["title"] = title
            if lyrics:
                self["lyrics"] = lyrics
        self.mime = [mime]

    def save(_):
        pass


class BrokenFile(dict):
    """Emulate file with broken tags"""
    def __init__(self, mime, tags):
        super(BrokenFile, self).__init__()
        for k, v in tags.items():
            self[k] = v
        self.mime = [mime]
# pylint: enable=R0903


def mock_edit_ok(text):
    """Mock click.edit(some_text) function"""
    return text


def mock_edit_fail(text):
    """Mock click.edit(some_text) failed function"""
    return None


def mock_get_audio(_):
    return FakeFile('audio/ogg', ['Artist'], ['Album'], ['Title'], 'Lyrics')


def mock_get(url, params=None):
    """Mock requests.get call for tests"""
    if re.search("NotFound", url):
        response = MockResponse(404, "Not found")
    elif params and params['song'] == "Some Track":
        text = ("song = {"
                "'artist':'Some Artist',"
                "'song':'Until The End',"
                "'lyrics':'Some lyrics',"
                "'url':'http://lyrics.wikia.com/Some_Artist:Some_Track'}")
        response = MockResponse(200, text)
    elif params and params['song'] == "Gracenote Track":
        text = ("song = {"
                "'artist':'Some Artist',"
                "'song':'Until The End',"
                "'lyrics':'Some lyrics',"
                "'url':'http://lyrics.wikia.com/Some_Artist:Gracenote_Track'}")
        response = MockResponse(200, text)
    elif re.search(r':Some_Track', url):
        text = ('<div class="lyricbox">Some lyrics</div>')
        response = MockResponse(200, text)
    elif re.search(r'\/Gracenote:', url):
        text = ('<div class="lyricbox"><p>Gracenote</p></div>')
        response = MockResponse(200, text)
    elif re.search('Gracenote_Track', url):
        response = MockResponse(404, '')
    else:
        response = MockResponse(200, '')
    return response
