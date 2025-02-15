import os, cv2, pyttsx3, pyvirtualcam, multiprocessing, logging, sys, traceback, json, colorama
from cvzone.PoseModule import PoseDetector
from pyvirtualcam import PixelFormat
from datetime import datetime
from os import environ
from dotenv import load_dotenv

from dependencies.Webhook import WebhookBuilder
from dependencies.Facerec import Facerec

# Initialize colorama for colored terminal output
colorama.init()

# Setup logging
os.makedirs(os.path.join(os.path.dirname(__file__), "logs\\"), exist_ok=True)
logger = logging.getLogger('logger')
fh = logging.FileHandler(os.path.join(os.path.dirname(__file__), "logs\s_cam.log"))
logger.addHandler(fh)
def exc_handler(exctype, value, tb):
    logger.exception(''.join(traceback.format_exception(exctype, value, tb)))
sys.excepthook = exc_handler

# Load environment variables and configuration
load_dotenv()
with open(os.path.join(os.path.dirname(__file__), "config.json"), "r") as conf_file:
    config = json.load(conf_file)

# Configuration settings
body_inc = config["camera"]["body_inc"]
face_inc = config["camera"]["face_inc"]
motion_inc = config["camera"]["motion_inc"]
undetected_time = config["camera"]["undetected_time"]
motion_detection = config["settings"]["motion_detection"]
speech = config["settings"]["speech"]
webserver = config["settings"]["webserver"]
notifications = config["settings"]["discord_notifications"]
url = environ.get("URL") # Use .get to avoid KeyError if URL is not set
cam_n = config["camera"]["main"]
fallback_fps = config["camera"]["fallback_fps"]

# Initialize text-to-speech engine
engine = pyttsx3.init()
def speak(text):
    print(text)
    if speech:
        engine.say(text)
        engine.runAndWait()

# Main loop
if __name__ == '__main__':
    multiprocessing.freeze_support()
    cap = cv2.VideoCapture(cam_n)
    if not cap.isOpened():  # Check if camera opened successfully
        print(f"Error: Could not open camera {cam_n}")
        sys.exit()
    cap.set(3, 1280)
    cap.set(4, 720)
    detector = PoseDetector(detectionCon=0.5, trackCon=0.5)

    webhook = WebhookBuilder(url, os.path.dirname(__file__))
    fr = Facerec()
    fr.load_encoding_images(os.path.join(os.path.dirname(__file__), r".\images"))

    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    if fps == 0.0:
        fps = fallback_fps
    size = (frame_width, frame_height)

    # ... (rest of the variable initialization)

    with pyvirtualcam.Camera(frame_width, frame_height, fps, fmt=PixelFormat.BGR) as cam:
        while True:
            # ... (check_frame_index code)

            ret, frame = cap.read()
            if not ret:  # Check if frame reading was successful
                print("Error: Could not read frame.")
                break

            # Motion detection (same as before)
            # ...

            # Face recognition (using the improved code)
            face_locations, face_names = fr.detect_known_faces(frame)  # Assuming this function handles encoding and comparison
            for (y1, x2, y2, x1), name in zip(face_locations, face_names): #unpacking face_location
                if name == "Unknown":
                    color = (0, 0, 225)
                else:
                    color = (0, 225, 0)
                cv2.putText(frame, name, (x1, y1 - 10), cv2.FONT_HERSHEY_DUPLEX, 1, color, 1)
                cv2.rectangle(frame, (x1, y1), (x2, y2), color, 1)

            if len(face_locations) > 0:  # Use len() to check list length
                face_c += 1
                face = True
                face_det.append(name)
            else:
                face = False

            # ... (rest of the body detection, recording, reset, files, and notification logic)

            if webserver:
                cam.send(frame) #send the current frame
                cam.sleep_until_next_frame()

    cap.release()
    cv2.destroyAllWindows()
