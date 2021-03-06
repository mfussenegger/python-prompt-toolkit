from __future__ import unicode_literals

from ..utils import EventHook
import threading

__all__ = (
    'BaseEventLoop',
)


class BaseEventLoop(object):
    #: When to trigger the `onInputTimeout` event.
    input_timeout = .5

    def __init__(self, input_processor, stdin):
        self.stdin = stdin
        self.input_processor = input_processor

        #: Called when there is no input for x seconds.
        #:   At this event, you can for instance start a background thread to
        #:   generate information about the input. E.g. get the code signature
        #:   of the function below the cursor position in the case of a REPL.
        self.onInputTimeout = EventHook()

        self._calls_from_executor = []
        self.closed = False

    def loop(self):
        raise NotImplementedError

    def close(self):
        self.closed = True

    def run_in_executor(self, callback):
        """
        Run a long running function in a background thread.
        (This is recommended for code that could block the `read_input` event
        loop.)
        Similar to Twisted's ``deferToThread``.
        """
        class _Thread(threading.Thread):
            def run(t):
                callback()

        _Thread().start()

    def call_from_executor(self, callback):
        raise NotImplementedError

    def process_queued_calls_from_executor(self):
        # Process calls from executor.
        calls_from_executor, self._calls_from_executor = self._calls_from_executor, []
        for c in calls_from_executor:
            c()
