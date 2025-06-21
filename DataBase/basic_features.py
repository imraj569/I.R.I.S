import subprocess
import os
import random
import tempfile
import pyautogui
from telebot import types
from datetime import datetime
import platform  # For checking the operating system
import logging   # For robust logging

# --- Better Logging Setup ---
# Using the logging module is more professional than print() for debugging.
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("bot.log"), # Log to a file
        logging.StreamHandler()         # Log to the console
    ]
)
logger = logging.getLogger(__name__)

class PCBotHandlers:
    """
    A class to organize all bot command handlers.
    This makes the code cleaner, more modular, and easier to maintain.
    """

    def __init__(self, bot, authorized_chat_ids):
        self.bot = bot
        self.AUTHORIZED_CHAT_IDS = set(authorized_chat_ids) # Use a set for faster lookups

    def is_authorized(self, chat_id):
        """Checks if a user's chat_id is in the authorized list."""
        return chat_id in self.AUTHORIZED_CHAT_IDS

    def _execute_command(self, command_args):
        """A safer, more robust way to run system commands."""
        try:
            # This part hides the console window on Windows for a cleaner execution
            startup_info = None
            if platform.system() == "Windows":
                startup_info = subprocess.STARTUPINFO()
                startup_info.dwFlags |= subprocess.STARTF_USESHOWWINDOW

            subprocess.run(command_args, check=True, text=True, capture_output=True, startupinfo=startup_info)
            logger.info(f"Command '{' '.join(command_args)}' executed successfully.")
            return True, None
        except FileNotFoundError:
            error_msg = f"Command not found: {command_args[0]}"
            logger.error(error_msg)
            return False, error_msg
        except subprocess.CalledProcessError as e:
            error_msg = f"Command failed: {e.stderr}"
            logger.error(error_msg)
            return False, error_msg
        except Exception as e:
            error_msg = f"An unexpected error occurred: {e}"
            logger.error(error_msg)
            return False, error_msg

    # --- System Control Commands (Now Cross-Platform) ---

    def handle_lock_command(self, message):
        """Handles the /lock command with support for multiple operating systems."""
        if not self.is_authorized(message.chat.id):
            self.bot.reply_to(message, "❌ You are not authorized to use this bot.")
            return

        os_name = platform.system()
        command = []
        if os_name == "Windows":
            command = ["rundll32.exe", "user32.dll,LockWorkStation"]
        elif os_name == "Linux":
            # This is a common command, but might vary with desktop environments
            command = ["xdg-screensaver", "lock"]
        elif os_name == "Darwin":  # macOS
            command = ["pmset", "displaysleepnow"]
        else:
            self.bot.reply_to(message, f"Unsupported OS for lock command: {os_name}")
            return

        success, error = self._execute_command(command)
        if success:
            self.bot.reply_to(message, "🖥️ PC has been locked.")
        else:
            self.bot.reply_to(message, f"❌ Failed to lock PC. Reason: {error}")

    def handle_power_command(self, message, action='shutdown'):
        """A single handler for shutdown and restart confirmations."""
        if not self.is_authorized(message.chat.id):
            self.bot.reply_to(message, "❌ You are not authorized to use this bot.")
            return

        action_name = action.capitalize()
        markup = types.InlineKeyboardMarkup(row_width=2)
        yes_button = types.InlineKeyboardButton(f"✅ Yes, {action_name}", callback_data=f"confirm_{action}_yes")
        no_button = types.InlineKeyboardButton("❌ No, Cancel", callback_data=f"confirm_{action}_no")
        markup.add(yes_button, no_button)
        self.bot.reply_to(message, f"⚠️ Are you sure you want to {action} the PC?", reply_markup=markup)

    def _execute_power_off(self, action='shutdown'):
        """Internal function to perform shutdown or restart.
        NOTE: On Linux/macOS, this may require 'sudo' privileges.
        """
        os_name = platform.system()
        command = []
        delay = "30"  # 30-second delay

        if os_name == "Windows":
            flag = "/s" if action == 'shutdown' else "/r"
            command = ["shutdown", flag, "/t", delay]
        elif os_name in ["Linux", "Darwin"]:
            # Requires passwordless sudo for the 'shutdown' command for the bot's user
            flag = "-h" if action == 'shutdown' else "-r"
            command = ["sudo", "shutdown", flag, "+0"] # +0 means in less than a minute
        else:
            return False, f"Unsupported OS for {action}: {os_name}"

        return self._execute_command(command)

    def handle_power_confirmation(self, call):
        """Handles the inline keyboard callback for power commands."""
        if not self.is_authorized(call.message.chat.id):
            self.bot.answer_callback_query(call.id, "Unauthorized", show_alert=True)
            return

        parts = call.data.split('_') # e.g., "confirm_shutdown_yes"
        action, confirmation = parts[1], parts[2]

        if confirmation == "no":
            self.bot.edit_message_text(f"✅ {action.capitalize()} cancelled.", call.message.chat.id, call.message.message_id)
            return

        # If "yes"
        self.bot.edit_message_text(f"🔌 Executing {action}... The PC will {action} in about 30 seconds.", call.message.chat.id, call.message.message_id)
        success, error = self._execute_power_off(action)
        if not success:
            # Send a new message if execution fails, as the bot might shut down before the edit completes
            self.bot.send_message(call.message.chat.id, f"❌ Failed to {action} PC. Reason: {error}")

    def handle_cancel_shutdown_command(self, message):
        """Handles the command to cancel a scheduled shutdown/restart."""
        if not self.is_authorized(message.chat.id):
            self.bot.reply_to(message, "❌ You are not authorized.")
            return
        
        os_name = platform.system()
        command = []
        if os_name == "Windows":
            command = ["shutdown", "/a"]
        elif os_name in ["Linux", "Darwin"]:
            command = ["sudo", "shutdown", "-c"]
        else:
            self.bot.reply_to(message, f"Unsupported OS: {os_name}")
            return
            
        success, error = self._execute_command(command)
        if success:
            self.bot.reply_to(message, "✅ Shutdown/Restart has been cancelled.")
        else:
            self.bot.reply_to(message, f"❌ Failed to cancel. Reason: {error or 'No pending shutdown.'}")


    # --- Utility Commands ---

    def handle_screenshot_command(self, message):
        """Takes a screenshot and sends it to the user with better feedback."""
        if not self.is_authorized(message.chat.id):
            self.bot.reply_to(message, "❌ You are not authorized.")
            return
        
        msg = None
        try:
            msg = self.bot.reply_to(message, "📸 Taking a screenshot, please wait...")
            screenshot = pyautogui.screenshot()
            
            # Using a temporary file is a great, safe approach
            with tempfile.NamedTemporaryFile(delete=True, suffix='.png') as temp_path:
                screenshot.save(temp_path.name)
                with open(temp_path.name, 'rb') as photo:
                    self.bot.send_photo(message.chat.id, photo, caption="✅ Screenshot captured!")
            
            # Clean up the "please wait" message
            self.bot.delete_message(message.chat.id, msg.message_id)
        except Exception as e:
            logger.error(f"Error taking screenshot: {e}")
            if msg:
                self.bot.edit_message_text(f"❌ Failed to take screenshot.\nError: {e}", message.chat.id, msg.message_id)
            else:
                self.bot.reply_to(message, f"❌ Failed to take screenshot.\nError: {e}")


    # --- Welcome and Help Messages ---

    @staticmethod
    def _wish_hour_wise(first_name):
        """Generates a time-appropriate greeting. Your original function was already great!"""
        hour = datetime.now().hour
        wishes = []
        if hour < 12:
            wishes = [f"Good Morning, {first_name}! ☀️ Rise and shine!", f"Top of the morning to you, {first_name}! 🌞"]
        elif 12 <= hour < 17:
            wishes = [f"Good Afternoon, {first_name}! ☀️", f"Hope your day is going well, {first_name}! 🌻"]
        elif 17 <= hour < 21:
            wishes = [f"Good Evening, {first_name}! 🌇", f"Hope you had a great day, {first_name}! 🌃"]
        else:
            wishes = [f"Good Night, {first_name}! 🌙 Sweet dreams!", f"Rest well, {first_name}! 😴"]
        return random.choice(wishes)

    def send_welcome_message(self):
        """Sends a personalized welcome message to all authorized users."""
        for chat_id in self.AUTHORIZED_CHAT_IDS:
            try:
                user = self.bot.get_chat(chat_id)
                first_name = user.first_name if hasattr(user, 'first_name') else "there"
                wish = self._wish_hour_wise(first_name)
                self.bot.send_message(chat_id, wish)
                logger.info(f"Sent welcome message to {chat_id} ({first_name})")
            except Exception as e:
                logger.error(f"Failed to send welcome message to chat_id {chat_id}: {e}")

    @staticmethod
    def get_help_message():
        """Returns a more detailed and richly formatted help message using Markdown."""
        return """
*Your Personal PC Assistant* 🤖

Here's a list of my capabilities:

*Automatic Features:*
📋 *Clipboard*: Any text you send is automatically copied to the PC's clipboard.
🔗 *URL Opener*: Any URL you send is opened in the default browser.
💾 *File Downloader*: Any file you send is saved to the Downloads folder.

*Available Commands:*
`/start` - 🎉 Starts the bot and shows a welcome message.
`/help` - 📜 Displays this help message.
`/screenshot` - 📸 Takes and sends a screenshot of your primary display.
`/lock` - 🖥️ Locks your PC immediately.

*Power Control:*
`/shutdown` - 🔌 Shuts down your PC after confirmation.
`/restart` - 🔄 Restarts your PC after confirmation.
`/cancel` - 🚫 Cancels a pending shutdown or restart.

_*Note:* Power commands on Linux/macOS might require special permissions._
        """