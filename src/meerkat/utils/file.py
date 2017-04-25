# -*- coding: utf-8 -*-

import os
import time


def follow(file_name, seek_end):
    with open(file_name) as f:
        if seek_end:
            f.seek(0, 2)
        while True:
            line = f.readline()
            if not line:
                try:
                    if f.tell() > os.path.getsize(file_name):
                        f.close()
                        break
                except FileNotFoundError:
                    pass
                time.sleep(1)
                continue
            yield line
