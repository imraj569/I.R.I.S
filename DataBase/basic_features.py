import subprocess, os, random
from telebot import types
from datetime import datetime

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

def _wish_hour_wise(username):
    morning_wishes = [
        f"Good Morning! 🌄 {username}",
        f"Rise and shine! ☀️ {username}",
        f"Wishing you a productive morning! 💼 {username}",
        f"Top of the morning to you! 🌅 {username}"
    ]
    afternoon_wishes = [
        f"Good Afternoon! 🙋‍♀️ {username}!",
        f"Hope your afternoon is going well! 🌞 {username}",
        f"Keep up the great work this afternoon! 💪 {username}",
        f"Enjoy your afternoon! 🍵 {username}"
    ]
    evening_wishes = [
        f"Good Evening! 💕 {username}",
        f"Hope you had a wonderful day! 🌆 {username}",
        f"Relax and enjoy your evening! 🌙 {username}",
        f"Wishing you a peaceful evening! 🕯️ {username}"
    ]
    night_wishes = [
        f"Hope you had a great day! 🌙 {username}!",
        f"Good night and sweet dreams! 😴 {username}",
        f"Rest well, {username}! 🌜",
        f"Wishing you a restful night! 💤 {username}"
    ]

    hour = datetime.now().hour
    if 5 <= hour < 12:
        return random.choice(morning_wishes)
    elif 12 <= hour < 17:
        return random.choice(afternoon_wishes)
    elif 17 <= hour < 21:
        return random.choice(evening_wishes)
    else:
        return random.choice(night_wishes)

def send_welcome_message(bot, CHAT_IDS):
    for chat_id in CHAT_IDS:
        try:
            user = bot.get_chat(chat_id)
            username = user.first_name or user.username or "there"
            wish = _wish_hour_wise(username)
            bot.send_message(chat_id, wish)
        except Exception as e:
            print(f"Could not send welcome message to {chat_id}: {e}")