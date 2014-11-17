"""
Tests for lyrics_tagger
"""
import unittest
import lyricstagger.misc as misc
from mutagen import id3

class FakeFile(dict):
    def __init__(self, mime, artist, album, title):
        super(FakeFile, self).__init__()
        if mime == "audio/mp3":
            self["TPE1"] = id3.TPE1(encoding=3, text=artist)
            self["TALB"] = id3.TALB(encoding=3, text=album)
            self["TIT2"] = id3.TIT2(encoding=3, text=title)
        else:
            self["album"] = album
            self["artist"] = artist
            self["title"] = title
        self.mime = [mime]

class BrokenFile(dict):
    def __init__(self, mime, tags):
        super(BrokenFile, self).__init__()
        for k, v in tags.items():
            self[k] = v
        self.mime = [mime]

# pylint: disable=R0904
class MiscCheck(unittest.TestCase):
    """Test miscelanous functions"""
    def test_get_tags_multi(self):
        """Test get_tags with multi-tag file"""
        for mime in ['audio/mp3', 'audio/ogg']:
            audio = FakeFile(mime, ['Artist'], ['Album'], ['Title'])
            tags = misc.get_tags(audio)
            self.assertEqual(tags['album'], "Album")
            self.assertEqual(tags['artist'], "Artist")
            self.assertEqual(tags['title'], "Title")

    def test_get_tags_single(self):
        """Test get_tags with single-tag file"""
        for mime in ['audio/mp3', 'audio/ogg']:
            audio = FakeFile(mime, 'Artist', 'Album', 'Title')
            tags = misc.get_tags(audio)
            self.assertEqual(tags['album'], "Album")
            self.assertEqual(tags['artist'], "Artist")
            self.assertEqual(tags['title'], "Title")

    def test_get_tags_broken(self):
        """Test get_tags with broken tags"""
        audio = BrokenFile('audio/ogg', {'test': 'Test',
                                         'album': 'Album',
                                         'title': 'Title'})
        tags = misc.get_tags(audio)
        self.assertEqual(tags, None)

# pylint: enable=R0904
if __name__ == '__main__':
    unittest.main()
