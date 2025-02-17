import os
import cv2
import pyttsx3
import pyvirtualcam
import multiprocessing
import logging
import sys
import traceback
import json
import colorama
from cvzone.PoseModule import PoseDetector
from pyvirtualcam import PixelFormat
from datetime import datetime
from os import environ
from dotenv import load_dotenv

from dependencies.Webhook import WebhookBuilder
from dependencies.Facerec import Facerec

# Initialize colorama for colored terminal output
colorama.init()

# Load configuration (ensure config.json is in the same directory as main.py)
config_path = os.path.join(os.path.dirname(__file__), "config.json")
try:
    with open(config_path, "r") as f:
        config = json.load(f)
    IMAGES_PATH = config["images_path"]
    TEMP_PATH = config["temp_path"]
    # Additional config settings
    body_inc = config["camera"]["body_inc"]
    face_inc = config["camera"]["face_inc"]
    motion_inc = config["camera"]["motion_inc"]
    undetected_time = config["camera"]["undetected_time"]
    motion_detection = config["settings"]["motion_detection"]
    speech = config["settings"]["speech"]
    webserver = config["settings"]["webserver"]
    notifications = config["settings"]["discord_notifications"]
    cam_n = config["camera"]["main"]
    fallback_fps = config["camera"]["fallback_fps"]
except (FileNotFoundError, json.JSONDecodeError, KeyError) as e:
    print(f"Error loading config.json: {e}")
    exit(1)

# Create directories for images and temp files (at the project root)
images_path = os.path.join(os.path.dirname(__file__), "..", IMAGES_PATH)
os.makedirs(images_path, exist_ok=True)
temp_path = os.path.join(os.path.dirname(__file__), "..", TEMP_PATH)
os.makedirs(temp_path, exist_ok=True)

# Setup logging
log_path = os.path.join(os.path.dirname(__file__), "logs")
os.makedirs(log_path, exist_ok=True)
logger = logging.getLogger('logger')
fh = logging.FileHandler(os.path.join(log_path, "s_cam.log"))
logger.addHandler(fh)
def exc_handler(exctype, value, tb):
    logger.exception(''.join(traceback.format_exception(exctype, value, tb)))
sys.excepthook = exc_handler

# Load environment variables
load_dotenv()
url = environ.get("URL")  # Use .get to avoid KeyError if URL is not set

# Initialize text-to-speech engine
engine = pyttsx3.init()
def speak(text):
    print(text)
    if speech:
        engine.say(text)
        engine.runAndWait()

# Discord bot command
@bot.command()
async def addface(ctx, name):
    temp_file_path = os.path.join(temp_path, f"ud_{name}.jpg")
    # ... other code for adding face

# Main loop
if __name__ == '__main__':
    multiprocessing.freeze_support()
    cap = cv2.VideoCapture(cam_n)
    if not cap.isOpened():  # Check if camera opened successfully
        print(f"Error: Could not open camera {cam_n}")
        sys.exit(1)
    cap.set(3, 1280)
    cap.set(4, 720)
    detector = PoseDetector(detectionCon=0.5, trackCon=0.5)

    webhook = WebhookBuilder(url, os.path.dirname(__file__))
    fr = Facerec()
    fr.load_encoding_images(images_path)  # Load face encodings

    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    if fps == 0.0:
        fps = fallback_fps
    size = (frame_width, frame_height)

    with pyvirtualcam.Camera(frame_width, frame_height, fps, fmt=PixelFormat.BGR) as cam:
        while True:
            ret, frame = cap.read()
            if not ret:  # Check if frame reading was successful
                print("Error: Could not read frame.")
                break

            # Motion detection
            # ... (your motion detection logic here)

            # Face recognition 
            face_locations, face_names = fr.detect_known_faces(frame)
            for (y1, x2, y2, x1), name in zip(face_locations, face_names):
                if name == "Unknown":
                    color = (0, 0, 225)
                else:
                    color = (0, 225, 0)
                cv2.putText(frame, name, (x1, y1 - 10), cv2.FONT_HERSHEY_DUPLEX, 1, color, 1)
                cv2.rectangle(frame, (x1, y1), (x2, y2), color, 1)

            if len(face_locations) > 0:
                face_c += 1
                face = True
                face_det.append(name)
            else:
                face = False

            # ... (rest of your body detection, recording, reset, files, and notification logic)

            if webserver:
                cam.send(frame)
                cam.sleep_until_next_frame()

    cap.release()
    cv2.destroyAllWindows()
