import requests
import os

# Credentials (Loaded from Env vars for security on Render)
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "8524623570:AAEEpmyVbTCu7z2aC56Ek-pLayoV3Er_uBA") 
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "5344147903") 

def send_telegram_message(message):
    """Sends a message to the specified Telegram chat."""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("Telegram Token or Chat ID not set. Skipping notification.")
        return False
        
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "HTML"
    }
    
    try:
        response = requests.post(url, json=payload)
        if response.status_code != 200:
            print(f"Telegram API Error: {response.status_code} - {response.text}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error sending Telegram notification: {e}")
        return False
