import time
import requests

# ==============================
# TELEGRAM BOT CONFIG
# ==============================

BOT_TOKEN = "8369673752:AAGChqjqvpQ3DW89WGgFW8IRTW94BjC2aoo"
CHAT_ID = "6918721957"

TELEGRAM_API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

# ==============================
# SEND MESSAGE FUNCTION
# ==============================

def send_message(text):
    payload = {
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "HTML"
    }
    try:
        response = requests.post(TELEGRAM_API_URL, data=payload, timeout=10)
        return response.json()
    except Exception as e:
        print("Telegram Error:", e)

# ==============================
# BOT START
# ==============================

if __name__ == "__main__":
    send_message("🤖 <b>Signal bot is ONLINE</b>\nScanning the market 24/7...")

    while True:
        send_message("📊 <b>TEST SIGNAL</b>\nAsset: EUR/USD\nDirection: BUY\nTimeframe: 1 MIN")
        time.sleep(60)
