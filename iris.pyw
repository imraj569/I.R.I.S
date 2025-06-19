import telebot, os, webbrowser, random, time, pyperclip
from telebot import types
from dotenv import load_dotenv

# It's better to import specific functions instead of using '*'
from DataBase.handle_files import handle_downloads
from DataBase.basic_features import (
    handle_lock_command, 
    handle_shutdown_command, 
    handle_shutdown_confirmation,
    send_welcome_message,
    INTERACTION_STICKERS, # Use constants
    WELCOME_STICKERS # Use constants
)

load_dotenv()

# --- CONFIGURATION ---
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_IDS = os.getenv("CHAT_IDS").split(",")
USERNAME = os.getlogin()
CONFIG = {
    'downloads_path': os.path.join(f"C:\\Users\\{USERNAME}\\Downloads"),
}
bot = telebot.TeleBot(BOT_TOKEN)

# A simple in-memory store for the last URL. Works for single-user context.
last_url = {}

# --- AUTHORIZATION ---
def is_authorized(chat_id):
    return str(chat_id) in CHAT_IDS

# 1. Command Handlers (Most Specific Text)
@bot.message_handler(commands=['start'])
def handle_start_command(message):
    if is_authorized(message.chat.id):
        bot.send_sticker(message.chat.id, random.choice(WELCOME_STICKERS))
        welcome_messages = [
            "Iris is awake and ready to assist! ✨",
            "Hello! Iris at your service.😊",
            "👋 Hi there! Iris is online and listening.",
            "Ready to go! 🚀 Iris is here for you.",
            "Iris is up and running. 💡"
        ]
        bot.send_message(message.chat.id, random.choice(welcome_messages))
    else:
        bot.send_message(message.chat.id, "You are not authorized to use this bot.")

@bot.message_handler(commands=['shutdown'])
def handle_shutdown(message):
    handle_shutdown_command(message, bot, is_authorized)

@bot.message_handler(commands=['lock'])
def lock_pc(message):
    handle_lock_command(message, bot, is_authorized)

# 2. Callback Query Handlers (Specific Callbacks First)
@bot.callback_query_handler(func=lambda call: call.data in ["confirm_yes", "confirm_no"])
def handle_shutdown_callback(call):
    handle_shutdown_confirmation(call, bot, is_authorized)

@bot.callback_query_handler(func=lambda call: call.data in ["open_url", "copy_url", "cancel_url"])
def handle_url_callback(call):
    chat_id = call.message.chat.id
    url_to_handle = last_url.get(chat_id)

    if not is_authorized(chat_id):
        bot.answer_callback_query(call.id, "Not authorized.")
        return

    if call.data == "open_url":
        if url_to_handle:
            webbrowser.open(url_to_handle)
            bot.edit_message_text("🌐 URL opened successfully.", chat_id, call.message.message_id)
            bot.send_sticker(chat_id, random.choice(INTERACTION_STICKERS))
        else:
            bot.edit_message_text("⚠️ No URL found to open. Please send a URL again.", chat_id, call.message.message_id)

    elif call.data == "copy_url":
        if url_to_handle:
            pyperclip.copy(url_to_handle)
            bot.edit_message_text("📋 URL copied to clipboard.", chat_id, call.message.message_id)
            bot.send_sticker(chat_id, random.choice(INTERACTION_STICKERS))
        else:
            bot.edit_message_text("⚠️ No URL found to copy. Please send a URL again.", chat_id, call.message.message_id)

    elif call.data == "cancel_url":
        bot.edit_message_text("❌ Action canceled.", chat_id, call.message.message_id)
    
    # Acknowledge the callback to remove the "loading" icon on the button
    bot.answer_callback_query(call.id)

# 3. Generic Message Handlers (Text, Files)
@bot.message_handler(content_types=['text'])
def handle_text_message(message):
    if not is_authorized(message.chat.id):
        bot.reply_to(message, "You are not authorized to use this bot.")
        return

    cleaned_text = message.text.strip()
    
    if cleaned_text.startswith(("http://", "https://")):
        # Handle URL
        url = cleaned_text
        last_url[message.chat.id] = url
        pyperclip.copy(url)

        markup = types.InlineKeyboardMarkup()
        markup.add(
            types.InlineKeyboardButton("🔓 Open URL", callback_data="open_url"),
            types.InlineKeyboardButton("📋 Copy URL", callback_data="copy_url"),
            types.InlineKeyboardButton("❌ Cancel", callback_data="cancel_url")
        )
        bot.send_message(
            message.chat.id, 
            f"✅ URL copied to clipboard.\n\nWhat would you like to do with this URL?\n{url}", 
            reply_markup=markup
        )
    else:
        # Handle normal text
        pyperclip.copy(cleaned_text)
        bot.send_message(message.chat.id, "✅ Text copied to clipboard. 📋")
        bot.send_sticker(message.chat.id, random.choice(INTERACTION_STICKERS))

@bot.message_handler(content_types=['document', 'photo', 'video', 'voice', 'audio'])
def process_uploaded_files(message):  
    handle_downloads(message, bot, is_authorized, CONFIG)

# --- MAIN EXECUTION ---
def main():
    print("Bot is starting...")
    send_welcome_message(bot, CHAT_IDS)
    bot.polling(non_stop=True, interval=0) # Use non_stop=True for cleaner looping

if __name__ == "__main__":
    while True:
        try:
            main()
        except Exception as e:
            print(f"An error occurred: {e}")
            print("Restarting in 5 seconds...")
            time.sleep(5)