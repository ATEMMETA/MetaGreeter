import os, cv2, pyttsx3, pyvirtualcam, multiprocessing, logging, sys, traceback, json, colorama, glob, requests, discord
from cvzone.PoseModule import PoseDetector
from pyvirtualcam import PixelFormat
from datetime import datetime
from os import environ
from dotenv import load_dotenv
from discord.ext import commands

from dependencies.Webhook import WebhookBuilder
from dependencies.Facerec import Facerec

# ... (colorama initialization, config loading, directory creation, logging setup, environment variables, text-to-speech)

ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png'}

intents = discord.Intents.default()
intents.message_content = True  # If you need to read message content
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.command()
async def addface(ctx, name):
    # ... (addface command code - make sure findface returns a valid path)

# Main loop
if __name__ == '__main__':
    multiprocessing.freeze_support()
    cap = cv2.VideoCapture(cam_n)
    if not cap.isOpened():
        print(f"Error: Could not open camera {cam_n}")
        sys.exit(1)
    cap.set(3, 1280)
    cap.set(4, 720)
    detector = PoseDetector(detectionCon=0.5, trackCon=0.5)  # If you're using pose detection

    webhook = WebhookBuilder(url, os.path.dirname(__file__))  # If you're using webhooks
    fr = Facerec()
    fr.load_encoding_images(images_path)

    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    if fps == 0.0:
        fps = fallback_fps

    with pyvirtualcam.Camera(frame_width, frame_height, fps, fmt=PixelFormat.BGR) as cam:
        face_c = 0
        face = False
        face_det = []  # Initialize the list to store detected face names

        while True:
            try:
                ret, frame = cap.read()
                if not ret:
                    break

                # Motion detection (add your logic here later)
                # ...

                # Face recognition
                face_locations, face_names = fr.detect_known_faces(frame)
                for (y1, x2, y2, x1), name in zip(face_locations, face_names):
                    if name == "Unknown":
                        color = (0, 0, 225)
                    else:
                        color = (0, 225, 0)
                    cv2.putText(frame, name, (x1, y1 - 10), cv2.FONT_HERSHEY_DUPLEX, 1, color, 1)
                    cv2.rectangle(frame, (x1, y1), (x2, y2), color, 1)

                    if name != "Unknown":  # Only store known faces
                        face_det.append(name)  # Add the detected name to the list

                if len(face_locations) > 0:
                    face_c += 1
                    face = True
                else:
                    face = False

                # Body detection, recording, etc. (add your logic here later)
                # ...

                if webserver:
                    cam.send(frame)
                    cam.sleep_until_next_frame()

            except cv2.error as e:
                logger.exception(f"OpenCV error in main loop: {e}")
                print(f"An OpenCV error occurred: {e}")
                break
            except Exception as e:
                logger.exception(f"Error in main loop: {e}")
                print(f"A general error occurred: {e}")
                break

    cap.release()
    cv2.destroyAllWindows()
    bot.run(os.getenv('DISCORD_TOKEN'))

