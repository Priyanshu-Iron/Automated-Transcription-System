import tkinter as tk
from tkinter import filedialog
import time
import os


class TranscriptionGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Automated Transcription System")
        self.root.geometry("600x400")
        self.monitor = None
        self.processing = False
        self.animation_dots = 0

        # GUI Elements
        self.directory_label = tk.Label(root, text="No directory selected")
        self.directory_label.pack(pady=10)

        self.select_btn = tk.Button(root, text="Select Directory", command=self.select_directory)
        self.select_btn.pack(pady=5)

        self.upload_btn = tk.Button(root, text="Upload File", command=self.upload_file)
        self.upload_btn.pack(pady=5)

        self.start_btn = tk.Button(root, text="Start Monitoring", command=self.start_monitoring, state="disabled")
        self.start_btn.pack(pady=5)

        self.stop_btn = tk.Button(root, text="Stop Monitoring", command=self.stop_monitoring, state="disabled")
        self.stop_btn.pack(pady=5)

        # Processing animation label
        self.processing_label = tk.Label(root, text="", font=("Arial", 12))
        self.processing_label.pack(pady=5)

        self.status_text = tk.Text(root, height=15, width=70)
        self.status_text.pack(pady=10)

    def set_monitor(self, monitor):
        self.monitor = monitor

    def select_directory(self):
        directory = filedialog.askdirectory()
        if directory:
            self.directory_label.config(text=f"Selected: {directory}")
            self.start_btn.config(state="normal")
            self.monitor.set_directory(directory)
            self.monitor.scan_existing_files()

    def upload_file(self):
        if not self.monitor or not self.monitor.monitor_dir:
            self.update_status("Please select a directory first!")
            return

        file_path = filedialog.askopenfilename(
            filetypes=[
                ("Media files", "*.mp3 *.wav *.mp4 *.mkv *.mov *.flv *.aac *.m4a"),
                ("All files", "*.*")
            ]
        )
        if file_path:
            self.monitor.process_single_file(file_path)
            self.update_status(f"Uploaded and queued for processing: {os.path.basename(file_path)}")

    def start_monitoring(self):
        if self.monitor:
            self.monitor.start_monitoring()
            self.start_btn.config(state="disabled")
            self.stop_btn.config(state="normal")
            self.update_status("Monitoring started...")

    def stop_monitoring(self):
        if self.monitor:
            self.monitor.stop_monitoring()
            self.start_btn.config(state="normal")
            self.stop_btn.config(state="disabled")
            self.update_status("Monitoring stopped")

    def update_status(self, message):
        timestamp = time.strftime('%H:%M:%S')
        self.status_text.insert(tk.END, f"{timestamp} - {message}\n")
        self.status_text.see(tk.END)
        # Update processing animation
        if "Processing" in message:
            self.processing = True
            self.animate_processing()
        elif "Completed" in message or "Error" in message:
            self.processing = False
            self.processing_label.config(text="")

    def animate_processing(self):
        if not self.processing:
            return
        dots = "." * (self.animation_dots % 4)
        self.processing_label.config(text=f"Processing{dots}")
        self.animation_dots += 1
        self.root.after(500, self.animate_processing)  # Update every 500ms

    def on_closing(self):
        if self.monitor:
            self.monitor.stop_monitoring()
        self.root.destroy()