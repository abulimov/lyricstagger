"""
Tests for lyrics_tagger
"""
import unittest
import lyrics_tagger.misc as misc


# pylint: disable=R0904
class MiscCheck(unittest.TestCase):
    """Test miscelanous functions"""
    def test_get_tags_multi(self):
        """Test get_tags with multi-tag file"""
        audio = {'artist': ['Artist'],
                 'album': ['Album'],
                 'title': ['Title']}
        tags = misc.get_tags(audio)
        self.assertEqual(tags['album'], "Album")
        self.assertEqual(tags['artist'], "Artist")
        self.assertEqual(tags['title'], "Title")

    def test_get_tags_single(self):
        """Test get_tags with single-tag file"""
        audio = {'artist': 'Artist',
                 'album': 'Album',
                 'title': 'Title'}
        tags = misc.get_tags(audio)
        self.assertEqual(tags['album'], "Album")
        self.assertEqual(tags['artist'], "Artist")
        self.assertEqual(tags['title'], "Title")

    def test_get_tags_broken(self):
        """Test get_tags with broken tags"""
        audio = {'test': 'Test',
                 'album': 'Album',
                 'title': 'Title'}
        tags = misc.get_tags(audio)
        self.assertEqual(tags, None)

# pylint: enable=R0904
if __name__ == '__main__':
    unittest.main()
