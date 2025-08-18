
import requests
import time
from load_env import DISCORD_WEBHOOK_URL


def send_notification_discord(message):
    """
    Send a message to a Discord channel using a webhook.
    """
    try:
        data = {
            "content": message
        }
        response = requests.post(DISCORD_WEBHOOK_URL, json=data)
        time.sleep(1)  # To avoid hitting rate limits
        if response.status_code != 204:
            print(f"Failed to send Discord notification: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Error sending Discord notification: {str(e)}")