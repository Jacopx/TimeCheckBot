from dotenv import load_dotenv
load_dotenv()

import os

# Telegram Bot Token (from BotFather)
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN", "YOUR_BOT_TOKEN_HERE")

# Google Sheets
SPREADSHEET_ID = os.environ.get("SPREADSHEET_ID", "YOUR_SPREADSHEET_ID_HERE")
SHEET_NAME = "BotData"
CREDENTIALS_FILE = "credentials.json"

# Timezone (Italy)
TIMEZONE = "Europe/Rome"
