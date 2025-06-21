import telebot
import os
import webbrowser
import random
import time
import pyperclip
import re
from telebot import types
from dotenv import load_dotenv
from functools import wraps

# --- Placeholder for your custom modules ---
# Replace these with your actual imports from DataBase.*
def handle_downloads(message, bot, config):
    bot.send_message(message.chat.id, f"Received {message.content_type}. Handling download...")
    print(f"File would be saved to: {config.DOWNLOADS_PATH}")

def send_welcome_message(bot, chat_ids):
    for chat_id in chat_ids:
        try:
            bot.send_message(chat_id, "✅ IRISH Bot has started and is now online.")
        except Exception as e:
            print(f"Could not send start message to {chat_id}: {e}")

def handle_shutdown_command(message, bot):
    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton("✅ Yes, shut down", callback_data="confirm_shutdown_yes"),
        types.InlineKeyboardButton("❌ No, cancel", callback_data="confirm_shutdown_no")
    )
    bot.send_message(message.chat.id, "Are you sure you want to shut down the bot?", reply_markup=markup)

def handle_shutdown_confirmation(call, bot):
    if call.data == "confirm_shutdown_yes":
        bot.send_message(call.message.chat.id, "Bot is shutting down. Goodbye! 👋")
        bot.stop_polling()
        # In a real scenario, you might want a more graceful exit.
        # For this script, we'll just exit the process.
        os._exit(0)
    else:
        bot.edit_message_text("Shutdown canceled.", call.message.chat.id, call.message.message_id)

def handle_lock_command(message, bot):
    os.system("rundll32.exe user32.dll,LockWorkStation")
    bot.reply_to(message, "💻 PC Locked.")

def help_message():
    return """
    *IRISH Bot Commands*
    /start - Greet the bot
    /help - Show this help message
    /screenshot - Take and send a screenshot of the PC
    /lock - Lock the PC
    /shutdown - Shut down the bot process

    *Other Features:*
    - Send any text to copy it to the PC's clipboard.
    - Send a URL to get options to open or copy it.
    - Send a 12-digit Aadhaar number (e.g., `1234 5678 9012`) to copy it without spaces.
    - Send any file (document, photo, etc.) to download it to the PC's Downloads folder.
    """

def handle_screenshot_command(message, bot):
    try:
        import pyautogui
        screenshot = pyautogui.screenshot()
        screenshot_path = os.path.join(os.path.expanduser('~'), 'screenshot.png')
        screenshot.save(screenshot_path)
        with open(screenshot_path, 'rb') as photo:
            bot.send_photo(message.chat.id, photo, caption="Here is your screenshot.")
        os.remove(screenshot_path)
    except ImportError:
        bot.send_message(message.chat.id, "Error: `pyautogui` library is not installed. Cannot take a screenshot.")
    except Exception as e:
        bot.send_message(message.chat.id, f"An error occurred: {e}")
# --- End of placeholders ---


# --- Configuration and State Management ---

load_dotenv()

class Config:
    """Holds all static configuration for the bot."""
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    # Fallback to empty string if not set, then split handles it gracefully
    ALLOWED_CHAT_IDS = os.getenv("CHAT_IDS", "").split(",")
    # Cross-platform path to the user's Downloads folder
    DOWNLOADS_PATH = os.path.join(os.path.expanduser('~'), 'Downloads')
    
    if not BOT_TOKEN or not ALLOWED_CHAT_IDS[0]:
        raise ValueError("BOT_TOKEN and CHAT_IDS must be set in the .env file.")

class BotState:
    """Holds the dynamic state of the bot."""
    def __init__(self):
        self.last_url = {}  # Maps chat_id to the last URL sent

# --- Constants for Callbacks ---
CALLBACK_OPEN_URL = "open_url"
CALLBACK_COPY_URL = "copy_url"
CALLBACK_CANCEL_URL = "cancel_url"
CALLBACK_CONFIRM_SHUTDOWN_YES = "confirm_shutdown_yes"
CALLBACK_CONFIRM_SHUTDOWN_NO = "confirm_shutdown_no"


# --- Bot Initialization ---
bot = telebot.TeleBot(Config.BOT_TOKEN)
bot_state = BotState()


# --- Authorization Decorator ---
def authorized_only(func):
    """Decorator to check if the user is authorized."""
    @wraps(func)
    def wrapper(message: types.Message, *args, **kwargs):
        if str(message.chat.id) in Config.ALLOWED_CHAT_IDS:
            return func(message, *args, **kwargs)
        else:
            bot.reply_to(message, "🚫 You are not authorized to use this bot.")
            print(f"Unauthorized access attempt by chat ID: {message.chat.id}")
    return wrapper

# --- Command Handlers ---

@bot.message_handler(commands=['start'])
@authorized_only
def start_command(message: types.Message):
    user_first_name = message.from_user.first_name or "there"
    responses = [
        f"Welcome, {user_first_name}! IRISH at your service.",
        f"Hi {user_first_name}, how can IRISH help you today?",
        f"Hey {user_first_name}! IRISH is ready to assist you.",
        f"Greetings {user_first_name}! IRISH is online."
    ]
    bot.send_message(message.chat.id, random.choice(responses))

@bot.message_handler(commands=['shutdown'])
@authorized_only
def shutdown_command(message: types.Message):
    handle_shutdown_command(message, bot)

@bot.message_handler(commands=['lock'])
@authorized_only
def lock_command(message: types.Message):
    handle_lock_command(message, bot)

@bot.message_handler(commands=['help'])
@authorized_only
def help_command(message: types.Message):
    bot.send_message(message.chat.id, help_message(), parse_mode="Markdown")

@bot.message_handler(commands=['screenshot'])
@authorized_only
def screenshot_command(message: types.Message):
    handle_screenshot_command(message, bot)


# --- Message Handlers (Text, Files) ---

def is_aadhaar(text: str) -> bool:
    return bool(re.fullmatch(r"\d{4}\s\d{4}\s\d{4}", text.strip()))

def format_aadhaar(text: str) -> str:
    return text.replace(" ", "")

@bot.message_handler(content_types=['text'])
@authorized_only
def text_handler(message: types.Message):
    """Handles all incoming text messages."""
    chat_id = message.chat.id
    cleaned_text = "\n".join(line.strip() for line in message.text.splitlines() if line.strip())

    if not cleaned_text:
        return

    # 1. Aadhaar Logic
    if is_aadhaar(cleaned_text):
        formatted = format_aadhaar(cleaned_text)
        pyperclip.copy(formatted)
        bot.send_message(chat_id, f"✅ Aadhaar number copied: `{formatted}`", parse_mode="Markdown")
        return

    # 2. URL Logic
    if cleaned_text.startswith(("http://", "https://")):
        url = cleaned_text
        bot_state.last_url[chat_id] = url
        markup = types.InlineKeyboardMarkup(row_width=2)
        markup.add(
            types.InlineKeyboardButton("🌐 Open URL", callback_data=CALLBACK_OPEN_URL),
            types.InlineKeyboardButton("📋 Copy URL", callback_data=CALLBACK_COPY_URL),
            types.InlineKeyboardButton("❌ Cancel", callback_data=CALLBACK_CANCEL_URL)
        )
        bot.send_message(chat_id, f"What do you want to do with this URL?\n`{url}`", reply_markup=markup, parse_mode="Markdown")
        return

    # 3. Default: Copy any other text
    pyperclip.copy(cleaned_text)
    bot.send_message(chat_id, "✅ Text copied to clipboard.")

@bot.message_handler(content_types=['document', 'photo', 'video', 'voice', 'audio'])
@authorized_only
def file_handler(message: types.Message):
    handle_downloads(message, bot, Config)


# --- Callback Query Handler ---

@bot.callback_query_handler(func=lambda call: True)
def handle_all_callbacks(call: types.CallbackQuery):
    """A single handler for all callback queries."""
    chat_id = call.message.chat.id
    
    # Always a good idea to check authorization on callbacks too
    if str(chat_id) not in Config.ALLOWED_CHAT_IDS:
        bot.answer_callback_query(call.id, text="🚫 Unauthorized", show_alert=True)
        return

    # Route based on callback data
    if call.data in [CALLBACK_CONFIRM_SHUTDOWN_YES, CALLBACK_CONFIRM_SHUTDOWN_NO]:
        handle_shutdown_confirmation(call, bot)

    elif call.data in [CALLBACK_OPEN_URL, CALLBACK_COPY_URL, CALLBACK_CANCEL_URL]:
        handle_url_action(call)
    
    # Acknowledge any other callbacks we might have missed
    else:
        bot.answer_callback_query(call.id)

def handle_url_action(call: types.CallbackQuery):
    """Handles callbacks related to URL actions."""
    chat_id = call.message.chat.id
    url = bot_state.last_url.get(chat_id)

    if not url:
        bot.answer_callback_query(call.id, "Original URL not found (bot may have restarted).", show_alert=True)
        bot.edit_message_text("Action expired.", chat_id, call.message.message_id)
        return

    if call.data == CALLBACK_OPEN_URL:
        webbrowser.open(url)
        bot.edit_message_text("✅ URL Opened.", chat_id, call.message.message_id)
        bot.answer_callback_query(call.id, text="🌐 Opening URL...")
    elif call.data == CALLBACK_COPY_URL:
        pyperclip.copy(url)
        bot.edit_message_text("✅ URL copied to clipboard.", chat_id, call.message.message_id)
        bot.answer_callback_query(call.id, text="📋 Copied!")
    elif call.data == CALLBACK_CANCEL_URL:
        bot.edit_message_text("❌ Action canceled.", chat_id, call.message.message_id)
        bot.answer_callback_query(call.id)
    
    # Clear the URL after action to prevent reuse
    if chat_id in bot_state.last_url:
        del bot_state.last_url[chat_id]


# --- Main Execution Block ---

if __name__ == "__main__":
    os.system('cls' if os.name == 'nt' else 'clear')
    print("🚀 Starting IRISH Bot...")
    
    try:
        send_welcome_message(bot, Config.ALLOWED_CHAT_IDS)
        print(f"Bot started. Authorized chats: {Config.ALLOWED_CHAT_IDS}")
        # Use non_stop polling for resilience
        bot.polling(non_stop=True, interval=1)
    except Exception as e:
        print(f"🔥 A critical error occurred: {e}")
        time.sleep(10)
        # In a real deployment, you might use a process manager like systemd
        # to automatically restart the script.