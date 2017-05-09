# -*- coding: utf-8 -*-

import os
import time


def follow(file_name, seek_end, wait=1, stop_condition=lambda: False):
    with open(file_name) as f:
        if seek_end:
            f.seek(0, 2)
        while True:
            if stop_condition():
                break
            line = f.readline()
            if not line:
                try:
                    if f.tell() > os.path.getsize(file_name):
                        break
                except FileNotFoundError:
                    pass
                time.sleep(wait)
                continue
            yield line


def count_lines(file_name):
    i = -1
    with open(file_name) as f:
        for i, _ in enumerate(f):
            pass
    return i + 1
