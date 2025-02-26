import os
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from transcriber import Transcriber


class TranscriptionHandler(FileSystemEventHandler):
    def __init__(self, monitor_dir, gui, transcriber):
        self.monitor_dir = monitor_dir
        self.gui = gui
        self.transcriber = transcriber
        self.processed_files = set()
        self.load_processed_files()

    def load_processed_files(self):
        if os.path.exists("processed_files.txt"):
            with open("processed_files.txt", "r") as f:
                self.processed_files = set(line.strip() for line in f)

    def save_processed_file(self, filepath):
        self.processed_files.add(filepath)
        with open("processed_files.txt", "a") as f:
            f.write(f"{filepath}\n")

    def on_created(self, event):
        if event.is_directory:
            return
        self.process_file(event.src_path)

    def process_file(self, filepath):
        if filepath in self.processed_files or not self.transcriber.is_supported_file(filepath):
            self.gui.update_status(f"Skipped: {os.path.basename(filepath)} (already processed)")
            return

        self.gui.update_status(f"Processing: {os.path.basename(filepath)}")
        try:
            start_time = time.time()
            transcript = self.transcriber.transcribe_file(filepath)
            end_time = time.time()
            duration = end_time - start_time
            self.transcriber.save_transcript(filepath, transcript)
            self.save_processed_file(filepath)
            self.gui.update_status(
                f"Completed: {os.path.basename(filepath)} (took {duration:.2f} seconds)"
            )
        except Exception as e:
            self.gui.update_status(f"Error processing {os.path.basename(filepath)}: {str(e)}")


class TranscriptionMonitor:
    def __init__(self, gui):
        self.gui = gui
        self.monitor_dir = None
        self.observer = None
        self.transcriber = Transcriber()
        self.handler = None  # Store handler for consistency

    def set_directory(self, directory):
        self.monitor_dir = directory

    def scan_existing_files(self):
        if not self.monitor_dir:
            return
        self.gui.update_status("Scanning existing files...")
        # Use a single handler instance
        if not self.handler:
            self.handler = TranscriptionHandler(self.monitor_dir, self.gui, self.transcriber)
        for root, _, files in os.walk(self.monitor_dir):
            for file in files:
                filepath = os.path.join(root, file)
                self.handler.process_file(filepath)

    def start_monitoring(self):
        if not self.monitor_dir:
            return
        # Reuse the same handler to preserve processed_files
        if not self.handler:
            self.handler = TranscriptionHandler(self.monitor_dir, self.gui, self.transcriber)
        self.observer = Observer()
        self.observer.schedule(self.handler, self.monitor_dir, recursive=True)
        self.observer.start()
        self.gui.update_status("Monitoring started...")

    def stop_monitoring(self):
        if self.observer:
            self.observer.stop()
            self.observer.join()
            self.observer = None
            self.gui.update_status("Monitoring stopped")

    def process_single_file(self, file_path):
        if self.monitor_dir and os.path.dirname(file_path) != self.monitor_dir:
            import shutil
            dest_path = os.path.join(self.monitor_dir, os.path.basename(file_path))
            shutil.copy(file_path, dest_path)
            file_path = dest_path
        if not self.handler:
            self.handler = TranscriptionHandler(self.monitor_dir, self.gui, self.transcriber)
        self.handler.process_file(file_path)