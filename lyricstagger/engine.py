import typing
import asyncio
import concurrent.futures
import click
import lyricstagger.log as log
import lyricstagger.misc as misc


ActionType = typing.Callable[[log.CliLogger, str], None]


class engine(object):
    """Engine runs actions, for many files, in parallel"""
    def __init__(self, threads: int = 4):
        self.logger = log.CliLogger()
        self.threads = threads
        self.loop = asyncio.get_event_loop()
        self.updates_future = None

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

    def _run_action(self, filepath: str, action: ActionType):
        """Run single action with logging"""
        self.logger.log_processing(filepath)
        action(self.logger, filepath)

    def run(self, path_list: typing.Iterable[str], action: ActionType,
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
