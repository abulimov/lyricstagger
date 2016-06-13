"""
Tests for lyrics_tagger
"""
import unittest
import mock
import lyricstagger.misc as misc
import test.fakers as fakers


# pylint: disable=R0904
class MiscCheck(unittest.TestCase):
    """Test miscelanous functions"""
    def test_get_tags_multi(self):
        """Test get_tags with multi-tag file"""
        for mime in ['audio/mp3', 'audio/ogg']:
            audio = fakers.FakeFile(mime, ['Artist'], ['Album'],
                                    ['Title'], 'Lyrics')
            tags = misc.get_tags(audio)
            self.assertEqual(tags['album'], "Album")
            self.assertEqual(tags['artist'], "Artist")
            self.assertEqual(tags['title'], "Title")
            self.assertEqual(tags['lyrics'], "Lyrics")

    def test_get_tags_single(self):
        """Test get_tags with single-tag file"""
        for mime in ['audio/mp3', 'audio/ogg']:
            audio = fakers.FakeFile(mime, 'Artist', 'Album', 'Title', 'Lyrics')
            tags = misc.get_tags(audio)
            self.assertEqual(tags['album'], "Album")
            self.assertEqual(tags['artist'], "Artist")
            self.assertEqual(tags['title'], "Title")
            self.assertEqual(tags['lyrics'], "Lyrics")

    def test_get_tags_broken(self):
        """Test get_tags with broken tags"""
        audio = fakers.BrokenFile('audio/ogg', {'test': 'Test',
                                                'album': 'Album',
                                                'title': 'Title'})
        tags = misc.get_tags(audio)
        self.assertEqual(tags, None)

    @mock.patch('lyricstagger.misc.click.edit', fakers.mock_edit_ok)
    def test_edit_lyrics_empty_ok(self):
        """Test edit_lyrics with empty lyrics and correct edit"""
        audio = fakers.FakeFile('audio/ogg', 'Artist', 'Album', 'Title')
        lyrics = misc.edit_lyrics(audio)
        self.assertEqual(lyrics, "")

    @mock.patch('lyricstagger.misc.click.edit', fakers.mock_edit_fail)
    def test_edit_lyrics_empty_fail(self):
        """Test edit_lyrics with empty lyrics and errored edit"""
        audio = fakers.FakeFile('audio/ogg', 'Artist', 'Album', 'Title')
        lyrics = misc.edit_lyrics(audio)
        self.assertEqual(lyrics, None)

    @mock.patch('lyricstagger.misc.click.edit', fakers.mock_edit_ok)
    def test_edit_lyrics_nonempty_ok(self):
        """Test edit_lyrics with non-empty lyrics and correct edit"""
        audio = fakers.FakeFile('audio/ogg', 'Artist', 'Album',
                                'Title', 'Lyrics')
        lyrics = misc.edit_lyrics(audio)
        self.assertEqual(lyrics, "Lyrics")

    @mock.patch('lyricstagger.misc.click.edit', fakers.mock_edit_fail)
    def test_edit_lyrics_nonempty_fail(self):
        """Test edit_lyrics with non-empty lyrics and errored edit"""
        audio = fakers.FakeFile('audio/ogg', 'Artist', 'Album',
                                'Title', 'Lyrics')
        lyrics = misc.edit_lyrics(audio)
        self.assertEqual(lyrics, None)

    def test_get_file_list(self):
        file_list = list(misc.get_file_list(["test/test_data"]))
        self.assertIn("test/test_data/test_dir_0/test_file_0.ogg", file_list)
        self.assertIn("test/test_data/test_dir_1/test_file_1.ogg", file_list)

# pylint: enable=R0904
if __name__ == '__main__':
    unittest.main()
