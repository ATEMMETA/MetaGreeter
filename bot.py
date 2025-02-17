import discord
import os
import asyncio
import logging
import sys
import traceback
import requests
import random
import colorama
import glob
import json
from discord.ext import commands
from os import environ
from dotenv import load_dotenv
from dependencies.Facedet import FaceDet  # Make sure this import is correct

colorama.init()

# Configuration
load_dotenv()
try:
    with open("config.json", "r") as f:
        config = json.load(f)
    TOKEN = os.environ.get("TOKEN") or config["token"]
    IMAGES_PATH = config["images_path"]
    TEMP_PATH = config["temp_path"]
except FileNotFoundError:
    print("Error: config.json not found.  Create it with 'token', 'images_path', and 'temp_path'.")
    sys.exit(1)  # Exit if config file is missing
except json.JSONDecodeError:
    print("Error: Invalid JSON in config.json")
    sys.exit(1)
except KeyError as e:
    print(f"Error: Missing key {e} in config.json")
    sys.exit(1)


# Path setup
images_path = os.path.join(os.path.dirname(__file__), IMAGES_PATH)
temp_path = os.path.join(TEMP_PATH, "temp_images")

# Logger setup
logger = logging.getLogger('logger')
fh = logging.FileHandler(os.path.join(os.path.dirname(__file__), "logs/d_bot.log"))
logger.addHandler(fh)

def exc_handler(exctype, value, tb):
    logger.exception(''.join(traceback.format_exception(exctype, value, tb)))

sys.excepthook = exc_handler

# Bot setup
intents = discord.Intents.default()  # Use default intents, then enable what you need
intents.message_content = True # Needed for reading message content
bot = commands.Bot(command_prefix='.', intents=intents)
bot.remove_command('help')

@bot.event
async def on_ready():
    print(f'Bot started successfully as {bot.user}.')
    await bot.change_presence(
        activity=discord.Activity(type=discord.ActivityType.watching, name=random.choice(["Your camera 📷", "Your house 🏠", "Everything 🤖"]))
    )

@bot.event
async def on_message(message):
    try:
        username = str(message.author.name)
        user_message = str(message.content)
        channel = str(message.channel.name)
        print(f'{username}: {user_message} ({channel})')
        await bot.process_commands(message)
    except Exception as e:
        logger.exception(f"Error in on_message: {e}")
        await message.channel.send("An error occurred. Please try again later.")

ALLOWED_EXTENSIONS = (".jpg", ".jpeg", ".png")

@bot.command()
async def addface(ctx, name):
    if not name.isalnum() or "_" in name:
        await ctx.send("Invalid name. Please use alphanumeric characters and no underscores.")
        return

    faces = [os.path.splitext(os.path.basename(face))[0] for ext in ALLOWED_EXTENSIONS for face in glob.glob(os.path.join(images_path, f"*{ext}"))]

    if name in faces:
        await ctx.send(f"**{name}** is already in the database.")
        return

    if not ctx.message.attachments:
        await ctx.send("No **image** attached to command.")
        return

    attachment = ctx.message.attachments[0]
    if not attachment.filename.lower().endswith(ALLOWED_EXTENSIONS):
        await ctx.send("Invalid file type. Only .jpg, .jpeg, and .png are allowed.")
        return

    try:
        img_data = requests.get(attachment.url).content
        temp_file_path = os.path.join(temp_path, f"ud_{name}.jpg")

        os.makedirs(temp_path, exist_ok=True) # Create the temp directory if it doesn't exist

        with open(temp_file_path, "wb") as handler:
            handler.write(img_data)

        facedet = FaceDet(os.path.dirname(__file__))  # Initialize facedet here
        detector = facedet.findface(temp_file_path, name)

        if detector:
            await ctx.send(f"**{name}** added to database.", file=discord.File(detector[2]))
            try: os.remove(detector[2]) # Remove the face detection output image
            except Exception as e: logger.error(f"Error removing detector output image: {e}")
        else:
            await ctx.send(f"**No face detected in image**.")

        os.remove(temp_file_path)  # Remove the temporary uploaded image
    except Exception as e:
        logger.exception(f"Error in addface: {e}")
        await ctx.send(f"An error occurred: {e}")
        try: os.remove(temp_file_path) # Attempt cleanup
        except: pass


@bot.command()
async def delface(ctx, name):
    faces = [os.path.splitext(os.path.basename(face))[0] for ext in ALLOWED_EXTENSIONS for face in glob.glob(os.path.join(images_path, f"*{ext}"))]

    if name in faces:
        for ext in ALLOWED_EXTENSIONS:
            file_path = os.path.join(images_path, f"{name}{ext}")
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                    await ctx.send(f"**{name}** removed from database.")
                    return  # Exit after successful deletion
                except Exception as e:
                    logger.exception(f"Error deleting file: {e}")
                    await ctx.send(f"Error deleting **{name}**. Please try again.")
                    return
        return  # If it gets here, the name was found but no matching file was deleted

    await ctx.send(f"**{name}** is not in the database.")



@bot.command()
async def listfaces(ctx):
    faces = [os.path.splitext(os.path.basename(face))[0] for ext in ALLOWED_EXTENSIONS for face in glob.glob(os.path.join(images_path, f"*{ext}"))]

    if not faces:
        await ctx.send("No faces in the database.")
        return

    message = ", ".join(faces)
    images = [discord.File(image) for face in faces for image in glob.glob(os.path.join(images_path, f"{face}.*")) if os.path.splitext(image)[1].lower() in ALLOWED_EXTENSIONS]

    try:
        if len(faces) > 1:
            await ctx.send(message + " (in order)", files=images)
        else:
            await ctx.send(message, files=images)
    except discord.HTTPException:
        await ctx.send(message)

@bot.command()
async def help(ctx):
    await ctx.send("**listfaces**, **delface** (name), **addface** (name) [attachment]")

async def main():
    await bot.start(TOKEN)

if __name__ == "__main__":
    asyncio.run(main())

