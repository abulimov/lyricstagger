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
import typing
import click
import lyricstagger.actions as actions
import lyricstagger.engine as engine


@click.group()
@click.version_option()
def main():
    """Scan music files, download missing lyrics and save it into tag."""


@main.command('tag')
@click.option('--threads', default=4, type=click.IntRange(1, None),
              help='Number of threads to use.')
@click.option('--force', default=False, is_flag=True,
              help='Overwrite existing lyrics.')
@click.argument("path_list", nargs=-1, type=click.Path(exists=True))
def tag_command(threads: int, force: bool, path_list: typing.Iterable[str]):
    """Download lyrics and tag every file."""
    label = click.style(u"Tagging...", fg="blue")
    if force:
        action = actions.tag_force
    else:
        action = actions.tag
    with engine.engine(threads=threads) as runner:
        # loop = asyncio.get_event_loop()
        # loop.run_until_complete(
        #    runner.run(path_list, action, progress=True, label=label))
        runner.run(path_list, action, progress=True, label=label)


@main.command('remove')
@click.option('--threads', default=4, type=click.IntRange(1, None),
              help='Number of threads to use.')
@click.argument("path_list", nargs=-1, type=click.Path(exists=True))
def remove_command(threads: int, path_list: typing.Iterable[str]):
    """Remove lyrics tags from every found file."""
    label = click.style(u"Removing lyrics tags...", fg="blue")
    with engine.engine(threads=threads) as runner:
        runner.run(path_list, actions.remove, progress=True, label=label)


@main.command('edit')
@click.argument("path_list", nargs=-1, type=click.Path(exists=True))
def edit_command(path_list: typing.Iterable[str]):
    """Edit lyrics for found files with EDITOR."""
    label = click.style(u"Manually editing lyrics tags...", fg="blue")
    with engine.engine(threads=1) as runner:
        runner.run(path_list, actions.edit, label=label)


@main.command('show')
@click.argument("path_list", nargs=-1, type=click.Path(exists=True))
def show_command(path_list: typing.Iterable[str]):
    """Print lyrics from found files to stdout."""
    label = click.style(u"Showing lyrics...", fg="blue")
    with engine.engine(threads=1) as runner:
        runner.run(path_list, actions.show, label=label)


@main.command('report')
@click.argument("path_list", nargs=-1, type=click.Path(exists=True))
def report_command(path_list: typing.Iterable[str]):
    """Report lyrics tag presence for musical files."""
    label = click.style(u"Status         Path", fg="blue")
    with engine.engine(threads=1) as runner:
        runner.run(path_list, actions.report, label=label)

if __name__ == '__main__':
    main()
