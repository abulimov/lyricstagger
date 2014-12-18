"""
Tests for lyrics_tagger
"""
import unittest
import mock
import lyricstagger.misc as misc
from mutagen import id3
from subprocess import CalledProcessError

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

class BrokenFile(dict):
    """Emulate file with broken tags"""
    def __init__(self, mime, tags):
        super(BrokenFile, self).__init__()
        for k, v in tags.items():
            self[k] = v
        self.mime = [mime]


def mock_call_ok(_):
    """Mock subprocess.check_call function"""
    pass

def mock_call_fail(args):
    """Mock subprocess.check_call failed function"""
    raise CalledProcessError(1, args[0])

# pylint: disable=R0904
class MiscCheck(unittest.TestCase):
    """Test miscelanous functions"""
    def test_get_tags_multi(self):
        """Test get_tags with multi-tag file"""
        for mime in ['audio/mp3', 'audio/ogg']:
            audio = FakeFile(mime, ['Artist'], ['Album'], ['Title'], 'Lyrics')
            tags = misc.get_tags(audio)
            self.assertEqual(tags['album'], "Album")
            self.assertEqual(tags['artist'], "Artist")
            self.assertEqual(tags['title'], "Title")
            self.assertEqual(tags['lyrics'], "Lyrics")

    def test_get_tags_single(self):
        """Test get_tags with single-tag file"""
        for mime in ['audio/mp3', 'audio/ogg']:
            audio = FakeFile(mime, 'Artist', 'Album', 'Title', 'Lyrics')
            tags = misc.get_tags(audio)
            self.assertEqual(tags['album'], "Album")
            self.assertEqual(tags['artist'], "Artist")
            self.assertEqual(tags['title'], "Title")
            self.assertEqual(tags['lyrics'], "Lyrics")

    def test_get_tags_broken(self):
        """Test get_tags with broken tags"""
        audio = BrokenFile('audio/ogg', {'test': 'Test',
                                         'album': 'Album',
                                         'title': 'Title'})
        tags = misc.get_tags(audio)
        self.assertEqual(tags, None)

    @mock.patch('lyricstagger.misc.subprocess.check_call', mock_call_ok)
    def test_edit_lyrics_empty_ok(self):
        """Test edit_lyrics with empty lyrics and correct edit"""
        audio = FakeFile('audio/ogg', 'Artist', 'Album', 'Title')
        lyrics = misc.edit_lyrics(audio)
        self.assertEqual(lyrics, "")

    @mock.patch('lyricstagger.misc.subprocess.check_call', mock_call_fail)
    def test_edit_lyrics_empty_fail(self):
        """Test edit_lyrics with empty lyrics and errored edit"""
        audio = FakeFile('audio/ogg', 'Artist', 'Album', 'Title')
        lyrics = misc.edit_lyrics(audio)
        self.assertEqual(lyrics, "")

    @mock.patch('lyricstagger.misc.subprocess.check_call', mock_call_ok)
    def test_edit_lyrics_nonempty_ok(self):
        """Test edit_lyrics with non-empty lyrics and correct edit"""
        audio = FakeFile('audio/ogg', 'Artist', 'Album', 'Title', 'Lyrics')
        lyrics = misc.edit_lyrics(audio)
        self.assertEqual(lyrics, "Lyrics")

    @mock.patch('lyricstagger.misc.subprocess.check_call', mock_call_fail)
    def test_edit_lyrics_nonempty_fail(self):
        """Test edit_lyrics with non-empty lyrics and errored edit"""
        audio = FakeFile('audio/ogg', 'Artist', 'Album', 'Title', 'Lyrics')
        lyrics = misc.edit_lyrics(audio)
        self.assertEqual(lyrics, "Lyrics")



# pylint: enable=R0904
if __name__ == '__main__':
    unittest.main()
