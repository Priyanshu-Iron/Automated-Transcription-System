import tkinter as tk
from gui import TranscriptionGUI
from file_monitor import TranscriptionMonitor

def main():
    root = tk.Tk()
    gui = TranscriptionGUI(root)
    monitor = TranscriptionMonitor(gui)
    gui.set_monitor(monitor)
    root.protocol("WM_DELETE_WINDOW", gui.on_closing)
    root.mainloop()

if __name__ == "__main__":
    main()