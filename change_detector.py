import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from typing import Callable 

class ChangeDetector(FileSystemEventHandler):
    def __init__(self, callback: Callable, debounce_seconds: int = 2):
        self.callback = callback
        self.debounce_seconds = debounce_seconds
        self.last_triggered = 0
    
    def on_any_event(self, event):
        # Ignore directory events and git internal files
        if event.is_directory or '.git' in event.src_path:
            return
        
        current_time = time.time()
        if current_time - self.last_triggered > self.debounce_seconds:
            self.last_triggered = current_time
            self.callback()


def watch_repository(repo_path: str, callback: Callable):
    """Watch a repository for file changes"""
    event_handler = ChangeDetector(callback)
    observer = Observer()
    observer.schedule(event_handler, repo_path, recursive=True)
    observer.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
