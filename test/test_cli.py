"""
Tests for CLI interface
"""
from __future__ import unicode_literals
from __future__ import print_function
import mock
import unittest
import lyricstagger.console as cli
import lyricstagger.log as log
import fakers


class CliCheck(unittest.TestCase):
    """Test console interface"""
    def test_cli_tag_empty_list(self):
        """Test tag command for empty file_list"""
        logger = log.cli_logger()
        cli.tag(logger, [])
        self.assertEqual(0, logger.stats['processed'])

    @mock.patch('lyricstagger.misc.get_audio', fakers.mock_get_audio)
    def test_cli_tag_ok_list(self):
        """Test tag command for real file_list"""
        logger = log.cli_logger()
        cli.tag(logger, ["test/test_data"])
        self.assertEqual(2, logger.stats['processed'])
        self.assertEqual(0, logger.stats['written'])

    def test_cli_remove_empty_list(self):
        """Test remove command for empty file_list"""
        logger = log.cli_logger()
        cli.remove(logger, [])
        self.assertEqual(0, logger.stats['processed'])

    @mock.patch('lyricstagger.misc.get_audio', fakers.mock_get_audio)
    def test_cli_remove_ok_list(self):
        """Test remove command for real file_list"""
        logger = log.cli_logger()
        cli.remove(logger, ["test/test_data"])
        self.assertEqual(2, logger.stats['processed'])
        self.assertEqual(2, logger.stats['removed'])

    def test_cli_edit_empty_list(self):
        """Test edit command for empty file_list"""
        logger = log.cli_logger()
        cli.edit(logger, [])
        self.assertEqual(0, logger.stats['processed'])

    @mock.patch('lyricstagger.misc.get_audio', fakers.mock_get_audio)
    @mock.patch('lyricstagger.misc.subprocess.check_call', fakers.mock_call_ok)
    def test_cli_edit_ok_list(self):
        """Test edit command for real file_list"""
        logger = log.cli_logger()
        cli.edit(logger, ["test/test_data"])
        self.assertEqual(2, logger.stats['processed'])
        self.assertEqual(2, logger.stats['written'])

    def test_cli_show_empty_list(self):
        """Test show command for empty file_list"""
        logger = log.cli_logger()
        cli.show(logger, [])
        self.assertEqual(0, logger.stats['processed'])

    @mock.patch('lyricstagger.misc.get_audio', fakers.mock_get_audio)
    def test_cli_show_ok_list(self):
        """Test show command for real file_list"""
        logger = log.cli_logger()
        cli.show(logger, ["test/test_data"])
        self.assertEqual(2, logger.stats['processed'])
        self.assertEqual(0, logger.stats['not_found'])

    def test_cli_report_empty_list(self):
        """Test report command for empty file_list"""
        logger = log.cli_logger()
        cli.report(logger, [])
        self.assertEqual(0, logger.stats['processed'])

    @mock.patch('lyricstagger.misc.get_audio', fakers.mock_get_audio)
    def test_cli_report_ok_list(self):
        """Test report command for real file_list"""
        logger = log.cli_logger()
        cli.report(logger, ["test/test_data"])
        self.assertEqual(2, logger.stats['processed'])
        self.assertEqual(0, logger.stats['not_found'])
