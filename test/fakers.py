from __future__ import unicode_literals
from __future__ import print_function
import re
from mutagen import id3


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

    def save(self):
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


def mock_edit_fail(_):
    """Mock click.edit(some_text) failed function"""
    return None


def mock_get_audio(_):
    return FakeFile('audio/ogg', ['Artist'], ['Album'], ['Title'], 'Lyrics')


def mock_get_wikia(url, params=None):
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
        text = '<div class="lyricbox">Some lyrics</div>'
        response = MockResponse(200, text)
    elif re.search(r'/Gracenote:', url):
        text = '<div class="lyricbox"><p>Gracenote</p></div>'
        response = MockResponse(200, text)
    elif re.search('Gracenote_Track', url):
        response = MockResponse(404, '')
    else:
        response = MockResponse(200, '')
    return response


def mock_get_darklyrics(url, params=None):
    """Mock requests.get call for tests"""
    if re.search("NotFound", url):
        response = MockResponse(404, "Not found")
    elif re.search(r'search', url):
        text = ('<body><div id="main">\n'
                '<div class="cntwrap">\n'
                '<div class="cont">\n'
                '<h3 class="seah">Artists:</h3>'
                '<div class="sen">'
                '<h2><a href="http://www.darklyrics.com/i/immortal.html" target="_blank">IMMORTAL</a></h2>'
                '<small>http://www.darklyrics.com/i/immortal.html</small>'
                '</div>'
                '<div class="sen">'
                '<h2><a href="http://www.darklyrics.com/i/immortalchoir.html" target="_blank">IMMORTAL CHOIR</a></h2>'
                '<small>http://www.darklyrics.com/i/immortalchoir.html</small>'
                '</div>'
                '</div>'
                '</div>'
                '</div>testdata</body>')
        response = MockResponse(200, text)
    elif re.search(r'immortal\.html', url):
        text = ('<body><div id="main">\n'
                '<div class="cntwrap">\n'
                '<div class="cont">\n'
                '<div class="album">'
                '<h2>album: <strong>"Battles In The North"</strong> (1995)</h2>'
                '<a href="../lyrics/immortal/battlesinthenorth.html#1">Battles In The North</a><br>'
                '</div>'
                '<div class="album">'
                '<h2>album: <strong>"Blizzard Beasts"</strong> (1997)</h2>'
                '<a href="../lyrics/immortal/blizzardbeasts.html#1">Intro</a><br>'
                '<a href="../lyrics/immortal/blizzardbeasts.html#2">Blizzard Beasts</a><br>'
                '</div>'
                '</div>'
                '</div>'
                '</div>testdata</body>')
        response = MockResponse(200, text)
    elif re.search(r'blizzardbeasts\.html', url):
        text = ('<body><div id="main">\n'
                '<div class="albumlyrics">\n'
                '<a href="#1">1. Shores In Flames</a><br />'
                '<a href="#2">2. Valhalla</a><br />'
                '<br /></div>\n'
                '<script language="javascript" type="text/javascript" src="../../rect.js"></script>'
                '<div class="lyrics">'
                '<h3><a name="1">1. Shores In Flames</a></h3><br />'
                'Mother winter leaves our land<br />\n'
                'It says: Set your sails<br />'
                '</div>'
                '</div>'
                '</div>testdata</body>')
        response = MockResponse(200, text)
    else:
        response = MockResponse(200, '')
    return response
