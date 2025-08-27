from dotenv import load_dotenv
import os

load_dotenv()

API_CREATE_GIFTS = os.getenv("API_CREATE_GIFTS")
HISTORY_URL = os.getenv("HISTORY_URL")
USER_BEARER = os.getenv("USER_BEARER")
USER_BEARER_BT = os.getenv("USER_BEARER_BT")
USERNAME_BT = os.getenv("USERNAME_BT")
PASSWORD_BT = os.getenv("PASSWORD_BT")
STATE_FILE = os.getenv("STATE_FILE")
TIME_FORMAT = os.getenv("TIME_FORMAT")
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")
