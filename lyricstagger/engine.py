import typing
import asyncio
import concurrent.futures
from enum import Enum
import click
import lyricstagger.log as log
import lyricstagger.misc as misc


class Action(Enum):
    edit = 1
    tag = 2
    tag_force = 3
    remove = 4
    show = 5
    report = 6


class engine(object):
    """Engine runs actions, for many files, in parallel"""
    def __init__(self, threads: int = 4):
        self.logger = log.CliLogger()
        self.threads = threads
        self.loop = asyncio.get_event_loop()
        self.updates_future = None
        self.action_map = {
            Action.edit: self.edit,
            Action.tag: self.tag,
            Action.tag_force: self.tag_force,
            Action.remove: self.remove,
            Action.show: self.show,
            Action.report: self.report,
        }

    def __enter__(self):
        self.updates_future = self.loop.run_in_executor(None, misc.have_updates)
        return self

    def __exit__(self, *_):
        self.loop.run_until_complete(self.updates_future)
        needs_update, latest = self.updates_future.result()
        if needs_update:
            message = click.style("New version of 'lyricstagger' available: ", fg="green")
            version_colored = click.style("{0}".format(latest), fg="blue")
            update_command = click.style(
                "pip install --upgrade 'git+https://github.com/abulimov/lyricstagger#egg=lyricstagger'",
                fg="blue")
            click.echo(message + version_colored)
            click.echo(
                click.style("Update with `", fg="green") +
                update_command +
                click.style("`", fg="green"))
        click.echo(self.logger.show_stats())

    def tag(self, filepath: str, overwrite: bool = False) -> None:
        """Try to tag lyrics for given file"""
        audio = misc.get_audio(filepath)
        data = misc.get_tags(audio)
        # we cannot find lyrics if we don't have tags
        if data:
            if overwrite or "lyrics" not in data:
                lyrics = misc.fetch(data["artist"],
                                    data["title"],
                                    data["album"])
                if lyrics:
                    self.logger.log_writing(filepath)
                    audio = misc.write_lyrics(audio, lyrics)
                    audio.save()
                else:
                    self.logger.log_not_found(filepath)

    def tag_force(self, filepath: str) -> None:
        """Wrapper for tag action setting overwrite to true"""
        self.tag(filepath, overwrite=True)

    def remove(self, filepath: str) -> None:
        """Remove given file"""
        audio = misc.get_audio(filepath)
        self.logger.log_removing(filepath)
        misc.remove_lyrics(audio)
        audio.save()

    def edit(self, filepath: str) -> None:
        """Edit given file's lyrics with EDITOR"""
        audio = misc.get_audio(filepath)
        lyrics = misc.edit_lyrics(audio)
        if lyrics:
            self.logger.log_writing(filepath)
            audio = misc.write_lyrics(audio, lyrics)
            audio.save()
        else:
            self.logger.log_no_lyrics_saved(filepath)

    def show(self, filepath: str) -> None:
        """Pretty print lyrics from given file"""
        audio = misc.get_audio(filepath)
        data = misc.get_tags(audio)
        if data and "lyrics" in data:
            click.secho("%s" % click.format_filename(filepath), fg="blue")
            click.secho("Artist: %s, Title: %s" % (data["artist"],
                                                   data["title"]),
                        fg="blue")
            click.echo()
            click.echo(data["lyrics"])
            click.echo()
        else:
            self.logger.log_not_found(filepath)
            click.secho("No lyrics in file '%s'" % filepath, fg="red")

    def report(self, filepath: str) -> None:
        """Show lyrics presence in given file"""
        audio = misc.get_audio(filepath)
        data = misc.get_tags(audio)
        if data and 'lyrics' not in data:
            self.logger.log_not_found(filepath)
            click.secho("no lyrics:    ", nl=False, fg="red")
        else:
            click.secho("lyrics found: ", nl=False, fg="green")
        click.echo("%s" % click.format_filename(filepath))

    def _run_action(self, filepath: str, action: Action):
        """Run single action with logging"""
        self.logger.log_processing(filepath)
        self.action_map[action](filepath)

    def run(self, path_list: typing.Iterable[str], action: Action,
            progress: bool=False, label: str="") -> None:
        """Run action function in threads for each file in path_list"""

        if progress:
            # we use click and async function to show progress bar
            async def wait_with_progress(coros):
                with click.progressbar(label=label,
                                       length=len(coros)) as progressbar:
                    for feature in asyncio.as_completed(coros, loop=self.loop):
                        await feature
                        progressbar.update(1)

            wait = wait_with_progress
        else:
            # just show the label if specified
            if label:
                click.echo(label)
            wait = asyncio.wait

        executor = concurrent.futures.ThreadPoolExecutor(self.threads)

        futures = [
            self.loop.run_in_executor(executor, self._run_action, filepath, action)
            for filepath in misc.get_file_list(path_list)
        ]
        if futures:
            self.loop.run_until_complete(
                wait(futures)
            )
