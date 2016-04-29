from threading import Thread
import typing
import click
import lyricstagger.log as log
import lyricstagger.misc as misc

from queue import Queue


ActionType = typing.Callable[[log.CliLogger, str], None]


class ActionThread(Thread):
    """Thread to perform action"""

    def __init__(self, logger: log.CliLogger, action: ActionType,
                 file_queue: Queue, result_queue: Queue = None):
        Thread.__init__(self)
        self.action = action
        self.logger = logger
        self.file_queue = file_queue
        self.result_queue = result_queue

    def run(self):
        while True:
            filepath = self.file_queue.get()
            self.logger.log_processing(filepath)
            self.action(self.logger, filepath)
            self.file_queue.task_done()
            if self.result_queue:
                self.result_queue.put(filepath)


class Engine(object):

    def __init__(self, threads: int = 4, logger: log.CliLogger = None):
        if logger:
            self.logger = logger
        else:
            self.logger = log.CliLogger()
        self.threads = threads

    def _massive_action_with_progress(self, path_list: typing.List[str],
                                      action: ActionType, label: str = "") -> None:
        """Run action function in threads for each file in path_list with progressbar"""
        file_queue = Queue()
        result_queue = Queue()
        for _ in range(self.threads):
            trd = ActionThread(self.logger, action, file_queue, result_queue)
            trd.setDaemon(True)
            trd.start()

        # get length of generator without converting it to list,
        # saves memory on large file lists, but can be a bit slower
        max_files = sum(1 for _ in misc.get_file_list(path_list))

        for filepath in misc.get_file_list(path_list):
            file_queue.put(filepath)

        with click.progressbar(label=label,
                               length=max_files) as progressbar:
            for _ in progressbar:
                result_queue.get()

        file_queue.join()


    def _massive_action(self, path_list: typing.List[str],
                        action: ActionType, label: str = "") -> None:
        """Run action function in threads for each file in path_list"""
        file_queue = Queue()
        for _ in range(self.threads):
            trd = ActionThread(self.logger, action, file_queue)
            trd.setDaemon(True)
            trd.start()
        if label:
            click.echo(label)
        for filepath in misc.get_file_list(path_list):
            file_queue.put(filepath)
        file_queue.join()


    def massive_action(self, path_list: typing.List[str], action: ActionType,
                       progress: bool = False, label: str = "") -> None:
        """Selector for _massive_action functions"""
        if progress:
            self._massive_action_with_progress(path_list, action, label)
        else:
            self._massive_action(path_list, action, label)

        click.echo(self.logger.show_stats())