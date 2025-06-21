import os
import re
import time
import telebot # Assuming you use pyTelegramBotAPI, adjust if necessary
from typing import Callable, Dict

# It's better to be explicit with imports instead of using '*'
# from DataBase.basic_features import is_authorized, get_config 

# --- Helper Function for Sanitizing Filenames ---

def _sanitize_filename(filename: str) -> str:
    """
    Removes characters that are invalid in filenames on most OSes.
    Also removes leading/trailing whitespace and dots.
    """
    if not filename:
        return ""
    # Remove invalid characters
    sanitized = re.sub(r'[\\/*?:"<>|]', "", filename)
    # Remove leading/trailing whitespace and dots, which can cause issues
    sanitized = sanitized.strip().strip('.')
    return sanitized

# --- Main Handler Function ---

def handle_downloads(message: telebot.types.Message, bot: telebot.TeleBot, is_authorized: Callable, config: Dict):
    """
    Handles downloading files, photos, videos, audio, and voice messages sent to the bot.
    Refactored for clarity, maintainability, and to avoid code repetition.
    """
    if not is_authorized(message.chat.id):
        bot.send_message(message.chat.id, "You are not authorized to use this bot.")
        return

    # --- Step 1: Extract file information based on content type ---
    content_type = message.content_type
    file_id = None
    original_filename = ""
    ui_name = content_type # User-friendly name for messages
    
    try:
        if content_type == 'document':
            doc = message.document
            file_id = doc.file_id
            original_filename = doc.file_name
            ui_name = "document 📩"
        
        elif content_type == 'photo':
            photo = message.photo[-1] # Highest resolution
            file_id = photo.file_id
            # Use caption for filename, otherwise generate a timestamped name
            if message.caption:
                original_filename = f"{message.caption}.jpg"
            else:
                timestamp = time.strftime('%Y%m%d_%H%M%S')
                original_filename = f"photo_{timestamp}.jpg"
            ui_name = "photo 📷"

        elif content_type == 'video':
            video = message.video
            file_id = video.file_id
            # Prefer the original filename if available, else generate one
            original_filename = video.file_name or f"video_{time.strftime('%Y%m%d_%H%M%S')}.mp4"
            ui_name = "video 🎥"

        elif content_type == 'audio':
            audio = message.audio
            file_id = audio.file_id
            original_filename = audio.file_name or "audio.mp3"
            ui_name = "audio 🎵"
            
        elif content_type == 'voice':
            voice = message.voice
            file_id = voice.file_id
            timestamp = time.strftime('%Y%m%d_%H%M%S')
            original_filename = f"voice_{timestamp}.ogg" # Voice messages are typically .ogg
            ui_name = "voice message 🎤"
        
        else:
            # This handles any other content types that might be sent
            return

        # --- Step 2: Sanitize the filename and prepare for download ---
        safe_filename = _sanitize_filename(original_filename)
        
        # If sanitizing results in an empty filename, create a default one
        if not safe_filename:
            timestamp = time.strftime('%Y%m%d_%H%M%S')
            safe_filename = f"download_{timestamp}"

        download_path = os.path.join(config['downloads_path'], safe_filename)

        # --- Step 3: Download the file and save it ---
        bot.send_message(message.chat.id, f"Please wait, downloading {ui_name}...")
        
        file_info = bot.get_file(file_id)
        downloaded_file = bot.download_file(file_info.file_path)

        with open(download_path, 'wb') as f:
            f.write(downloaded_file)

        bot.send_message(message.chat.id, f"Success! '{safe_filename}' downloaded. ✅🎉")

    except Exception as e:
        # Log the full error for debugging, but send a user-friendly message
        print(f"An error occurred while handling download for chat {message.chat.id}: {e}")
        bot.send_message(message.chat.id, f"❌ An error occurred while downloading the file. Please try again.")