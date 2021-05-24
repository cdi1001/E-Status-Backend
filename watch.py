import sys
import time
import logging
import os
import subprocess
from watchdog.observers import Observer
from watchdog.events import LoggingEventHandler


class SourceWatchHandler(LoggingEventHandler):

    def on_modified(self, event):
        super(LoggingEventHandler, self).on_modified(event)
        subprocess.call(['make', 'generate_dev'])


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')
    BASE_PATH = os.path.dirname(os.path.realpath(__file__))
    path = os.path.join(BASE_PATH, 'source')
    event_handler = SourceWatchHandler()
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
