import tkinter as tk
from tkinter import LabelFrame, Button, simpledialog
import threading
import os
import configparser
import sys
from tk_face_read import start_face_detection
from tk_qr_reder import start_qr_read

# Determine the base directory
if getattr(sys, 'frozen', False):  # If running as a PyInstaller executable
    base_dir = sys._MEIPASS  # Temp directory for bundled files
else:
    base_dir = os.path.dirname(os.path.abspath(__file__))

# Full path to settings.ini
config_file = os.path.join(base_dir, "settings.ini")

# Initialize the configuration parser
config = configparser.ConfigParser()

# Load settings if the file exists
if os.path.exists(config_file) and config.read(config_file):
    camid_id_for_qr = config.getint("Settings", "camid_id_for_qr", fallback=0)
    cam_id_for_face = config.getint("Settings", "cam_id_for_face", fallback=1)
else:
    print(f"Error: {config_file} not found or could not be loaded.")
    camid_id_for_qr = 0  # Default QR Camera ID
    cam_id_for_face = 1  # Default Face Camera ID

# Function to configure settings and save them
def open_settings():
    global camid_id_for_qr, cam_id_for_face

    new_camid_id_for_qr = simpledialog.askinteger("Settings", "Enter Camera ID for QR Code Detection:", initialvalue=camid_id_for_qr)
    if new_camid_id_for_qr is None:
        return

    new_cam_id_for_face = simpledialog.askinteger("Settings", "Enter Camera ID for Face Detection:", initialvalue=cam_id_for_face)
    if new_cam_id_for_face is None:
        return

    camid_id_for_qr = new_camid_id_for_qr
    cam_id_for_face = new_cam_id_for_face

    config.set("Settings", "camid_id_for_qr", str(camid_id_for_qr))
    config.set("Settings", "cam_id_for_face", str(cam_id_for_face))

    with open(config_file, "w") as configfile:
        config.write(configfile)

    print(f"Settings Updated: QR Cam ID = {camid_id_for_qr}, Face Cam ID = {cam_id_for_face}")

# Initialize main application window
root = tk.Tk()
root.title("Smart Gate Pass")
root.geometry("800x400")

# Create a frame for Cam1
cam1_frame = LabelFrame(root, text="QR Code Detection", padx=10, pady=10)
cam1_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

# Create a frame for Cam2
cam2_frame = LabelFrame(root, text="Face Detection", padx=10, pady=10)
cam2_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

root.grid_columnconfigure(0, weight=1)
root.grid_columnconfigure(1, weight=1)
root.grid_rowconfigure(0, weight=1)

# Placeholder labels for camera feeds
cam1_label = tk.Label(cam1_frame, text="QR Code Detection")
cam1_label.pack(expand=True, fill="both")

cam2_label = tk.Label(cam2_frame, text="Face Detection")
cam2_label.pack(expand=True, fill="both")

# Define threads to run each camera feed function concurrently
def start_qr_thread():
    try:
        start_qr_read(camid_id_for_qr, cam1_label)
    except Exception as e:
        print(f"Error in QR Thread: {e}")

def start_face_thread():
    try:
        start_face_detection(cam_id_for_face, cam2_label)
    except Exception as e:
        print(f"Error in Face Thread: {e}")

# Create and start threads
qr_thread = threading.Thread(target=start_qr_thread, daemon=True)
face_thread = threading.Thread(target=start_face_thread, daemon=True)

qr_thread.start()
face_thread.start()

# Add a Settings button
settings_button = Button(root, text="Settings", command=open_settings)
settings_button.grid(row=1, column=0, columnspan=2, pady=10, sticky="ew")

# Run the main loop
root.mainloop()
