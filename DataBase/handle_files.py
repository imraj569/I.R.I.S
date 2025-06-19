import os
import random
import time

def sanitize_filename(filename):
    """Removes characters that are illegal in Windows filenames."""
    if not filename:
        return ""
    return "".join(c for c in filename if c not in r'\/:*?"<>|')

def _download_and_save_file(message, bot, file_id, file_path, download_path, original_filename, file_type_emoji):
    """Helper function to download and save any file type."""
    try:
        bot.send_message(message.chat.id, f"Please wait, downloading {file_type_emoji} {original_filename}...")
        
        file_info = bot.get_file(file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        
        with open(download_path, 'wb') as f:
            f.write(downloaded_file)

        bot.send_message(message.chat.id, f"File '{os.path.basename(download_path)}' downloaded successfully! ✅🎉")
    
    except Exception as e:
        error_message = f"Error downloading file: {str(e)}"
        print(error_message)
        bot.send_message(message.chat.id, error_message)
        bot.send_sticker(message.chat.id, "CAACAgIAAxkBAAJgO2fmwOZMqxvVtOkx_5jU3NtIe9g0AAJbJwACtr6RShhscyk6rv-KNgQ") # Error sticker

def handle_downloads(message, bot, is_authorized, config):
    if not is_authorized(message.chat.id):
        bot.send_message(message.chat.id, "You are not authorized to use this bot.")
        return

    downloads_dir = config['downloads_path']
    timestamp = time.strftime('%Y%m%d_%H%M%S')
    
    content_type = message.content_type
    file_id = None
    original_filename = ""
    file_type_emoji = "📄"

    if content_type == 'document':
        file_id = message.document.file_id
        original_filename = message.document.file_name
        file_type_emoji = "📩"
    
    elif content_type == 'photo':
        file_id = message.photo[-1].file_id # Highest resolution
        sanitized_caption = sanitize_filename(message.caption)
        original_filename = f"{sanitized_caption}.jpg" if sanitized_caption else f"photo_{timestamp}.jpg"
        file_type_emoji = "📷"

    elif content_type == 'video':
        file_id = message.video.file_id
        original_filename = f"video_{timestamp}.mp4"
        file_type_emoji = "🎥"
        
    elif content_type == 'voice':
        file_id = message.voice.file_id
        original_filename = f"voice_{timestamp}.ogg"
        file_type_emoji = "🎤"

    elif content_type == 'audio':
        file_id = message.audio.file_id
        original_filename = sanitize_filename(message.audio.file_name) or f"audio_{timestamp}.mp3"
        file_type_emoji = "🎵"

    if file_id:
        download_path = os.path.join(downloads_dir, original_filename)
        _download_and_save_file(message, bot, file_id, None, download_path, original_filename, file_type_emoji)