import subprocess, os, random
from telebot import types
from datetime import datetime

# SUGGESTION: Use constants for static data instead of functions.
# It's more conventional and slightly more performant.
WELCOME_STICKERS = [
    "CAACAgIAAxkBAAJf5WfmtVXidHnj67roSiWpylWDS9O5AAK0JwACvjCQSk_nZILWHmN8NgQ",
    "CAACAgIAAxkBAAJf-2fmtw-rwqAifoZyrfqMMYapm9z9AAK_LAACTfaRSh-GXIPitZ5INgQ",
    "CAACAgIAAxkBAAJf72fmtYVTX-Lp4fq9QyUiMsM_eopcAAJ0MwACyRiRSmcbBQMdUrBJNgQ"
]

INTERACTION_STICKERS = [
    "CAACAgUAAxkBAAJfL2fibm3cr9uiuMDNRGet9J6B889jAAIQFwACoeIRVyFZ0CncMXujNgQ",
    "CAACAgIAAxkBAAJf5GfmtUZY74OoyVzSIQPEs6YeCNNWAAIbKgACAheQSpxgKEc6i5NTNgQ",
    "CAACAgIAAxkBAAJf-WfmtvmYSILvqv7ZtzoaKxG_WNqQAAKUKwACFuqQSuNJI0k3VjqWNgQ",
    "CAACAgIAAxkBAAJf-2fmtw-rwqAifoZyrfqMMYapm9z9AAK_LAACTfaRSh-GXIPitZ5INgQ"
]

def handle_lock_command(message, bot, is_authorized):
    if is_authorized(message.chat.id):
        bot.send_message(message.chat.id, "PC is Locked 🔐")
        subprocess.run(["rundll32.exe", "user32.dll,LockWorkStation"])
    else:
        bot.send_message(message.chat.id, "You are not authorized to use this bot.")

def handle_shutdown_command(message, bot, is_authorized):
    if is_authorized(message.chat.id):
        markup = types.InlineKeyboardMarkup()
        yes_button = types.InlineKeyboardButton("✅ Yes", callback_data="confirm_yes")
        no_button = types.InlineKeyboardButton("❌ No", callback_data="confirm_no")
        markup.add(yes_button, no_button)
        bot.send_message(message.chat.id, "⚠️ Are you sure you want to shut down the PC?", reply_markup=markup)
    else:
        bot.send_message(message.chat.id, "You are not authorized to use this bot.")

def _shutdown_pc():
    # It's safer to use the full path for system commands in some environments
    os.system("shutdown /s /t 5")

def handle_shutdown_confirmation(call, bot, is_authorized):
    if is_authorized(call.message.chat.id):
        if call.data == "confirm_yes":
            # Edit the original message to give feedback
            bot.edit_message_text("✅ Confirmed. Shutting down the PC in 5 seconds...", call.message.chat.id, call.message.message_id)
            _shutdown_pc()
        elif call.data == "confirm_no":
            bot.edit_message_text("❌ Shutdown cancelled.", call.message.chat.id, call.message.message_id)
    else:
        bot.send_message(call.message.chat.id, "You are not authorized to use this bot.")
    bot.answer_callback_query(call.id) # Acknowledge the callback

def _wish_hour_wise():
   hour = datetime.now().hour
   if 5 <= hour < 12:
     return "Good Morning! 🌄 Boss"
   elif 12 <= hour < 17:
     return "Good Afternoon! 🙋‍♀️ Boss!"
   elif 17 <= hour < 21:
     return "Good Evening! 💕 Boss"
   else:
     return "Hope you had a great day! 🌙 Boss!"

def send_welcome_message(bot, CHAT_IDS):
    wish = _wish_hour_wise()
    for chat_id in CHAT_IDS:
        try:
            bot.send_sticker(chat_id, random.choice(WELCOME_STICKERS))
            bot.send_message(chat_id, wish)
        except Exception as e:
            print(f"Could not send welcome message to {chat_id}: {e}")