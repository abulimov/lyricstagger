"""
Tests for Wikia helper
"""
import re
import mock
import unittest
from lyrics_tagger.helpers import Wikia


# pylint: disable=R0903
class MockResponse:
    """Mock requests.Response class for tests"""
    def __init__(self, code, text):
        self.status_code = code
        self.text = text
# pylint: enable=R0903


def mock_get(url):
    """Mock requests.get call for tests"""
    if re.search('NotFound', url):
        response = MockResponse(404, 'Not found')
    elif re.search(r'Some\+Track', url):
        text = ("song = {"
                "'artist':'Some Artist',"
                "'song':'Until The End',"
                "'lyrics':'Some lyrics',"
                "'url':'http://lyrics.wikia.com/Some_Artist:Some_Track'}")
        response = MockResponse(200, text)
    elif re.search(r'Gracenote\+Track', url):
        text = ("song = {"
                "'artist':'Some Artist',"
                "'song':'Until The End',"
                "'lyrics':'Some lyrics',"
                "'url':'http://lyrics.wikia.com/Some_Artist:Gracenote_Track'}")
        response = MockResponse(200, text)
    elif re.search('Some_Track', url):
        response = MockResponse(200, 'Some lyrics')
    elif re.search(r'\/Gracenote:', url):
        text = ('Gracenote lyrics')
        response = MockResponse(200, text)
    elif re.search('Gracenote_Track', url):
        response = MockResponse(404, '')
    else:
        response = MockResponse(200, '')
    return response


# pylint: disable=R0904
class WikiaCheck(unittest.TestCase):
    """Tests for Wikia lyrics downloader"""
    def test_parser_bad(self):
        """test Wikia.parse function with bad data"""
        bad_data = "<body>testdata<br>lyricbox</body>"
        bad_lyrics = Wikia.parse(bad_data, False)
        self.assertEqual(bad_lyrics, None)

    def test_parser_good(self):
        """test Wikia.parse function with good data"""
        good_data = ('<body><div class="lyricbox">'
                     '&#79;&#110;&#101;&#32;&#109;&#111;&#114;&#101;&#32;'
                     '&#99;&#104;&#97;&#114;&#108;&#97;&#116;&#97;&#110;'
                     '&#32;&#103;&#111;&#101;&#115;&#32;&#109;&#117;'
                     '&#116;&#101;</div>testdata</body>')
        good_lyrics = Wikia.parse(good_data, False)
        self.assertNotEqual(good_lyrics, None)
        self.assertEqual(good_lyrics, "One more charlatan goes mute")

    def test_parser_good_instrumental(self):
        """test Wikia.parse function with good instrumental data"""
        good_data = ('<div class="lyricbox">'
                     '<span style="padding:1em">'
                     '<a href="/Category:Instrumental" '
                     'class="image image-thumbnail link-internal" '
                     'title="Instrumental">'
                     '<img src="http://img2.wikia.nocookie.net/'
                     '__cb20090423154754/lyricwiki/images/thumb/1/1e/'
                     'TrebleClef.png/30px-TrebleClef.png" '
                     'alt="TrebleClef" class="" '
                     'data-image-key="TrebleClef.png" '
                     'data-image-name="TrebleClef.png" '
                     'width="30" height="68"></a></span>'
                     '&#32;<b>&#73;&#110;&#115;&#116;&#114;&#117;'
                     '&#109;&#101;&#110;&#116;&#97;&#108;</b>&#10;</div>')
        good_lyrics = Wikia.parse(good_data, False)
        self.assertNotEqual(good_lyrics, None)
        self.assertEqual(good_lyrics, "{{Instrumental}}")

    def test_parser_good_gracenote(self):
        """test Wikia.parse function with good gracenote data"""
        data_gracenote = ('<div class="lyricbox"><div class="rtMatcher">'
                          '<a href="http://www.ringtonematcher.com/co/'
                          'ringtonematcher/02/noc.asp?sid=WILWros&amp;artist='
                          '2Pac&amp;song=Aint%2BHard%2B2%2BFind" rel='
                          '"nofollow" target="_blank"></a><span class='
                          '"adNotice">Ad</span></div><p>&#84;&#104;&#101;'
                          '&#121;&#32;&#115;&#97;&#121;&#44;&#32;&#105;&#110;'
                          '&#102;&#108;&#117;&#101;'
                          '&#110;&#99;&#101;&#100;&#32;&#98;&#121;&#32;&#99;'
                          '&#114;&#105;&#109;&#101;&#44;&#32;&#97;&#100;&#100;'
                          '&#105;&#99;&#116;&#101;&#100;&#32;&#116;&#111;&#32;'
                          '&#103;&#114;&#105;&#110;&#100;&#105;&#110;&#39;')
        good_lyrics = Wikia.parse(data_gracenote, True)
        self.assertNotEqual(good_lyrics, None)
        self.assertEqual(good_lyrics, ("They say, influenced by crime, "
                                       "addicted to grindin'"))

    @mock.patch('lyrics_tagger.helpers.wikia.requests.get', mock_get)
    def test_getter_not_found(self):
        """Test Wikia.get_raw_data for 404 code"""
        data = Wikia.get_raw_data("Artist", "NotFound")
        self.assertEqual(data, None)

    @mock.patch('lyrics_tagger.helpers.wikia.requests.get', mock_get)
    def test_getter_normal(self):
        """Test Wikia.get_raw_data for existing track"""
        data = Wikia.get_raw_data("Some Artist", "Some Track")
        self.assertNotEqual(data, None)
        self.assertEqual(data[0], 'Some lyrics')

    @mock.patch('lyrics_tagger.helpers.wikia.requests.get', mock_get)
    def test_getter_normal_gracenote(self):
        """Test Wikia.get_raw_data for existing gracenote track"""
        data = Wikia.get_raw_data("Some Artist",
                                  "Gracenote Track")
        self.assertNotEqual(data, None)
        self.assertEqual(data[0], 'Gracenote lyrics')
        self.assertEqual(data[1], True)

# pylint: enable=R0904
if __name__ == '__main__':
    unittest.main()
