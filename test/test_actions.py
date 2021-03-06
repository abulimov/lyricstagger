"""
Tests for actions
"""
from __future__ import unicode_literals
from __future__ import print_function
import mock
import unittest
import lyricstagger.actions as a
import lyricstagger.engine as engine
from test import fakers


class CliCheck(unittest.TestCase):
    """Test console interface"""
    def test_cli_tag_empty_list(self):
        """Test tag command for empty file_list"""
        runner = engine.engine()
        runner.run([], a.tag)
        self.assertEqual(0, runner.logger.stats['processed'])

    @mock.patch('lyricstagger.misc.get_audio', fakers.mock_get_audio)
    def test_cli_tag_ok_list(self):
        """Test tag command for real file_list"""
        runner = engine.engine()
        runner.run(["test/test_data"], a.tag)
        self.assertEqual(2, runner.logger.stats['processed'])
        self.assertEqual(0, runner.logger.stats['written'])

    def test_cli_remove_empty_list(self):
        """Test remove command for empty file_list"""
        runner = engine.engine()
        runner.run([], a.remove)
        self.assertEqual(0, runner.logger.stats['processed'])

    @mock.patch('lyricstagger.misc.get_audio', fakers.mock_get_audio)
    def test_cli_remove_ok_list(self):
        """Test remove command for real file_list"""
        runner = engine.engine()
        runner.run(["test/test_data"], a.remove)
        self.assertEqual(2, runner.logger.stats['processed'])
        self.assertEqual(2, runner.logger.stats['removed'])

    def test_cli_edit_empty_list(self):
        """Test edit command for empty file_list"""
        runner = engine.engine()
        runner.run([], a.edit)
        self.assertEqual(0, runner.logger.stats['processed'])

    @mock.patch('lyricstagger.misc.get_audio', fakers.mock_get_audio)
    @mock.patch('lyricstagger.misc.click.edit', fakers.mock_edit_ok)
    def test_cli_edit_ok_list(self):
        """Test edit command for real file_list"""
        runner = engine.engine()
        runner.run(["test/test_data"], a.edit)
        self.assertEqual(2, runner.logger.stats['processed'])
        self.assertEqual(2, runner.logger.stats['written'])

    def test_cli_show_empty_list(self):
        """Test show command for empty file_list"""
        runner = engine.engine()
        runner.run([], a.show)
        self.assertEqual(0, runner.logger.stats['processed'])

    @mock.patch('lyricstagger.misc.get_audio', fakers.mock_get_audio)
    def test_cli_show_ok_list(self):
        """Test show command for real file_list"""
        runner = engine.engine()
        runner.run(["test/test_data"], a.show)
        self.assertEqual(2, runner.logger.stats['processed'])
        self.assertEqual(0, runner.logger.stats['not_found'])

    def test_cli_report_empty_list(self):
        """Test report command for empty file_list"""
        runner = engine.engine()
        runner.run([], a.report)
        self.assertEqual(0, runner.logger.stats['processed'])

    @mock.patch('lyricstagger.misc.get_audio', fakers.mock_get_audio)
    def test_cli_report_ok_list(self):
        """Test report command for real file_list"""
        runner = engine.engine()
        runner.run(["test/test_data"], a.report)
        self.assertEqual(2, runner.logger.stats['processed'])
        self.assertEqual(0, runner.logger.stats['not_found'])
