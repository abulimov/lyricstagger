"""lyricstagger

Usage:
  lyricstagger (tag|remove|report|edit|show) (<path>...)
  lyricstagger --help
  lyricstagger --version

Options:
  --help                  Show this screen.
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
from __future__ import print_function
import sys
try:
    import click
except ImportError:
    sys.exit(u"Missing click module (install: pip install click)")
import lyricstagger.actions as actions


@click.group()
@click.version_option()
def main():
    """Scan music files, download missing lyrics and save it into tag."""


@main.command('tag')
@click.option('--threads', default=4, type=click.IntRange(1, None),
              help='Number of threads to use.')
@click.argument("path_list", nargs=-1, type=click.Path(exists=True))
@actions.summary
def tag_command(logger, threads, path_list):
    """Download lyrics and tag every file."""
    label = click.style(u"Tagging...", fg="blue")
    actions.massive_action(logger, path_list, actions.tag,
                           threads=threads,
                           progress=True,
                           label=label)


@main.command('remove')
@click.option('--threads', default=4, type=click.IntRange(1, None),
              help='Number of threads to use.')
@click.argument("path_list", nargs=-1, type=click.Path(exists=True))
@actions.summary
def remove_command(logger, threads, path_list):
    """Remove lyrics tags from every found file."""
    label = click.style(u"Removing lyrics tags...", fg="blue")
    actions.massive_action(logger, path_list, actions.remove,
                           threads=threads,
                           progress=True,
                           label=label)


@main.command('edit')
@click.argument("path_list", nargs=-1, type=click.Path(exists=True))
@actions.summary
def edit_command(logger, path_list):
    """Edit lyrics for found files with EDITOR."""
    label = click.style(u"Manually editing lyrics tags...", fg="blue")
    actions.massive_action(logger, path_list, actions.edit, label=label)


@main.command('show')
@click.argument("path_list", nargs=-1, type=click.Path(exists=True))
@actions.summary
def show_command(logger, path_list):
    """Print lyrics from found files to stdout."""
    label = click.style(u"Showing lyrics...", fg="blue")
    actions.massive_action(logger, path_list, actions.show, label=label)


@main.command('report')
@click.argument("path_list", nargs=-1, type=click.Path(exists=True))
@actions.summary
def report_command(logger, path_list):
    """Report lyrics tag presence for musical files."""
    label = click.style(u"Status         Path", fg="blue")
    actions.massive_action(logger, path_list, actions.report, label=label)

if __name__ == '__main__':
    main()
