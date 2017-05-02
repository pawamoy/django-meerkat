# -*- coding: utf-8 -*-

import threading


class StoppableThread(threading.Thread):
    """Thread class with a stop() method. The thread itself has to check
    regularly for the stopped() condition."""

    def __init__(self, *args, **kwargs):
        super(StoppableThread, self).__init__(*args, **kwargs)
        self._stopped = threading.Event()

    def stop(self):
        self._stopped.set()

    def stopped(self):
        return self._stopped.isSet()
