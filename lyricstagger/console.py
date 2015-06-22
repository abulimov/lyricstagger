"""lyricstagger

Usage:
  lyricstagger (tag|remove|report|edit|show) (<path>...)
  lyricstagger (-h | --help)
  lyricstagger --version

Options:
  -h --help                  Show this screen.
  --version                  Show version.
  <path>                     Path to start recursive search for files, \
or list of files.
  remove                     Remove lyrics tags from every found file.
  tag                        Download lyrics and add lyrics tag \
for every found file.
  report                     Show all found files without lyrics tag.
  edit                       Edit lyrics for found files with EDITOR.
  show                       Print lyrics from found files to stdout.
"""
from __future__ import unicode_literals
from __future__ import print_function
import sys
import lyricstagger.actions as actions
try:
    import click
except ImportError:
    sys.exit("Missing click module (install: pip install click)")


@click.group()
@click.version_option()
def main():
    """Scan music files, download missing lyrics and save it into tag."""


@main.command('tag')
@click.argument("path_list", nargs=-1, type=click.Path(exists=True))
@actions.summary
def tag_command(logger, path_list):
    """Download lyrics and tag every file."""
    actions.massive_action(logger, path_list, actions.tag, progress=True)


@main.command('remove')
@click.argument("path_list", nargs=-1, type=click.Path(exists=True))
@actions.summary
def remove_command(logger, path_list):
    """Remove lyrics tags from every found file."""
    actions.massive_action(logger, path_list, actions.remove, progress=True)


@main.command('edit')
@click.argument("path_list", nargs=-1, type=click.Path(exists=True))
@actions.summary
def edit_command(logger, path_list):
    """Edit lyrics for found files with EDITOR."""
    actions.massive_action(logger, path_list, actions.edit)


@main.command('show')
@click.argument("path_list", nargs=-1, type=click.Path(exists=True))
@actions.summary
def show_command(logger, path_list):
    """Print lyrics from found files to stdout."""
    actions.massive_action(logger, path_list, actions.show)


@main.command('report')
@click.argument("path_list", nargs=-1, type=click.Path(exists=True))
@actions.summary
def report_command(logger, path_list):
    """Report lyrics tag presence for musical files."""
    click.secho("Status         Path", fg="blue")
    actions.massive_action(logger, path_list, actions.report)
