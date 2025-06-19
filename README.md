# I.R.I.S. - Intelligent Remote Interaction System 🤖

A powerful, yet simple, Python-based Telegram bot designed to give you secure remote control over your Windows PC from anywhere in the world, right from your phone.

![-----------------------------------------------------](https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/rainbow.png)

## ✨ Key Features

*   **💻 Remote Command Execution:** Run any shell command directly from Telegram.
*   **📂 File Management:** Upload files from your PC to Telegram or download files from Telegram to your PC's `Downloads` folder.
*   **📸 Real-time Screenshots:** Instantly grab a screenshot of your PC's current display.
*   **📋 Cross-device Clipboard:** Send text or links to your bot to have them instantly copied to your PC's clipboard.
*   **🔐 Power & Session Control:** Securely lock, shut down, or restart your PC with confirmation.
*   **🛡️ Secure & Authorized:** Only pre-approved Chat IDs can interact with the bot.

![-----------------------------------------------------](https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/rainbow.png)

## 🚀 Getting Started

Follow these steps to get I.R.I.S. up and running on your system.

### Prerequisites

*   Python 3.x
*   A Telegram Account
*   Git

### Installation & Setup

1.  **Clone the repository:**
    ```sh
    git clone https://github.com/imraj569/I.R.I.S.git
    cd I.R.I.S
    ```

2.  **Install dependencies:**
    *(First, ensure you have a `requirements.txt` file with the following content, then run the command.)*

    **`requirements.txt`:**
    ```
    pyTelegramBotAPI
    python-dotenv
    pyperclip
    Pillow
    ```

    **Installation command:**
    ```sh
    pip install -r requirements.txt
    ```

3.  **Configure Environment Variables:**

    Create a file named `.env` in the project's root directory. This file will store your secret credentials.

    *   **Get your Bot Token:** Talk to [@BotFather](https://t.me/BotFather) on Telegram to create a new bot and get its unique token.
    *   **Get your Chat ID:** Talk to [@userinfobot](https://t.me/userinfobot) on Telegram to find your unique numeric Chat ID.

    Add your credentials to the `.env` file like this:
    ```env
    # .env file

    BOT_TOKEN="YOUR_TELEGRAM_BOT_TOKEN_HERE"
    CHAT_IDS="YOUR_CHAT_ID_1,ANOTHER_AUTHORIZED_CHAT_ID_2"
    ```
    > **Note:** You can add multiple chat IDs separated by commas to authorize more than one user.

4.  **Run the Bot:**
    Execute the main script, and I.R.I.S. will come to life!
    ```sh
    python iris.py
    ```

![-----------------------------------------------------](https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/rainbow.png)

## 🤖 Command List

Here are all the commands you can use to interact with I.R.I.S.:

*   `/start` - Checks if the bot is awake and ready.
*   `/help` - Shows the list of available commands.
*   `/lock` - Locks the PC's screen.
*   `/shutdown` - Initiates PC shutdown with a confirmation prompt.
*   `/screenshot` - Takes and sends a screenshot of the current display.
*   `/run <command>` - Executes a shell command (e.g., `/run ipconfig`).
*   `/upload <full_path_to_file>` - Uploads a specified file from the PC.
*   **Send any text/URL** - Copies the text to the PC's clipboard.
*   **Send any file (photo, doc, video, etc.)** - Downloads the file to the PC's `Downloads` folder.

![-----------------------------------------------------](https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/rainbow.png)

## ⚠️ Disclaimer

This project is intended for **educational purposes only**. It demonstrates the capabilities of Python for remote automation and interaction with APIs. The creator is not responsible for any illegal or malicious activities conducted using this bot. Use it responsibly and only on devices you own and have permission to manage.

![-----------------------------------------------------](https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/rainbow.png)

## 🧑‍💻 Connect With Me

Feel free to reach out, and let's connect!

<a href="https://github.com/imraj569" target="_blank">
<img src=https://img.shields.io/badge/github-%2324292e.svg?&style=for-the-badge&logo=github&logoColor=white alt=github style="margin-bottom: 5px;" />
</a>
<a href="https://www.instagram.com/im.raj.569/" target="_blank">
<img src=https://img.shields.io/badge/instagram-%23000000.svg?&style=for-the-badge&logo=instagram&logoColor=white alt=instagram style="margin-bottom: 5px;" />
</a>
