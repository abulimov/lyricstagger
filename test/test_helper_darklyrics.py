"""
Tests for Wikia helper
"""
from unittest import TestCase, mock
from lyricstagger.helpers import DarkLyrics
from test import fakers


# pylint: disable=R0904
class DarkLyricsCheck(TestCase):
    """Tests for darklyrics.com downloader"""

    def test_parse_artist_link_bad(self):
        """Test DarkLyrics.get_artist_link function with bad data"""
        bad_data = "<body>testdata<br></body>"
        link = DarkLyrics.parse_artist_link(bad_data)
        self.assertEqual(link, None)

    def test_parse_artist_link_good(self):
        """Test DarkLyrics.get_artist_link function with good data"""
        good_data = ('<body><div id="main">\n'
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
        link = DarkLyrics.parse_artist_link(good_data)
        self.assertNotEqual(link, None)
        self.assertEqual(link, "http://www.darklyrics.com/i/immortal.html")

    def test_parse_album_link_bad(self):
        """Test DarkLyrics.get_artist_link function with bad data"""
        bad_data = "<body>testdata<br></body>"
        link = DarkLyrics.parse_album_link(bad_data, "artist")
        self.assertEqual(link, None)

    def test_parse_album_link_good(self):
        """Test DarkLyrics.get_artist_link function with good data"""
        good_data = ('<body><div id="main">\n'
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
        link = DarkLyrics.parse_album_link(good_data, "Blizzard Beasts")
        self.assertNotEqual(link, None)
        self.assertEqual(link, "http://www.darklyrics.com/lyrics/immortal/blizzardbeasts.html")

    def test_parser_bad(self):
        """Test DarkLyrics.parse function with bad data"""
        bad_data = "<body>testdata<br>lyricbox</body>"
        bad_lyrics = DarkLyrics.parse(bad_data, "song")
        self.assertEqual(bad_lyrics, None)

    def test_parser_good(self):
        """Test DarkLyrics.parse function with good data"""
        good_data = ('<body><div id="main">\n'
                     '<div class="albumlyrics">\n'
                     '<a href="#1">1. Shores In Flames</a><br />'
                     '<a href="#2">2. Valhalla</a><br />'
                     '<br /></div>\n'
                     '<script language="javascript" type="text/javascript" src="../../rect.js"></script>'
                     '<div class="lyrics">'
                     '<h3><a name="1">1. Shores In Flames</a></h3><br />'
                     'Mother winter leaves our land<br />\n'
                     'It says: Set your sails<br />'
                     '<div class="thanks">lll<br>'
                     '<br>'
                     'Thanks to someone for sending these lyrics.</div>'
                     '<div class="note">Submits, comments, corrections are welcomed at webmaster@darklyrics.com</div>'
                     '</div>'
                     '</div>'
                     '</div>testdata</body>')
        good_lyrics = DarkLyrics.parse(good_data, "Shores In Flames")
        self.assertNotEqual(good_lyrics, None)
        self.assertEqual(good_lyrics, "Mother winter leaves our land\nIt says: Set your sails")

    @mock.patch('lyricstagger.helpers.darklyrics.requests.get', fakers.mock_get_darklyrics)
    def test_getter_not_found(self):
        """Test DarkLyrics.fetch for 404 code"""
        helper = DarkLyrics()
        data = helper.fetch("Artist", "NotFound", "Some Album")
        self.assertEqual(data, None)

    @mock.patch('lyricstagger.helpers.darklyrics.requests.get', fakers.mock_get_darklyrics)
    def test_fetch_normal(self):
        """Test DarkLyrics.fetch for existing track"""
        helper = DarkLyrics()
        lyrics = helper.fetch("Immortal", "Shores In Flames", "Blizzard Beasts")
        self.assertNotEqual(lyrics, None)
        self.assertEqual(lyrics, "Mother winter leaves our land\nIt says: Set your sails")

# pylint: enable=R0904
